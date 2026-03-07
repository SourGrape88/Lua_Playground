import sys

from styling import apply_style
from lupa import LuaRuntime
from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QPlainTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFrame)
from PyQt6.QtGui import QPainter, QColor, QFont 
from PyQt6.QtCore import QTimer 
from PyQt6.Qsci import QsciScintilla, QsciLexerLua


# ---------CANVAS (GRAPHICS) ------------------------------------

class Canvas(QWidget):

    def __init__(self, lua):
        super().__init__()
        self.lua = lua
        # Position of the animated circle
        self.x = 300
        # Speed of the Circle
        self.dx = 2

        # List of Draw Commands
        self.draw_commands = []

        # List of Lua Commands
        self.lua_draw_commands = []

        # Create a Timer that Fires Repeatedly
        self.timer = QTimer()
        # Connect the timer to our Update Function
        self.timer.timeout.connect(self.update_frame)
        # Start Timer at ~60 FPS
        self.timer.start(16)

    # -------------DRAW COMMAND FUNCTIONS ------------------
    def draw_circle(self, x, y, r, color=(100, 200, 255)):
        """Add a Circle Command to the Draw List"""
        if color is None:
            color = (100, 200, 255)
        elif hasattr(color, 'values'):
            color = tuple(color.values())
        self.lua_draw_commands.append(("circle", x, y, r, color))

    def draw_rect(self, x, y, w, h, color=(150, 70, 100)):
        """Add a Rectangle Command to the Draw List"""
        if color is None:
            color = (255, 20, 50)
        elif hasattr(color, 'values'):
            color = tuple(color.values())
        self.lua_draw_commands.append(("rect", x, y, w, h, color))

    # ------------------------------------------------------------

    def update_frame(self):

        """The Update Function"""

        # Demo Animation (moving circle)
        self.x += self.dx
        # Bounce if it hits left or right edge of screen
        if self.x < 200 or self.x > 500:
          self.dx = -self.dx

        # Clear Previous Frame's Commands
        self.draw_commands.clear()
        #self.lua_draw_commands.clear()

        # --- Call Lua Update() If it Exists -------
        lua_update = getattr(self.lua.globals(), "update", None)
        if lua_update:
            try:
                lua_update()
            except Exception as e:
                print(f"Lua Update Error: {e}")

        # Add Python Demo Shapes
        self.draw_commands.append(("circle", self.x, 200, 40, (100, 200, 255)))
        self.draw_commands.append(("rect", 100, 300, 60, 60, (150, 70, 100)))

        # Add Lua Shapes
        self.draw_commands.extend(self.lua_draw_commands)

        # Update Frame/Trigger Frame Repaint
        self.update()

    def paintEvent(self, event):
        """Draw All Commands"""
        # Called Whenever the Widget needs to Redraw
        painter = QPainter(self)

        # Draw Background
        painter.fillRect(self.rect(), QColor(30, 30, 30))

        # Loop through all Draw Commands
        for cmd in self.draw_commands:
            # If the first command in line is Circle...
            if cmd[0] == "circle":
                _, x, y, r, color = cmd
                painter.setBrush(QColor(*color))
                painter.drawEllipse(x, y, r, r)

            elif cmd[0] == "rect":
                _, x, y, w, h, color = cmd
                painter.setBrush(QColor(*color))
                painter.drawRect(x, y, w, h)

class LuaEditor(QsciScintilla):
    def __init__(self):
        super().__init__()

        # Font
        font = QFont("Consolas", 16)
        self.setFont(font)
        #self.setMarginsForegroundColor(QColor("#ECA0BE"))
        #self.setMarginsBackgroundColor(QColor("#3C6774"))
        self.setMarginsFont(QFont("Consolas", 12, QFont.Weight.Bold))

        # Selection Highlight Color
        self.setSelectionBackgroundColor(QColor("#E31815"))
        self.setSelectionForegroundColor(QColor("#8205C5"))

        # Syntax Highlighting
        #editor = QsciScintilla()
        
        # Lexer
        lexer = QsciLexerLua() # Lua Syntax
        lexer.setDefaultFont(font)

        # Text Editor Background Color
        lexer.setDefaultPaper(QColor("#E31815"))

        # Text Editor Font Color
        lexer.setColor(QColor("#F2BC71"), 0)

        # Comments
        lexer.setColor(QColor("#851764"), 1)
        lexer.setColor(QColor("#C5EBCA"), 2)
        
        # Numbers
        lexer.setColor(QColor("#B0D2F3"), 3)

        # Keywords (function, if, end, etc)
        #lexer.setKeywords(0,"and break do else elseif end false for function if in local nil not or repeat return then true until while")
        lexer.setColor(QColor("#D78F24"), 4)

        # Strings
        lexer.setColor(QColor("#5B3EEB"), 5)
        lexer.setColor(QColor("#9A8C09"), 6)
        lexer.setColor(QColor("#CE9178"), 7)

        # Operators
        lexer.setColor(QColor("#0A24F5"), 9)

        # Identifiers
        # Identifier Background
        lexer.setPaper(QColor("#E31815"), 10)

        # Identifier Foreground
        lexer.setColor(QColor("#9CDCFE"), 10)

        

        #for style in range(128):
            #lexer.setFont(font, style)
            #lexer.setPaper(QColor("#53AFD3"), style)

        # Text Editor Font Background Color
        #lexer.setPaper(QColor("#FFFFFF"))

        
        self.setLexer(lexer)
        self.setPaper(QColor("#7E53D3"))
        
        #for style in range(128):
            #lexer.setPaper(QColor("#C11818"), style)

        # Text Editor Colors
        

        # Line Numbers
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "0000") # Adjust width for line numbers
        # Line Number Color
        self.setMarginsForegroundColor(QColor("#D12631"))

        # Line Number Background Color
        self.setMarginsBackgroundColor(QColor("#234EB3"))
     
        # Auto-Close Brackets
        self.setAutoCompletionReplaceWord(False) # So it doesnt replace Existing Text
        self.setAutoCompletionUseSingle(QsciScintilla.AutoCompletionUseSingle.AcusAlways) # Single Suggestion Only
        self.setAutoCompletionThreshold(1) # Trigger Quickly
        self.setAutoIndent(True)
        
        # AutoComplete & Brace Matching
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionThreshold(1) # Trigger After 2 Characters

        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        self.setAutoIndent(True)
        self.setIndentationWidth(4)
        self.setTabWidth(4)
        self.setTabIndents(True)

    def keyPressEvent(self, event):
        char = event.text()

        pairs = {"(":")", "{":"}", "[":"]"}

        if char in pairs:
            closing = pairs[char]
            line, index = self.getCursorPosition()
            self.insert(char + closing)

            # Move Cursor Between Brackets
            self.setCursorPosition(line, index + 1)
        else:
            super().keyPressEvent(event)
        

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

app = QApplication(sys.argv)
apply_style(app)
window = MainWindow()
window.show()
sys.exit(app.exec())