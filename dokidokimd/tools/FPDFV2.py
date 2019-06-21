import re
import struct
import zlib
from functools import wraps
from io import BytesIO
from urllib.request import urlopen

from fpdf import FPDF
from fpdf.php import substr, sprintf
from fpdf.py3k import PY3K, b


def make_re(regex):
    return re.compile(regex, flags=re.DOTALL)


def image_is_jpeg(img_type):
    return img_type == 'jpg' or img_type == 'jpeg'


# noinspection PyMethodOverriding
class FPDFV2(FPDF):
    def load_resource(self, reason, filename):
        if reason == "image":
            if filename.startswith("http://") or filename.startswith("https://"):
                f = BytesIO(urlopen(filename).read())
            else:
                f = open(filename, "rb")
            return f
        else:
            self.error("Unknown resource loading reason \"%s\"" % reason)

    def _parsepng(self, filename, file):
        # Extract info from a PNG file
        if file:
            f = file
            f.seek(0)
        if not file:
            f = self.load_resource("image", filename)

        # Check signature
        magic = f.read(8).decode("latin1")
        signature = '\x89' + 'PNG' + '\r' + '\n' + '\x1a' + '\n'
        if not PY3K:
            signature = signature.decode("latin1")
        if magic != signature:
            self.error('Not a PNG file: ' + filename)

        # Read header chunk
        f.read(4)
        chunk = f.read(4).decode("latin1")
        if chunk != 'IHDR':
            self.error('Incorrect PNG file: ' + filename)
        w = self._freadint(f)
        h = self._freadint(f)
        bpc = ord(f.read(1))
        if bpc > 8:
            self.error('16-bit depth not supported: ' + filename)
        ct = ord(f.read(1))
        if ct == 0 or ct == 4:
            colspace = 'DeviceGray'
        elif ct == 2 or ct == 6:
            colspace = 'DeviceRGB'
        elif ct == 3:
            colspace = 'Indexed'
        else:
            self.error('Unknown color type: ' + filename)

        if ord(f.read(1)) != 0:
            self.error('Unknown compression method: ' + filename)
        if ord(f.read(1)) != 0:
            self.error('Unknown filter method: ' + filename)
        if ord(f.read(1)) != 0:
            self.error('Interlacing not supported: ' + filename)
        f.read(4)

        dp = '/Predictor 15 /Colors '
        dp += '3' if colspace == 'DeviceRGB' else '1'
        dp += ' /BitsPerComponent ' + str(bpc) + ' /Columns ' + str(w) + ''

        # Scan chunks looking for palette, transparency and image data
        pal = ''
        trns = ''
        data = bytes() if PY3K else str()
        n = 1
        while n is not None:
            n = self._freadint(f)
            my_type = f.read(4).decode("latin1")
            if my_type == 'PLTE':
                # Read palette
                pal = f.read(n)
                f.read(4)
            elif my_type == 'tRNS':
                # Read transparency info
                t = f.read(n)
                if ct == 0:
                    trns = [ord(substr(t, 1, 1))]
                elif ct == 2:
                    trns = [
                        ord(substr(t, 1, 1)),
                        ord(substr(t, 3, 1)),
                        ord(substr(t, 5, 1))
                    ]
                else:
                    pos = t.find('\x00'.encode("latin1"))
                    if pos != -1:
                        trns = [pos, ]
                f.read(4)
            elif my_type == 'IDAT':
                # Read image data block
                data += f.read(n)
                f.read(4)
            elif my_type == 'IEND':
                break
            else:
                f.read(n + 4)
        if colspace == 'Indexed' and not pal:
            self.error('Missing palette in ' + filename)
        f.close()
        info = {
            'w': w, 'h': h,
            'cs': colspace, 'bpc': bpc,
            'f': 'FlateDecode', 'dp': dp,
            'pal': pal, 'trns': trns
        }
        if ct >= 4:  # if ct == 4, or == 6
            # Extract alpha channel
            data = zlib.decompress(data)
            color = b('')
            alpha = b('')
            if ct == 4:
                # Gray image
                length = 2 * w
                for i in range(h):
                    pos = (1 + length) * i
                    color += b(data[pos])
                    alpha += b(data[pos])
                    line = substr(data, pos + 1, length)
                    re_c = make_re('(.).'.encode("ascii"))
                    re_a = make_re('.(.)'.encode("ascii"))
                    color += re_c.sub(lambda m: m.group(1), line)
                    alpha += re_a.sub(lambda m: m.group(1), line)
            else:
                # RGB image
                length = 4 * w
                for i in range(h):
                    pos = (1 + length) * i
                    color += b(data[pos])
                    alpha += b(data[pos])
                    line = substr(data, pos + 1, length)
                    re_c = make_re('(...).'.encode("ascii"))
                    re_a = make_re('...(.)'.encode("ascii"))
                    color += re_c.sub(lambda m: m.group(1), line)
                    alpha += re_a.sub(lambda m: m.group(1), line)
            del data
            data = zlib.compress(color)
            info['smask'] = zlib.compress(alpha)
            if self.pdf_version < '1.4':
                self.pdf_version = '1.4'
        info['data'] = data
        return info

    def _parsejpg(self, filename, file):
        # Extract info from a JPEG file
        f = None
        try:
            if file:
                f = file
                f.seek(0)
            if not file:
                f = self.load_resource("image", filename)
            while True:
                marker_high, marker_low = struct.unpack('BB', f.read(2))

                def marker_in_range(ival):
                    """returns if marker is in the range"""
                    return ival[0] <= marker_low <= ival[1]

                if marker_high != 0xFF or marker_low < 0xC0:
                    raise SyntaxError('No JPEG marker found')
                elif marker_low == 0xDA:  # SOS
                    raise SyntaxError('No JPEG SOF marker found')
                elif (marker_low == 0xC8 or  # JPG
                      marker_in_range((0xD0, 0xD9)) or  # RSTx
                      marker_in_range((0xF0, 0xFD))):  # JPGx
                    pass
                else:
                    data_size, = struct.unpack('>H', f.read(2))
                    data = f.read(data_size - 2) if data_size > 2 else ''

                    if ((marker_in_range((0xC0, 0xC3)) or  # SOF0 - SOF3
                         marker_in_range((0xC5, 0xC7)) or  # SOF4 - SOF7
                         marker_in_range((0xC9, 0xCB)) or  # SOF9 - SOF11
                         marker_in_range((0xCD, 0xCF)))):  # SOF13 - SOF15
                        bpc, height, width, layers = struct.unpack_from('>BHHB', data)
                        colspace = 'DeviceRGB' if layers == 3 else ('DeviceCMYK' if layers == 4 else 'DeviceGray')
                        break
        except Exception as e:
            if f:
                f.close()
            self.error('Missing or incorrect image file: %s. error: %s' % (filename, str(e)))

        with f:
            # Read whole file from the start
            f.seek(0)
            data = f.read()
        return {'w': width, 'h': height,
                'cs': colspace, 'bpc': bpc,
                'f': 'DCTDecode', 'data': data}

    def check_page(fn):
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            if not self.page and not kwargs.get('split_only'):
                self.error("No page open, you need to call add_page() first")
            else:
                return fn(self, *args, **kwargs)

        return wrapper

    @check_page
    def image(self, name, tmp_x=None, y=None, w=0, h=0, type='', link='', file=None):
        if name not in self.images:
            # First use of image, get info
            if type == '':
                pos = name.rfind('.')
                if not pos:
                    self.error(('image file has no extension and no type was specified: ' + name))
                type = substr(name, pos + 1)

            type = type.lower()
            if image_is_jpeg(type):
                info = self._parsejpg(name, file)
            elif type == 'png':
                info = self._parsepng(name, file)
            else:
                # Allow for additional formats
                # maybe the image is not showing the correct extension,
                # but the header is OK,
                succeed_parsing = False
                # try all the parsing functions
                parsing_functions = [
                    self._parsejpg,
                    self._parsepng,
                    self._parsegif
                ]
                for pf in parsing_functions:
                    try:
                        info = pf(name, file)
                        succeed_parsing = True
                        break
                    except:
                        pass
                # last resource
                if not succeed_parsing:
                    mtd = '_parse' + type
                    if not hasattr(self, mtd):
                        self.error('Unsupported image type: ' + type)
                    info = getattr(self, mtd)(name, file)
                mtd = '_parse' + type

                if not hasattr(self, mtd):
                    self.error('Unsupported image type: ' + type)
                info = getattr(self, mtd)(name)
            info['i'] = len(self.images) + 1
            self.images[name] = info
        else:
            info = self.images[name]

        # Automatic width and height calculation if needed
        if w == 0 and h == 0:
            # Put image at 72 dpi
            w = info['w'] / self.k
            h = info['h'] / self.k
        elif w == 0:
            w = h * info['w'] / info['h']
        elif h == 0:
            h = w * info['h'] / info['w']

        # Flowing mode
        if y is None:
            if (self.y + h > self.page_break_trigger
                    and not self.in_footer
                    and self.accept_page_break):
                # Automatic page break
                tmp_x = self.x
                self.add_page()
                self.x = tmp_x
            y = self.y
            self.y += h

        if tmp_x is None:
            tmp_x = self.x
        self._out(sprintf('q %.2f 0 0 %.2f %.2f %.2f cm /I%d Do Q',
                          w * self.k, h * self.k,
                          tmp_x * self.k, (self.h - (y + h)) * self.k,
                          info['i']))
        if link:
            self.link(tmp_x, y, w, h, link)
