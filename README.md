# Linguflex
Linguflex ist ein **persönlicher KI-Assistent** ("Jarvis"), der **auf gesprochenes Wort reagiert**.

## Key Features
Linguflex kann:
- **Persönlichkeiten** nachahmen
- **Musik** abspielen
- **Termine** managen
- **E-Mails** abrufen
- das **Wetter** ansagen
- **Nachrichten** präsentieren
- **im Internet suchen** (Texte oder Bilder)
- **Bilder erzeugen** auf Grundlage eurer Beschreibungen  
- **Licht** in eurem Zimmer kontrollieren
- und hat euer Aktienportfolio im Auge.
  
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

### Basismodule

```
user_interface
openai_generator
microphone_recorder
whisper_speechtotext
system_texttospeech
```

Ermöglichen grundlegende Sprachkommunikation mit dem Assistenten.  

#### Mikrophon-Kalibrierung
Zunächst sollte das Mikrophons in der Sektion [microphone_recorder] der Konfigurationsdatei config.txt eingestellt werden. Die Aufzeichnung beginnt, wenn der Pegel den Wert in `volume_start_recording` übersteigt und stoppt, wenn der Pegel unter den Wert in `volume_stop_recording` fällt. Um diese Werte zu ermitteln, wird debug_show_volume = True gesetzt und Linguflex gestartet, die exakten Pegelwerte werden dann in das Consolefenster geschrieben.


###  Text-zu-Sprache-Module

Diese Module ermöglichen eine verbesserte Sprachausgabe und ersetzen das vorhandene Modul `system_texttospeech` im Abschnitt `[modules]` der Konfigurationsdatei.  

