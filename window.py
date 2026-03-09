# ---------- WINDOW.PY -----------------------

# This Script Controls the Main UI Layout

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QPlainTextEdit, QLabel, QApplication, QTabWidget
from PyQt6.QtGui import QMovie, QPixmap
from PyQt6.QtCore import QTimer
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

        self.tabs = QTabWidget()
        # Makes the "X" to Close Tabs
        self.tabs.setTabsClosable(True)
        # Remove Tab when "X" is Clicked
        self.tabs.tabCloseRequested.connect(self.close_tab)

        # Start with One Tab
        self.new_tab("Main.lua")

        # New Tab Button
        self.new_tab_button = QPushButton("New Tab")
        self.new_tab_button.clicked.connect(lambda: self.new_tab())


        # Create the Code/Text Editor
        #self.editor = LuaEditor()

        # Create a "Run Button"
        self.run_button = QPushButton("Run")

        # Create Status Indicator
        self.status_icon = QLabel()
        self.status_icon.setMinimumWidth(80)
        self.status_icon.setFixedSize(64, 64)
        self.status_icon.setScaledContents(True)
        self.idle_icon = QMovie("assets/status_light/Idle_Status_Light.gif") # Idle GIF
        self.run_icon = QMovie("assets/status_light/Running_Status_Light.gif") # Running GIF
        self.run_icon.setSpeed(50)
        self.finished_icon = QMovie("assets/status_light/Finished_Status_Light.gif") # Finished GIF
        self.error_icon = QMovie("assets/status_light/Error_Status_Light.gif")
        self.status_icon.setMovie(self.idle_icon)
        self.idle_icon.start()

        # Create the Output Console
        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(100)

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
        button_layout.addWidget(self.status_icon)
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

        # Redirect Lua Print() to the Ouput Console
        def lua_print(*args):
            text = " ".join(str(a) for a in args)
            self.console.appendPlainText(text)
        
        self.lua_globals.print = lua_print

    def new_tab(self, filename="Untitled.lua"):
        editor = LuaEditor()
        index = self.tabs.addTab(editor, filename)
        self.tabs.setCurrentIndex(index)

    def close_tab(self, index):
        self.tabs.removeTab(index)

    def current_editor(self):
        return self.tabs.currentWidget()

    def run_lua_code(self):
        # Placeholder for now: Just print Editor Text to Console
        code = self.current_editor().text()
        
        # Clear Console Before Running
        self.console.clear()
        
        try:
            # Start "Running Code" Status Light
            self.status_icon.setMovie(self.run_icon)
            self.run_icon.start()

            # Force the UI to Redraw
            QApplication.processEvents()

            # Clear Previous Lua Draw Commands
            self.canvas.lua_draw_commands.clear()
            # Execute New Lua Code
            self.lua.execute(code)
            # Start "Finished" Status Light
            self.run_icon.stop()
            self.status_icon.setMovie(self.finished_icon)
            self.finished_icon.start()
            QTimer.singleShot(2000, self.reset_status) # 1500 = 1.5 Seconds
        except Exception as e:
            self.console.appendPlainText(f"Lua Error: {e}")
            self.status_icon.setMovie(self.error_icon)
            self.error_icon.start()
            #QTimer.singleShot(200, self.reset_status)

    def reset_status(self):
        self.status_icon.setMovie(self.idle_icon)
        self.idle_icon.start()