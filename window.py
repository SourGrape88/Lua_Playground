# ---------- WINDOW.PY -----------------------

# This Script Controls the Main UI Layout

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QPlainTextEdit, QLabel, QApplication, QTabWidget
from PyQt6.QtGui import QMovie, QPixmap
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

        # Adds Status Indicator
        self.status_indicator = StatusIndicator()
        # Adds the Output Console
        self.console = OutputConsole()

        # Create a "Run Button"
        self.run_button = QPushButton("Run")

        # Layouts
        main_layout = QVBoxLayout() # Vertical: Screens + Buttons + Console
        top_layout = QHBoxLayout() # Horizontal: Editor + Canvas
        button_layout = QHBoxLayout() # Run + Status Buttons

        top_layout.addWidget(self.tabs, stretch=1)
        top_layout.addWidget(self.canvas, stretch=1)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.console)

        button_layout.addWidget(self.run_button, stretch=1)
        button_layout.addWidget(self.status_indicator)
        button_layout.addWidget(self.new_tab_button)

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
            self.lua.execute(code)
            # Start "Finished" Status Light
            self.status_indicator.set_finished()
            QTimer.singleShot(2000, self.status_indicator.set_idle) # 1500 = 1.5 Seconds
        except Exception as e:
            self.console.log(f"Lua Error: {e}")
            self.status_indicator.set_error()

    def reset_status(self):
        self.status_icon.setMovie(self.idle_icon)
        self.idle_icon.start()