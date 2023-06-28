from core import BaseModule, Request, cfg, log, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR
from linguflex_functions import LinguFlexBase, linguflex_function
from pydantic import Field
from datetime import datetime, timedelta
from typing import List
from notebook_helper import Notebook
import json

notebook = Notebook()
entries = notebook.return_entries()

class create_or_update_notebook(LinguFlexBase):
    """
    Creates a new notebook or updates an existing one with given entries. 
    This function receives a list of texts and a notebook name. If the notebook name is given,
    it adds entries from the list to the notebook. If the notebook does not exist, it creates one.
    """
    list_of_texts: List[str] = Field(..., description="List of text entries to be written into the notebook. Can be an empty list.")
    notebook_name: str = Field(default="Default Notebook", description="Name of the notebook to be updated or created. If not provided, entries will be added to the current active notebook.")

    def execute(self):
        global entries
        retval = notebook.write_entries(self.list_of_texts, self.notebook_name)
        entries = notebook.return_entries()
        return retval

class delete_notebook_entry(LinguFlexBase):
    "Adds entry to the notebook"
    id: str = Field(..., description="Id of the entry to be deleted from notebook")

    def execute(self):
        global entries
        retval = notebook.delete_entry(self.id)
        entries = notebook.return_entries()
        return retval

class return_notebook_entries(LinguFlexBase):
    "Returns all entries in the current notebook"

    def execute(self):
        return notebook.return_entries()

class change_notebook_name(LinguFlexBase):
    "Changes the name of the current notebook"
    new_notebook_name: str = Field(..., description="New name of the notebook")

    def execute(self):
        return notebook.change_name(self.new_notebook_name)

class switch_to_notebook(LinguFlexBase):
    "Switches to notebook with given name; only call when explicitly asked to"
    notebook_name: str = Field(default="Default Notebook", description="Name of the notebook to switch to")

    def execute(self):
        global entries
        retval = notebook.switch(self.notebook_name)
        entries = notebook.return_entries()
        return retval

# class new_notebook(LinguFlexBase):
#     "Loads a new notebook"
#     notebook_name: str = Field(default="Default Notebook", description="Leave empty if not specified; name of notebook that should be created")
#     list_of_texts: List[str] = Field(..., description="List of texts to be written into notebook, can be empty")

#     def execute(self):
#         global entries
#         retval = notebook.create_new(self.notebook_name)
#         entries = notebook.return_entries()
#         return retval

class list_all_notebook_names(LinguFlexBase):
    "Retrieves a list of all available notebooks"

    def execute(self):
        return notebook.get_all_notebook_names()
    
class ProvideNotebookData(BaseModule):
    def cycle(self, request: Request) -> None: 
        #print (f"Notebook WR: {entries}")
        request.notebook = entries


    def on_function_added(self, 
            request: Request,
            name: str,
            type: str) -> None: 
        
        string_entries = 'Notebook: '
        for entry in entries["entries"]:
            string_entries += json.dump(entry)

        if not string_entries in request.prompt:
            request.prompt += string_entries