Die Module für Azure und Elevenlabs können parallel betrieben werden und benötigen API Keys, die in der jeweiligen Sektion in der Konfigurationsdatei hinterlegt oder als Umgebungsvariable definiert werden. Lokalisierte Stimmen werden für diese beiden Module in ihrer jeweiligen Stimm-Konfigurationsdatei verwaltet.
Diese beiden Module besitzen zur Konfiguration jeweils eigenen 


  - `edge_texttospeech` nutzt das Fenster des Edge-Browsers für die Sprachausgabe, bietet eine kostenlose, qualitativ hochwertige Sprachsynthese, aufgrund der Verwendung des Browserfenstersaber mit etwas herabgesetzter Stabilität und Komfort 
  - `azure_texttospeech` bietet eine qualitativ hochwertige, stabile und komfortable Sprachsynthese und benötigt jedoch einen [Microsoft Azure API-Schlüssel](https://portal.azure.com/), Umgebungsvariable für den API-Key: LINGU_AZURE_SPEECH_KEY, Stimm-Konfigurationsdatei: azure_texttospeech.voices.de/en.json
  - `elevenlabs_texttospeech` bietet ebenfalls qualitativ hochwertige, stabile und komfortable Sprachsynthese mit emotionaler Ausgabe und benötigt einen [Elevenlabs API-Schlüssel](https://beta.elevenlabs.io/Elevenlabs), Umgebungsvariable für den API-Key: LINGU_ELEVENLABS_SPEECH_KEY, Stimm-Konfigurationsdatei: elevenlabs_texttospeech.voices.de/en.json
  
###  Erweiterungsmodule

- personality_switch
  - wechselt zur angegebenen Persönlichkeit
  - die Startpersönlichkeit kann in der Konfiguration unter "character" angegeben werden
  - verfügbare Persönlichkeiten werden in der personality_switch.de/en.json-Datei in modules/basic verwaltet

  Anwendungsbeispiele:
    - "verwandele dich in Bruce Willis"
	- "sei Micky Maus"
	- "wechsle den Charakter zum Assistenten"

- notebook
  - kann als Zwischenablage für Informationen genutzt werden

  Anwendungsbeispiel:
    - "schreib die URL vom laufenden Song ins Notizbuch"
    - "erzeuge ein Notizbuch Tiere und schreibe Katze, Maus und Elefant hinein"

- media_playout
  - ermöglicht Suche und Abspiel von Musikstücken und Musikplaylists
  - lauter und leiser
  - in Playlists kann ein Lied vor und zurück gesprungen werden
  - benötigt einen [Google Cloud API key](https://console.cloud.google.com/) mit Zugriff auf die YouTube Data API v3 (Projekt erstellen, YouTube API für das Projekt aktivieren, API-Schlüssel erstellen)
  
  Anwendungsbeispiel:
    - "spiele eine Playlist von Robbie Williams"
    - "ein Lied weiter"
    - "leiser", "stop", "pause", "weiter"
  
- google_information
  - ruft Echtzeitinformationen aus dem Internet ab
  - benötigt einen [SerpAPI-Schlüssel](https://serpapi.com/), der in der Konfigurationsdatei oder in der Umgebungsvariable LINGU_SERP_API_KEY hinterlegt wird
  
  Anwendungsbeispiel:
    - "google, wer 2023 Fussballmeister wurde"

- auto_action
  - ermöglicht dem Assistenten bei schwierigen Fragen den Zugriff auf die Fähigkeiten aller Module
  
  Anwendungsbeispiel:
    - "wer wurde 2023 Fussballmeister?"

- google_calendar
  - integriert den Google Kalenders, um Ereignisse abzurufen und hinzuzufügen, nutzt die Google Calendar API 
  - benötigt die Datei [credentials.json](https://developers.google.com/calendar/api/quickstart/python?hl=de#authorize_credentials_for_a_desktop_application) im Ausführungsverzeichnis von Linguflex
  - bei der ersten Ausführung auf einem Gerät wird der Benutzer weiterhin aufgefordert, seine Google-Anmeldedaten einzugeben
  
  Anwendungsbeispiel:
    - "was habe ich für Termine?"
    - "neuer Termin übermorgen 9 Uhr Zahnarzt"
    - "verschiebe den Termin mit dem Abendessen um eine Stunde"
  
- weather_forecast
  - ruft aktuelle Wetterdaten ab
  - benötigt einen [OpenWeatherMap-API-Schlüssel](https://openweathermap.org/api), der in der Konfigurationsdatei oder in der Umgebungsvariable LINGU_OPENWEATHERMAP_API_KEY hinterlegt wird
  
  Anwendungsbeispiel:
    - "wie wird das Wetter morgen früh?"

- news_summary
  - fasst die aktuelle Nachrichten der Tagesschau zusammen aus den Themengebieten Allgemeine Nachrichten, Wirtschaft, Technologie, Forschung, Inland, Ausland oder Gesellschaft 
  
  Anwendungsbeispiel:
    - "wie sind die Technik-Nachrichten?"
  
- picture_search
  - sucht im Internet nach einem Bild und zeigt es an
  - benötigt einen [Google API-Schlüssel](https://console.cloud.google.com) mit Freigabe für die Custom Search API und einen [CX-Schlüssel](https://cse.google.com/cse/all)
  - diese Schlüssel werden in der Konfigurationsdatei unter api_key und cx_key eingegeben oder als die Umgebungsvariablen LINGU_GOOGLE_API_KEY und LINGU_GOOGLE_CX_KEY festgelegt
  
  Anwendungsbeispiel:
    - "zeige ein Bild von Salvador Dali"

- picture_generator
  - generiert ein Bild mit der DALL-E Bildgenerator-API, die von OpenAI bereitgestellt wird, und zeigt es an
  - kann bei intensiver Nutzung [gewisse Kosten](https://openai.com/pricing) verursachen  

  Anwendungsbeispiel:
    - "male ein Bild vom Eiffelturm im Stil von Salvador Dali"

- email_imap
  - ruft E-Mails mit dem IMAP-Protokoll ab
  - Anmeldedaten (IMAP-Server, Benutzername und Passwort) werden in der Konfigurationsdatei hinterlegt

  Anwendungsbeispiel:
    - "habe ich neue EMails?"
 
- stocks_portfolio  
  - ruft Daten des Anlageportfolios ab und fasst diese zusammen
  - abrufbare Anlageportfolios werden als comdirect Musterportfolio erstellt und in der Konfigurationsdatei hinterlegt

  Anwendungsbeispiel:
    - "wie geht es meinen Aktien?"
  
- emoji_game 
  - startet ein Ratespiel, in dem der Nutzer ein "zufällig" ausgewähltes Werk (Film, Buch oder Serie) anhand von Emojis erraten muss
    - "lass uns Emojis raten spielen"

- lights_control
  - steuert Farben und Helligkeit von Tuya Smartbulbs
  - Lampen werden in der lights_control.json im Verzeichnis modules/full eingerichtet
  - detaillierte Anweisungen zum Erhalten der notwendigen Daten (Namen, Geräte-ID, IP-Adresse, "Local Key" und Version) erhalten Sie auf der Website des [tinytuya Projekts](https://pypi.org/project/tinytuya/) im Abschnitt "Setup Wizard - Getting Local Keys"
  
    - "mach die Lampe am PC gelb"
    - "tauche alle Lampen in Sonnenuntergangsfarben"
  
