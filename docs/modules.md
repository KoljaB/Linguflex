# Modules

## Module docs

- [Brain](./brain.md)
- [Mimic](./mimic.md)
- [Music](./music.md)
- [Weather](./weather.md)
- [Mail](./mail.md)
- [House](./house.md)

## Sorting modules

In the settings.yaml in the "Linguflex/lingu" folder there is a section "modules".  
The icons displayed in the top right of Linguflex will be shown in the order defined under this section

## Disable a module

Every module whose directory folder starts with an underscore ("_") will be ignored at the start of Linguflex.

You can disable any linguflex module by preceding a underscore before the module directory name:  
- navigate to the folder "Linguflex/lingu/modules"
- select a module (for example, say "weather" module)
- disable the module by renaming the directory (rename "weather" to "_weather") and add an underscore at the beginning

## Module structure

If you want to develop your own linguflex modules or want to understand how it works behind the scenes, here is what makes a linguflex module.

A module contains:
- business logic
  The part where you implement everything that does not directly involve linguflex. Usually hidden in a "handlers" folder within the module directory
- logic.py
  Encapsulates interaction with the business logic. Methods provided here can be called from the user interface or the inference file.
- inference.py
  Defines the functions to interact with the LLM. Here you store every data structures that should be populated by AI.
- state.py
  Hold the data structures that define the state of the module. Also contains the module symbol. Every data structure used here must be serializable because it can be stored on hard disk.
- ui.py
  Implements the window that opens when the user clicks on the module symbol.
- inference.XX.json
  Defines the keywords for the language defined by the shortcut XX for which the module reacts to. Since linguflex uses a vast amount of function calls we can't offer weaker LLMs a huge bunch of functions to choose from. Everything above 3-5 functions will confuse the model. So we preselect the functions which are offered to the model by a simple keyword matching algorithm. You define some keywords like "*mail*" (wildcards allowed) within the inference.XX.json file and as soon as the user's input contains one of these keywords the matching function will be offered to the LLM.

This structure allows us to encapsulate every important part of the module inference process into it's own file.
