import base64
import io
from enum import Enum

from PIL import Image

from dokidokimd.tools.ddmd_logger import get_logger

logger = get_logger(__name__)


class ImageFormat(Enum):
    BMP = 0
    PNG = 1
    JPEG = 2
    GIF = 3
    TIFF = 4


def image_to_b64(image: bytes) -> str:
    byte_string = base64.b64encode(image)
    return byte_string


def b64_to_image(b64_string: str) -> bytes:
    decoded_string = base64.b64decode(b64_string)
    image = Image.open(io.BytesIO(decoded_string))
    return image

