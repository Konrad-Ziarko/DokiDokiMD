import base64
import io
from enum import Enum

from dokidokimd.dd_logger.dd_logger import get_logger

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from PIL import Image

module_logger = get_logger('coder')


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


if __name__ == '__main__':
    with open('../../tests/functional/test_create_pdf_from_jpegs/images/1.jpg', 'rb') as image_file:
        encoded_string = image_to_b64(image_file.read())
        print(encoded_string)

        img = b64_to_image(encoded_string)
