import re

class ConvertNumbersToText:

    def konvertiere_int_in_gesprochenen_text(self, zahl: int) -> str:
        einheiten = ["", "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun"]
        zehner = ["", "zehn", "zwanzig", "dreißig", "vierzig", "fünfzig", "sechzig", "siebzig", "achtzig", "neunzig"]
        hunderter = ["", "einhundert", "zweihundert", "dreihundert", "vierhundert", "fünfhundert", "sechshundert", "siebenhundert", "achthundert", "neunhundert"]
        ausnahmen = {0: "null", 11: "elf", 12: "zwölf", 16: "sechzehn", 17: "siebzehn"}

        if zahl in ausnahmen:
            return ausnahmen[zahl]
        if zahl < 10:
            return einheiten[zahl]
        if zahl < 100:
            zehn = zahl // 10
            eins = zahl % 10
            if eins == 0:
                return zehner[zehn]
            else:
                if zehn == 1:
                    return einheiten[eins] + zehner[zehn]
                else:
                    if eins == 1:
                        return einheiten[eins][:-1] + "und" + zehner[zehn]
                    else:
                        return einheiten[eins] + "und" + zehner[zehn]
        if zahl < 1000:
            hundert = zahl // 100
            rest = zahl % 100
            if rest == 0:
                return hunderter[hundert]
            else:
                return hunderter[hundert] + self.konvertiere_int_in_gesprochenen_text(rest)
        if zahl < 10000:
            tausend = zahl // 1000
            rest = zahl % 1000
            if rest == 0:
                if tausend == 1:
                    return einheiten[tausend][:-1] + "tausend"
                else:
                    return einheiten[tausend] + "tausend"
            else:
                if tausend == 1:
                    hundert = rest // 100
                    if 6 < hundert <= 9:
                        rest = rest % 100
                        return einheiten[hundert] + "zehnhundert" + (self.konvertiere_int_in_gesprochenen_text(rest) if rest != 0 else "")
                    else:
                        return einheiten[tausend][:-1] + "tausend" + self.konvertiere_int_in_gesprochenen_text(rest)
                return einheiten[tausend] + "tausend" + self.konvertiere_int_in_gesprochenen_text(rest)

        return str(zahl)
    
    def optimiere(self, text: str) -> str:
        text = self.ersetze_zahlen_mit_text(text)
        pattern = r"°C(?!\w)"
        text =  re.sub(pattern, " Grad Celsius", text)
        pattern_range = r"(\b\d+)-(\d+\b)"
        text = re.sub(pattern_range, r"\1 bis \2", text)
        text = text.replace('m/s', 'Meter pro Sekunde')
        return text
    
    def ersetze_zahlen_mit_text(self, text: str) -> str:
        # Die Funktion, die auf jedes Match angewendet wird. Sie wandelt die Zahl in einen String um, 
        # ruft die Methode `konvertiere_int_in_gesprochenen_text` auf und gibt das Ergebnis zurück.
        def replace_with_text(match):
            zahl = int(match.group(0))
            return self.konvertiere_int_in_gesprochenen_text(zahl)
        
        # Ersetzt jede Zahl im Text durch ihren gesprochenen Text.
        return re.sub(r'\b\d{1,4}\b', replace_with_text, text)    