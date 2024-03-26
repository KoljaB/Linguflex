Linguflex modules are designed to provide a clear framework for development for and interaction with LLM and to clearly separate business logic from system-specific code. The module structure ensures that each critical aspect of the module's inference process is encapsulated in its respective file, providing a comprehensive and efficient framework for development within the Linguflex ecosystem.

1. **Handlers Folder**: 
   - Contains business logic that is independent of Linguflex, allowing for isolated testing.
   - This is where you implement everything that does not directly involve Linguflex.

2. **Inference.py**:
   - Defines the functions to interact with the LLM.
   - Every class derived from `Populatable` defines such a function.
   - Includes Pydantic Fields as data structures to be populated by AI.
   - The `on_populated` method is executed after the fields have been populated and may call business logic functions.
   - May also call business logic functions from logic.py.

3. **Inference.XY.json**:
   - Tailors functions for specific languages, denoted by the language shortcut 'XY'.
   - Outlines keywords correlating to the functions defined in inference.py.
   - A function is available for the LLM to call only if a keyword match is found (wildcard * allowed)
   - Limits the functions offered to the LLM, ideally restricting it to 3-5 functions, which prevents overwhelming it and helps avoiding confusion.
   - Optional prompts: `init_prompt` when a function is offered, `success_prompt` after successful function execution, and `fail_prompt` if the function fails.

4. **Logic.py**:
   - Contains business logic specifically related to Linguflex.
   - Calls business logic from the Handlers folder.
   - Performs additional Linguflex-related actions like state handling or raising triggers.
   - Methods can be called from the UI or inference.py

5. **State.py**:
   - Acts as a data class maintaining the module’s state.
   - This state is accessible from both logic and UI.
   - Stores module-related data (like the symbol).
   - Includes a `save()` method for serialization to file.
   - All data structures used must be serializable as they might be stored on hard disk.

6. **UI.py**:
   - Defines the user interface (window that opens when the user clicks the module symbol)
   - Offers on-the-fly module configurations and runtime adjustments.
