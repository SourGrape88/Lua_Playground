# ---------- WINDOW.PY -----------------------

# This Script Controls the Main UI Layout

import sys, subprocess, os, builtins
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QApplication, QSplitter
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import QTimer, Qt

# Modules ---------------------
from graphics_canvas import Canvas
from output_console import OutputConsole
from code_editor import CodeEditor
from editor_tabs import EditorTabs
from status_indicator import StatusIndicator
from overlay_widget import HolographicOverlay
from lsp_manager import LSPClient
from neovim_widget import NeovimWidget
from language_runner import LanguageRunner
from game_functions import draw_circle, draw_circlefill, draw_rect, draw_rectfill, draw_line, print_to_canvas, cls

from lupa import LuaRuntime

def lua_color(color, default):
    
    if color is None:
        return default
    try:
        return tuple(color[i] for i in range(1, 4))
    except Exception:
        return default

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Lua Setup
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua_globals = self.lua.globals()

        # Start LSP Clients
        self.lua_client = LSPClient(["lua-language-server", "-E", "main.lua"])
        self.lua_client.start()

        self.python_client = LSPClient(["pyright-langserver", "--stdio"])
        self.python_client.start()

        # Add the Output Console
        self.output_console = OutputConsole()

        # Pass Lua to Canvas
        self.canvas = Canvas(self.lua)
        builtins.print = lambda *args, **kwargs: self.output_console.log(" ".join(str(a) for a in args))
        #self.lua_globals.print = lambda *args: self.output_console.log(" ".join(str(a) for a in args))
        
        # Adds Status Indicator
        self.status_indicator = StatusIndicator()
        self.status_indicator.setParent(self.canvas)
        self.status_indicator.move(self.canvas.width() -self.status_indicator.width() - 10, 10)
        self.status_indicator.raise_()

        # Adds Editor_tabs File
        self.nvim_editor = NeovimWidget()

        # Script Runner
        self.runner = LanguageRunner()
        self.runner.lua_runtime = self.lua
        self.runner.canvas = self.canvas

        # Menu Bar Setup -------------------------------------
        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu("File")
        file_menu.addAction("Restart IDE", self.restart_ide)

        run_menu = self.menu_bar.addMenu("Run")
        run_menu_action = run_menu.addAction("Run Script")
        run_menu_action.triggered.connect(self.run_lua_code)

        # ---- LSP Polling Timer -----
        self.lsp_timer = QTimer()
        self.lsp_timer.timeout.connect(self.process_lsp_messages)
        self.lsp_timer.start(150)

        # ---- Central Widget ----
        central = QWidget()
        central_layout = QVBoxLayout()
        #central_layout.setContentsMargins(5, 5, 5, 5)
        central.setLayout(central_layout)
        self.setCentralWidget(central)

        # Splitter for File Explorer, Code Editor, And Canvas (top Section)
        splitter = QSplitter()
        splitter.addWidget(self.nvim_editor)
        splitter.addWidget(self.canvas)
        splitter.setSizes([500, 500])
        central_layout.addWidget(splitter)

        # ---- Output Console at the bottom ----
        central_layout.addWidget(self.output_console)
        self.setWindowTitle("Lua Playground")
        self.resize(800, 600)

        # Connect Run Button
        #self.run_button.clicked.connect(self.run_lua_code)

        # Expose Python draw functions to Lua
        self.lua_globals.circle = lambda x=10, y=50, r=50, color=None, thickness=2: \
        draw_circle(self.canvas, x, y, r, lua_color(color, (100, 200, 255)), thickness)

        self.lua_globals.circlefill = lambda x=100, y=100, r=50, color=None: \
            draw_circlefill(self.canvas, x, y, r, lua_color(color, (200, 200, 55)))

        self.lua_globals.rect = lambda x=200, y=200, w=70, h=50, color=None, thickness=2: \
            draw_rect(self.canvas, x, y, w, h, lua_color(color, (200, 50, 255)), thickness)

        self.lua_globals.rectfill = lambda x=300, y=200, w=70, h=50, color=None: \
            draw_rectfill(self.canvas, x, y, w, h, lua_color(color, (200, 150, 255)))

        self.lua_globals.print = lambda text, x=10, y=20, color=None, size=12: \
            print_to_canvas(self.canvas, text, x, y, lua_color(color, (255, 255, 255)), size)

        self.lua_globals.line = lambda x1=400, y1=200, x2=500, y2=500, color=None, thickness=2: \
            draw_line(self.canvas, x1, y1, x2, y2, lua_color(color, (255, 255, 255)), thickness)
        # Put the OpenGL Overlay inside the container
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

        # Keep status indicator at the Top-Right of the graphics Canvas
        self.status_indicator.move(
            self.canvas.width() - self.status_indicator.width() - 10,
              10)

    def run_lua_code(self):
        # Placeholder for now: Just print Editor Text to Console
    
        code = self.nvim_editor.get_text()
        self.canvas.lua_draw_commands.clear()
        
        try:
            # Start "Running Code" Status Light
            self.status_indicator.set_running()
            
            # Force the UI to Redraw
            QApplication.processEvents()

            print("Running Lua Script...\n")
            output = self.runner.execute("lua", code)
            if output:
                print(output)
   
            # Start "Finished" Status Light
            QTimer.singleShot(500, self.status_indicator.set_finished)
            QTimer.singleShot(2000, self.status_indicator.set_idle) # 1500 = 1.5 Seconds
        except Exception as e:
            print("---- Lua Error ----")
            print(str(e))
            print("-------------------")
            self.status_indicator.set_error()

    def create_new_editor_tab(self, *args, **kwargs):
        pass

    def reset_status(self):
        self.status_indicator.set_idle()

    def process_lsp_messages(self):
        """Check Both LSP Clients for New Messages"""
        for client in [self.lua_client, self.python_client]:
            while True:
                response = client.get_response()

                if not response:
                    break
                
    def restart_ide(self):
        """Restart the IDE by Launching a New Python Process for this Script"""
        python_exe = sys.executable # Path to Python Interpreter
        script_path = os.path.abspath(sys.argv[0]) # Current Script (main.py)

        # Launch a New Process
        subprocess.Popen([python_exe, script_path], cwd=os.getcwd())

        # Close the Current Instance
        QApplication.quit()
        