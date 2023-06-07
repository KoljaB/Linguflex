# Linguflex

Linguflex ist eine innovative Plattform, die eine natürliche Interaktion mit Textgeneratoren wie OpenAI GPT ermöglicht und die Erstellung schlanker, effizienter Erweiterungsmodule unterstützt. Vorgefertigte Module bieten eine Vielfalt an Funktionen – von Terminkalender- und E-Mail-Verwaltung über Echtzeitzugriff auf Webinformationen wie Wetterupdates oder Nachrichten bis hin zur Medienwiedergabe und Steuerung von Smart-Home-Geräten. Linguflex hebt sich hervor durch seine Erweiterbarkeit, kompakten Modulcode und die Flexibilität, individuellen Anwendungsanforderungen gerecht zu werden.

### Release-Stand
- Vanilla-Konfiguration:  
`microphone_recorder`  
`whisper_speechtotext`  
`openai_generator`  
`system_texttospeech`  
- Basis-Konfiguration:  
`user_interface`  
`edge_texttospeech`
`azure_texttospeech`
`elevenlabs_texttospeech`  
`google_calendar`  
`email_imap`  
`google_information`  
`auto_action`  

In den nächsten Tagen werden schrittweise zunächst alle Module der Basis- und anschließend die der Komplett-Konfiguration veröffentlicht.

