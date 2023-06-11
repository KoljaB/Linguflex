# Linguflex

Linguflex ist ein **persönlicher Assistent**, der **auf gesprochenes Wort reagiert**, wie es ein Mensch tun würde.

Sie sprechen ins Mikrophon, Linguflex hört zu und reagiert auf Ihre Anweisungen. Sie können Linguflex bitten, Ihre **Termine zu planen**, Updates zu **E-Mails**, **Wetter** und **Nachrichten** zu liefern, **Medien abzuspielen** oder Ihre **Smart-Home**-Geräte zu steuern. Sie können Linguflex erweitern und anpassen, um genau das zu tun, was Sie benötigen.

## Key Features

- **Sprachsteuerung**  
  - versteht gesprochene Anweisungen und kann darauf reagieren
- **Personalisierung**
  - modular aufgebaut, kann individuell auf die Bedürfnisse des Benutzers angepasst werden
- **Home-Automation**
  - kann Smart-Home-Geräte steuern und Musik oder Videos abspielen
- **Informationsaufbereitung**
  - kann Informationen zu Nachrichten, Wetter, EMails, Terminen etc sammeln und präsentieren

## Voraussetzungen

- Python 3.9.9
- OpenAI API key

Um einen OpenAI API-Schlüssel zu erhalten, gegebenenfalls ein Konto auf [platform.openai.com](https://platform.openai.com/) erstellen. Klicken Sie danach auf Ihren Profilnamen in der rechten oberen Ecke, navigieren Sie im Menü zu "View API Keys" und klicken Sie auf "Create new secret key".

## Installation

1. Installieren Sie [Python 3.9.9](https://www.python.org/downloads/release/python-399/)
2. Klonen Sie das Linguflex-Repository:
   - laden Sie die ZIP-Datei herunter und extrahieren Sie sie, oder
   - führen Sie `git clone https://github.com/KoljaB/Linguflex.git` aus, falls Sie Git installiert haben.
3. Navigieren Sie zum Linguflex-Verzeichnis: `cd linguflex`
4. (Optional) Erstellen Sie eine virtuelle Umgebung: `python -m venv env` und aktivieren Sie sie mit `env\Scripts\activate`
5. Installieren Sie die Abhängigkeiten entsprechend dem gewünschten Installationstyp:
   - für eine Vanilla-Installation: `pip install -r requirements.txt`
   - für eine Basis-Installation: `pip install -r requirements_basic.txt`
   - für eine Komplett-Installation: `pip install -r requirements_full.txt`
6. Geben Sie den OpenAI API-Schlüssel ein:
   - Datei `config.txt` öffnnen API-Schlüssel im Abschnitt `[openai_generator]` eintragen

Hinweis: Die Verwendung zusätzlicher Module über die Vanilla-Installation hinaus kann zusätzliche Konfigurationsänderungen erfordern, wie das Hinzufügen weiterer API-Schlüssel. Weitere Informationen dazu gibt es in den Modulbeschreibungen.

## Start

Um Linguflex zu starten, öffnen Sie ein Konsolenfenster und geben Sie folgenden Befehl ein:
```
python linguflex
```

## Konfiguration

Eine Linguflex-Konfiguration ist eine Textdatei, die die zu ladenden Module und ihre Einstellungen beschreibt. Standardmäßig lädt Linguflex die Konfiguration aus der Datei `config.txt`. Alternativ können Sie den Pfad zu einer anderen Konfigurationsdatei als Kommandozeilenparameter angeben.

Das Repository enthält drei Beispielkonfigurationen:
1. Standard (Vanilla): Ermöglicht eine grundlegende Sprachkommunikation mit dem GPT-Modell
2. Basis (Basic): Beinhaltet zusätzliche Module für erweiterte Funktionen
3. Voll (Full): Stellt alle verfügbaren Module bereit

Wir empfehlen, mit der Vanilla-Konfiguration zu beginnen und nach und nach bevorzugte Module hinzuzufügen, da einige Module zusätzliche Einrichtungsschritte erfordern. Bitte schauen Sie dazu in die Dateien `config_basic.txt` oder `config_full.txt`, um zu sehen, wie einzelne Module konfiguriert und zur `config.txt`-Datei hinzugefügt werden können.


## Module

Die zu ladenden Module werden im Abschnitt `[modules]` der Konfigurationsdatei angegeben. Linguflex lädt und startet alle Module in der angegebenen Reihenfolge.

### Vanilla-Installation (Standard)

```
microphone_recorder
whisper_speechtotext
openai_generator
system_texttospeech
```

Die Vanilla-Konfiguration wird für die Erstinstallation empfohlen und ermöglicht eine grundlegende Sprachkommunikation mit der Chat-KI. Der OpenAI-API-Schlüssel sollte im Abschnitt `[openai_generator]` der Datei `config.txt` wie folgt eingegeben werden:

```
[openai_generator]
openai_api_key=TRAGE DEINEN OPENAI API-SCHLÜSSEL HIER EIN
```

Alternativ können Sie Ihren Schlüssel als Umgebungsvariable `LINGU_OPENAI_API_KEY` speichern.

Konfigurationsparameter für die Standardkonfiguration:
- Der Mikrofonaufzeichner beginnt die Aufzeichnung, wenn der Eingangspegel den in `volume_start_recording` definierten Schwellenwert überschreitet, und stoppt, wenn der Pegel unter den in `volume_stop_recording` angegebenen Wert fällt.
- Wenn Sie GPT-4 anstelle von GPT-3.5 Turbo verwenden möchten, ändern Sie den Wert des Parameters `gpt_model` auf "gpt-4".

Die bestehende Whisper-Installation nutzt die CPU. Um die Spracherkennung mit der GPU zu beschleunigen, muss PyTorch mit CUDA-Unterstützung installiert werden.

### Basis-Installation

Die Basis-Installation, definiert in `config_basic.txt`, erweitert die Vanilla-Installation um die folgenden Module:

- UI-Modul  
  `user_interface`
  - verbesserte Benutzeroberfläche zur Anzeige der Kommunikation mit der Chat-KI 
  - Breite und Höhe des Fensters können in der Datei `config.txt` angepasst werden (siehe Beispielkonfiguration in `config_basic.txt`)

- Text-zu-Sprache-Module
  - verbesserte Sprachausgabe
  - ersetzen Sie das vorhandene Modul `system_texttospeech` im Abschnitt `[modules]` der Konfigurationsdatei durch eines dieser Text-zu-Sprache-Module:
  - `edge_texttospeech` nutzt das Fenster des Edge-Browsers für die Sprachausgabe, bietet eine kostenlose, qualitativ hochwertige Sprachsynthese, aber mit verringerter Stabilität und Komfort (aufgrund der Verwendung des Browserfensters).
  - `azure_texttospeech` bietet eine qualitativ hochwertige, stabile und komfortable Sprachsynthese, benötigt jedoch einen Microsoft Azure API-Schlüssel. Sie können ein Konto unter [portal.azure.com](https://portal.azure.com/) erstellen, eine Ressource erstellen und den Schlüssel im Abschnitt "Schlüssel und Endpunkte" erhalten.
  - `elevenlabs_texttospeech` bietet auch eine qualitativ hochwertige, stabile und komfortable Sprachsynthese, jedoch mit emotionalerer Ausgabe. Um es zu nutzen, benötigen Sie einen Elevenlabs API-Schlüssel. Erstellen Sie ein Konto unter [elevenlabs.io](https://beta.elevenlabs.io/) und navigieren Sie zu Ihren Profileinstellungen, um den API-Schlüssel zu finden.
  - API-Schlüssel sollten in der Datei `config.txt` eingegeben oder als Umgebungsvariablen definiert werden (`LINGU_AZURE_SPEECH_KEY` oder `LINGU_ELEVENLABS_SPEECH_KEY`).

- Kalender-Modul  
  `google_calendar`
  - integriert den Google Kalender, um Ereignisse abzurufen und hinzuzufügen
  - benötigt die Datei `credentials.json` im Ausführungsverzeichnis von Linguflex. Um diese Datei zu erhalten, folgen Sie den unten stehenden Anweisungen:
    - erstellen Sie ein Projekt auf [console.cloud.google.com](https://console.cloud.google.com/) und navigieren Sie zu "APIs & Dienste" -> "Anmeldedaten"
    - klicken Sie auf "Anmeldedaten erstellen" und wählen Sie "OAuth-Client-ID", um eine neue OAuth-Client-ID zu erstellen
    - klicken Sie unter "OAuth 2.0-Client-IDs" auf das Download-Symbol auf der rechten Seite, um die Datei `credentials.json` herunterzuladen
  - fehlt die Datei `credentials.json`, wird eine Protokollnachricht "[Kalender] FEHLER: [Errno 2] Datei oder Verzeichnis nicht gefunden: 'credentials.json'" angezeigt
  - bei der ersten Ausführung auf einem Gerät wird der Benutzer aufgefordert, seine Google-Anmeldedaten einzugeben
  - die Anmeldeinformationen werden in der Datei `token.pickle` gespeichert, um zukünftige Anmeldungen zu vermeiden

- Email-Modul:  
  `email_imap`
  - ruft E-Mails mit dem IMAP-Protokoll ab
  - IMAP-Server, Benutzername und Passwort sollten im Abschnitt `[email_imap]` der Konfigurationsdatei eingegeben werden (siehe Beispiel in `config_basic.txt`)

- Modul zur Echtzeit-Informationssuche:  
  `google_information`
  - ruft Echtzeitinformationen aus dem Internet ab
  - benötigt einen SerpAPI-Schlüssel, den Sie von [serpapi.com](https://serpapi.com/) erhalten können. Geben Sie den Schlüssel in der Konfigurationsdatei ein oder setzen Sie ihn als Umgebungsvariable `LINGU_SERP_API_KEY`

- Modul zum Wechseln der Persönlichkeit:  
  `personality_switch`
  - weist der Chat-KI einen vordefinierten Charakter bzw. eine Persönlichkeit zu, die während einer Sitzung geändert werden kann
  - der Startcharakter kann in der Konfigurationsdatei festgelegt werden

- Modul zur automatischen Aktionsauswahl:  
  `auto_action`
  - wenn die angeforderte Aktion nicht vom Sprachmodell erfüllt wird, prüft dieses Modul die Aktionen, die von anderen Modulen bereitgestellt werden, und führt sie aus, wenn sie geeignet sind
  - das GPT 3.5-Modell hat Einschränkungen, abhängig von der Komplexität der von anderen Modulen bereitgestellten Aktionen. GPT-4 erzielt in solchen Fällen deutlich bessere Ergebnisse.

### Komplett-Installation

Die Komplett-Installation, definiert in `config_full.txt`, beinhaltet alle Module aus der Grundkonfiguration und erweitert sie um zusätzliche Module:

- Media-Playback-Modul:  
  `media_playout`
  - nutzt YouTube und Firefox zum Abspielen von Audio- und Videodateien
  - benötigt einen kompatiblen Geckodriver (ein Automatisierungsausführbar für Firefox) im Ausführungsverzeichnis von Linguflex. Sie können die passende Version von der Seite [Geckodriver Releases](https://github.com/mozilla/geckodriver/releases) herunterladen. Beachten Sie, dass die Kompatibilität je nach Ihrer installierten Firefox-Version variieren kann.

- Wetter-Modul:  
  `weather_summary`
  - ruft aktuelle Wetterdaten ab
  - benötigt einen OpenWeatherMap-API-Schlüssel, der in der Konfigurationsdatei eingetragen oder als `LINGU_OPENWEATHERMAP_API_KEY` Umgebungsvariable gesetzt werden sollte. Zusätzlich sollten Sie die `default_city` in der Konfigurationsdatei zu Ihrem Standort ändern

- Nachrichten-Modul:  
  `news_summary`
  - fasst die neuesten Nachrichten zusammen
  - das Sprachmodell kann nach allgemeinen Schlagzeilen oder Nachrichten in spezifischen Kategorien wie Wirtschaft, Technologie, Forschung, Inland, Ausland oder Gesellschaft gefragt werden
  - das Modul holt Informationen von Tagesschau.de mit Hilfe von BeautifulSoup

- Bildsuch-Modul:  
  `pic_search`
  - sucht im Internet nach einem Bild und zeigt es an
  - benötigt einen Google API-Schlüssel und CX-Schlüssel. Sie können diese Schlüssel in der Konfigurationsdatei (`config_full.txt`) eingeben oder sie als die Umgebungsvariablen `LINGU_GOOGLE_API_KEY` und `LINGU_GOOGLE_CX_KEY` festlegen
  - um den Google-API-Schlüssel zu erhalten, melden Sie sich mit Ihrem Google-Konto bei [console.cloud.google.com](https://console.cloud.google.com) an. Erstellen Sie ein neues Projekt und suchen Sie in der Bibliothek nach "Custom Search API". Aktivieren Sie es für Ihr Projekt und erstellen Sie API-Anmeldedaten, indem Sie unter "Anmeldedaten" "API-Schlüssel" auswählen.
  - um den Google CX-Schlüssel zu erhalten, melden Sie sich mit Ihrem Google-Konto bei [cse.google.com/cse/all](https://cse.google.com/cse/all) an. Erstellen Sie eine neue Suchmaschine und geben Sie die erforderlichen Informationen an, wie die zu durchsuchenden Websites. Nach Erstellung der Suchmaschine finden Sie die "Search engine ID", die für dieses Modul benötigte CX-Schlüssel.

- Bildgenerierungsmodul:  
  `pic_generate`
  - generiert ein Bild mit der DALL-E Bildgenerator-API, die von OpenAI bereitgestellt wird, und zeigt es an
  - beachten Sie, dass dieses Modul Kosten verursacht, die auf der OpenAI-Preisseite ([openai.com/pricing](https://openai.com/pricing)) zu finden sind

- Modul zur Steuerung von Smart-Home-Lichtern:  
  `lights_control`
  - steuert Farben und Helligkeit von Tuya Smartbulbs
  - jede Lampe sollte in der Konfigurationsdatei mit einem Namen, Geräte-ID, IP-Adresse, "Local Key" und Version konfiguriert werden. Beispiel-Einträge finden Sie in `config_full.txt`.
  - detaillierte Anweisungen zum Erhalten der notwendigen Daten finden Sie auf der Website des [tinytuya Projekts](https://pypi.org/project/tinytuya/) im Abschnitt "Setup Wizard - Getting Local Keys"

- Emoji-Spiel-Modul:  
  `emoji_game`
  - präsentiert eine Auswahl an Emojis, die ein "zufällig" ausgewähltes Werk (Film, Buch oder Serie) repräsentieren, das erraten werden muss

- Depot-Zusammenfassungsmodul:  
  `depot_summary`
  - ruft Daten des Anlageportfolios ab und fasst diese zusammen
  - das Anlageportfolio wird als comdirect Musterportfolio erstellt und der externe Link zum Portfolio wird in der Konfigurationsdatei gespeichert

## Zukünftige Entwicklung

Die nächste geplante Funktion ist ein Webserver-Modul, das es Benutzern ermöglicht, Linguflex von überall aus mit einem Smartphone zu bedienen. Die aktuelle Implementierung des Webservers ist funktionsfähig, benötigt aber vor der Freigabe weitere Verbesserungen. Der bestehende Webserver ist eine eigenständige Flask-Anwendung, um die Implementierung von CORS/Flask-Anwendungen auf dem Linguflex-Server zu vermeiden. Die aktuelle Interprozesskommunikation zwischen Linguflex und dem Webserver basiert derzeit noch auf Textdateien und beinhaltet daher einige weniger wünschenswerte Aspekte (Spinwaits etc).
