# Linguflex

### Worum geht's?
Linguflex ermöglicht die Interaktion mit Textgeneratoren ("Chat-KIs") in natürlicher Sprache. 
Es bietet Module zur Verwaltung von Terminkalender und Emails, Abrufen aktueller Infos aus dem Internet ("googlen"), Abspielen von Audio- und Videoinhalten, Smart-Home (Lichtsteuerung), Nachrichten, Wetter und einiges mehr.

### Release-Stand
Die aktuelle Linguflex-Version umfasst die Vanilla-Konfiguration. In den nächsten Tagen werden schrittweise die Module zunächst für die Basis- und dann für die Komplett-Konfiguration veröffentlicht.

### Voraussetzungen
- Python 3.9.9 (https://www.python.org/downloads/release/python-399/)
- OpenAI API key  
Für einen OpenAI API key gegebenenfalls Account bei OpenAI eröffnen ([platform.openai.com](https://platform.openai.com/)). Anschließend rechts oben auf den Profilnamen klicken, dann im Menü auf "View API Keys" und anschließend auf "Create new secret key".

### Installation
Python installieren, Linguflex Repository lokal kopieren. 

### Inbetriebnahme
Es wird empfohlen, zunächst die Vanilla-Konfiguration zu starten und dann schrittweise weitere Module hinzuzufügen.

### Start von Linguflex
Konsolenfenster öffnen und folgendes eingeben:  
  
`python linguflex`

### Konfiguration
Textdatei mit den zu ladenden Modulen und deren Konfigurationseinstellungen. Es wird empfohlen, mit der einfachen Vanilla-Konfiguration zu beginnen und dann schrittweise Module zu ergänzen. Zusätzlich zur Vanilla-Konfiguration gibt es eine Basic-Konfiguration mit weiteren grundlegenden Modulen sowie eine Komplett-Konfiguration mit allen zur Verfügung stehenden Modulen. Es wird die in der Datei config.txt hinterlegte Konfiguration geladen oder die optional per Kommandozeilenparameter übergebene.

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

### Text-To-Speech-Module
`edge_texttospeechy`
`azure_texttospeech`
`elevenlabs_texttospeech`  
  
Als nächster Schritt zur Erweiterung der Vanilla-Konfiguration wird empfohlen, eine professionellere Sprachausgabe zu installieren. Dazu wird das Modul system_texttospeech aus der Sektion [modules] der Konfigurationsdatei entfernt und durch eines der oben angegebenen Sprachausgabemodule ersetzt. Edge nutzt das Edge-Browserfenster und bietet kostenlose, hochqualitative Sprachausgabe auf Kosten von Stabilität und Komfort (aufgrund des Browserfensters). Azure ist kostenpflichtig, bietet jedoch einen großzügigen Gratiszeitraum. Hierfür wird ein Microsoft Azure API Key benötigt (Account erstellen unter [portal.azure.com](https://portal.azure.com/), dann Ressource erstellen und in der Ressource links auf "Schlüssel und Endpunkt" klicken). Elevenlabs ist ebenfalls kostenpflichtig mit Gratiszeitraum und benötigt einen Elevenlabs API Key (Account erstellen unter [elevenlabs.io](https://beta.elevenlabs.io/), dann rechts oben auf das Profilbild und auf "Profile" klicken). Die API Keys werden in die config.txt eingetragen oder als Umgebungsvariable definiert (LINGU_AZURE_SPEECH_KEY bzw LINGU_ELEVENLABS_SPEECH_KEY).

### UI-Modul
`user_interface`  
  
Standardmäßig zeigt Linguflex ein Konsolenfenster mit Loggingmeldungen an. Das UI-Modul stellt zusätzlich ein ansprechenderes User Interface bereit zur Anzeige der Kommunikation mit der Chat KI.

### Terminkalender-Modul
`google_calendar`  
  
Integration mit dem Google Calendar zum Abruf und Eintragen von Terminen. 
Benötigt die Datei credentials.json im Ausführungsverzeichnis von Linguflex. Dazu in [console.cloud.google.com](https://console.cloud.google.com/) ein Projekt anlegen, und unter "APIs und Dienste" links auf "Anmeldedaten". Dann auf "Anmeldedaten erstellen" und eine neue OAuth-ClientId erstellen. Diese wird anschließend unter OAuth 2.0-Client-IDs gelistet, dort ist ganz rechts ein Pfeil nach unten. Dort draufklicken und dann auf "JSON herunterladen". 
Fehlt die credentials.json wird die Logmeldung ""[calendar] ERROR:[Errno 2] No such file or directory: 'credentials.json'" ausgegeben. 
Bei der ersten Ausführung auf einem Gerät wird der Benutzer weiterhin aufgefordert, seine Google-Anmeldeinformationen einzugeben. Diese Informationen werden dann in einer Datei token.pickle gespeichert, um zukünftige Anmeldungen zu vermeiden. 

### EMail-Modul
`email_imap`  
  
Abruf von EMails. IMAP-Server, Benutzername und Passwort werden in die Sektion [email] der Konfigurationsdatei geschrieben, siehe Beispiel in config_basis.txt.

### Abruf von Echtzeit-Informationen aus dem Internet
`google`  
  
Abruf von Echtzeitinformationen aus dem Internet. Benötigt einen SerpAPI-Key (erhältlich unter [serpapi.com](https://serpapi.com/)), der in die Konfigurationsdatei eingetragen oder in die Umgebungsvariable LINGU_SERP_API_KEY geschrieben wird.

### Webserver-Modul
`webserver`  
  
Dieses Modul kommuniziert mit dem Webserver in modules/basic/webserver, der separat gestartet werden muss. Der Webserver öffnet den Port 5000, der in der lokalen Firewall für TCP-Kommunikation freigegeben werden muss. Der Webclient in modules/basic/webclient kann auf ein Smartphone kopiert werden. IP und Port des Webservers müssen in der index.html eingetragen werden. Hier kann auch zB ein Router auf Port 80 angegeben werden, der eine Weiterleitung auf den lokalen Webserver vornimmt, so dass Linguflex auch unterwegs genutzt werden kann.

### Persönlichkeits-Modul
`personality`  
  
Schreibt der Chat-KI einen vorgefertigten Charakter zu, der dann während einer Session gewechselt werden kann.

### Modul zur selbständigen Aktionsauswahl
`autoaction`  
  
Ermöglich der KI, unter allen zur Verfügung stehenden Aktionen und Fähigkeiten selbständig eine passende auszuwählen. um die Anfrage bestmöglich zu erfüllen.
    
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
