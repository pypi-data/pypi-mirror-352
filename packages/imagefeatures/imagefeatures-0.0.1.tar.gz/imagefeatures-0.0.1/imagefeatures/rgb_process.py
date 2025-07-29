"""Process an image for its mean channels in R/G/B."""

import numpy as np
from PIL import Image


def rgb_process(image: Image.Image) -> dict[str, float]:
    """Process an image for RGB."""
    np_img = np.array(image)
    pixels = np_img.reshape(-1, 3)
    avg_r, avg_g, avg_b = pixels.mean(axis=0)
    return {
        "average_red": avg_r,
        "average_green": avg_g,
        "average_blue": avg_b,
    }
