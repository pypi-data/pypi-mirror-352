import numpy as np
import pytest
from imgzen import utils


@pytest.fixture
def dummy_image():
    return np.full((100, 100, 3), 128, dtype=np.uint8)


def test_rotate_image(dummy_image):
    rotated = utils.rotate_image(dummy_image, angle=90)
    assert rotated.shape == dummy_image.shape


def test_resize_image(dummy_image):
    resized = utils.resize_image(dummy_image, width=50)
    assert resized.shape[1] == 50


def test_enhance_contrast(dummy_image):
    contrasted = utils.enhance_contrast(dummy_image)
    assert contrasted.shape == dummy_image.shape


def test_blur_background(dummy_image):
    blurred = utils.blur_background(dummy_image)
    assert blurred.shape == dummy_image.shape


def test_auto_correction(dummy_image):
    corrected = utils.auto_correction(dummy_image)
    assert corrected.shape == dummy_image.shape
