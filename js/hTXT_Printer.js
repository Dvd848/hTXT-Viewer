'use strict';

const pauseIfNeeded = async function(counter, then) {
    // https://stackoverflow.com/questions/38735201/
    // Calling performance.now is slow,
    //  so only check every 1000 iterations
    if (counter && counter % 1000 === 0) {
        const now = performance.now();

        // Have 0.1 second elapsed?
        if (now - then > 100) {
            await oneMoment();
            then = performance.now();
        }
    }

    return then;
};

const oneMoment = function() {
    return new Promise(resolve => setTimeout(resolve));
}

const AsciiTable = Object.freeze({
    ESC              : "\x1B"
});

const PrinterFunctions = Object.freeze({
    UNSUPPORTED         : "\x00",
    UNDERLINE           : "\x2D",
    CODE_AREA_EXPAND    : "\x36",
    INIT_PRINTER        : "\x40",
    LINE_SPACING_72     : "\x41",
    SET_PAGE_LENGTH     : "\x43",
    BOLD_ON             : "\x47",
    BOLD_OFF            : "\x48",
    SUBSUPERSCRIPT      : "\x53",
    SUBSUPERSCRIPT_OFF  : "\x54",
    DOUBLE_WIDE_MODE    : "\x57",
    LEFT_MARGIN         : "\x6C",
});

const AnsiColors = Object.freeze({
    BLACK   : 0,
    RED     : 1,
    GREEN   : 2,
    YELLOW  : 3,
    BLUE    : 4,
    MAGENTA : 5,
    CYAN    : 6,
    WHITE   : 7,
});

class PrinterEscape {
    static COLORS = Object.freeze({
        [AnsiColors.BLACK]:   "#0C0C0C",
        [AnsiColors.RED]:     "#AA0000",
        [AnsiColors.GREEN]:   "#00AA00",
        [AnsiColors.YELLOW]:  "#AA5500",
        [AnsiColors.BLUE]:    "#0037DA",
        [AnsiColors.MAGENTA]: "#AA00AA",
        [AnsiColors.CYAN]:    "#00AAAA",
        [AnsiColors.WHITE]:   "#AAAAAA"
    });

    static BOLD_COLORS = Object.freeze({
        [AnsiColors.BLACK]:   "#CCCCCC",
        [AnsiColors.RED]:     "#FF5555",
        [AnsiColors.GREEN]:   "#55FF55",
        [AnsiColors.YELLOW]:  "#FFFF55",
        [AnsiColors.BLUE]:    "#5555FF",
        [AnsiColors.MAGENTA]: "#FF55FF",
        [AnsiColors.CYAN]:    "#55FFFF",
        [AnsiColors.WHITE]:   "#FFFFFF"
    });

    constructor(rawString) {
        this.rawString = rawString;
        this._parseEscape()
    }

    _parseEscape() {
        this._arguments = [];
        this.raw_arguments = this.rawString.substring(2, this.rawString.length);
        
        let args = this.raw_arguments;
        if (args != "") {
            for (let arg of args) {
                this._arguments.push(arg.charCodeAt(0));
            }
        }
        
        this._function = this.rawString[1];
    }

    static color(color, bold) {
        if (bold) {
            return PrinterEscape.BOLD_COLORS[color];
        }
        else {
            return PrinterEscape.COLORS[color];
        }
    }

    get func() {
        return this._function;
    }

    get args() {
        
        if ([PrinterFunctions.UNDERLINE, PrinterFunctions.SUBSUPERSCRIPT].includes(this._function)) {
            return (this._arguments[0] == 0) ? false : true;
        }
        else {
            console.log(`Cannot interpret arguments for function ${this._function}`);
        }
        
    }
}

const ESCAPE_PATTERN = `${AsciiTable.ESC}(
${PrinterFunctions.INIT_PRINTER}|
${PrinterFunctions.SET_PAGE_LENGTH}.|
${PrinterFunctions.BOLD_ON}|
${PrinterFunctions.BOLD_OFF}|
${PrinterFunctions.SUBSUPERSCRIPT}.|
${PrinterFunctions.SUBSUPERSCRIPT_OFF}|
${PrinterFunctions.UNDERLINE}.|
${PrinterFunctions.CODE_AREA_EXPAND}|
${PrinterFunctions.DOUBLE_WIDE_MODE}.|
${PrinterFunctions.LINE_SPACING_72}.|
${PrinterFunctions.LEFT_MARGIN}.|
)`.replaceAll("\n", "", "g");

// Create a regular expression object
const ESCAPE_PATTERN_REGEX = new RegExp(ESCAPE_PATTERN, "g");

