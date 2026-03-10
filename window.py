# ---------- WINDOW.PY -----------------------

# This Script Controls the Main UI Layout

import sys, subprocess, os
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QApplication, QSplitter
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import QTimer, Qt

# Modules ---------------------
from graphics_canvas import Canvas
from code_editor import CodeEditor
from editor_tabs import EditorTabs
from status_indicator import StatusIndicator
from output_console import OutputConsole
from file_explorer import FileExplorer
from file_manager import FileManager
from overlay_widget import HolographicOverlay

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

        # Add File Explorer from file_explorer.py
        self.file_explorer = FileExplorer()
        self.file_explorer.doubleClicked.connect(self.handle_explorer_click)

        # Adds Status Indicator
        self.status_indicator = StatusIndicator()
        print("StatusIndicator Parent:", self.status_indicator.parent())
        print("Is Visible:", self.status_indicator.isVisible())
        # Adds the Output Console
        self.console = OutputConsole()
        self.console.lua_runtime = self.lua
        self.console.runner.canvas = self.canvas
        self.console.log("Hello Byron!")
        #self.console.run_terminal_command("lua -v")

        # Add File Manager from file_manager.py
        self.file_manager = FileManager(self.tabs, self.console)

        # Ctrl + s "Save" Shortcut
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        # When "Ctrl+S" is pressed, run save_file function
        self.save_shortcut.activated.connect(self.file_manager.save_file)


        # Create a "Run Button"
        self.run_button = QPushButton("Run")

        # Create an "Open File" Button
        #self.open_button = QPushButton("Open")
        # When the "Open File" Button is pressed, run the open_file function
        #self.open_button.clicked.connect(self.open_file)

        # Menu Bar Setup -------------------------------------
        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu("File")
        file_menu.addAction("New Tab", self.tabs.new_tab)
        file_menu.addAction("Open", self.file_manager.open_file)
        file_menu.addAction("Restart IDE", self.restart_ide)
        #menu_bar.addMenu(file_menu)
        #self.setMenuBar(menu_bar)

        # Language Menu
        language_menu = self.menu_bar.addMenu("Language")
        language_menu.addAction("Lua", lambda: self.set_language("lua"))
        language_menu.addAction("Python", lambda: self.set_language("python"))

        # Layouts -----------------------------------------
        
        # ---- Central Widget ----
        central = QWidget()
        central_layout = QVBoxLayout()
        #central_layout.setContentsMargins(5, 5, 5, 5)
        central.setLayout(central_layout)
        self.setCentralWidget(central)

        # Splitter for File Explorer, Code Editor, And Canvas (top Section)
        splitter = QSplitter()
        splitter.addWidget(self.file_explorer) # Left = File Explorer
        splitter.addWidget(self.tabs) # Middle = Editor Tabs
        splitter.addWidget(self.canvas) # Right = Canvas
        splitter.setSizes([50, 500, 500]) # Set Size for File Explorer, Code Editor, and Canvas
        central_layout.addWidget(splitter)

        # Button Layout (Middle Section): Run, Status Indicator, New tab, Open
        button_layout = QHBoxLayout() # Run + Status Buttons
        button_layout.addWidget(self.run_button, stretch=1)
        self.status_indicator.setParent(central)
        button_layout.addWidget(self.status_indicator)
        central_layout.addLayout(button_layout)
        #button_layout.addWidget(self.new_tab_button)
        #button_layout.addWidget(self.open_button)

        # ---- Console ----
        central_layout.addWidget(self.console)

        # Create a Container for Run + Status
        #self.button_container = QWidget()
        #self.button_container.setLayout(button_layout)

        # Main Vertical Layout (Vertical): Top = Splitter, Middle = Buttons, Bottom = Console
        #main_layout = QVBoxLayout() # Vertical: Screens + Buttons + Console
        #main_layout.addWidget(splitter) # Add Splitter Containing the Screens
        #main_layout.addLayout(button_layout) # Middle : Buttons
        #main_layout.addWidget(self.console) # Bottom: Output Console
    
        self.setWindowTitle("Lua Playground")
        self.resize(800, 600)

        # Connect Run Button
        self.run_button.clicked.connect(self.run_lua_code)

        # Expose Python draw functions to Lua
        self.lua_globals.circle = self.canvas.draw_circle
        self.lua_globals.rect = self.canvas.draw_rect

        # Redirect Lua Print() to Output Console
        self.lua_globals.print = lambda *args: self.console.log(" ".join(str(a) for a in args))

        # Overlay Widget -------
        #self.overlay_container = QWidget(self.centralWidget())
        #self.overlay_container.setGeometry(0, 0, self.centralWidget().width(), self.centralWidget().height())
        #self.overlay_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        #self.overlay_container.show()

        # Put the OpenGL overlay inside the container
        self.overlay = HolographicOverlay(central)
        self.overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.overlay.setGeometry(central.geometry())
        self.overlay.lower()
        self.overlay.show()

        self.status_indicator.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Resize Overlay to Fill Central Widget
        self.overlay.setGeometry(0, 0, self.centralWidget().width(), self.centralWidget().height()) # Overlay follows Window Size

    def run_lua_code(self):
        # Placeholder for now: Just print Editor Text to Console
        editor = self.tabs.current_editor()
        if editor is None:
            self.console.log("No Editor Open to Run Code.")
            return
        
        code = editor.text()
        # Clear Console Before Running
        self.console.clear_console()
        
        try:
            # Start "Running Code" Status Light
            self.status_indicator.set_running()
            
            # Force the UI to Redraw
            QApplication.processEvents()

            # Clear Previous Lua Draw Commands
            self.canvas.lua_draw_commands.clear()
            # Execute New Lua Code
            self.console.log("Running Script...\n")
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

    def handle_explorer_click(self, index):
        filepath = self.file_explorer.filepath_from_index(index)
        self.file_manager.open_file_from_explorer(filepath)
    
    def set_language(self, language):
        """Change the Active Scripting Language"""
        self.console.language = language
        self.console.log(f"Language Set to: {language}")

    def restart_ide(self):
        """Restart the IDE by Launching a New Python Process for this Script"""
        python_exe = sys.executable # Path to Python Interpreter
        script_path = os.path.abspath(sys.argv[0]) # Current Script (main.py)

        # Launch a New Process
        subprocess.Popen([python_exe, script_path], cwd=os.getcwd())

        # Close the Current Instance
        QApplication.quit()
        