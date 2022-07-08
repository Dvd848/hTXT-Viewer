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
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Union, Any
from collections import namedtuple
from enum import Enum

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
    # CP 437
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

    # CP 862
    0x80: 'א', 0x81: 'ב', 0x82: 'ג', 0x83: 'ד', 0x84: 'ה', 0x85: 'ו', 0x86: 'ז', 0x87: 'ח',
    0x88: 'ט', 0x89: 'י', 0x8A: 'ך', 0x8B: 'כ', 0x8C: 'ל', 0x8D: 'ם', 0x8E: 'מ', 0x8F: 'ן',
    0x90: 'נ', 0x91: 'ס', 0x92: 'ע', 0x93: 'ף', 0x94: 'פ', 0x95: 'ץ', 0x96: 'צ', 0x97: 'ק',
    0x98: 'ר', 0x99: 'ש', 0x9A: 'ת',
}

CURRENT_SCRIPT  = Path(__file__).parent.resolve()
FONT_PATH       = CURRENT_SCRIPT / '..' / 'resources' / 'clacon2.ttf'

FONT_SIZE               = 16
FONT_WIDTH              = 8
FONT_HEIGHT             = 13
CONSOLE_WIDTH_DEFAULT   = 80
CONSOLE_WIDTH_MIN       = 40
CONSOLE_WIDTH_MAX       = 1000

Theme = namedtuple("namedtuple", "bgcolor fgcolor")
THEMES = {
    "dark" : Theme((0x0C, 0x0C, 0x0C), (0xCC, 0xCC, 0xCC)),
    "light": Theme((0xFF, 0xFF, 0xFF), (0x00, 0x00, 0x00))
}


class AnsiFunctions(Enum):
    # https://en.wikipedia.org/wiki/ANSI_escape_code
    # https://notes.burke.libbey.me/ansi-escape-codes/
    UNSUPPORTED         = "0"
    CURSOR_FORWARD      = "C"
    CURSOR_BACK         = "D"
    ERASE_IN_DISPLAY    = "J"
    SGR                 = "m"

class AnsiColors(Enum):
    BLACK   = 0
    RED     = 1
    GREEN   = 2
    YELLOW  = 3
    BLUE    = 4
    MAGENTA = 5
    CYAN    = 6
    WHITE   = 7

class AnsiSgrCommands(Enum):
    SET_FGCOLOR = 0
    SET_BGCOLOR = 1
    SET_DEFAULT = 2

AnsiSgrCommand = namedtuple("AnsiSgrCommand", "type value")

class AnsiEdCommands(Enum):
    CURSOR_TO_END   = 0
    CURSOR_TO_START = 1
    ENTIRE_SCREEN   = 2


class AnsiEscape():
    """Represents an ANSI Escape Sequence."""

    COLORS = {
        AnsiColors.BLACK:   (12, 12, 12),
        AnsiColors.RED:     (170, 0, 0),
        AnsiColors.GREEN:   (0, 170, 0),
        AnsiColors.YELLOW:  (170, 85, 0),
        AnsiColors.BLUE:    (0, 0, 170),
        AnsiColors.MAGENTA: (170, 0, 170),
        AnsiColors.CYAN:    (0, 170, 170),
        AnsiColors.WHITE:   (170, 170, 170)
    }

    FGCOLOR_BASE = 30
    BGCOLOR_BASE = 40

    def __init__(self, raw_string: str) -> None:
        """Initialize an ANSI escape sequence from a raw string.
        
            For example:
               AnsiEscape("\x1b[1;37;41m") 
               AnsiEscape("\x1b[16C")

            Params:
                raw_string: 
                    The raw ANSI escape sequence.
        """
        self.raw_string = raw_string
        self._parse_ansi(raw_string)

    def _parse_ansi(self, raw_string: str) -> None:
        """Parse the ANSI escape sequence and separate it to a function and arguments.
        
            Params:
                raw_string: 
                    The raw ANSI escape sequence.
        """
        self._arguments = []
        arguments = raw_string[2:-1]
        if arguments != b"":
            for argument in arguments.split(b";"):
                try:
                    self._arguments.append(int(argument))
                except ValueError:
                    print(f"Unable to parse argument \"{argument.decode('ascii')}\" of \"{raw_string.decode('ascii')}\"")
        self._function = chr(raw_string[-1])

    def __repr__(self) -> str:
        return f"AnsiEscape(function = {self._function}, arguments = {self._arguments})"

    @property
    def function(self) -> AnsiFunctions:
        """Return the ANSI function."""
        try:
            return AnsiFunctions(self._function)
        except ValueError:
            print(f"Unsupported function: {self._function}")
            return AnsiFunctions.UNSUPPORTED

    @property
    def arguments(self) -> Any:
        """Returns the ANSI function arguments depending on the function."""
        if self.function in [AnsiFunctions.CURSOR_FORWARD, AnsiFunctions.CURSOR_BACK]:
            return self._arguments[0] if len(self._arguments) > 0 else 1
        elif self.function == AnsiFunctions.SGR:
            res = []
            for arg in self._arguments:
                if self.FGCOLOR_BASE <= arg < self.FGCOLOR_BASE + len(self.COLORS):
                    res.append(AnsiSgrCommand(AnsiSgrCommands.SET_FGCOLOR, self.COLORS[AnsiColors(arg - self.FGCOLOR_BASE)]))
                elif self.BGCOLOR_BASE <= arg < self.BGCOLOR_BASE + len(self.COLORS):
                    res.append(AnsiSgrCommand(AnsiSgrCommands.SET_BGCOLOR, self.COLORS[AnsiColors(arg - self.BGCOLOR_BASE)]))
                elif arg == 0:
                    res.append(AnsiSgrCommand(AnsiSgrCommands.SET_DEFAULT, 0))
            return res
        elif self.function == AnsiFunctions.ERASE_IN_DISPLAY:
            return AnsiEdCommands(self._arguments[0] if len(self._arguments) > 0 else 0)
        else:
            raise NotImplemented(f"Cannot interpret arguments for function {str(self.function)}")


