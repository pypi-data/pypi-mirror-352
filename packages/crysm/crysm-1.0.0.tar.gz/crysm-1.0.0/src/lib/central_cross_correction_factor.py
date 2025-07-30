from dataclasses import dataclass
from pathlib import Path

import numpy as np
import tifffile as tf

from lib.mib import load_mib


@dataclass
class CorrectionStats:
    cross_mean: float
    central_mean: float
    rest_mean: float
    factor: float
    central_factor: float
    num_extra_pixels: int


def find_center_cross_correction(flatfield_image: Path):
    """Loads a flatfield image (.mib or .tiff) and calculate the intensity difference between the central cross and the rest of the image"""
    if flatfield_image.suffix == ".mib":
        img = load_mib(flatfield_image.read_bytes())[0]
    else:
        img = tf.imread(flatfield_image)
    assert img.shape == (512, 512)
    cross_mask = np.zeros_like(img)
    cross_mask[255:257, :] = 1  # Cross
    cross_mask[:, 255:257] = 1  # Cross
    cross_mask[255:257, 255:257] = 2  # Central 4

    cross = img[cross_mask == 1]
    rest = img[cross_mask == 0]
    central = img[cross_mask == 2]
    cross_mean = np.mean(cross)
    central_mean = np.mean(central)
    rest_mean = np.mean(rest)
    factor = cross_mean / rest_mean
    central_factor = central_mean / rest_mean
    num_extra_pixels = 2 if factor < 1.9 else 4

    return CorrectionStats(
        cross_mean=cross_mean,
        central_mean=central_mean,
        rest_mean=rest_mean,
        factor=factor,
        central_factor=central_factor,
        num_extra_pixels=num_extra_pixels,
    )
