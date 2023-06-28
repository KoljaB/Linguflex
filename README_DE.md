# Linguflex
Linguflex ist ein **persönlicher KI-Assistent** ("Jarvis"), der **auf gesprochenes Wort reagiert**.

## Key Features
Linguflex kann:

- **Persönlichkeiten** nachahmen 🎭
- **Musik** abspielen 🎵
- **Termine** managen 📆
- **E-Mails** abrufen 📧
- das **Wetter** ansagen ☀️🌦️
- **Nachrichten** präsentieren 📰
- im **Internet suchen** (Texte oder Bilder) 🔍
- **Bilder erzeugen** 🎨
- **Lampen steuern** 💡
- und hat euer Aktienportfolio im Auge 📊
  
Linguflex ist auf englisch und deutsch verfügbar.

## Voraussetzungen
- [Python 3.9.9](https://www.python.org/downloads/release/python-399/)
- [OpenAI API Schlüssel](https://platform.openai.com/) 

## Installation
```
pip install -r requirements.txt
```
oder für eine Minimalkonfiguration ("Vanilla"): `pip install -r requirements_minimal.txt`

OpenAI API-Schlüssel entweder:
- in die Datei `config.txt` im Bereich [openai_generator] in den Schlüssel "api_key" eintragen
- oder in die Umgebungsvariable LINGU_OPENAI_API_KEY eintragen

Hinweis: für schnellere Spracherkennung mit GPU-Unterstützung sollte vor der (pytorch-)Installation das [NVIDIA® CUDA® Toolkit](https://developer.nvidia.com/cuda-toolkit) installiert werden.

## Start
```
python linguflex
```

## Konfiguration
Die `config.txt` beinhaltet:
- Systemeinstellungen wie zB die verwendeten Sprache
- die zu ladenden Module im Abschnitt [modules] (Module werden in der hier angegebenen Reihenfolge geladen und gestartet)
- die Einstellungsparameter der Module

---

# Basismodule

```
user_interface
openai_generator
microphone_recorder
whisper_speechtotext
system_texttospeech
```

Ermöglichen grundlegende Sprachkommunikation mit dem Assistenten.  

## Mikrophon-Kalibrierung
Zunächst sollte das Mikrophons in der Sektion [microphone_recorder] der Konfigurationsdatei config.txt eingestellt werden. Die Aufzeichnung beginnt, wenn der Pegel den Wert in `volume_start_recording` übersteigt und stoppt, wenn der Pegel unter den Wert in `volume_stop_recording` fällt. Um diese Werte zu ermitteln, wird debug_show_volume = True gesetzt und Linguflex gestartet, die exakten Pegelwerte werden dann in das Consolefenster geschrieben.

---

#  Text-zu-Sprache-Module

Diese Module ermöglichen eine verbesserte Sprachausgabe und ersetzen das vorhandene Modul `system_texttospeech` im Abschnitt `[modules]` der Konfigurationsdatei.  

Die Module für Azure und Elevenlabs können parallel betrieben werden und benötigen API Keys, die in der jeweiligen Sektion in der Konfigurationsdatei hinterlegt oder als Umgebungsvariable definiert werden. Lokalisierte Stimmen werden für diese beiden Module in ihrer jeweiligen Stimm-Konfigurationsdatei verwaltet.
Diese beiden Module besitzen zur Konfiguration jeweils eigenen 


  - `edge_texttospeech` nutzt das Fenster des Edge-Browsers für die Sprachausgabe, bietet eine kostenlose, qualitativ hochwertige Sprachsynthese, aufgrund der Verwendung des Browserfenstersaber mit etwas herabgesetzter Stabilität und Komfort 
  - `azure_texttospeech` bietet eine qualitativ hochwertige, stabile und komfortable Sprachsynthese und benötigt jedoch einen [Microsoft Azure API-Schlüssel](https://portal.azure.com/), Umgebungsvariable für den API-Key: LINGU_AZURE_SPEECH_KEY, Stimm-Konfigurationsdatei: azure_texttospeech.voices.de/en.json
  - `elevenlabs_texttospeech` bietet ebenfalls qualitativ hochwertige, stabile und komfortable Sprachsynthese mit emotionaler Ausgabe und benötigt einen [Elevenlabs API-Schlüssel](https://beta.elevenlabs.io/Elevenlabs), Umgebungsvariable für den API-Key: LINGU_ELEVENLABS_SPEECH_KEY, Stimm-Konfigurationsdatei: elevenlabs_texttospeech.voices.de/en.json

---

# Erweiterungsmodule

## Persönlichkeiten nachahmen 🎭
´personality_switch´
- Funktion: Wechselt zur angegebenen Persönlichkeit.
- Hinweis: Die Startpersönlichkeit kann in der Konfiguration unter "character" angegeben werden. Verfügbare Persönlichkeiten werden in der personality_switch.de/en.json-Datei in modules/basic verwaltet.

**Beispiele:**
- *"Verwandle dich in Bruce Willis"*
- *"Sei Micky Maus"*
- *"Wechsle den Charakter zum Assistenten"*

---

## Notizbuch 📔
´notebook´
- Funktion: Kann als Zwischenablage für Informationen genutzt werden

**Beispiele:**
- *"Schreib die URL vom laufenden Song ins Notizbuch"*
- *"Erzeuge ein Notizbuch Tiere und schreibe Katze, Maus und Elefant hinein"*

---

## Media Playout 🎵
´media_playout´
- Funktion: Ermöglicht Suche und Abspiel von Musikstücken und Musikplaylists. In Playlists kann ein Lied vor und zurück gesprungen werden.
- Hinweis: Benötigt einen [Google Cloud API key](https://console.cloud.google.com/) mit Zugriff auf die YouTube Data API v3.

**Beispiele:**
- *"Spiele eine Playlist von Robbie Williams"*
- *"Ein Lied weiter"*
- *"Leiser", "Stop", "Pause", "Weiter"*

---

## Internetsuche Text 🔍 
´google_information´
- Funktion: Ruft Echtzeitinformationen aus dem Internet ab.
- Hinweis: Benötigt einen [SerpAPI-Schlüssel](https://serpapi.com/).

**Beispiel:**
- *"Google, wer wurde 2023 Fußballmeister?"*

---

## Auto Action ✨
- Funktion: Ermöglicht dem Assistenten bei schwierigen Fragen den Zugriff auf die Fähigkeiten aller Module.

**Beispiel:**
- *"Wer wurde 2023 Fußballmeister?"*

---

## Termine managen 📆
´google_calendar´
- Funktion: Integriert den Google Kalender, um Ereignisse abzurufen und hinzuzufügen.
- Hinweis: Benötigt die Datei [credentials.json](https://developers.google.com/calendar/api/quickstart/python?hl=de#authorize_credentials_for_a_desktop_application).

**Beispiele:**
- *"Was habe ich für Termine?"*
- *"Neuer Termin übermorgen 9 Uhr Zahnarzt"*
- *"Verschiebe den Termin mit dem Abendessen um eine Stunde"*

---

## Wetter ☀️🌦️
´weather_forecast´
- Funktion: Ruft aktuelle Wetterdaten ab.
- Hinweis: Benötigt einen [OpenWeatherMap-API-Schlüssel](https://openweathermap.org/api).

**Beispiel:**
- *"Wie wird das Wetter morgen früh?"*

---

## Nachrichten 📰
´news_summary´
- Funktion: Fasst die aktuelle Nachrichten der Tagesschau zusammen.

**Beispiel:**
- *"Wie sind die Technik-Nachrichten?"*

---

## Bildsuche 🔍🖼️
´picture_search´
- Funktion: Sucht im Internet nach einem Bild und zeigt es an.
- Hinweis: Benötigt einen [Google API-Schlüssel](https://console.cloud.google.com) mit Freigabe für die Custom Search API und einen [CX-Schlüssel](https://cse.google.com/cse/all).

**Beispiel:**
- *"Zeige ein Bild von Salvador Dali"*

---

## Bilderzeugung 🎨
´picture_generator´
- Funktion: Generiert ein Bild auf Grundlage einer Beschreibung und zeigt es an.
- Hinweis: Kann bei intensiver Nutzung [gewisse Kosten](https://openai.com/pricing) verursachen.

**Beispiel:**
- *"Male ein Bild vom Eiffelturm im Stil von Salvador Dali"*

---

## Emailzugriff  📧
´email_imap´
- Funktion: Ruft E-Mails mit dem IMAP-Protokoll ab.

**Beispiel:**
- *"Habe ich neue EMails?"*

---

## Investmentdaten 📊  
´stocks_portfolio´
- Funktion: Ruft Daten des Anlageportfolios ab und fasst diese zusammen.

**Beispiel:**
- *"Wie geht es meinen Aktien"*
