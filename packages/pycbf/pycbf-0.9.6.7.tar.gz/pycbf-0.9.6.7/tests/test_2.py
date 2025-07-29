import pytest

import pycbf


def test_2(dials_data):
    data_dir = dials_data("pycbf", pathlib=True)
    cbf = pycbf.cbf_handle_struct()
    cbf.read_file(str(data_dir / "adscconverted.cbf"), 0)
    cbf.select_datablock(0)
    g = cbf.construct_goniometer()
    print(("Rotation axis is", g.get_rotation_axis()))
    assert g.get_rotation_axis() == pytest.approx([1, 0, 0])
    d = cbf.construct_detector(0)
    print(("Beam center is", d.get_beam_center()))
    assert d.get_beam_center() == pytest.approx([1535.5, 1535.5, 157.52387, -157.52387])


def test2_asbytefilename(dials_data):
    data_dir = dials_data("pycbf", pathlib=True)
    cbf = pycbf.cbf_handle_struct()
    cbf.read_file(str(data_dir / "adscconverted.cbf").encode(), 0)
    cbf.select_datablock(0)
    g = cbf.construct_goniometer()
    print(("Rotation axis is", g.get_rotation_axis()))
    assert g.get_rotation_axis() == pytest.approx([1, 0, 0])
    d = cbf.construct_detector(0)
    print(("Beam center is", d.get_beam_center()))
    assert d.get_beam_center() == pytest.approx([1535.5, 1535.5, 157.52387, -157.52387])


def test_2_buffered(dials_data):
    data_dir = dials_data("pycbf", pathlib=True)
    cbf = pycbf.cbf_handle_struct()
    buffer = (data_dir / "adscconverted.cbf").read_bytes()
    cbf.read_buffer(buffer)
    cbf.select_datablock(0)
    g = cbf.construct_goniometer()
    print(("Rotation axis is", g.get_rotation_axis()))
    assert g.get_rotation_axis() == pytest.approx([1, 0, 0])
    d = cbf.construct_detector(0)
    print(("Beam center is", d.get_beam_center()))
    assert d.get_beam_center() == pytest.approx([1535.5, 1535.5, 157.52387, -157.52387])