### Voraussetzungen
- Python 3.9.9 (https://www.python.org/downloads/release/python-399/)
- OpenAI API key  
Für einen OpenAI API key gegebenenfalls Account bei OpenAI eröffnen ([platform.openai.com](https://platform.openai.com/)). Anschließend rechts oben auf den Profilnamen klicken, dann im Menü auf "View API Keys" und anschließend auf "Create new secret key".

### Installation
Python installieren, Linguflex Repository lokal kopieren. 

### Start von Linguflex
Konsolenfenster öffnen und folgendes eingeben:  
  
`python linguflex`

### Konfiguration
Eine Linguflex-Konfiguration ist eine Textdatei, welche die zu ladenden Modulen und deren Einstellungen beschreibt. Standardmäßig lädt Linguflex die Konfiguration, die in der Datei config.txt hinterlegt ist. Optional kann der Pfad zu einer anderen Konfigurationsdatei per Kommandozeilenparameter übergeben werden.
Es werden drei Beispielkonfigurationen mitgeliefert:  
1. Vanilla (Sprachkommunikation mit dem GPT-Modell)
2. Basis (inkl grundlegende Erweiterungsmodule)
3. Komplett (alle verfügbaren Module)

Es wird empfohlen, mit der einfachen Vanilla-Konfiguration zu beginnen und dann sukzessive präferierte Module zu ergänzen, da deren Inbetriebnahme oft mit zusätzlichen Schritten verbunden ist. Wie ein einzelnes Modul in der config.txt angelegt und konfiguriert wird kann den Dateien config_basic.txt oder config_full.txt entnommen werden.

### Module
In der Sektion [modules] der config-Datei werden die zu ladenden Module angegeben. Linguflex lädt und startet alle Module in der hier angegebenen Reihenfolge.
  
  
## Vanilla-Konfiguration
`microphone_recorder`
`whisper_speechtotext`
`openai_generator`
`system_texttospeech`  

Diese einfache Grundkonfiguration wird zur ersten Inbetriebnahme empfohlen und ermöglicht eine grundlegende Sprachkommunikation mit der Chat KI. Sie ist in config_vanilla.txt und initial in der config.txt hinterlegt. 

Zunächst den OpenAI API key in die config.txt in der Sektion [openai_generator] eintragen. 
```
[openai_generator]
openai_api_key=ENTER YOUR OPENAI API-KEY HERE
```
Alternativ kann der Key auch in die Umgebungsvariable LINGU_OPENAI_API_KEY geschrieben werden.

Konfigurationsparameter der Vanillakonfiguration:
Der Mikrofon-Rekorder nimmt auf, sobald der Eingangspegel über dem in der volume_start_recording festgelegten Schwellwert steigt und beendet die Aufnahme, wenn der Pegel unter den von volume_stop_recording festgelegten Wert fällt.  
Wenn GPT 4 statt GTP 3.5 Turbo verwendet werden soll, den Wert des Parameters gpt_model auf "gpt-4" ändern.
  
  
## Basis-Konfiguration
Die Basis-Konfiguration liegt in config_basic.txt und erweitert Vanilla um ausgereiftere Text-To-Speech Module, ein User Interface, Terminkalender-Integration, EMail-Support, den Abruf von Echtzeit-Informationen mit Google, ein Webservermodul zur Bedienung mit Smartphones, ein Modul zur Steuerung des Charakters / der Persönlichkeit der Chat-KI und ein Modul zur selbständigen automatischen Auswahl von durch andere Module bereitgestellten Aktionen durch die KI. 

### UI-Modul
`user_interface`  
  
Standardmäßig zeigt Linguflex ein Konsolenfenster mit Loggingmeldungen an. Das UI-Modul stellt zusätzlich ein ansprechenderes User Interface bereit zur Anzeige der Kommunikation mit der Chat KI. Breite und Höhe des Fensters können in der config.txt eingestellt werden (siehe Beispielkonfiguration in config_basic.txt).

### Text-To-Speech-Module
`edge_texttospeech`
`azure_texttospeech`
`elevenlabs_texttospeech`  
  
Liefert eine professionellere Sprachausgabe. Dazu wird das Modul Sprachausgabemodul "system_texttospeech" aus der Sektion [modules] der Konfigurationsdatei entfernt und durch eines der oben angegebenen Sprachausgabemodule ersetzt. Das Modul edge_texttospeech nutzt zur Sprachausgabe das Edge-Browserfenster und bietet so kostenlose, hochqualitative Sprachausgabe mit reduzierter Stabilität und Komfort (aufgrund des Browserfensters). Hierfür wird ein Microsoft Azure API Key benötigt (Account erstellen unter [portal.azure.com](https://portal.azure.com/), dann Ressource erstellen und in der Ressource links auf "Schlüssel und Endpunkt" klicken). Zur Nutzung der Elevenlabs-Sprachausgabe wird ein Elevenlabs API Key benötit (Account erstellen unter [elevenlabs.io](https://beta.elevenlabs.io/), dann rechts oben auf das Profilbild und auf "Profile" klicken). Die API Keys werden in die config.txt eingetragen oder als Umgebungsvariable definiert (LINGU_AZURE_SPEECH_KEY bzw LINGU_ELEVENLABS_SPEECH_KEY).

### Terminkalender-Modul
`google_calendar`  
  
Integration mit dem Google Calendar zum Abruf und Eintragen von Terminen. 
Benötigt die Datei credentials.json im Ausführungsverzeichnis von Linguflex. Dazu in [console.cloud.google.com](https://console.cloud.google.com/) ein Projekt anlegen, und unter "APIs und Dienste" links auf "Anmeldedaten". Dann auf "Anmeldedaten erstellen" und eine neue OAuth-ClientId erstellen. Diese wird anschließend unter OAuth 2.0-Client-IDs gelistet, dort ist ganz rechts ein Pfeil nach unten. Dort draufklicken und dann auf "JSON herunterladen". 
Fehlt die credentials.json wird die Logmeldung ""[calendar] ERROR:[Errno 2] No such file or directory: 'credentials.json'" ausgegeben. 
Bei der ersten Ausführung auf einem Gerät wird der Benutzer weiterhin aufgefordert, seine Google-Anmeldeinformationen einzugeben. Diese Informationen werden dann in einer Datei token.pickle gespeichert, um zukünftige Anmeldungen zu vermeiden. 

### EMail-Modul
`email_imap`  
  
Abruf von EMails. IMAP-Server, Benutzername und Passwort werden in die Sektion [email_imap] der Konfigurationsdatei geschrieben, siehe Beispiel in config_basis.txt.

### Abruf von Echtzeit-Informationen aus dem Internet
`google`  
  
Abruf von Echtzeitinformationen aus dem Internet. Benötigt einen SerpAPI-Key (erhältlich unter [serpapi.com](https://serpapi.com/)), der in die Konfigurationsdatei eingetragen oder in die Umgebungsvariable LINGU_SERP_API_KEY geschrieben wird.

### Webserver-Modul
`webserver`  
  
Dieses Modul kommuniziert mit dem Webserver in modules/basic/webserver, der separat gestartet wird. Der Webserver öffnet den Port 5000, der in der lokalen Firewall für TCP-Kommunikation freigegeben wird. Der Webclient in modules/basic/webclient kann auf ein Smartphone kopiert werden. IP und Port des Webservers müssen in der index.html eingetragen werden. Es kann auch zB ein Router auf Port 80 angegeben werden, der eine Weiterleitung auf den lokalen Webserver vornimmt, so dass Linguflex auch unterwegs genutzt werden kann. Achtung: das funktioniert zwar in der Praxis, wird aber aufgrund potentieller Sicherheitslücken der rudimentären Webserver-Implementierung ausdrücklich nicht empfohlen.

### Persönlichkeits-Modul
`personality`  
  
Schreibt der Chat-KI einen vorgefertigten Charakter zu, der dann während einer Session gewechselt werden kann.

### Modul zur selbständigen Aktionsauswahl
`auto_action`  
  
Ermöglich der KI, unter allen zur Verfügung stehenden Aktionen und Fähigkeiten selbständig eine passende auszuwählen. um die Anfrage bestmöglich zu erfüllen. Das GPT 3.5 Modell kommt je nach Komplexität der zur Verfügung gestellten Aktionen an seine Grenzen, GPT 4 performt deutlich besser. 
    
## Komplett-Konfiguration
Die Komplett-Konfiguration ist in config_full.txt hinterlegt und beinhaltet zusätzlich zur Basic-Konfiguration noch Audio- und Video-Ausspiel, aktuelle Wetterdaten, Smart-Home Lichtsteuerung, Abruf von Nachrichten, Suche nach Bildern im Internet, Erzeugung von Bildern mit Bildgeneratoren, den Abruf aktueller Investmentdepot-Daten und Spiele.

### Modul für Audio- und Videoausspiel
`playout`  
  
Nutzt Youtube und Firefox, um Audios und Videos auszuspielen. Benötigt einen zur installierten Firefox-Version passenden Geckodriver (ein einzelnes Executable zur Automatisierung von Firefox, erhältlich hier: https://github.com/mozilla/geckodriver/releases) im Ausführungsordner von Linguflex.

### Wetter-Modul
`weather`  
  
Benötigt einen OpenWeatherMap API Key (https://openweathermap.org/api), der in der Konfigurationsdatei oder in der Umgebungsvariable LINGU_OPENWEATHERMAP_API_KEY hinterlegt wird. In der Konfigurationsdatei kann eine Stadt als default_city eingetragen werden, für die Wetterdaten abgerufen werden, wenn der Chat KI kein anderer Ort mitgeteilt wurde.

### SmartHome Lichtsteuerung
`lights`  
  
Steuert Farben und Helligkeit von Tuya Smartbulbs Lampen. Zu jeder Lampe wird ein frei vergebbarer Name, sowie Id, IP-Adresse, Key und Version in der Konfigurationsdatei hinterlegt. Id, IP, Key und Version können mit dem Konsolenbefehl "python -m tinytuya scan" automatisch aus dem WLAN gelesen werden ([pypi.org/project/tinytuya](https://pypi.org/project/tinytuya/)).

### Nachrichten-Modul
`news`  
  
Fasst die aktuellen Tagesnachrichten zusammen.

### Bildersuche-Modul
`pic_search`  
  
Sucht im Internet nach einem Bild und zeigt dieses an.

### Bildererzeugungs-Modul
`pic_generate`  
  
Erzeugt ein Bild mit dem DALL-E Bildgenerator unter Nutzung der OpenAI API und zeigt dieses an. Zu jeder Nutzung fallen Kosten an ([openai.com/pricing](https://openai.com/pricing)).

### Depot-Modul
`depot`  
  
Abruf und Zusammenfassung von Investmentdepot-Daten. Das Investment-Depot wird als comdirect-Musterdepot angelegt und der externe Link dazu ("Aktionen gesamtes Musterdepot" => "Freunden zeigen") in der Konfigurationsdatei abgelegt.

### Spiele-Modul
`games`  
  
Zeigt eine Auswahl von Emojis, die ein "zufällig" ausgewähltes Werk (Film, Buch oder Serie) repräsentieren, welches daraufhin erraten werden muss.
