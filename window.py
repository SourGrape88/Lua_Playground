# ---------- WINDOW.PY -----------------------

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QPlainTextEdit
from graphics_canvas import Canvas
from code_editor import LuaEditor
from lupa import LuaRuntime

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Lua Setup
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua_globals = self.lua.globals()

        # Pass Lua to Canvas
        self.canvas = Canvas(self.lua)

        # Create the Text Editor
        self.editor = LuaEditor()

        
        # Create a "Run Button"
        self.run_button = QPushButton("Run")
        # Create the Output Console
        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(100)

        # Layouts
        main_layout = QVBoxLayout() # Vertical: Buttons + Horizontal + Console
        top_layout = QHBoxLayout() # Horizontal: Editor + Canvas

        top_layout.addWidget(self.editor, stretch=1)
        top_layout.addWidget(self.canvas, stretch=1)

        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.run_button)
        main_layout.addWidget(self.console)

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

        # Redirect Lua Print() to the Ouput Console
        def lua_print(*args):
            text = " ".join(str(a) for a in args)
            self.console.appendPlainText(text)
        
        self.lua_globals.print = lua_print

    def run_lua_code(self):
        # Placeholder for now: Just print Editor Text to Console
        code = self.editor.text()
        try:
            # Clear Previous Lua Draw Commands
            self.canvas.lua_draw_commands.clear()
            # Execute New Lua Code
            self.lua.execute(code)
        except Exception as e:
            self.console.appendPlainText(f"Lua Error: {e}")