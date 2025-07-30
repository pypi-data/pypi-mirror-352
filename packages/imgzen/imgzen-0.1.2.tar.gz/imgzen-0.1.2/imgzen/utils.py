import cv2
import numpy as np
from typing import Optional, Tuple


def rotate_image(img: np.ndarray, angle: float = 90.0, scale: float = 1.0) -> np.ndarray:
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)

    matrix = cv2.getRotationMatrix2D(center, angle, scale)

    return cv2.warpAffine(img, matrix, (w, h))


def resize_image(
    img: np.ndarray, width: Optional[float] = None, height: Optional[float] = None
) -> np.ndarray:
    if width is None and height is None:
        return img

    (h, w) = img.shape[:2]

    if width is None and height is not None:
        r = height / float(h)
        dim = (int(w * r), int(height))
    elif width is not None and height is None:
        r = width / float(w)
        dim = (int(width), int(h * r))
    else:
        return img

    return cv2.resize(img, dim, interpolation=cv2.INTER_AREA)


def enhance_contrast(img: np.ndarray) -> np.ndarray:
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])

    return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)


def blur_background(img: np.ndarray, kernel: Tuple[int, int] = (15, 15)) -> np.ndarray:
    return cv2.GaussianBlur(img, kernel, 0)


def auto_correction(img: np.ndarray) -> np.ndarray:
    img_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

    l, a, b = cv2.split(img_lab)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    corrected_img = cv2.merge((cl, a, b))

    return cv2.cvtColor(corrected_img, cv2.COLOR_LAB2BGR)
