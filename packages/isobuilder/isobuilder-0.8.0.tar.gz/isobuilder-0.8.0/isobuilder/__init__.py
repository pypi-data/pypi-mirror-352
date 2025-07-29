"""Class used for mounting iso images."""

import hashlib
import logging
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from fileinput import FileInput
from hashlib import md5
from ipaddress import IPv4Address, IPv4Interface
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from passlib.hosts import linux_context

from isobuilder.constants import (
    AUTO_INTSTALL,
    GRUB,
    GRUB_CFG,
    ISOLINUX_CFG,
    LATE_COMMAND,
    TXT_CFG,
)


class IsoBuilderError(Exception):
    """Raise by the IsoBuilder class."""


@dataclass
class IsoBuilderHost:
    """Dataclass to hold config data for the host

    Arguments:
        fddn: the host fqdn
        ipaddress: the host ip address
        netmask: the host netmask
        gateway: the host default gateway
        ipv4_primary: the host ipv4 primary interface
        ipv6_primary: the host ipv6 primary interface
    """

    fqdn: str
    ipaddress: IPv4Interface
    gateway: IPv4Address
    ipv4_primary: str
    ipv6_primary: Optional[str] = None


@dataclass
class IsoBuilderDirs:
    """Data class to hole the directories for the IsoBuilder

    Arguments:
        source_iso: Path to the source iso image
        source_mount: The location to mount the source iso image
        build_dir: directory used for building the custom image
        output_dir: The location to store the resulting iso

    """

    source_iso: Path
    source_mount: Path
    build_dir: Path
    output_dir: Path

    def mkdirs(self):
        """Make all the directories."""
        for mydir in [self.source_mount, self.build_dir, self.output_dir]:
            mydir.mkdir(parents=True, exist_ok=True)


