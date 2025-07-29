""""Testing class for IsoBuilder."""
from argparse import Namespace

from isobuilder.cli import get_args, get_log_level, get_primary_int


def test_get_args():
    """Test the get args method."""
    assert isinstance(get_args(["test.exampl.org"]), Namespace)


def test_get_log_level():
    """Test the get log level method."""
    assert get_log_level(3) == 10


def test_get_get_primary_int():
    """Test get primary interface"""
    data = {
        "eno1": {"gw4": "192.0.2.1"},
        "eno2": {"gw6": "2001:db8::"},
    }
    assert get_primary_int(data, 4) == "eno1"
    assert get_primary_int(data, 6) == "eno2"
    assert get_primary_int(data, 5) is None
