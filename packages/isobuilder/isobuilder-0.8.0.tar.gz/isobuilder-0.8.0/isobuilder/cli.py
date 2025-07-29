# /usr/bin/env python3
"""CLi too for building ISOs"""
import logging

from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentParser,
    Namespace,
    RawDescriptionHelpFormatter,
)
from ipaddress import IPv4Interface, IPv4Address
from pathlib import Path
from typing import Dict, List, Optional
from subprocess import run

import yaml

from isobuilder import IsoBuilder, IsoBuilderDirs, IsoBuilderHost, IsoBuilderError


logger = logging.getLogger(__name__)


class ArgparseFormatter(ArgumentDefaultsHelpFormatter, RawDescriptionHelpFormatter):
    """Custom argparse formatter class for cookbooks.

    It can be used as the ``formatter_class`` for the ``ArgumentParser`` instances and it has the
    capabilities of both :py:class:`argparse.ArgumentDefaultsHelpFormatter` and
    :py:class:`argparse.RawDescriptionHelpFormatter`.
    """


def get_args(args: Optional[List] = None) -> Namespace:
    """Parse and return the arguments.

    Returns:
        Namespace: The parsed argument namespace
    """
    parser = ArgumentParser(description=__doc__, formatter_class=ArgparseFormatter)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase logging level. more -v's mean higher logging level",
    )
    parser.add_argument(
        "-c",
        "--config-file",
        type=Path,
        default="/etc/isobuilder.yaml",
        help="The location for the config file.",
    )
    parser.add_argument(
        "-P",
        "--drac-password",
        default="calvin",
        help="The drac password used to generate the root password",
    )
    parser.add_argument(
        "--source-mount",
        type=Path,
        help="Where to mount the source iso image, will be appeneded with the hostname",
    )
    parser.add_argument(
        "--build-dir",
        type=Path,
        help=(
            "The directory used to build the customised image, "
            "will be appeneded with the hostname."
        ),
    )
    parser.add_argument(
        "-d",
        "--nodes-dir",
        type=Path,
        help="The location of the icann-nodes repo",
    )
    parser.add_argument(
        "-i",
        "--source-iso",
        type=Path,
        help="The source iso image used for the initial file set.",
    )
    parser.add_argument(
        "--disk-id",
        type=str,
        default="PERC",
        help="The ID of the disk from /sys/block/*/device/model",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="The output directory where we store the completed iso.",
    )
    parser.add_argument("node", help="The node we are building the iso for")
    if args is None:  # pragma: no cover
        return parser.parse_args()
    return parser.parse_args(args)


def get_log_level(args_level: int) -> int:
    """Convert an integer to a logging log level.

    Arguments:
        args_level (int): The log level as an integer

    Returns:
        int: the logging loglevel
    """
    return {
        0: logging.ERROR,
        1: logging.WARN,
        2: logging.INFO,
        3: logging.DEBUG,
    }.get(args_level, logging.DEBUG)


def get_primary_int(network_data: Dict, address_family: int) -> Optional[str]:
    """Parse the network_data and return the primary ip interface.

    The primary interface is which ever interfaces as the default gateway

    Arguments:
        network_data: dictionary of network data
        address_family: the address family either 4 or 6

    Returns:
        the primary interface.

    """
    for interface, config in network_data.items():
        if f"gw{address_family}" in config:
            if config[f"gw{address_family}"]:
                return interface
    return None


def get_config(args: Namespace) -> Dict:  # pragma: no cover
    """load the config file and merge with arguments.

    Arguments:
        args: the parsed argument namespace

    Returns:
        dictionary representing the config

    """
    yaml_data = yaml.safe_load(args.config_file.read_text())
    config = {k: Path(v) for k, v in yaml_data.items()}
    clean_args = {k: v for k, v in vars(args).items() if v is not None}
    config = {**config, **clean_args}
    for required_params in [
        "source_mount",
        "build_dir",
        "nodes_dir",
        "source_iso",
        "output_dir",
    ]:
        if required_params not in config:
            raise ValueError(f"missing config {required_params}")

    return config


def main() -> int:  # pragma: no cover
    """Main program Entry point.

    Returns:
        int: the status return code
    """
    args = get_args()
    logging.basicConfig(level=get_log_level(args.verbose))
    config = get_config(args)
    run(["git", "pull"], cwd=config["nodes_dir"], check=True)
    node_path = config["nodes_dir"] / f"{args.node}.yaml"
    if not node_path.is_file():
        logging.error("%s: no such file. Please generate the config first", node_path)
        return 1

    yaml_data = yaml.safe_load(node_path.read_text())
    ipv4_primary = get_primary_int(yaml_data["network::interfaces"], 4)
    if ipv4_primary is None:
        logging.error("%s: unable to find ipv4 primary interface", node_path)
        return 1

    ipv6_primary = get_primary_int(yaml_data["network::interfaces"], 6)
    ipaddress = IPv4Interface(yaml_data["network::interfaces"][ipv4_primary]["addr4"])
    gateway = IPv4Address(yaml_data["network::interfaces"][ipv4_primary]["gw4"])

    iso_host = IsoBuilderHost(
        fqdn=args.node,
        ipaddress=ipaddress,
        gateway=gateway,
        ipv4_primary=ipv4_primary,
        ipv6_primary=ipv6_primary,
    )
    iso_dirs = IsoBuilderDirs(
        source_iso=config["source_iso"],
        source_mount=config["source_mount"] / args.node,
        build_dir=config["build_dir"] / args.node,
        output_dir=config["output_dir"],
    )
    iso_builder = IsoBuilder(
        host=iso_host,
        dirs=iso_dirs,
        drac_password=args.drac_password,
        disk_id=args.disk_id,
    )
    try:
        iso_builder.build()
    except IsoBuilderError as error:
        logger.error("%s: error occurred building\n%s", args.node, error)
        return 1

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
