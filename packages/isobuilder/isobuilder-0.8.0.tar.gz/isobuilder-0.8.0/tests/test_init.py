""""Testing class for IsoBuilder."""


from ipaddress import IPv4Interface, IPv4Address
from pathlib import Path

import mock
import pytest

from isobuilder import IsoBuilder, IsoBuilderDirs, IsoBuilderError, IsoBuilderHost
from isobuilder.constants import AUTHORIZED_KEYS, GRUB, GRUB_CFG, ISOLINUX_CFG, TXT_CFG


class TestIsoBuilder:
    """ "Testing class for IsoBuilder."""

    @pytest.fixture(autouse=True)
    def setup_method(self, tmp_path):
        """Initialise test instance."""
        self.tmp_path = tmp_path
        build_dir = tmp_path / "build"
        # We don't really sync the source iso so build needed dirs
        (build_dir / "isolinux").mkdir(parents=True, exist_ok=True)
        (build_dir / "boot" / "grub").mkdir(parents=True, exist_ok=True)
        self.iso_host = IsoBuilderHost(
            fqdn="test.example.org",
            ipaddress=IPv4Interface("192.0.2.1/24"),
            gateway=IPv4Address("192.0.2.254"),
            ipv4_primary="eno1",
            ipv6_primary="eno1",
        )
        self.iso_dirs = IsoBuilderDirs(
            source_iso=Path("/foo/test.iso"),
            source_mount=tmp_path / "cdrom",
            build_dir=build_dir,
            output_dir=tmp_path / "output",
        )
        with mock.patch('isobuilder.Path.mkdir', return_value=True):
            self.iso_builder = IsoBuilder(
                host=self.iso_host,
                drac_password="calvin",
                dirs=self.iso_dirs,
                disk_id='PERC',
            )
        assert isinstance(self.iso_builder, IsoBuilder)

    def test_output_iso(self):
        """Test the output_iso property."""
        assert (
            self.iso_builder.output_iso
            == self.tmp_path / "output" / "test.example.org.iso"
        )

    def test_run_command_exception(self):
        """Test the exception handeling of _run_command"""
        with pytest.raises(
            IsoBuilderError,
            match=(
                "false: failed to execute: "
                r"Command '\['false'\]' returned non-zero exit status 1."
            ),
        ):
            self.iso_builder._run_command("false")

    @mock.patch('isobuilder.subprocess.run', return_value=True)
    def test_umount_iso(self, mock_run_command):
        """Test the mount ISO."""
        self.iso_builder.umount_iso()
        mock_run_command.assert_called()

    @mock.patch('isobuilder.subprocess.run', return_value=True)
    def test_mount_iso(self, mock_run_command):
        """Test the mount ISO."""
        self.iso_builder.mount_iso()
        mock_run_command.assert_called()

    @mock.patch('isobuilder.shutil.rmtree', return_value=True)
    @mock.patch('isobuilder.subprocess.run', return_value=True)
    def test_sync_build_dir(self, mock_run_command, mock_rmtree):
        """Test the mount ISO."""
        self.iso_builder.sync_build_dir()
        mock_run_command.assert_called()
        mock_rmtree.assert_called()

    @mock.patch('isobuilder.IsoBuilder._update_md5sums', return_value=None)
    def test_write_custom_files(self, mock_update_md5):
        """Test writing custom files."""
        self.iso_builder.write_custom_files()
        grub = (self.iso_dirs.build_dir / "dnsops" / "grub").read_text()
        grub2 = (self.iso_dirs.build_dir / "boot" / "grub" / "grub.cfg").read_text()
        assert grub == GRUB
        assert grub2 == GRUB_CFG

    @mock.patch('isobuilder.shutil.copy', return_value=True)
    def test_write_ioslinux_files(self, mock_copy):
        """Test writing custom files."""
        self.iso_builder.write_ioslinux_files()
        isolinux = (self.iso_dirs.build_dir / "isolinux" / "isolinux.cfg").read_text()
        txt_cfg = (self.iso_dirs.build_dir / "isolinux" / "txt.cfg").read_text()
        mock_copy.assert_called_once()
        assert isolinux == ISOLINUX_CFG
        assert txt_cfg == TXT_CFG

    @mock.patch('isobuilder.IsoBuilder._run_command', return_value=True)
    def test_mkiso(self, mock_run_command):
        """Test mkios method."""
        self.iso_builder.mkiso()
        mock_run_command.assert_called_once()

    @mock.patch('isobuilder.IsoBuilder.mkiso', return_value=True)
    @mock.patch('isobuilder.IsoBuilder.write_ioslinux_files', return_value=True)
    @mock.patch('isobuilder.IsoBuilder.write_custom_files', return_value=True)
    @mock.patch('isobuilder.IsoBuilder.sync_build_dir', return_value=True)
    @mock.patch('isobuilder.IsoBuilder.mount_iso', return_value=True)
    @mock.patch('isobuilder.IsoBuilder.umount_iso', return_value=True)
    def test_build(
        self,
        mock_umount_iso,
        mock_mount_iso,
        mock_sync_build,
        mock_write_custom,
        mock_write_ioslinux,
        mock_mkiso,
    ):
        """Test the build command."""
        self.iso_builder.build()
        mock_umount_iso.assert_called()
        mock_mount_iso.assert_called_once()
        mock_sync_build.assert_called_once()
        mock_write_custom.assert_called_once()
        mock_mkiso.assert_called_once()
