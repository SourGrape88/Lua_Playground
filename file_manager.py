# -----------------FILE_MANAGER.PY------------
from PyQt6.QtWidgets import QFileDialog
import os

class FileManager:

    def __init__(self, tabs, console):
        self.tabs = tabs
        self.console = console
    
    def save_file(self):

        # Gets the Current Editor
        editor = self.tabs.current_editor()
        if editor is None:
            return
        # Reads the Filepath, If No Filepath, Return None
        filepath = getattr(editor, "filepath", None)

        # If Filepath Doesnt Exist Yet -> Save As
        if filepath is None:
            filepath, _ = QFileDialog.getSaveFileName(
                None,
                "Save Lua File",
                "",
                "Lua Files (*.lua);;All Files (*)"
            )

            if not filepath:
                return
            
            # Store the Filepath
            editor.filepath = filepath
            filename = filepath.split("/")[-1]
            self.tabs.setTabText(self.tabs.currentIndex(), filename)
        
        # Write File to Disk (Copy file for saving)
        with open(editor.filepath, "w", encoding="utf-8") as f:
            f.write(editor.text())

        self.console.log(f"Saved: {editor.filepath}")

    def open_file(self):

        filepath, _ = QFileDialog.getOpenFileName(
            None,
            "Open File",
            "",
            "Lua Files (*.lua);;Python Files (*.py);;All Files (*)"
        )

        if not filepath:
            return
        
        # Open file, Read All Text, Store as a Variable
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()

        filename = filepath.split("/")[-1]

        # Create a New Tab when Opening a New File
        self.tabs.new_tab(filename, filepath)
        editor = self.tabs.current_editor()
        editor.setText(code)

        self.console.log(f"Opened: {filepath}")

    def open_file_from_explorer(self, filepath):
        
        # If it's a Folder, don't try to Open it
        if os.path.isdir(filepath):
            #self.console.log(f"Folder: {filepath}")
            return
        
        with open(filepath, "r", encoding="utf-8") as f: # Open File for Reading
            code = f.read() # Read Contents of the File

        filename = filepath.split("/")[-1] # Get File Name For Tab Label
        self.tabs.new_tab(filename, filepath) # Create New Editor Tab
        editor = self.tabs.current_editor() # Set Current Tab
        editor.setText(code) # Fill New Tab with File Contents

        # Detect Language from File Extension
        if filepath.endswith(".lua"):
            editor.set_language("lua")

        elif filepath.endswith(".py"):
            editor.set_language("python")

        self.console.log(f"Opened from Explorer: {filepath}")