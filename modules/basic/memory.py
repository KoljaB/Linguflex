from core import ActionModule, Request, cfg, log, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR
from linguflex_functions import LinguFlexBase, linguflex_function
from pydantic import Field, BaseModel
from datetime import datetime, timedelta
from typing import List
from memory_helper import Memory, Information
from typing import List, Any
import json

memory = Memory()

class store_information_to_memory(LinguFlexBase):
    """
    Memorizes information by storing it into a database and making it accessible.
    This function receives a list of information bits and an optional category. 
    Store precisely, exclusively and compact what the user asked for and DO NOT MAKE UP STUFF.
    """
    list_of_information: List[Information] = Field(..., description="List of information entries, each consisting of a content string and optional data.")
    category: str = Field(default=None, description="Optional: category information will be stored into.")

    def execute(self):
        memory.store(self.list_of_information, self.category)
        return memory.fetch(self.category)

class fetch_information_from_memory(LinguFlexBase):
    "Recalls / remembers information from the memory"
    category: str = Field(default=None, description="Optional: category of information to be fetched")

    def execute(self):
        return memory.fetch(self.category)
     
class change_memory_category(LinguFlexBase):
    "Switches to memory category with given name; only call when explicitly asked to"
    category: str = Field(default=None, description="Optional: name of category to switch to.")

    def execute(self):
        return memory.switch_to_category(self.category)

class delete_memory_information(LinguFlexBase):
    "Deletes information from memory"
    list_of_indices: List[int] = Field(..., description="List of indices of the information to be deleted from the current memory category.")

    def execute(self):
        return memory.delete_entries(self.list_of_indices)

class delete_memory_category(LinguFlexBase):
    "Deletes category from memory"
    category: str = Field(..., description="Name of category to be deleted. Must not have any information in it to be allowed to delete.")

    def execute(self):
        return memory.delete_category(self.category)

class list_all_memory_categories(LinguFlexBase):
    "Retrieves a list of all available memory categories"

    def execute(self):
        return memory.get_categories()
    
class move_information_to_category(LinguFlexBase):
    "Moves information to category"
    list_of_indices: List[int] = Field(..., description="List of indices of the information to be moved.")
    category: str = Field(..., description="Category information will be stored into.")

    def execute(self):
        memory.move(self.list_of_indices, self.category)
        return memory.fetch(self.category)
    
class ProvideMemoryData(ActionModule):
    def init(self) -> None: 
        self.server.register_event("memory_category_changed", memory.switch_to_category)

    def cycle(self, request: Request) -> None: 
        memory_data = memory.fetch()
        memory_data["categories"] = memory.get_categories()
        self.server.set_event("memory_data", memory_data)

        #request.memory = memory.fetch()

    def on_function_added(self, 
            request: Request,
            function_name: str,
            caller_name: str,
            type: str) -> None: 
        
        # if we added a function from this module (meaning we reacted to any keywords)
        if self.name == caller_name:
            request.add_prompt(f"Memory: {json.dumps(memory.fetch())}")
            request.add_prompt(f"Memory categories: {json.dumps(memory.get_categories())}")