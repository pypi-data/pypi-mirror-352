import pytest

from pycbf.img import Img


def test_create_handle():
    Img()


def test_no_field():
    i = Img()
    with pytest.raises(KeyError):
        i.get_field("Name")


def test_get_number():
    i = Img()
    assert i.get_number("sadasdasd") == 0.0


@pytest.fixture
def mar_image(dials_data):
    return dials_data("pycbf", pathlib=True) / "endonat3_001.mar2300"


def test_regression_image(mar_image):
    with open(mar_image, "rb") as f:
        img = Img()
        hi = img.read_mar345header(f)
        img.read_mar345data(f, hi)


def test_image_reading(mar_image):
    # Currently, problems building numpy on mac-arm, so don't require
    np = pytest.importorskip("numpy")

    img = np.asarray(Img.read_mar345(mar_image))
    assert img.shape == (2300, 2300)
    assert img.any()
    assert (img == 0).sum() == 1131017
    assert (img != 0).sum() == 4158983

    img_base = Img.read_mar345(mar_image)
    assert (img == img_base.image).all()
