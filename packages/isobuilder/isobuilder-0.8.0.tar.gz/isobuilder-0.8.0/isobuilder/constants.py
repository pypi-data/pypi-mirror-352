AUTHORIZED_KEYS = """ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDwYgIyxyeI9kkxQuO0unybG6dmuMmARJSjew+Ue6HlCLEh7RjE2G3mMywztk7EKXrIs93leBacp2l2PrUp0HkijH4IreAsMh81P56UPLWAfsWoU3UfYGJw1OFAPCIaWCyCegKfaB9DcIi3NXWtI0t7gcPgnmhDMVxmqinZ9+eYKy79Vt5iK8cLJzedsSAjmV2R9Q7JS6Ic6IV0Rj0GzwPBbI+gJenGUE0oLAmZfSAYJFMvBhKk6HrIp4zMVbnKinGoN4HkxeeP+oqyiJIqRWP8hhyKJoeHZ7a94TSRG1TEg1v6SEoDgqLXojC6b1mZpt0uN616gEbvOpC6B4xXHcAr peadmin@master1"""  # noqa

ISOLINUX_CFG = """serial 1 115200
include menu.cfg
default menu.c32
prompt 1
timeout 50"""


TXT_CFG = """label dnsops
  menu label ^DNS Engineering Base System
  kernel /casper/vmlinuz
  append ds=nocloud;s=/cdrom/nocloud/ initrd=/casper/initrd autoinstall debug ramdisk_size=16384 root=/dev/ram ipv6.disable=1 console=ttyS1,115200n8 ---
label memtest
  menu label Test ^memory
  kernel /install/mt86plus
label hd
  menu label ^Boot from first hard disk
  localboot 0x80"""  # noqa

GRUB = """GRUB_DEFAULT=0
GRUB_TIMEOUT=3
GRUB_DISTRIBUTOR=`lsb_release -i -s 2> /dev/null || echo Debian`
GRUB_CMDLINE_LINUX_DEFAULT=""
GRUB_CMDLINE_LINUX="rootdelay=90 console=tty0 console=ttyS1,115200n8"
GRUB_TERMINAL=serial
GRUB_SERIAL_COMMAND="serial --speed=115200 --unit=1 --word=8 --parity=no --stop=1" """

GRUB_CFG = """
if loadfont /boot/grub/font.pf2 ; then
        set gfxmode=auto
        insmod efi_gop
        insmod efi_uga
        insmod gfxterm
        terminal_output gfxterm
fi
serial --speed=115200 --unit=1 --word=8 --parity=no --stop=1 --unit=1
terminal --timeout=5 serial console
set menu_color_normal=white/black
set menu_color_highlight=black/light-gray
set timeout=5

menuentry "Install Ubuntu Server" {
        set gfxpayload=keep
        linux   /casper/vmlinuz "ds=nocloud;s=/cdrom/nocloud/" autoinstall debug ramdisk_size=16384 root=/dev/ram ipv6.disable=1 console=ttyS1,115200n8 ---
        initrd  /casper/initrd
}

menuentry "Rescue a broken system" {
        set gfxpayload=keep
        linux   /casper/vmlinuz  rescue/enable=true console=ttyS1,115200n8 ---
        initrd  /casper/initrd
}
grub_platform
if [ "$grub_platform" = "efi" ]; then
menuentry 'Boot from next volume' {
        exit
}
menuentry 'UEFI Firmware Settings' {
        fwsetup
}
fi
"""  # noqa
# hostname and ipv6_primary are formated in later
LATE_COMMAND = "\n".join(
    [
        "#!/bin/sh",
        "echo {hostname} > /target/etc/hostname",
        "cp /cdrom/dnsops/grub /target/etc/default/",
        "mkdir -p /target/root/.ssh",
        f"echo '{AUTHORIZED_KEYS}' > /target/root/.ssh/authorized_keys",
        "chmod 0600 /target/root/.ssh/authorized_keys",
        "chmod 0700 /target/root/.ssh",
        "echo 'net.ipv6.conf.all.accept_ra = 0' >/target/etc/sysctl.d/net.ipv6.conf.all.accept_ra.conf",  # noqa
        "echo 'net.ipv6.conf.default.accept_ra = 0' >/target/etc/sysctl.d/net.ipv6.conf.default.accept_ra.conf",  # noqa
        "echo 'net.ipv6.conf.{ipv6_primary}.accept_ra = 0' >/target/etc/sysctl.d/net.ipv6.conf.interface.accept_ra.conf",  # noqa
        "echo 'precedence ::ffff:0:0/96 100' >/target/etc/gai.conf",
        "in-target update-grub",
        "exit 0",
    ]
)

