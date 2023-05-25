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

const SpecialCharacters = Object.freeze({
    UNSUPPORTED         : "\x00",
    CENTER              : "\xD9",
    NEWLINE             : "\r\n",
    PARAGRAPH           : ".P",
    LEFT_ALIGN          : "\xDA",
    H2                  : "\xCB",
    H3                  : "\xCA",
    SUBSCRIPT           : "\x19",
    SUPERSCRIPT         : "\x18",
});

class EinsteinEscape {
    constructor(rawString) {
        this.rawString = rawString;
    }
}

const ESCAPE_PATTERN = `(
${SpecialCharacters.CENTER}|
${SpecialCharacters.NEWLINE}##NEWLINE##|
${SpecialCharacters.PARAGRAPH.replace(".", "\\.")}|
${SpecialCharacters.LEFT_ALIGN}
)`.replaceAll("\n", "", "g").replace("##NEWLINE##", "\n");

// Create a regular expression object
const ESCAPE_PATTERN_REGEX = new RegExp(ESCAPE_PATTERN, "g");

const LEFT_RIGHT_MARK = String.fromCharCode(8206);

function hasHebrewCharacters(str) {
    const regex = /[\u0590-\u05FF]/;
    return regex.test(str);
}

class CodePageTranslator {
    constructor() {
        this.translationMap = {
            "art": {
                0x01: '', 0x02: '', 0x03: '', 0x04: '', 0x05: '', 0x06: '', 0x07: '',
                0x08: '', 0x09: '', 0x0B: '', 0x0C: '', 0x0E: '', 0x0F: '',
                0x10: '', 0x11: '', 0x12: '', 0x13: '', 0x14: '', 0x15: '', 0x16: '', 0x17: '',
                /*0x18: '', 0x19: '',*/ 0x1A: '', 0x1B: '←', 0x1C: '', 0x1D: '', 0x1E: '', 0x1F: '',

                0x28: ')', 0x29: '(',

                0x9B: '¢', 0x9C: '£', 0x9D: '¥', 0x9E: '₧', 0x9F: 'ƒ',
                0xA0: 'á', 0xA1: 'í', 0xA2: 'ó', 0xA3: 'ú', 0xA4: 'ñ', 0xA5: 'Ñ', 0xA6: 'ª', 0xA7: 'º',
                0xA8: '¿', 0xA9: '⌐', 0xAA: '¬', 0xAB: '½', 0xAC: '¼', 0xAD: '¡', 0xAE: '«', 0xAF: '»',
                0xB0: '░', 0xB1: '▒', 0xB2: '▓', 0xB3: '│', 0xB4: '┤', 0xB5: '┘', 0xB6: '┌', 0xB7: 'α',
                0xB8: 'β', 0xB9: 'Γ', 0xBA: 'π', 0xBB: /*'╗'*/'Σ', 0xBC: 'σ', 0xBD: 'μ', 0xBE: 'γ', 0xBF: '┐',
                0xC0: '└', 0xC1: '┴', 0xC2: '┬', 0xC3: '├', 0xC4: '─', 0xC5: '┼', 0xC6: '╞', 0xC7: '╟',
                0xC8: '╚', 0xC9: '╔',/* 0xCA: '╩', 0xCB: '╦',*/ 0xCC: '╠', 0xCD: '═', 0xCE: '╬', 0xCF: '╧',
                0xD0: '╨', 0xD1: '╤', 0xD2: '╥', 0xD3: '╙', 0xD4: '╘', 0xD5: '╒', 0xD6: '╓', 0xD7: '╫',
                0xD8: '╪', /*0xD9: '┘', 0xDA: '┌',*/ 0xDB: ' ', 0xDC: '▄', 0xDD: '▌', 0xDE: '▐', 0xDF: '▀',
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
            content += String.fromCharCode(x);
            then = await pauseIfNeeded(counter, then);
            counter++;
            if (counter % 100 == 0) {
                progressCallback("Translating characters", (counter / buffer.length) * 100);
            }
        }
        
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
                // If this is an escape sequence, create the object and skip it
                res.push(new EinsteinEscape(escapeLocations[i]))
                i += escapeLocations[i].length
            }
            else {
                // Otherwise, this is a character 
                const char = this.translateChar(content[i].charCodeAt(0));
                if (char != "")
                {
                    res.push(char);
                }
                i += 1;
            }
            then = await pauseIfNeeded(i, then); // TODO: Might skip mod(1000) since i jumps in values
            if (i % 100 == 0) {
                progressCallback("Collecting content", (i / content.length) * 100);
            }
        }