class IsoBuilder:
    """Class for building imrs ISOs."""

    def __init__(
        self,
        host: IsoBuilderHost,
        drac_password: str,
        dirs: IsoBuilderDirs,
        disk_id: str,
    ):
        """Main init class

        Arguments:
            host: Object containing the configuration for the host
            drac_password: the drac password is used as a seed for the root password
            disk_id: The id to search for for the boot disk
            dirs: dataclass holding all the dirs we need

        """
        self.logger = logging.getLogger(__name__)
        self.host = host
        self._drac_password = drac_password
        self.disk_id = disk_id
        self._dirs = dirs
        self._dirs.mkdirs()
        self.output_iso = dirs.output_dir / f"{host.fqdn}.iso"

    def _run_command(
        self, command: str, check: bool = True
    ) -> subprocess.CompletedProcess:  # type: ignore
        """Run a cli command.

        Arguments:
            command: the command to run

        """
        self.logger.debug("%s: running command: %s", self.host.fqdn, command)
        try:
            # use capture_output=capture_output when using python3.7
            return subprocess.run(
                shlex.split(command),
                check=check,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as error:
            raise IsoBuilderError(f"{command}: failed to execute: {error}") from error

    def umount_iso(self) -> None:
        """Unmount iso."""
        self.logger.info("%s: unmount: %s", self.host.fqdn, self._dirs.source_mount)
        self._run_command(f"fusermount -u {self._dirs.source_mount}", False)

    def mount_iso(self) -> None:
        """Mount the iso image"""
        self.logger.info("%s: mount: %s", self.host.fqdn, self._dirs.source_mount)
        self._run_command(f"fuseiso {self._dirs.source_iso} {self._dirs.source_mount}")

    def sync_build_dir(self) -> None:
        """Sync the source iso image into a build directory."""
        # TODO: no need to cast on 3.7 when python3.7
        self.logger.info(
            "%s: sync: %s -> %s",
            self.host.fqdn,
            self._dirs.source_mount,
            self._dirs.build_dir,
        )
        shutil.rmtree(str(self._dirs.build_dir), ignore_errors=True)
        self._run_command(
            f"rsync -a --chmod=u+w {self._dirs.source_mount}/ {self._dirs.build_dir}"
        )

    def _update_md5sums(self, path: Path) -> None:
        """Update the md5 sum for a specific path.

        Argumetns:
            path: the path to update

        """
        new_hash = md5(path.read_bytes()).hexdigest()
        relative_path = f"./{path.relative_to(self._dirs.build_dir)}\n"
        self.logger.debug("searching for: %s", relative_path)
        with FileInput(
            str(self._dirs.build_dir / "md5sum.txt"), inplace=True, backup=".bak"
        ) as in_file:
            for line in in_file:
                if line.endswith(relative_path):
                    line = f"{new_hash} {relative_path}"
                print(line, end="")

    def write_custom_files(self) -> None:
        """Update the build dir with custom files."""
        self.logger.info("%s: write custom files", self.host.fqdn)
        (self._dirs.build_dir / "dnsops").mkdir(parents=True, exist_ok=True)
        (self._dirs.build_dir / "nocloud").mkdir(parents=True, exist_ok=True)
        root_password = hashlib.md5(
            f"{self.host.fqdn}:{self._drac_password}".encode()
        ).hexdigest()
        root_password_hash = linux_context.hash(root_password)
        late_command = LATE_COMMAND.format(
            hostname=self.host.fqdn, ipv6_primary=self.host.ipv6_primary
        )
        self.logger.debug("%s: write late_command", self.host.fqdn)
        late_command_path = self._dirs.build_dir / "dnsops" / "late_command"
        late_command_path.write_text(late_command)
        late_command_path.chmod(0o555)
        auto_install: Dict[str, Any] = AUTO_INTSTALL.copy()
        auto_install["autoinstall"]["identity"] = {
            "hostname": self.host.fqdn,
            "password": root_password_hash,
            "username": "root",
        }
        # The above doesn;t set the password as the user already exists so we need the following
        auto_install["autoinstall"]["user-data"]["chpasswd"] = {
            "expire": False,
            "list": [f"root:{root_password_hash}"],
        }
        auto_install["autoinstall"]["network"]["network"]["ethernets"][
            self.host.ipv4_primary
        ] = {
            "accept-ra": False,
            "addresses": [str(self.host.ipaddress.with_prefixlen)],
            "gateway4": str(self.host.gateway),
            "nameservers": {
                "addresses": ["8.8.8.8"],
            },
        }
        self.logger.debug("%s: write autoinstal.yam file", self.host.fqdn)
        (self._dirs.build_dir / "nocloud" / "user-data").write_text(
            "#cloud-config\n" + yaml.safe_dump(auto_install)
        )
        (self._dirs.build_dir / "nocloud" / "meta-data").touch()
        self.logger.debug("%s: write grub file", self.host.fqdn)
        (self._dirs.build_dir / "dnsops" / "grub").write_text(GRUB)
        self.logger.debug("%s: write grub2 file", self.host.fqdn)
        grub_file = self._dirs.build_dir / "boot" / "grub" / "grub.cfg"
        grub_file.write_text(GRUB_CFG)
        self._update_md5sums(grub_file)

    def write_ioslinux_files(self) -> None:
        """ "Write the files required for iso linux"""
        self.logger.info("%s: write isolinux files", self.host.fqdn)
        self.logger.debug("%s: write isolinux.cfg file", self.host.fqdn)
        (self._dirs.build_dir / "isolinux" / "isolinux.cfg").write_text(ISOLINUX_CFG)
        self.logger.debug("%s: write txt.cfg file", self.host.fqdn)
        (self._dirs.build_dir / "isolinux" / "txt.cfg").write_text(TXT_CFG)
        self.logger.debug("%s: copy menu.c32", self.host.fqdn)
        shutil.copy(
            "/usr/lib/syslinux/modules/bios/menu.c32",
            str(self._dirs.build_dir / "isolinux"),
        )

    def mkiso(self) -> None:
        """Make the iso image."""
        try:
            self.output_iso.unlink()
        except FileNotFoundError:
            # TODO: on python3.7 us missing_ok=True
            pass
        command = f"""mkisofs -r -V "DNSEng Media" -cache-inodes -l -input-charset utf-8 \
                      -o {self.output_iso} {self._dirs.build_dir}"""
        self.logger.info("%s: mkiso: %s", self.host.fqdn, self.output_iso)
        self._run_command(command)

    def build(self) -> None:
        """Run all the bits to generate the iso."""
        self.umount_iso()
        self.mount_iso()
        self.sync_build_dir()
        self.write_custom_files()
        # This is only needed for BIOS boot systems
        # self.write_ioslinux_files()
        self.mkiso()
        self.umount_iso()
        print(
            f"{self.host.fqdn}: ISO has been generated and avalible at: {self.output_iso}"
        )
