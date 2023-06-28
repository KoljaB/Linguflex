import json
import os
from datetime import datetime, timedelta

class Notebook:
    def __init__(self, name='Default Notebook'):
        self.entries = []
        self.counter = 0
        self.load_file = 'notebooks.json'
        if not os.path.exists(self.load_file):
            self.notebooks = {}
            self.create_new(name)
        else:
            with open(self.load_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.notebooks = data['notebooks']
                self.name = data['current_notebook']
                self.switch(self.name)

    def get_all_notebook_names(self):
        return list(self.notebooks.keys())                    

    def write_entries(self, texts, notebook_name='Default Notebook'):

        if len(notebook_name) == 0 or notebook_name == 'Default Notebook':
            notebook_name = self.name

        if notebook_name not in self.notebooks:  
            self.notebooks[notebook_name] = []

        if isinstance(texts, str):   
            texts = [texts]          

        entries = []
        for text in texts:
            self.counter += 1
            entry = {
                'text': text,
                'id': str(self.counter),
                'creation_date': str(datetime.now())
            }
            self.notebooks[notebook_name].append(entry)
            entries.append(entry)
            
        self.save_to_disk()

        self.name = notebook_name
        self.switch(self.name)

        return self.entries

    def delete_entry(self, id):
        self.entries = [entry for entry in self.entries if entry['id'] != id]
        self.notebooks[self.name] = self.entries
        self.save_to_disk()

    def return_entries(self):
        return {
            'name': self.name,
            'entries': self.entries
        }

    def change_name(self, name):
        self.notebooks[name] = self.notebooks.pop(self.name)
        self.name = name
        self.save_to_disk()

    def switch(self, name):
        if name in self.notebooks:
            self.name = name
            self.entries = self.notebooks[name]
            if len(self.entries) > 0:
                self.counter = max(int(entry['id']) for entry in self.entries)
            else:
                self.counter = 1
            self.save_to_disk()
            return f"switched successful to notebook {name}"
        return f"ERROR: notebook {name} not found"
        

    def create_new(self, name='Default Notebook'):
        self.name = name
        self.entries = []
        self.counter = 0
        self.notebooks[self.name] = self.entries
        self.save_to_disk()

    def save_to_disk(self):
        with open(self.load_file, 'w', encoding='utf-8') as f:
            data = {
                'current_notebook': self.name,
                'notebooks': self.notebooks
            }
            json.dump(data, f, indent=4)