def create_tile(console_width: int, color: Tuple[int, int, int]) -> Tuple[Image.Image, ImageDraw.ImageDraw]:
    """Helper function to create a single tile to hold a single line of text.
    
        Params:
            console_width: 
                The requested console width.
            
            color: 
                The tile's background color.

        Returns:
            A tuple containing the tile itself and the ImageDraw object for that tile.
    """
    img = Image.new('RGB', (console_width * FONT_WIDTH, FONT_HEIGHT), color = color)
    d = ImageDraw.Draw(img)

    return img, d

def write_to_img(d: ImageDraw.ImageDraw, c: str, offset: int, bgcolor: Tuple[int, int, int], fgcolor: Tuple[int, int, int], font) -> None:
    """Helper function to write a single character to the given tile.

        Params:
            d:
                The ImageDraw object for the tile.

            c:
                The character to write.

            offset:
                The offset to write the character to.

            bgcolor:
                The requested background color.

            fgcolor:
                The requested text color.

            font:
                The requested font.
    """
    d.rectangle(((FONT_WIDTH * offset, 0), ((FONT_WIDTH * offset) + FONT_WIDTH, FONT_HEIGHT)), fill=bgcolor)
    d.text((FONT_WIDTH * offset, 0), c, fill = fgcolor, font = font)

def decode_file(buffer: bytes) -> List[Union[str, AnsiEscape]]:
    """Decode a given text and return the decoded result.
    
        This function accepts a buffer containing text encoded with CP862/CP437 (and optionally ANSI Escape codes).
        It translates the text to UTF-8 and returns a list of decoded characters, together with AnsiEscape objects
        representing the ANSI Escape codes.

        For example, given the following input:
            "\x80A\x1b[1;37;41m\xdb"
        The function will return:
            ['א', 'A', AnsiEscape("\x1b[1;37;41m"), '█']

        Params:
            buffer:
                Input buffer.

        Returns:
            List of characters/AnsiEscape objects.
    """
    res = []

    #buffer = ansi_escape.sub(b'', buffer)

    # First, we find the offset for all ANSI escape sequences, and store them in a dictionary
    ansi_locations = {}
    for match in ansi_escape.finditer(buffer):
        ansi_locations[match.start()] = match.group()
    
    # Now we iterate the buffer character by character
    i = 0
    while i < len(buffer):
        if i in ansi_locations:
            # If this is an ANSI escape sequence, create the object and skip it
            res.append(AnsiEscape(ansi_locations[i]))
            i += len(ansi_locations[i])
        else:
            # Otherwise, this is a character 
            # Try to decode using the translation table and fallback to standard ASCII
            byte = buffer[i]
            try:
                c = translation[byte]
            except KeyError:
                c = chr(byte)
            res.append(c)
            i += 1

    return res

