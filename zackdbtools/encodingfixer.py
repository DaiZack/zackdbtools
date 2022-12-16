import re
badencodedict = {"√©": {"utf8": "é", "ascii": "e"},
 "√°": {"utf8": "á", "ascii": "a"},
 "√≠": {"utf8": "í", "ascii": "i"},
 "√≥": {"utf8": "ó", "ascii": "o"},
 "√∂": {"utf8": "ö", "ascii": "o"},
 "√º": {"utf8": "ü", "ascii": "u"},
 "√¥": {"utf8": "ô", "ascii": "o"},
 "√®": {"utf8": "è", "ascii": "e"},
 "√ß": {"utf8": "ç", "ascii": "c"},
 "√±": {"utf8": "ñ", "ascii": "n"},
 "√∏": {"utf8": "ø", "ascii": "o"},
 "√´": {"utf8": "ë", "ascii": "e"},
 "√§": {"utf8": "ä", "ascii": "a"},
 "√•": {"utf8": "å", "ascii": "a"},
 "√Å": {"utf8": "Á", "ascii": "A"},
 "√∫": {"utf8": "ú", "ascii": "u"},
 "√ª": {"utf8": "û", "ascii": "u"},
 "√Ø": {"utf8": "ï", "ascii": "i"},
 "√â": {"utf8": "É", "ascii": "E"},
 "√†": {"utf8": "à", "ascii": "a"},
 "√¶": {"utf8": "æ", "ascii": "ae"},
 "√Æ": {"utf8": "î", "ascii": "i"},
 "√¢": {"utf8": "â", "ascii": "a"},
 "√£": {"utf8": "ã", "ascii": "a"},
 "√î": {"utf8": "Ô", "ascii": "O"},
 "√ü": {"utf8": "ß", "ascii": "ss"},
 "√ì": {"utf8": "Ó", "ascii": "O"},
 "√≤": {"utf8": "ò", "ascii": "o"},
 "√Ω": {"utf8": "ý", "ascii": "y"},
 "√ñ": {"utf8": "Ö", "ascii": "O"},
 "√™": {"utf8": "ê", "ascii": "e"},
 "√Ä": {"utf8": "À", "ascii": "A"},
 "√ò": {"utf8": "Ø", "ascii": "O"},
 "√Ö": {"utf8": "Å", "ascii": "A"},
 "√∞": {"utf8": "ð", "ascii": "eth"},
 "√á": {"utf8": "Ç", "ascii": "C"},
 "√Ç": {"utf8": "Â", "ascii": "A"},
 "√π": {"utf8": "ù", "ascii": "u"},
 "√í": {"utf8": "Ò", "ascii": "O"},
 "√¨": {"utf8": "ì", "ascii": "i"},
 "√ú": {"utf8": "Ü", "ascii": "U"},
 "√à": {"utf8": "È", "ascii": "E"},
 "√û": {"utf8": "Þ", "ascii": "Th"}}

def fix_encoding(text, encoding="utf8"):
    if encoding == "utf8":
        return re.sub("|".join(badencodedict.keys()), lambda m: badencodedict[m.group(0)]["utf8"], text, flags=re.I)
    elif encoding == "ascii":
        return re.sub("|".join(badencodedict.keys()), lambda m: badencodedict[m.group(0)]["ascii"], text, flags=re.I)


if __name__ == "__main__":
    text = "carrefour dentaire de montr√©al photos"
    print(fix_encoding(text, "utf8"))
    with open('/tmp/locationkeyword.csv') as f:
        texts = f.readlines()
    with open('/tmp/locationkeyword_fixed.csv', 'w') as f:
        for text in texts:
            f.write(fix_encoding(text, "utf8"))

