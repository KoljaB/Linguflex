# Linguflex

## Worum geht's?
Linguflex ermöglicht die Interaktion mit Textgeneratoren in natürlicher Sprache. 
Es bietet Module zur Verwaltung von Terminkalender und Emails, Abrufen aktueller Infos aus dem Internet ("googlen"), Abspielen von Audio- und Videoinhalten, Smart-Home (Lichtsteuerung), Nachrichten, Wetter und einiges mehr.

## Voraussetzungen
- Python 3.9.9
- OpenAI API key  
Für einen OpenAI API key gegebenenfalls Account bei OpenAI eröffnen (https://platform.openai.com/). Anschließend rechts oben auf den Profilnamen klicken, dann im Menü auf "View API Keys" und anschließend auf "Create new secret key".

## Installation
`pip install linguflex`

## Start von Linguflex
`python linguflex`

## Konfiguration
Textdatei mit den zu ladenden Modulen und deren Konfigurationseinstellungen. Es wird empfohlen, mit der einfachen Vanilla-Konfiguration zu beginnen und dann schrittweise Module zu ergänzen. Linguflex lädt die in der config.txt hinterlegte Konfiguration, es sei denn es wird per Kommandozeilenparameter eine andere übergeben.

## Module
In der Sektion [modules] der config-Datei werden die zu ladenden Module angegeben. Linguflex lädt und startet alle Module in der hier angegebenen Reihenfolge.

### Vanilla-Konfiguration
Diese einfache Grundkonfiguration ermöglicht Sprachkommunikation und besteht lediglich aus vier Modulen:
- microphone_recorder
- whisper_speechtotext
- openai_generator
- system_texttospeech

Sie ist in config_vanilla.txt und initial in der config.txt hinterlegt.

Zunächst OpenAI API key in die config.txt in der Sektion [openai_generator] eingetragen. 
```
[openai_generator]
openai_api_key=ENTER YOUR OPENAI API-KEY HERE
```
Alternativ kann der Key auch in die Umgebungsvariable LINGU_OPENAI_API_KEY geschrieben werden.

Konfigurationsparameter der Vanillakonfiguration:
Der Mikrofon-Rekorder nimmt auf, sobald der Eingangspegel über dem in der volume_start_recording festgelegten Schwellwert steigt und beendet die Aufnahme, wenn der Pegel unter den von volume_stop_recording festgelegten Wert fällt.  
Wenn GPT 4 statt GTP 3.5 Turbo verwendet werden soll, den Wert des Parameters gpt_model auf "gpt-4" ändern.

### Basis-Konfiguration
Die Basis-Konfiguration erweitert die Vanilla-Konfiguration um ein fortschrittlicheres Text-To-Speech Modul, ein User Interface, Terminkalender-Integration, EMail-Support, den Abruf von Echtzeit-Informationen mit Google, ein Webservermodul zur Bedienung mit Smartphones, ein Modul zur Steuerung des Charakters / der Persönlichkeit der Chat-KI und ein Modul zur selbständigen automatischen Auswahl von durch Modulen bereitgestellten Aktionen durch die KI.

### Text-To-Speech Module
- edge_texttospeechy
- azure_texttospeech und azure_texttospeech_tofile
- elevenlabs_texttospeech und elevenlabs_texttospeech_tofile

Als nächster Schritt zur Erweiterung der Vanilla-Konfiguration wird empfohlen, eine professionellere Sprachausgabe zu installieren. Dazu wird das Modul system_texttospeech aus der Sektion [modules] der Konfigurationsdatei entfernt und durch eines der oben angegebenen Sprachausgabemodule ersetzt. Edge ist kostenlos und nutzt das Edge-Browserfenster. Azure benötigt einen Microsoft Azure API Key (Account erstellen unter portal.azure.com, dann Ressource erstellen und in der Ressource links auf "Schlüssel und Endpunkt" klicken). Elevenlabs benötigt einen Elevenlabs API Key (Account erstellen unter elevenlabs.io, dann rechts oben auf das Profilbild und auf "Profile" klicken). Die API Keys werden in die config.txt eingetragen oder als Umgebungsvariable definiert (LINGU_AZURE_SPEECH_KEY bzw LINGU_ELEVENLABS_SPEECH_KEY). Weitere 

### UI Modul

