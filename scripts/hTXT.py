"""
hTXT: A Python module to decode old Hebrew text files encoded with Code page 862

https://github.com/Dvd848/hTXT-Viewer

MIT License

Copyright (c) 2022 Dvd848

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import argparse
import re

from pathlib import Path
from tkinter import CURRENT
from PIL import Image, ImageDraw, ImageFont
from typing import List
from collections import namedtuple

# 7-bit C1 ANSI sequences
# https://stackoverflow.com/questions/14693701/
ansi_escape = re.compile(b'''
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', re.VERBOSE)

translation = {
    0x01: '☺', 0x02: '☻', 0x03: '♥', 0x04: '♦', 0x05: '♣', 0x06: '♠', 0x07: '•', 
    0x08: '◘', 0x09: '○', 0x0B: '♂', 0x0C: '♀', 0x0E: '♫', 0x0F: '☼', 
    0x10: '►', 0x11: '◄', 0x12: '↕', 0x13: '‼', 0x14: '¶', 0x15: '§', 0x16: '▬', 0x17: '↨', 
    0x18: '↑', 0x19: '↓', 0x1A: '→', 0x1B: '←', 0x1C: '∟', 0x1D: '↔', 0x1E: '▲', 0x1F: '▼', 

    0x9B: '¢', 0x9C: '£', 0x9D: '¥', 0x9E: '₧', 0x9F: 'ƒ', 
    0xA0: 'á', 0xA1: 'í', 0xA2: 'ó', 0xA3: 'ú', 0xA4: 'ñ', 0xA5: 'Ñ', 0xA6: 'ª', 0xA7: 'º', 
    0xA8: '¿', 0xA9: '⌐', 0xAA: '¬', 0xAB: '½', 0xAC: '¼', 0xAD: '¡', 0xAE: '«', 0xAF: '»',
    0xB0: '░', 0xB1: '▒', 0xB2: '▓', 0xB3: '│', 0xB4: '┤', 0xB5: '╡', 0xB6: '╢', 0xB7: '╖', 
    0xB8: '╕', 0xB9: '╣', 0xBA: '║', 0xBB: '╗', 0xBC: '╝', 0xBD: '╜', 0xBE: '╛', 0xBF: '┐',
    0xC0: '└', 0xC1: '┴', 0xC2: '┬', 0xC3: '├', 0xC4: '─', 0xC5: '┼', 0xC6: '╞', 0xC7: '╟', 
    0xC8: '╚', 0xC9: '╔', 0xCA: '╩', 0xCB: '╦', 0xCC: '╠', 0xCD: '═', 0xCE: '╬', 0xCF: '╧',
    0xD0: '╨', 0xD1: '╤', 0xD2: '╥', 0xD3: '╙', 0xD4: '╘', 0xD5: '╒', 0xD6: '╓', 0xD7: '╫',
    0xD8: '╪', 0xD9: '┘', 0xDA: '┌', 0xDB: '█', 0xDC: '▄', 0xDD: '▌', 0xDE: '▐', 0xDF: '▀',
    0xE0: 'α', 0xE1: 'ß', 0xE2: 'Γ', 0xE3: 'π', 0xE4: 'Σ', 0xE5: 'σ', 0xE6: 'µ', 0xE7: 'τ', 
    0xE8: 'Φ', 0xE9: 'Θ', 0xEA: 'Ω', 0xEB: 'δ', 0xEC: '∞', 0xED: 'φ', 0xEE: 'ε', 0xEF: '∩',
    0xF0: '≡', 0xF1: '±', 0xF2: '≥', 0xF3: '≤', 0xF4: '⌠', 0xF5: '⌡', 0xF6: '÷', 0xF7: '≈', 
    0xF8: '°', 0xF9: '∙', 0xFA: '·', 0xFB: '√', 0xFC: 'ⁿ', 0xFD: '²', 0xFE: '■', 0xFF: chr(160),

    0x80: 'א', 0x81: 'ב', 0x82: 'ג', 0x83: 'ד', 0x84: 'ה', 0x85: 'ו', 0x86: 'ז', 0x87: 'ח',
    0x88: 'ט', 0x89: 'י', 0x8A: 'ך', 0x8B: 'כ', 0x8C: 'ל', 0x8D: 'ם', 0x8E: 'מ', 0x8F: 'ן',
    0x90: 'נ', 0x91: 'ס', 0x92: 'ע', 0x93: 'ף', 0x94: 'פ', 0x95: 'ץ', 0x96: 'צ', 0x97: 'ק',
    0x98: 'ר', 0x99: 'ש', 0x9A: 'ת',
}

CURRENT_SCRIPT = Path(__file__).parent.resolve()
FONT_PATH = CURRENT_SCRIPT / '..' / 'resources' / 'clacon2.ttf'
FONT_SIZE = 16
FONT_WIDTH = 8
FONT_HEIGHT = 13
CONSOLE_WIDTH_DEFAULT = 80
CONSOLE_WIDTH_MIN = 40
CONSOLE_WIDTH_MAX = 1000

LEFT_RIGHT_MARK = u"\u200E"

Theme = namedtuple("namedtuple", "bgcolor fgcolor")
THEMES = {
    "dark" : Theme((0x0C, 0x0C, 0x0C), (0xCC, 0xCC, 0xCC)),
    "light": Theme((0xFF, 0xFF, 0xFF), (0x00, 0x00, 0x00))
}

def create_tile(console_width, color):
    img = Image.new('RGB', (console_width * FONT_WIDTH, FONT_HEIGHT), color = color)
    d = ImageDraw.Draw(img)

    return img, d

def decode_file(buffer: bytes) -> List[str]:
    res = []
    buffer = ansi_escape.sub(b'', buffer)
    for byte in buffer:
        try:
            c = translation[byte]
        except KeyError:
            c = chr(byte)
        res.append(c)
    
    return res

def file_to_image(buffer: bytes, **kwargs) -> Image:

    console_width = kwargs.get("console_width", CONSOLE_WIDTH_DEFAULT)
    if console_width < CONSOLE_WIDTH_MIN or console_width > CONSOLE_WIDTH_MAX:
        raise ValueError(f"Console width {console_width} not in allowed range ({CONSOLE_WIDTH_MIN}-{CONSOLE_WIDTH_MAX}")

    try:
        theme = THEMES[kwargs.get("theme", "dark")]
    except KeyError:
        raise ValueError(f"Unknown theme: {kwargs['theme']}")

    try:
        font = ImageFont.truetype(str(FONT_PATH), FONT_SIZE)
    except Exception:
        raise FileNotFoundError(f"Can't find font: {FONT_PATH}")

    content = decode_file(buffer)
    
    tiles = []

    img, d = create_tile(console_width, theme.bgcolor)
    offset = 0

    for c in content:
        if c == "\n":
            tiles.append(img)
            img, d = create_tile(console_width, theme.bgcolor)
            offset = 0
        elif c == "\r":
            pass
        else:
            d.text((FONT_WIDTH * offset, 0), c, fill = theme.fgcolor, font = font)
            offset += 1            

    if tiles[-1] != img:
        tiles.append(img)
        
    height = len(tiles) * FONT_HEIGHT
    output = Image.new('RGB', (console_width * FONT_WIDTH, height), color = theme.bgcolor)

    for i, img in enumerate(tiles):
        output.paste(img, (0, FONT_HEIGHT * i))

    return output

def main(input_path: str, output_path: str, **kwargs) -> None:
    with open(input_path, "rb") as f:
        output = file_to_image(f.read(), **kwargs)
        output.save(output_path)
        print(f"Saved to '{output_path}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decode old Hebrew text files encoded with Code Page 862")
    parser.add_argument('-i', '--input', type=str, required=True, help="Input file")
    parser.add_argument('-o', '--output', type=str, help="Output file")
    parser.add_argument('-w', '--console-width', type=int, default=CONSOLE_WIDTH_DEFAULT, help="Console width")
    parser.add_argument('-t', '--theme', choices=["dark", "light"], default="dark", help="Image theme")

    args = parser.parse_args()
    kwargs = {}

    if args.console_width:
        kwargs["console_width"] = args.console_width
    
    if args.theme:
        kwargs["theme"] = args.theme

    output_file = None
    if args.output is not None:
        output_file = args.output
    else:
        input_file = Path(args.input).absolute()
        output_file = str(input_file.parent / input_file.stem) + ".png"

    try:
        main(args.input, output_file, **kwargs)
    except Exception as e:
        raise SystemExit(f"Error: {str(e)}")