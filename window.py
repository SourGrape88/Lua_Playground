# ---------- WINDOW.PY -----------------------

# This Script Controls the Main UI Layout

import sys, subprocess, os
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QPlainTextEdit, QLabel, QApplication, QTabWidget, QFileDialog, QTreeView, QSplitter, QMenu, QMenuBar
from PyQt6.QtGui import QMovie, QPixmap, QShortcut, QKeySequence, QFileSystemModel
from PyQt6.QtCore import QTimer
from graphics_canvas import Canvas
from code_editor import LuaEditor
from editor_tabs import EditorTabs
from status_indicator import StatusIndicator
from output_console import OutputConsole
from lupa import LuaRuntime

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Lua Setup
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua_globals = self.lua.globals()

        # Pass Lua to Canvas
        self.canvas = Canvas(self.lua)
        # Adds Editor_tabs File
        self.tabs = EditorTabs()
        self.new_tab_button = QPushButton("New Tab")
        self.new_tab_button.clicked.connect(lambda: self.tabs.new_tab())

        # Ctrl + s "Save" Shortcut
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        # When "Ctrl+S" is pressed, run save_file function
        self.save_shortcut.activated.connect(self.save_file)

        # Adds Status Indicator
        self.status_indicator = StatusIndicator()
        # Adds the Output Console
        self.console = OutputConsole()
        self.console.lua_runtime = self.lua
        self.console.log("Hello Byron!")
        self.console.run_terminal_command("lua -v")

        # Create a "Run Button"
        self.run_button = QPushButton("Run")

        # Create an "Open File" Button
        self.open_button = QPushButton("Open")
        # When the "Open File" Button is pressed, run the open_file function
        self.open_button.clicked.connect(self.open_file)

        # --- File Explorer Setup ---------------------
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("") # Start at the Current Directory
        self.file_model.setNameFilters(["*.lua"]) # Only Show Lua Files
        self.file_model.setNameFilterDisables(False) # Hide Non-Matching Files

        self.file_explorer = QTreeView() # Creates Tree View Widget
        self.file_explorer.setModel(self.file_model) # Link model to Tree View
        self.file_explorer.setRootIndex(self.file_model.index("./")) # Root = Project Folder
        self.file_explorer.doubleClicked.connect(self.open_file_from_explorer) # When Double Clicked, Run "open_file_from_explorer"
        self.file_explorer.setHeaderHidden(True) # Hides Size/type Columns
        self.file_explorer.setMinimumWidth(50) # Makes File Exp Small

        # Menu Bar Setup -------------------------------------
        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu("File")
        file_menu.addAction("New Tab", self.tabs.new_tab)
        file_menu.addAction("Open", self.open_file)
        file_menu.addAction("Restart IDE", self.restart_ide)
        #menu_bar.addMenu(file_menu)
        #self.setMenuBar(menu_bar)

        # Layouts -----------------------------------------
        
        # Splitter for File Explorer, Code Editor, And Canvas (top Section)
        splitter = QSplitter()
        splitter.addWidget(self.file_explorer) # Left = File Explorer
        splitter.addWidget(self.tabs) # Middle = Editor Tabs
        splitter.addWidget(self.canvas) # Right = Canvas
        splitter.setSizes([50, 500, 500]) # Set Size for File Explorer, Code Editor, and Canvas

        # Button Layout (Middle Section): Run, Status Indicator, New tab, Open
        button_layout = QHBoxLayout() # Run + Status Buttons
        button_layout.addWidget(self.run_button, stretch=1)
        button_layout.addWidget(self.status_indicator)
        #button_layout.addWidget(self.new_tab_button)
        #button_layout.addWidget(self.open_button)

        # Main Vertical Layout (Vertical): Top = Splitter, Middle = Buttons, Bottom = Console
        main_layout = QVBoxLayout() # Vertical: Screens + Buttons + Console
        main_layout.addWidget(splitter) # Add Splitter Containing the Screens
        main_layout.addLayout(button_layout) # Middle : Buttons
        main_layout.addWidget(self.console) # Bottom: Output Console
    
        # Create a Central Widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.setWindowTitle("Lua Playground")
        self.resize(800, 600)

        # Connect Run Button
        self.run_button.clicked.connect(self.run_lua_code)

        # Expose Python draw functions to Lua
        self.lua_globals.circle = self.canvas.draw_circle
        self.lua_globals.rect = self.canvas.draw_rect

        # Redirect Lua Print() to Output Console
        self.lua_globals.print = lambda *args: self.console.log(" ".join(str(a) for a in args))


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
                self,
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
            self,
            "Save Lua File",
            "",
            "Lua Files (*.lua);;All Files (*)"
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

    def open_file_from_explorer(self, index):
        filepath = self.file_model.filePath(index) # Get Filepath
        if not filepath.endswith(".lua"): # Skip Non-Lua Files
            return
        
        with open(filepath, "r", encoding="utf-8") as f: # Open File for Reading
            code = f.read() # Read Contents of the File

        filename = filepath.split("/")[-1] # Get File Name For Tab Label
        self.tabs.new_tab(filename, filepath) # Create New Editor Tab
        editor = self.tabs.current_editor() # Set Current Tab
        editor.setText(code) # Fill New Tab with File Contents

        self.console.log(f"Opened from Explorer: {filepath}")

    def run_lua_code(self):
        # Placeholder for now: Just print Editor Text to Console
        editor = self.tabs.current_editor()
        if editor is None:
            self.console.log("No Editor Open to Run Code.")
            return
        
        code = editor.text()
        # Clear Console Before Running
        self.console.clear()
        
        try:
            # Start "Running Code" Status Light
            self.status_indicator.set_running()
            
            # Force the UI to Redraw
            QApplication.processEvents()

            # Clear Previous Lua Draw Commands
            self.canvas.lua_draw_commands.clear()
            # Execute New Lua Code
            self.console.log("Running Lua Script...\n")
            self.lua.execute(code)
            # Start "Finished" Status Light
            #self.status_indicator.set_finished()
            QTimer.singleShot(500, self.status_indicator.set_finished)
            QTimer.singleShot(2000, self.status_indicator.set_idle) # 1500 = 1.5 Seconds
        except Exception as e:
            self.console.log("---- Lua Error ----")
            self.console.log(str(e))
            self.console.log("-------------------")
            self.status_indicator.set_error()

    def reset_status(self):
        self.status_indicator.set_idle()

    def restart_ide(self):
        """Restart the IDE by Launching a New Python Process for this Script"""
        python_exe = sys.executable # Path to Python Interpreter
        script_path = os.path.abspath(sys.argv[0]) # Current Script (main.py)

        # Launch a New Process
        subprocess.Popen([python_exe, script_path], cwd=os.getcwd())

        # Close the Current Instance
        QApplication.quit()
        