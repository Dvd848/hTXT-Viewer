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

const AnsiFunctions = Object.freeze({
    // https://en.wikipedia.org/wiki/ANSI_escape_code
    // https://notes.burke.libbey.me/ansi-escape-codes/
    UNSUPPORTED         : "0",
    CURSOR_UP           : "A",
    CURSOR_FORWARD      : "C",
    CURSOR_BACK         : "D",
    ERASE_IN_DISPLAY    : "J",
    SGR                 : "m",
    SAVE_CUR_POS        : "s",
    RESTORE_CUR_POS     : "u",
    CURSOR_POSITION     : "H"
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

const AnsiSgrCommands = Object.freeze({
    SET_DEFAULT : 0,
    SET_BOLD    : 1,
    SET_FGCOLOR : 30,
    SET_BGCOLOR : 40,
});

class AnsiSgrCommand {
    constructor(type, value) {
        this.type = type
        this.value = value
    }
}

const AnsiEdCommands = Object.freeze({
    CURSOR_TO_END   : 0,
    CURSOR_TO_START : 1,
    ENTIRE_SCREEN   : 2
});

class AnsiEscape {
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

    static NUM_COLORS = Object.keys(AnsiEscape.COLORS).length;

    static FGCOLOR_BASE = 30;
    static BGCOLOR_BASE = 40;

    constructor(rawString) {
        this.rawString = rawString;
        this._parseAnsi()
    }

    _parseAnsi() {
        this._arguments = [];
        this.raw_arguments = this.rawString.substring(2, this.rawString.length - 1);
        let args = this.raw_arguments;
        if (args != "") {
            for (let arg of args.split(";")) {
                const parsed = parseInt(arg);
                if (!isNaN(parsed)) { 
                    this._arguments.push(parsed);
                }
                else {
                    console.log(`Unable to parse argument "${arg}" of "${this.rawString}"`);
                }
            }
        }
        this._function = this.rawString[this.rawString.length - 1];
    }

    static color(color, bold) {
        if (bold) {
            return AnsiEscape.BOLD_COLORS[color];
        }
        else {
            return AnsiEscape.COLORS[color];
        }
    }

    get func() {
        return this._function;
    }

    get args() {
        if ([AnsiFunctions.CURSOR_FORWARD, AnsiFunctions.CURSOR_BACK, AnsiFunctions.CURSOR_UP].includes(this._function)) {
            return (this._arguments.length > 0) ? this._arguments[0] : 1;
        }
        else if (this._function == AnsiFunctions.SGR) {
            let res = [];
            for (let arg of this._arguments) {
                if ((AnsiEscape.FGCOLOR_BASE <= arg) && (arg < AnsiEscape.FGCOLOR_BASE + AnsiEscape.NUM_COLORS)) {
                    res.push(new AnsiSgrCommand(AnsiSgrCommands.SET_FGCOLOR, arg - AnsiEscape.FGCOLOR_BASE));
                }
                else if ((AnsiEscape.BGCOLOR_BASE <= arg) && (arg < AnsiEscape.BGCOLOR_BASE + AnsiEscape.NUM_COLORS)) {
                    res.push(new AnsiSgrCommand(AnsiSgrCommands.SET_BGCOLOR, arg - AnsiEscape.BGCOLOR_BASE));
                }
                else if (arg == AnsiSgrCommands.SET_DEFAULT) {
                    res.push(new AnsiSgrCommand(AnsiSgrCommands.SET_DEFAULT, 0));
                }
                else if (arg == AnsiSgrCommands.SET_BOLD) {
                    res.push(new AnsiSgrCommand(AnsiSgrCommands.SET_BOLD, 0));
                }
                else {
                    console.log(`Unsupported SGR argument ${arg}`);
                }
            }

            return res;
        }
        else if (this._function == AnsiFunctions.ERASE_IN_DISPLAY) {
            return (this._arguments) ? this._arguments[0] : 0;
        }
        else if (this._function == AnsiFunctions.CURSOR_POSITION) {
            if (this._arguments.length == 2) {
                return this._arguments;
            }
            else {
                let row = 1
                let col = 1;
                if (this._raw_arguments.length > 1)
                {
                    if (this._raw_arguments[0] == ";") {
                        col = this._arguments[0];
                    }
                    else if (this._raw_arguments[this._raw_arguments.length - 1] == ";") {
                        row = this._arguments[0];
                    }
                }

                return [row, col];
            }
        }
        else {
            console.log(`Cannot interpret arguments for function ${this._function}`);
        }
    }
}

const ANSI_ESCAPE_PATTERN = /[\u001b\u009b←][[()#;?]*((?:[0-9]{1,4}(?:;[0-9]{0,4})*)?)([0-9A-ORZcf-nqrysu=><])/g;
const LEFT_RIGHT_MARK = String.fromCharCode(8206);

class CodePageTranslator {
    constructor() {
        this.translationMap = {
            "art": {
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

    async translate(buffer) {
        let then = performance.now();
        let counter = 0;
        let content = "";
        for (let x of buffer) {
            content += this.translateChar(x);
            then = await pauseIfNeeded(counter, then);
            counter++;
        }
        
        let ansiLocations = {};
        let match;
        counter = 0;

        while (match = ANSI_ESCAPE_PATTERN.exec(content)) {
            ansiLocations[match.index] = match[0];

            then = await pauseIfNeeded(counter, then);
            counter++;
        }

        
        let i = 0;
        let res = []
        while (i < content.length) {
            if (i in ansiLocations) {
                // If this is an ANSI escape sequence, create the object and skip it
                res.push(new AnsiEscape(ansiLocations[i]))
                i += ansiLocations[i].length
            }
            else {
                // Otherwise, this is a character 
                res.push(content[i])
                i += 1
            }
            then = await pauseIfNeeded(i, then); // TODO: Might skip mod(1000) since i jumps in values
        }

        return res;
    }

};


class AnsiParser {
    constructor() {
    }

    async parse(content, terminal) {
        let then = performance.now();
        let counter = 0;
        for (let c of content) {
            if (!(c instanceof AnsiEscape)) {
                terminal.write(c);
            }
            else {
                if (c.func == AnsiFunctions.CURSOR_FORWARD) {
                    terminal.moveRight(c.args);
                }
                else if (c.func == AnsiFunctions.CURSOR_BACK) {
                    terminal.moveLeft(c.args);
                }
                else if (c.func == AnsiFunctions.CURSOR_UP) {
                    terminal.moveUp(c.args);
                }
                else if (c.func == AnsiFunctions.ERASE_IN_DISPLAY) {
                    if (c.args == AnsiEdCommands.ENTIRE_SCREEN) {
                        terminal.clearScreen();
                    }
                }
                else if (c.func == AnsiFunctions.SAVE_CUR_POS) {
                    terminal.saveCurrentPosition();
                }
                else if (c.func == AnsiFunctions.RESTORE_CUR_POS) {
                    terminal.restoreCurrentPosition();
                }
                else if (c.func == AnsiFunctions.CURSOR_POSITION) {
                    terminal.setCurrentPosition(c.args[0] - 1, c.args[1] - 1);
                }
                else if (c.func == AnsiFunctions.SGR) {
                    for (let command of c.args) {
                        if (command.type == AnsiSgrCommands.SET_FGCOLOR) {
                            terminal.setFgColor(command.value);
                        }
                        else if (command.type == AnsiSgrCommands.SET_BGCOLOR) {
                            terminal.setBgColor(command.value);
                        }
                        else if (command.type == AnsiSgrCommands.SET_DEFAULT) {
                            terminal.setDefaultColors();
                        }
                        else if (command.type == AnsiSgrCommands.SET_BOLD) {
                            terminal.setBold(true);
                        }
                    }
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
        }
    }
}


class Terminal {
    constructor(terminalWidth) {
        this.fontWidth = 8;
        this.fontHeight = 15;
        this.terminalWidth = terminalWidth;

        this.skipNextNewline = false;

        this.saved_row = null;
        this.saved_col = null;

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
        ctx.font = "16px Classic Console Neue";


        if (character == "\n") {
            if (!this.skipNextNewline) {
                this.row += 1;
                this.col = 0;
            }
        }
        else if (character  == "\r" || character == "♣") {
            //skip
            //this.skipNextNewline = false;
        }
        else {
            ctx.fillStyle = AnsiEscape.color(this.background, false);
            ctx.fillRect(this.col * this.fontWidth, 0, this.fontWidth, this.fontHeight);

            ctx.fillStyle = AnsiEscape.color(this.foreground, this.bold);
            ctx.fillText(character, this.col * this.fontWidth, 0);
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

    moveRight(n) {
        this.col = Math.min(this.col + n, this.terminalWidth);
    }

    moveLeft(n) {
        this.col = Math.max(this.col - n, 0);
    }

    moveUp(n) {
        this.row = Math.max(this.row - n, 0);
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

    saveCurrentPosition() {
        this.saved_row = this.row;
        this.saved_col = this.col;
    }

    restoreCurrentPosition() {
        if (this.saved_row !== null && this.saved_col !== null) {
            this.row = this.saved_row;
            this.col = this.saved_col;
    
            this.saved_row = null;
            this.saved_col = null;
        }
        else {
            console.log(`Attempt to restore position when position not saved`);
        }
    }

    setCurrentPosition(row, col) {
        this.row = row;
        this.col = col;
    }

    async toCanvas() {
        let res = document.createElement('canvas');
        if (this.tiles.length > 0) {
            res.width = this.tiles[0].width;
            res.height = this.tiles[0].height * this.tiles.length;
            let ctx = res.getContext('2d');

            let col = 0;
            for (let tile of this.tiles) {
                ctx.drawImage(tile.getContext('2d').canvas, 0, col * this.tiles[0].height);
                if (col && col % 5 === 0) {
                    await oneMoment();
                }
                col++;
            }
        }
        return res;
    }
}