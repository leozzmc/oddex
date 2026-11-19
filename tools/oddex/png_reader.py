"""Minimal stdlib PNG reader for indexed/grayscale images (enough to validate GBA sprites).

    img = read_png(path)   # img.width, img.height, img.bit_depth, img.color_type,
                           # img.palette [(r, g, b), ...], img.rows [[index, ...], ...]
"""
import struct
import zlib
from dataclasses import dataclass, field


@dataclass
class Png:
    width: int
    height: int
    bit_depth: int
    color_type: int
    palette: list = field(default_factory=list)
    rows: list = field(default_factory=list)

    def bbox(self, top=0, height=None):
        """(min_x, min_y, max_x, max_y) of non-zero indices within rows [top, top+height)."""
        height = self.height - top if height is None else height
        xs, ys = [], []
        for y in range(top, top + height):
            for x, v in enumerate(self.rows[y]):
                if v:
                    xs.append(x)
                    ys.append(y - top)
        return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def _unfilter(raw, width, height, bpp_bits):
    stride = (width * bpp_bits + 7) // 8
    step = max(1, bpp_bits // 8)
    out, prev, pos = [], bytearray(stride), 0
    for _ in range(height):
        ftype, line = raw[pos], bytearray(raw[pos + 1: pos + 1 + stride])
        pos += 1 + stride
        for i in range(stride):
            a = line[i - step] if i >= step else 0
            b, c = prev[i], prev[i - step] if i >= step else 0
            if ftype == 1:
                line[i] = (line[i] + a) & 0xFF
            elif ftype == 2:
                line[i] = (line[i] + b) & 0xFF
            elif ftype == 3:
                line[i] = (line[i] + (a + b) // 2) & 0xFF
            elif ftype == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 0xFF
        out.append(bytes(line))
        prev = line
    return out


def read_png(path):
    data = open(path, 'rb').read()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'{path}: not a PNG')
    pos, idat, img = 8, b'', None
    while pos < len(data):
        length, kind = struct.unpack('>I4s', data[pos: pos + 8])
        body = data[pos + 8: pos + 8 + length]
        pos += 12 + length
        if kind == b'IHDR':
            w, h, depth, ctype, _, _, interlace = struct.unpack('>IIBBBBB', body)
            if interlace:
                raise ValueError(f'{path}: interlaced PNGs are not supported')
            img = Png(w, h, depth, ctype)
        elif kind == b'PLTE':
            img.palette = [tuple(body[i: i + 3]) for i in range(0, len(body), 3)]
        elif kind == b'IDAT':
            idat += body
        elif kind == b'IEND':
            break
    if img.color_type not in (0, 3):
        raise ValueError(f'{path}: must be an indexed (palette) or grayscale PNG, got color type {img.color_type}')
    depth = img.bit_depth
    for line in _unfilter(zlib.decompress(idat), img.width, img.height, depth):
        if depth == 8:
            img.rows.append(list(line[: img.width]))
        else:
            per, mask = 8 // depth, (1 << depth) - 1
            row = []
            for byte in line:
                for k in range(per):
                    row.append((byte >> (8 - depth * (k + 1))) & mask)
            img.rows.append(row[: img.width])
    return img