const LEFT_RIGHT_MARK = String.fromCharCode(8206);

class CodePageTranslator {
    constructor() {
        this.translationMap = {
            "art": {
                0x01: '', 0x02: '', 0x03: '', 0x04: '', 0x05: '', 0x06: '', 0x07: '',
                0x08: '', 0x09: '', 0x0B: '', 0x0C: '', 0x0E: '', 0x0F: '',
                0x10: '', 0x11: '', 0x12: '', 0x13: '', 0x14: '', 0x15: '', 0x16: '', 0x17: '',
                0x18: '', 0x19: '', 0x1A: '', 0x1B: '', 0x1C: '', 0x1D: '', 0x1E: '', 0x1F: '',

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
                0xF8: '°', 0xF9: '∙', 0xFA: '·', 0xFB: '√', 0xFC: 'ⁿ', 0xFD: '²', 0xFE: '■', 0xFF: String.fromCharCode(160)
            },

            "hebrew": {
                0x80: 'א', 0x81: 'ב', 0x82: 'ג', 0x83: 'ד', 0x84: 'ה', 0x85: 'ו', 0x86: 'ז', 0x87: 'ח',
                0x88: 'ט', 0x89: 'י', 0x8A: 'ך', 0x8B: 'כ', 0x8C: 'ל', 0x8D: 'ם', 0x8E: 'מ', 0x8F: 'ן',
                0x90: 'נ', 0x91: 'ס', 0x92: 'ע', 0x93: 'ף', 0x94: 'פ', 0x95: 'ץ', 0x96: 'צ', 0x97: 'ק',
                0x98: 'ר', 0x99: 'ש', 0x9A: 'ת',
            }
        };

    }

    translateChar(asciiValue) {
        if (asciiValue in this.translationMap.art) {
            return this.translationMap.art[asciiValue];
        }

        if (asciiValue in this.translationMap.hebrew) {
            return this.translationMap.hebrew[asciiValue];// + LEFT_RIGHT_MARK;
        }

        return String.fromCharCode(asciiValue);
    }

    async translate(buffer, progressCallback) {
        let then = performance.now();
        let counter = 0;
        let content = "";
        
        for (let x of buffer) {
            content += String.fromCharCode(x); //this.translateChar(x);
            then = await pauseIfNeeded(counter, then);
            counter++;
            if (counter % 100 == 0) {
                progressCallback("Translating characters", (counter / buffer.length) * 100);
            }
        }
        
        content = content.replaceAll("\r\n\r\n", "\r\n");
        
        let escapeLocations = {};
        let match;
        counter = 0;

        while (match = ESCAPE_PATTERN_REGEX.exec(content)) {
            //console.log(match[0])
            escapeLocations[match.index] = match[0];

            then = await pauseIfNeeded(counter, then);
            counter++;
        }

        
        let i = 0;
        let res = []
        while (i < content.length) {
            if (i in escapeLocations) {
                // If this is an ANSI escape sequence, create the object and skip it
                res.push(new PrinterEscape(escapeLocations[i]))
                i += escapeLocations[i].length
            }
            else {
                // Otherwise, this is a character 
                const char = this.translateChar(content[i].charCodeAt(0));
                if (char != "")
                {
                    res.push(char);
                }
                i += 1
            }
            then = await pauseIfNeeded(i, then); // TODO: Might skip mod(1000) since i jumps in values
            if (i % 100 == 0) {
                progressCallback("Collecting content", (i / content.length) * 100);
            }
        }

        return res;
    }

};


class PrinterParser {
    constructor() {
    }

    async parse(content, terminal, progressCallback) {
        let then = performance.now();
        let counter = 0;
        for (let c of content) {
            if (!(c instanceof PrinterEscape)) {
                terminal.write(c);
            }
            else {
                if ([
                    PrinterFunctions.INIT_PRINTER,
                    PrinterFunctions.SET_PAGE_LENGTH,
                    PrinterFunctions.CODE_AREA_EXPAND,
                    PrinterFunctions.DOUBLE_WIDE_MODE,
                    PrinterFunctions.LINE_SPACING_72,
                    PrinterFunctions.LEFT_MARGIN
                ].includes(c.func)) {
                    // nop
                }
                else if (c.func == PrinterFunctions.BOLD_ON) {
                    terminal.setBold(true);
                }
                else if (c.func == PrinterFunctions.BOLD_OFF) {
                    terminal.setBold(false);

                    // Not sure why, but this command is used to cancel subscript & superscript as well
                    terminal.setSubscript(false);
                    terminal.setSuperscript(false);
                }
                else if (c.func == PrinterFunctions.UNDERLINE) {
                    terminal.setUnderline(c.args);
                }
                else if (c.func == PrinterFunctions.SUBSUPERSCRIPT) {
                    if (c.args) {
                        terminal.setSubscript(true);
                        terminal.setSuperscript(false);
                    }
                    else {
                        terminal.setSubscript(false);
                        terminal.setSuperscript(true);
                    }
                }
                else if (c.func == PrinterFunctions.SUBSUPERSCRIPT_OFF) {
                    terminal.setSubscript(false);
                    terminal.setSuperscript(false);
                }
                else {
                    console.log(`Unsupported function ${c.func}`);
                }
            }
            if (counter > 489) {
                //break;
            }
            then = await pauseIfNeeded(counter, then);
            counter++;
            if (counter % 100 == 0) {
                progressCallback("Parsing content", (counter / content.length) * 100);
            }
        }
    }
}


