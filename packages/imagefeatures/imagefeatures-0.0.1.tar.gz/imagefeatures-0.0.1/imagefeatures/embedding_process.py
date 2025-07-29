"""Process an image for embeddings."""

from imgbeddings import imgbeddings  # type: ignore
from PIL import Image

_IBED = imgbeddings()


def embedding_process(image: Image.Image) -> dict[str, float]:
    """Process an image for embeddings."""
    embedding = _IBED.to_embeddings(image).flatten().tolist()  # type: ignore
    return {f"embedding_{count}": x for count, x in enumerate(embedding)}
