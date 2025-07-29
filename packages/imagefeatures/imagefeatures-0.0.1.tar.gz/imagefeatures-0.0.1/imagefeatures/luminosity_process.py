"""Process an image for its luminosity."""

from PIL import Image


def luminosity_process(image: Image.Image) -> dict[str, float]:
    """Process an image for luminosity."""
    histogram = image.histogram()
    pixels = sum(histogram)
    brightness = sum(i * histogram[i] for i in range(256)) / pixels
    return {"luminosity": brightness}