        return res;
    }

};


class EinsteinParser {
    constructor() {
    }

    async parse(content, progressCallback) {
        let then = performance.now();
        let counter = 0;
        let line = "";
        let res = [];
        let closing = "";

        for (let c of content) {
            if (!(c instanceof EinsteinEscape)) {
                line += c;
            }
            else {
                switch (c.rawString) {
                    case SpecialCharacters.NEWLINE:
                        line += closing;
                        if (!closing.includes("</div>"))
                        {
                            line += "<br />";
                        }

                        line = line.replaceAll(new RegExp(`((?:${SpecialCharacters.H2}.)+)`, 'g'), function (match, capture) { 
                            return "<span style='text-decoration: underline; font-weight: bold; color: white;'>" 
                                    + capture.replaceAll(SpecialCharacters.H2, "") + "</span>";
                        }).replaceAll(new RegExp(`((?:${SpecialCharacters.H3}.)+)`, 'g'), function (match, capture) { 
                            return "<span style='font-weight: bold; color: white;'>" + capture.replaceAll(SpecialCharacters.H3, "") + "</span>";
                        }).replaceAll(new RegExp(`${SpecialCharacters.SUBSCRIPT}([^${SpecialCharacters.SUBSCRIPT}]+)${SpecialCharacters.SUBSCRIPT}`, 'g'), 
                            function (match, capture) { 
                                return "<sub>" + capture + "</sub>";
                        }).replaceAll(new RegExp(`${SpecialCharacters.SUPERSCRIPT}([^${SpecialCharacters.SUPERSCRIPT}]+)${SpecialCharacters.SUPERSCRIPT}`, 'g'), 
                            function (match, capture) { 
                                return "<sup>" + capture + "</sup>";
                        });

                        /*
                        if (!hasHebrewCharacters(line))
                        {
                            line = "<div style='direction: ltr;'>" + line + "</div>";
                        }
                        */

                        closing  = "";
                        if ( (res.length == 0) && (line.startsWith(";")) )
                        {
                            console.log(`Skipping line: ${line}`)
                        }
                        else
                        {
                            res.push(line);
                        }
                        line = "";
                        break;
                    case SpecialCharacters.CENTER:
                        closing = "</div>" + closing;
                        line += "<div style='text-align: center'>";
                        break;
                    case SpecialCharacters.PARAGRAPH:
                        line += "<br/>";
                        break;
                    case SpecialCharacters.LEFT_ALIGN:
                        closing = "</div>" + closing;
                        line += "<div style='text-align: left'>";
                        break;
                    //case SpecialCharacters.H2:
                    //    break;
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
        res.push(line);

        /*
        res = res.substring(res.indexOf("<br />"));

        res = res.replaceAll(new RegExp(`((?:${SpecialCharacters.H2}.)+)`, 'g'), function (match, capture) { 
            return "<span style='text-decoration: underline; font-weight: bold;'>" + capture.replaceAll(SpecialCharacters.H2, "") + "</span>";
        });

        res = res.replaceAll(new RegExp(`((?:${SpecialCharacters.H3}.)+)`, 'g'), function (match, capture) { 
            return "<span style='font-weight: bold;'>" + capture.replaceAll(SpecialCharacters.H3, "") + "</span>";
        });
        */

        res = res.join("");

        return res;
    }
}
