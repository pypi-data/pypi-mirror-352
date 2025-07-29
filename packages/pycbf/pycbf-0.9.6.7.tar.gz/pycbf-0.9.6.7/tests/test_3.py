import pycbf
from pycbf.utils import cbf2str


def test_get_local_integer_byte_order():
    assert cbf2str(pycbf.get_local_integer_byte_order()) == "little_endian"


def test_get_local_real_byte_order():
    assert cbf2str(pycbf.get_local_real_byte_order()) == "little_endian"


def test_get_local_real_format():
    assert cbf2str(pycbf.get_local_real_format()) == "ieee 754-1985"


def test_compute_cell_volume():
    assert pycbf.compute_cell_volume((2.0, 3.0, 4.0, 90.0, 90.0, 90.0)) == 24.0