AUTO_INTSTALL = {
    "autoinstall": {
        "version": 1,
        "early-commands": [
            "umount /media || true",
        ],
        "locale": "en_US.UTF-8",
        "network": {
            "network": {
                "version": 2,
                "ethernets": {},
            },
        },
        "apt": {
            "primary": [
                {
                    "arches": ["defaut"],
                    "uri": "http://prod.mirror.dns.icann.org/repos/main/ubuntu/",
                },
            ],
        },
        "storage": {
            "layout": {
                "name": "lvm",
                "reset-partition": True,
                "config": [
                    {
                        "type": "disk",
                        "id": "disk0",
                        "wipe": "superblock",
                        "grub_device": True,
                        "match": {
                            "size": "smallest",
                        },
                    },
                    {
                        "type": "partition",
                        "id": "bios_boot",
                        "size": "1MB",
                    },
                    {
                        "type": "partition",
                        "id": "efi",
                        "size": "200MB",
                    },
                    {
                        "type": "partition",
                        "id": "root",
                        "size": "8GB",
                    },
                    {
                        "type": "partition",
                        "id": "lvm_partition",
                        "size": -1,
                    },
                    {
                        "id": "volgroup1",
                        "type": "lvm_volgroup",
                        "name": "vg1",
                        "devices": ["lvm_partition"],
                    },
                    {
                        "type": "lvm_partition",
                        "id": "swap",
                        "name": "lvm_swap",
                        "volgroup": "vg1",
                        "size": "4GB",
                    },
                    {
                        "type": "lvm_partition",
                        "id": "usr",
                        "name": "lvm_usr",
                        "size": "8GB",
                        "volgroup": "vg1",
                    },
                    {
                        "type": "lvm_partition",
                        "id": "var",
                        "name": "lvm_var",
                        "size": "8GB",
                        "volgroup": "vg1",
                    },
                    {
                        "type": "lvm_partition",
                        "id": "opt",
                        "name": "lvm_opt",
                        "size": "500GB",
                        "volgroup": "vg1",
                    },
                    {
                        "type": "format",
                        "id": "root_fs",
                        "volume": "root",
                        "fstype": "ext4",
                    },
                    {
                        "type": "format",
                        "id": "swap_fs",
                        "volume": "lvm_swap",
                        "fstype": "swap",
                    },
                    {
                        "type": "format",
                        "id": "usr_fs",
                        "volume": "lvm_usr",
                        "fstype": "ext4",
                    },
                    {
                        "type": "format",
                        "id": "var_fs",
                        "volume": "lvm_var",
                        "fstype": "ext4",
                    },
                    {
                        "type": "format",
                        "id": "opt_fs",
                        "volume": "lvm_opt",
                        "fstype": "ext4",
                    },
                    {
                        "type": "mount",
                        "device": "root_fs",
                        "point": "/",
                    },
                    {
                        "type": "mount",
                        "device": "usr_fs",
                        "point": "/usr",
                    },
                    {
                        "type": "mount",
                        "device": "var_fs",
                        "point": "/var",
                    },
                    {
                        "type": "mount",
                        "device": "opt_fs",
                        "point": "/opt",
                    },
                ],
            },
        },
        "ssh": {
            "install-server": True,
            "authorized-keys": [AUTHORIZED_KEYS],
        },
        "late-commands": [
            "/cdrom/dnsops/late_command",
        ],
        "user-data": {"disable_root": False, "chpasswd": {}},
    }
}
