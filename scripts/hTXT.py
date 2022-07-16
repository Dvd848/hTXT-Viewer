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
import os

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


class AnsiFunctions(Enum):
    # https://en.wikipedia.org/wiki/ANSI_escape_code
    # https://notes.burke.libbey.me/ansi-escape-codes/
    UNSUPPORTED         = "0"
    CURSOR_UP           = "A"
    CURSOR_FORWARD      = "C"
    CURSOR_BACK         = "D"
    ERASE_IN_DISPLAY    = "J"
    SGR                 = "m"
    SAVE_CUR_POS        = "s"
    RESTORE_CUR_POS     = "u"
    CURSOR_POSITION     = "H"

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
    SET_DEFAULT = 0
    SET_BOLD    = 1
    SET_FGCOLOR = 30
    SET_BGCOLOR = 40

AnsiSgrCommand = namedtuple("AnsiSgrCommand", "type value")

class AnsiEdCommands(Enum):
    CURSOR_TO_END   = 0
    CURSOR_TO_START = 1
    ENTIRE_SCREEN   = 2


class AnsiEscape():
    """Represents an ANSI Escape Sequence."""
    COLORS = {
        AnsiColors.BLACK:   (0x0C, 0x0C, 0x0C),
        AnsiColors.RED:     (0xAA, 0x00, 0x00),
        AnsiColors.GREEN:   (0x00, 0xAA, 0x00),
        AnsiColors.YELLOW:  (0xAA, 0x55, 0x00),
        AnsiColors.BLUE:    (0x00, 0x37, 0xDA),
        AnsiColors.MAGENTA: (0xAA, 0x00, 0xAA),
        AnsiColors.CYAN:    (0x00, 0xAA, 0xAA),
        AnsiColors.WHITE:   (0xAA, 0xAA, 0xAA),    
    }

    BOLD_COLORS = {
        AnsiColors.BLACK:   (0xCC, 0xCC, 0xCC),
        AnsiColors.RED:     (0xFF, 0x55, 0x55),
        AnsiColors.GREEN:   (0x55, 0xFF, 0x55),
        AnsiColors.YELLOW:  (0xFF, 0xFF, 0x55),
        AnsiColors.BLUE:    (0x55, 0x55, 0xFF),
        AnsiColors.MAGENTA: (0xFF, 0x55, 0xFF),
        AnsiColors.CYAN:    (0x55, 0xFF, 0xFF),
        AnsiColors.WHITE:   (0xFF, 0xFF, 0xFF)
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
        self._raw_arguments = raw_string[2:-1]
        arguments = self._raw_arguments
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
        if self.function in [AnsiFunctions.CURSOR_FORWARD, AnsiFunctions.CURSOR_BACK, AnsiFunctions.CURSOR_UP]:
            return self._arguments[0] if len(self._arguments) > 0 else 1
        elif self.function == AnsiFunctions.SGR:
            res = []
            for arg in self._arguments:
                if self.FGCOLOR_BASE <= arg < self.FGCOLOR_BASE + len(self.COLORS):
                    res.append(AnsiSgrCommand(AnsiSgrCommands.SET_FGCOLOR, AnsiColors(arg - self.FGCOLOR_BASE)))
                elif self.BGCOLOR_BASE <= arg < self.BGCOLOR_BASE + len(self.COLORS):
                    res.append(AnsiSgrCommand(AnsiSgrCommands.SET_BGCOLOR, AnsiColors(arg - self.BGCOLOR_BASE)))
                elif arg == AnsiSgrCommands.SET_BOLD.value:
                    res.append(AnsiSgrCommand(AnsiSgrCommands.SET_BOLD, 0))
                elif arg == AnsiSgrCommands.SET_DEFAULT.value:
                    res.append(AnsiSgrCommand(AnsiSgrCommands.SET_DEFAULT, 0))
            return res
        elif self.function == AnsiFunctions.ERASE_IN_DISPLAY:
            return AnsiEdCommands(self._arguments[0] if len(self._arguments) > 0 else 0)
        elif self.function == AnsiFunctions.CURSOR_POSITION:
            if (len(self._arguments) == 2):
                return self._arguments
            else:
                row = 1
                col = 1
                if (len(self._raw_arguments) > 1):
                    if (self._raw_arguments[0] == ";"):
                        col = self._arguments[0]
                    elif (self._raw_arguments[-1] == ";"):
                        row = self._arguments[0]
                return [row, col]
        else:
            raise NotImplementedError(f"Cannot interpret arguments for function {str(self.function)}")

    @classmethod
    def color(cls, color: AnsiColors, bold: bool) -> Tuple[int, int, int]:
        """Return the RGB code for the given color.

        Params:
            color:
                A color code.

            bold:
                Whether to use normal colors or regular colors.

        Returns:
            The matching RGB code as a tuple.
        
        """
        if (bold):
            return cls.BOLD_COLORS[color]
        else:
            return cls.COLORS[color]


class Terminal():
    """Simulates a terminal."""

    FONT_PATH       = Path(__file__).parent.resolve() / '..' / 'resources' / 'clacon2.ttf'

    FONT_SIZE               = 16
    FONT_WIDTH              = 8
    FONT_HEIGHT             = 13
    CONSOLE_WIDTH_DEFAULT   = 80
    CONSOLE_WIDTH_MIN       = 40
    CONSOLE_WIDTH_MAX       = 1000

    def __init__(self, width: int) -> None:
        self.width = width

        self.skipNextNewline = False

        self.saved_row = None
        self.saved_col = None

        try:
            self.font = ImageFont.truetype(str(self.FONT_PATH), self.FONT_SIZE)
        except Exception:
            raise FileNotFoundError(f"Can't find font: {self.FONT_PATH}")

        self.clear_screen()
        self.set_default_colors()
    
    def write(self, character: str) -> None:
        """Write a single character to the terminal.
        
        Params:
            character:
                The character to write to the terminal.
        """

        # If the tile doesn't exist yet, create it
        for _ in range(len(self.tiles), self.row + 1):
            img = Image.new('RGB', (self.width * self.FONT_WIDTH, self.FONT_HEIGHT), color = AnsiEscape.color(AnsiColors.BLACK, False))
            self.tiles.append(img)
        

        img = self.tiles[self.row]
        d = ImageDraw.Draw(img)

        if (character == "\n"):
            if not self.skipNextNewline:
                self.row += 1
                self.col = 0
        elif character in ["\r", "♣"]:
            # skip
            pass
        else:
            # Background
            d.rectangle(((self.FONT_WIDTH * self.col, 0), ((self.FONT_WIDTH * self.col) + self.FONT_WIDTH, self.FONT_HEIGHT)), 
                        fill=AnsiEscape.color(self.background, False))
            # Foreground
            d.text((self.FONT_WIDTH * self.col, 0), character, fill = AnsiEscape.color(self.foreground, self.bold), font = self.font)

            self.col += 1
            self.skipNextNewline = False
            
            if (self.col == self.width):
                self.row += 1
                self.col = 0
                self.skipNextNewline = True

    def move_right(self, n: int) -> None:
        """Move the cursor right n times."""
        self.col = min(self.col + n, self.width)

    def move_left(self, n: int) -> None:
        """Move the cursor left n times."""
        self.col = max(self.col - n, 0)

    def move_up(self, n: int) -> None:
        """Move the cursor up n times."""
        self.row = max(self.row - n, 0)
    

    def clear_screen(self) -> None:
        """Clear the screen."""
        self.row = 0
        self.col = 0

        # Since we don't know the height of the final image, we process it with "tiles".
        # Each tile represents a single line containing "console_width" characters. 
        # Once we are done processing the entire file, we "paste" the tiles one after the other
        # to receive the complete image.
        self.tiles = []
    

    def set_fgcolor(self, color: AnsiColors) -> None:
        """Set foreground color."""
        self.foreground = color
    

    def set_bgcolor(self, color: AnsiColors) -> None:
        """Set background color."""
        self.background = color
    

    def set_default_colors(self) -> None:
        """Reset terminal colors."""
        self.set_fgcolor(AnsiColors.WHITE)
        self.set_bgcolor(AnsiColors.BLACK)
        self.bold = False
    

    def set_bold(self, bold: bool) -> None:
        """Set boldness."""
        self.bold = bold
    

    def save_current_position(self) -> None:
        """Save current cursor position."""
        self.saved_row = self.row
        self.saved_col = self.col
    

    def restore_current_position(self) -> None:
        """Restore current cursor position."""
        if (self.saved_row != None and self.saved_col != None):
            self.row = self.saved_row
            self.col = self.saved_col
    
            self.saved_row = None
            self.saved_col = None
        else:
            print(f"Attempt to restore position when position not saved")

    def set_current_position(self, row: int, col: int) -> None:
        """Set current cursor position."""
        self.row = row
        self.col = col
    

    def to_img(self) -> Image.Image:
        """Export the terminal to an image."""
        # Create the full image by pasting the tiles one after the other
        height = len(self.tiles) * self.FONT_HEIGHT
        output = Image.new('RGB', (self.width * self.FONT_WIDTH, height), color = AnsiEscape.color(AnsiColors.BLACK, False))

        for i, img in enumerate(self.tiles):
            output.paste(img, (0, self.FONT_HEIGHT * i))

        return output


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
                skip_ansi:
                    Whether or not to parse ANSI escape codes. Default is False.
    """

    console_width = kwargs.get("console_width", Terminal.CONSOLE_WIDTH_DEFAULT)
    if console_width < Terminal.CONSOLE_WIDTH_MIN or console_width > Terminal.CONSOLE_WIDTH_MAX:
        raise ValueError(f"Console width {console_width} not in allowed range ({Terminal.CONSOLE_WIDTH_MIN}-{Terminal.CONSOLE_WIDTH_MAX}")

    skip_ansi = kwargs.get("skip_ansi", False)

    terminal = Terminal(console_width)
    content = decode_file(buffer)

    for c in content:
        if not isinstance(c, AnsiEscape):
            terminal.write(c)
        else:
            if skip_ansi:
                continue
            if c.function == AnsiFunctions.CURSOR_FORWARD:
                terminal.move_right(c.arguments)
            elif c.function == AnsiFunctions.CURSOR_BACK:
                terminal.move_left(c.arguments)
            elif c.function == AnsiFunctions.CURSOR_UP:
                terminal.move_up(c.arguments)
            elif c.function == AnsiFunctions.ERASE_IN_DISPLAY:
                if c.arguments == AnsiEdCommands.ENTIRE_SCREEN:
                    terminal.clear_screen()
            elif c.function == AnsiFunctions.SAVE_CUR_POS:
                terminal.save_current_position()
            elif c.function == AnsiFunctions.RESTORE_CUR_POS:
                terminal.restore_current_position()
            elif c.function == AnsiFunctions.CURSOR_POSITION:
                terminal.set_current_position(c.arguments[0] - 1, c.arguments[1] - 1)
            elif c.function == AnsiFunctions.SGR:
                for command in c.arguments:
                    if command.type == AnsiSgrCommands.SET_FGCOLOR:
                        terminal.set_fgcolor(command.value)
                    elif command.type == AnsiSgrCommands.SET_BGCOLOR:
                        terminal.set_bgcolor(command.value)
                    elif command.type == AnsiSgrCommands.SET_DEFAULT:
                        terminal.set_default_colors()
                    elif command.type == AnsiSgrCommands.SET_BOLD:
                        terminal.set_bold(True)
    
    return terminal.to_img()

def main(input_path: str, output_path: str, **kwargs) -> None:
    if not Path(input_path).is_file():
        raise FileNotFoundError(f"Can't find file '{input_path}'")
        
    print(f"Parsing '{input_path}'")
    with open(input_path, "rb") as f:
        output = file_to_image(f.read(), **kwargs)
        output.save(output_path)
        print(f"Saved to '{output_path}'")

if __name__ == "__main__":
    BATCH_EXTENSIONS = set(x.lower() for x in [".txt", ".ans", ".sos", ".asc", ".ansi", ".nfo"])

    parser = argparse.ArgumentParser(description="Decode old Hebrew text files encoded with Code Page 862")
    parser.add_argument('-w', '--console-width', type=int, default=Terminal.CONSOLE_WIDTH_DEFAULT, help="Console width")
    parser.add_argument('-s', '--skip_ansi', action='store_true', default=False, help="Skip ANSI Color codes")

    input_group = parser.add_mutually_exclusive_group(required = True)
    input_group.add_argument('-i', '--input', type=str, help="Input file")
    input_group.add_argument('-id', '--input-dir', type=str, help="Input directory")

    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument('-o', '--output', type=str, help="Output file")
    output_group.add_argument('-od', '--output-dir', type=str, help="Output directory")

    args = parser.parse_args()

    if args.input_dir is not None and args.output is not None:
        parser.error('If the input is a directory (-id), the output must be a directory as well (-od)')

    kwargs = {}

    kwargs["console_width"] = args.console_width
    kwargs["skip_ansi"] = args.skip_ansi

    if args.input_dir is not None:
        input_dir = Path(args.input_dir)
        output_base_dir = Path(args.output_dir) if args.output_dir is not None else input_dir
        error_count = 0
        file_count = 0
        for root, dirs, files in os.walk(args.input_dir):
            for file in files:
                lower_file = file.lower()
                rel_dir = os.path.relpath(root, args.input_dir)
                file_processed = False
                for extension in BATCH_EXTENSIONS:
                    if lower_file.endswith(extension):
                        file_processed = True
                        file_count += 1
                        input_path = input_dir / rel_dir / file
                        output_path = output_base_dir / rel_dir / (input_path.stem + ".png")
                        try:
                            output_path.parent.mkdir(parents = True, exist_ok = True)
                            main(str(input_path), str(output_path), **kwargs)
                        except Exception as e:
                            error_count += 1
                            print(f"Error: {str(e)}")
                if not file_processed:
                    print(f"Skipping '{lower_file}' due to extension")
        
        print(f"\n{file_count} files processed." )
        if error_count > 0:
            print(f"{error_count} errors encountered during processing, please check log.")
    else:
        output_file = None
        if args.output is not None:
            output_file = args.output
        else:
            input_file = Path(args.input).absolute()
            output_filename = input_file.stem + ".png"
            if args.output_dir is not None:
                output_file = str(Path(args.output_dir) / output_filename)
            else:
                output_file = str(input_file.parent / output_filename)

        try:
            main(args.input, output_file, **kwargs)
        except Exception as e:
            raise SystemExit(f"Error: {str(e)}")
            #raise
