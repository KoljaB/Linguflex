from core import log, DEBUG_LEVEL_MAX, DEBUG_LEVEL_MID, DEBUG_LEVEL_ERR

import json
import os
from datetime import datetime, timedelta
from pydantic import Field, BaseModel
from typing import List, Any

DEFAULT_CATEGORY = "MainMemory"
MEMORY_FILENAME = "memory.json"

class Information(BaseModel):
    content: str = Field(..., description="Information content / data description")
    data: Any = Field(None, description="Optional: use for JSON or data")

class Memory:
    def __init__(self, category=DEFAULT_CATEGORY):
        if not os.path.exists(MEMORY_FILENAME):
            self.memory = {}
            self.create_new(category)
        else:
            with open(MEMORY_FILENAME, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    self.memory = data["memory"]
                    self.category = data["category"]
                    self.switch_to_category(self.category, False)
                except Exception as e:
                    log(DEBUG_LEVEL_ERR, f"   [memory] ERROR: Could not load memory file due to {str(e)}")
                    raise e

    def get_categories(self):
        return list(self.memory.keys())                    

    def fetch(self, category=None):
        if category is None or len(category) == 0:
            category = self.category

        if category in self.memory:
            return {
                "result" : "success",
                "list_of_information" : self.memory[category],
                "category": category,
            }
        else:
            log(DEBUG_LEVEL_ERR, f"  [memory] error category {category} not found")
            return {
                "result" : "ERROR",
                "reason" : "category not found"
            }
    
    def store(self, list_of_information, category=None):
        if category is None or len(category) == 0:
            category = self.category

        category_created = False
        if category not in self.memory:  
            category_created = True
            self.memory[category] = []

        if isinstance(list_of_information, str):   
            list_of_information = [Information(content=list_of_information)]          

        if isinstance(list_of_information, list) and all(isinstance(info, str) for info in list_of_information):
            list_of_information = [Information(content=info) for info in list_of_information]            

        for index, information in enumerate(list_of_information):
            information_dict = information.dict()
            information_dict['index'] = index
            self.memory[category].append(information_dict)

        self.category = category
        retval = self.switch_to_category(self.category)
        if category_created:
            retval["category_created"] = "True"
        return retval

    def switch_to_category(self, category, save_to_disk = True):
        log(DEBUG_LEVEL_MAX, f"  [memory] switching to category {category}")
        if category in self.memory:
            self.category = category
            if save_to_disk: self.save_to_disk()
            return self.fetch(self.category)
        else:
            return f"ERROR: category {category} not found"      

    def create_new(self, category=DEFAULT_CATEGORY):
        self.category = category
        if category not in self.memory:  
            self.memory[category] = []
        self.save_to_disk()

    def save_to_disk(self):
        try:
            with open(MEMORY_FILENAME, 'w', encoding='utf-8') as f:
                data = {
                    "memory": self.memory,
                    "category": self.category,
                }
                json.dump(data, f, indent=4)
        except Exception as e:
            log(DEBUG_LEVEL_ERR, f"  [memory] error could not save memory file due to {str(e)}")
            raise e
        
    def delete_entries(self, ids):
        items = [entry for entry in self.memory[self.category] if entry['index'] not in ids]
        self.memory[self.category] = items
        for i, entry in enumerate(self.memory[self.category]):
            entry['index'] = i
        self.save_to_disk()    
        return self.fetch(self.category)        

    def delete_category(self, category):
        if category in self.memory and not self.memory[category] and not category is DEFAULT_CATEGORY:
            del self.memory[category]
            self.category = DEFAULT_CATEGORY
            self.save_to_disk()
            return self.fetch(self.category)
        else:
            if category is DEFAULT_CATEGORY:
                return {
                    "result": "ERROR",
                    "message": f"Can not remove default category {category}"
                }
            elif not category in self.memory:
                return {
                    "result": "ERROR",
                    "message": f"Category {category} does not exist"
                }
            else:
                return {
                    "result": "ERROR",
                    "message": f"Category {category} is not empty, can only delete empty categories"
                }
        
    def move(self, ids, category):
        if category not in self.memory:  
            self.memory[category] = []

        moved_entries = []
        remaining_entries = []
        for entry in self.memory[self.category]:
            if entry['index'] in ids:
                moved_entries.append(entry)
            else:
                remaining_entries.append(entry)

        if moved_entries:
            self.memory[self.category] = remaining_entries
            for i, entry in enumerate(self.memory[self.category]):
                entry['index'] = i
            for i, entry in enumerate(moved_entries):
                entry['index'] = i + len(self.memory[category])
            self.memory[category].extend(moved_entries)
            self.save_to_disk()
            return {
                "result": "success",
                "message": f"Moved {len(moved_entries)} entries to category {category}"
            }
        else:
            return {
                "result": "ERROR",
                "message": "No entries found with provided IDs in current category"
            }