def file_to_image(buffer: bytes, **kwargs) -> Image.Image:
    """Export a given text file as a decoded image.

        Params:
            buffer:
                Buffer representing the text file.
            
            kwargs:
                console_width: 
                    Console Width (in characters). Default is CONSOLE_WIDTH_DEFAULT.
                theme:
                    Default color theme ("dark" / "light"). Default is "dark".
                skip_ansi:
                    Whether or not to parse ANSI escape codes. Default is False.
    """

    console_width = kwargs.get("console_width", CONSOLE_WIDTH_DEFAULT)
    if console_width < CONSOLE_WIDTH_MIN or console_width > CONSOLE_WIDTH_MAX:
        raise ValueError(f"Console width {console_width} not in allowed range ({CONSOLE_WIDTH_MIN}-{CONSOLE_WIDTH_MAX}")

    try:
        theme = THEMES[kwargs.get("theme", "dark")]
    except KeyError:
        raise ValueError(f"Unknown theme: {kwargs['theme']}")

    skip_ansi = kwargs.get("skip_ansi", False)

    try:
        font = ImageFont.truetype(str(FONT_PATH), FONT_SIZE)
    except Exception:
        raise FileNotFoundError(f"Can't find font: {FONT_PATH}")

    content = decode_file(buffer)
    
    # Since we don't know the height of the final image, we process it with "tiles".
    # Each tile represents a single line containing "console_width" characters. 
    # Once we are done processing the entire file, we "paste" the tiles one after the other
    # to receive the complete image.

    tiles = []

    img, d = create_tile(console_width, theme.bgcolor)
    offset = 0

    bgcolor = theme.bgcolor
    fgcolor = theme.fgcolor

    def newline(img: Image.Image, d: ImageDraw.ImageDraw) -> Tuple[Image.Image, ImageDraw.ImageDraw, int]:
        tiles.append(img)
        img, d = create_tile(console_width, theme.bgcolor)
        offset = 0
        return img, d, offset

    for c in content:
        if c == "\n":
            # Save the previous tile and start a new one
            img, d, offset = newline(img, d)
        elif c in ["\r", "♣"]:
            # Skip these characters
            continue
        elif isinstance(c, AnsiEscape):
            if skip_ansi:
                # Skip the ANSI escape sequence if requested
                continue

            # Otherwise, handle it according to the function
            if c.function == AnsiFunctions.CURSOR_FORWARD:
                for i in range(c.arguments):
                    write_to_img(d, " ", offset, theme.bgcolor, theme.fgcolor, font)
                    offset += 1
                    if offset >= console_width:
                        img, d, offset = newline(img, d)
            elif c.function == AnsiFunctions.CURSOR_BACK:
                offset = min(0, offset - c.arguments)
            elif c.function == AnsiFunctions.ERASE_IN_DISPLAY:
                if c.arguments == AnsiEdCommands.ENTIRE_SCREEN:
                    tiles = []
                    img, d = create_tile(console_width, theme.bgcolor)
                    offset = 0
            elif c.function == AnsiFunctions.SGR:
                for command in c.arguments:
                    if command.type == AnsiSgrCommands.SET_FGCOLOR:
                        fgcolor = command.value
                    elif command.type == AnsiSgrCommands.SET_BGCOLOR:
                        bgcolor = command.value
                    elif command.type == AnsiSgrCommands.SET_DEFAULT:
                        fgcolor = theme.fgcolor
                        bgcolor = theme.bgcolor
        else:
            # Just text, write it
            write_to_img(d, c, offset, bgcolor, fgcolor, font)
            offset += 1

            if offset >= console_width:
                # A new line is needed here as well
                img, d, offset = newline(img, d)

    if len(tiles) == 0 or tiles[-1] != img:
        # Append the last tile if we didn't do so already
        tiles.append(img)
        
    # Create the full image by pasting the tiles one after the other
    height = len(tiles) * FONT_HEIGHT
    output = Image.new('RGB', (console_width * FONT_WIDTH, height), color = theme.bgcolor)

    for i, img in enumerate(tiles):
        output.paste(img, (0, FONT_HEIGHT * i))

    return output

def main(input_path: str, output_path: str, **kwargs) -> None:
    print(f"Parsing '{input_path}'")
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
    parser.add_argument('-s', '--skip_ansi', action='store_true', default=False, help="Skip ANSI Color codes")

    args = parser.parse_args()
    kwargs = {}

    kwargs["console_width"] = args.console_width
    kwargs["theme"] = args.theme
    kwargs["skip_ansi"] = args.skip_ansi

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
        #raise