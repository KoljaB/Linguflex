# Linguflex

### Worum geht's?
Linguflex ermöglicht die Interaktion mit Textgeneratoren ("Chat-KIs") in natürlicher Sprache. 
Es bietet Module zur Verwaltung von Terminkalender und Emails, Abrufen aktueller Infos aus dem Internet ("googlen"), Abspielen von Audio- und Videoinhalten, Smart-Home (Lichtsteuerung), Nachrichten, Wetter und einiges mehr.

### Voraussetzungen
- Python 3.9.9
- OpenAI API key  
Für einen OpenAI API key gegebenenfalls Account bei OpenAI eröffnen (platform.openai.com). Anschließend rechts oben auf den Profilnamen klicken, dann im Menü auf "View API Keys" und anschließend auf "Create new secret key".

### Installation
`pip install linguflex`

### Start von Linguflex
`python linguflex`

### Konfiguration
Textdatei mit den zu ladenden Modulen und deren Konfigurationseinstellungen. Es wird empfohlen, mit der einfachen Vanilla-Konfiguration zu beginnen und dann schrittweise Module zu ergänzen. Linguflex lädt die in der config.txt hinterlegte Konfiguration, es sei denn es wird per Kommandozeilenparameter eine andere übergeben.

### Module
In der Sektion [modules] der config-Datei werden die zu ladenden Module angegeben. Linguflex lädt und startet alle Module in der hier angegebenen Reihenfolge.

## Vanilla-Konfiguration
`microphone_recorder`
`whisper_speechtotext`
`openai_generator`
`system_texttospeech`  

Diese einfache Grundkonfiguration ermöglicht grundlegende Sprachkommunikation mit der Chat KI. Sie ist in config_vanilla.txt und initial in der config.txt hinterlegt.

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
Die Basis-Konfiguration ist in config_basis.txt hinterlegt und erweitert die Vanilla-Konfiguration um ein fortschrittlicheres Text-To-Speech Modul, ein User Interface, Terminkalender-Integration, EMail-Support, den Abruf von Echtzeit-Informationen mit Google, ein Webservermodul zur Bedienung mit Smartphones, ein Modul zur Steuerung des Charakters / der Persönlichkeit der Chat-KI und ein Modul zur selbständigen automatischen Auswahl von durch Modulen bereitgestellten Aktionen durch die KI.

### Text-To-Speech-Module
`edge_texttospeechy`
`azure_texttospeech`
`elevenlabs_texttospeech`  
  
Als nächster Schritt zur Erweiterung der Vanilla-Konfiguration wird empfohlen, eine professionellere Sprachausgabe zu installieren. Dazu wird das Modul system_texttospeech aus der Sektion [modules] der Konfigurationsdatei entfernt und durch eines der oben angegebenen Sprachausgabemodule ersetzt. Edge ist kostenlos und nutzt das Edge-Browserfenster. Azure benötigt einen Microsoft Azure API Key (Account erstellen unter portal.azure.com, dann Ressource erstellen und in der Ressource links auf "Schlüssel und Endpunkt" klicken). Elevenlabs benötigt einen Elevenlabs API Key (Account erstellen unter elevenlabs.io, dann rechts oben auf das Profilbild und auf "Profile" klicken). Die API Keys werden in die config.txt eingetragen oder als Umgebungsvariable definiert (LINGU_AZURE_SPEECH_KEY bzw LINGU_ELEVENLABS_SPEECH_KEY).

### UI-Modul
`user_interface`  
  
Standardmäßig zeigt Linguflex lediglich ein Konsolenfenster mit Loggingmeldungen an. Dieses Modul stellt zusätzlich ein ansprechenderes User Interface bereit zur Anzeige der Kommunikation mit der Chat KI.

### Terminkalender-Modul
`calendar`  
  
Integration mit dem Google Calendar zum Abruf und Eintragen von Terminen. Benötigt eine Datei credentials.json im Ausführungsverzeichnis von Linguflex. Dazu in console.cloud.google.com ein Projekt anlegen, und unter "APIs und Dienste" links auf "Anmeldedaten". Dann auf "Anmeldedaten erstellen" und eine neue OAuth-ClientId erstellen. Diese wird anschließend unter OAuth 2.0-Client-IDs gelistet, dort ist ganz rechts ein Pfeil nach unten. Dort draufklicken und dann auf "JSON herunterladen". Außerdem erfordert das Modul, dass der Benutzer bei der ersten Ausführung auf einem Gerät seine Google-Anmeldeinformationen eingibt. Die Anmeldeinformationen werden dann in einer Datei token.pickle gespeichert, um zukünftige Anmeldungen zu vermeiden.

### EMail-Modul
`email`  
  
Abruf von EMails. IMAP-Server, Benutzername und Passwort werden in die Sektion [email] der Konfigurationsdatei geschrieben, siehe Beispiel in config_basis.txt.

### Informationsabruf-Modul
`google`  
  
Abruf von Echtzeitinformationen aus dem Internet. Benötigt einen SerpAPI-Key (erhältlich unter serpapi.com), der in die Konfigurationsdatei eingetragen oder in die Umgebungsvariable LINGU_SERP_API_KEY geschrieben wird.

### Webserver-Modul
`webserver`  
  
Dieses Modul kommuniziert mit dem Webserver in modules/basic/webserver, der separat gestartet werden muss. Der Webserver öffnet den Port 5000, der in der lokalen Firewall für TCP-Kommunikation freigegeben werden muss. Der Webclient in modules/basic/webclient kann auf ein Smartphone kopiert werden. IP und Port des Webservers müssen in der index.html eingetragen werden. Hier kann auch zB ein Router auf Port 80 angegeben werden, der eine Weiterleitung auf den lokalen Webserver vornimmt, so dass Linguflex auch unterwegs genutzt werden kann.

### Persönlichkeit-Modul
`personality`  
  
Schreibt der Chat-KI einen vorgefertigten Charakter zu, der dann während einer Session gewechselt werden kann.

### Modul zur selbständigen Aktionsauswahl
`autoaction`  
  
Ermöglich der KI, unter allen zur Verfügung stehenden Aktionen und Fähigkeiten selbständig eine passende auszuwählen. um die Anfrage bestmöglich zu erfüllen.