class Terminal {
    constructor(terminalWidth) {
        this.fontWidth = 8;
        this.fontHeight = 15;
        this.terminalWidth = terminalWidth;

        this.underline = false;
        this.subscript = false;
        this.superscript = false;

        this.skipNextNewline = false;

        this.fontFace = "Classic Console Neue";
        this.defaultFontSize = 16;
        this.subSuperFontSize = 11;

        this.fontSize = this.defaultFontSize;

        this.clearScreen();
        this.setDefaultColors();
    }

    write(character) {
        for (let r = this.tiles.length; r <= this.row; r++) {
            let newCanvas = document.createElement('canvas');
            newCanvas.width = this.fontWidth * (this.terminalWidth);
            newCanvas.height = this.fontHeight;
            
            this.tiles.push(newCanvas);
        }

        const canvas = this.tiles[this.row];
        
        const ctx = canvas.getContext('2d');
        ctx.textBaseline = "top";

        if (character == "\n") {
            if (!this.skipNextNewline) {
                this.row += 1;
                this.col = 0;
            }
        }
        else if (character  == "\r") {
            //skip
        }
        else {
            ctx.fillStyle = PrinterEscape.color(this.background, false);
            ctx.fillRect(this.col * this.fontWidth, 0, this.fontWidth, this.fontHeight);

            ctx.fillStyle = PrinterEscape.color(this.foreground, false);

            if ( (this.subscript) || (this.superscript) )
            {
                this.fontSize = this.subSuperFontSize;
            }
            else
            {
                this.fontSize = this.defaultFontSize;
            }
            ctx.font = this.font();

            ctx.fillText(character, this.col * this.fontWidth, (this.subscript) ? 6 : 0);

            if (this.underline) {
                ctx.fillStyle = PrinterEscape.color(this.foreground, false);
                ctx.fillRect(this.col * this.fontWidth, this.fontHeight - 1, this.fontWidth, 1);
            }

            this.col += 1;
            this.skipNextNewline = false;
            
            if (this.col == this.terminalWidth)
            {
                this.row += 1;
                this.col = 0;
                this.skipNextNewline = true;
            }
        }
    }

    font() {
        let res = "";
        if (this.bold)
        {
            res += "bold ";
        }

        res += this.fontSize.toString() + "px";
        res += " " + this.fontFace;

        return res;
    }

    clearScreen() {
        this.row = 0;
        this.col = 0;
        this.tiles = [];
    }

    setFgColor(color) {
        this.foreground = color;
    }

    setBgColor(color) {
        this.background = color;
    }

    setDefaultColors() {
        this.setFgColor(AnsiColors.WHITE);
        this.setBgColor(AnsiColors.BLACK);
        this.bold = false;
    }

    setBold(bold) {
        this.bold = bold;
    }

    setUnderline(underline) {
        this.underline = underline;
    }

    setSubscript(subscript) {
        this.subscript = subscript;
    }

    setSuperscript(superscript) {
        this.superscript = superscript;
    }

    async toCanvas(progressCallback) {
        let res = document.createElement('canvas');
        if (this.tiles.length > 0) {
            res.width = this.tiles[0].width;
            // TODO: https://bugzilla.mozilla.org/show_bug.cgi?id=1282074
            // In Firefox, the max value for each dimension is 32767
            res.height = this.tiles[0].height * this.tiles.length;
            let ctx = res.getContext('2d');

            let col = 0;
            for (let tile of this.tiles) {
                ctx.drawImage(tile.getContext('2d').canvas, 0, col * this.tiles[0].height);
                if (col && col % 5 === 0) {
                    await oneMoment();
                }
                col++;
                if (col % 100 == 0) {
                    progressCallback("Creating image", (col / this.tiles.length) * 100);
                }
            }
        }
        return res;
    }
}