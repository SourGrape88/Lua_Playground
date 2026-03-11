# -----------CODE_EDITOR.PY-----------------

from PyQt6.Qsci import QsciScintilla, QsciLexerLua, QsciLexerPython
from PyQt6.QtGui import QFont, QColor

from tokenizer import highlight_python, highlight_lua

class CodeEditor(QsciScintilla):
    TOKEN_COLORS = {
        "namespace": "#FFD700",
        "type": "#446152",
        "class": "#2F00FF",
        "enum": "#F7D591",
        "interface": "#00CCFF",
        "struct": "#A73473",
        "typeParameter": "#00CCFF",
        "parameter": "#095B39",
        "variable": "#FF8543",
        "property": "#285673",
        "enumMember": "#460546",
        "event": "#D71414",
        "function": "#777F1B", # works for lua
        "method": "#F9C4ED",
        "macro": "#FF6600",
        "keyword": "#FF00BF", # Works for both
        "modifier": "#FFA500",
        "comment": "#A507F5", # Works for both
        "string": "#00FF1E",  # works for both
        "number": "#FCB5D6", # Works for Lua
        "regexp": "#FF0055",
        "operator": "#73A37D",
        "decorator": "#FF00FF",
        }
    
    def __init__(self):
        super().__init__()

        red = "#E31815"
        gold = "#FFC02D"
        blue = "#23B340"
        redQColor = QColor("#E31815")
        goldQColor = QColor("#FFC02D")
        
        # Convert BBGGRR Format for Scintilla
        red_bbggrr = (redQColor.blue() << 16 | (redQColor.green() << 8) | redQColor.red())
        gold_bbggrr = (goldQColor.blue() << 16 | (goldQColor.green() << 8) | goldQColor.red())

        # Set default text style background (covers whitespace and non-token text)
        self.SendScintilla(self.SCI_STYLESETBACK, 1, red_bbggrr)  # red = #E31815
        self.SendScintilla(self.SCI_STYLESETFORE, 1, gold_bbggrr)  # optional default text color (Gold)

        self.setPaper(redQColor)

        # Font
        font = QFont("FiraMono Nerd Font", 16)
        bold = QFont("FiraMono Nerd Font", 16)
        bold.setBold(True)
        self.setFont(font)

        margin_font = QFont("FiraMono Nerd Font", 16)
        margin_font.setBold(True)
        self.setMarginsFont(margin_font)

        self.textChanged.connect(self.on_text_changed)

        # Store Current Language
        self.language = "lua"

        # Selection Highlight Color
        self.setSelectionBackgroundColor(QColor("#EA7674"))
        self.setSelectionForegroundColor(QColor("#FFFFFF"))

        # Syntax Highlighting
        
        self.setPaper(QColor(red))
        self.setColor(QColor(gold))

        # Lua Lexer
        self.lua_lexer = QsciLexerLua() # Lua Syntax
        self.lua_lexer.setDefaultFont(font)

        for style in range(128):
            self.lua_lexer.setColor(QColor(gold), style)
            self.lua_lexer.setFont(font, style)
        
        # Python Lexer
        self.python_lexer = QsciLexerPython()
        self.python_lexer.setDefaultFont(font)

        for style in range(128):
            self.python_lexer.setFont(font, style)
            self.python_lexer.setColor(QColor(red), style)

        #self.lua_lexer.setDefaultPaper(QColor(red))
        self.textChanged.connect(self.on_text_changed)
        
        self.python_lexer.setDefaultPaper(QColor(red))

        #self.python_lexer.setColor(QColor(blue), QsciLexerPython.Comment)
        self.python_lexer.setFont(bold, QsciLexerPython.Comment)

        # Identifier = Default Words
        self.python_lexer.setColor(QColor("#00CCFF"), QsciLexerPython.Identifier)
        #self.python_lexer.setFont(bold, QsciLexerPython.Identifier)

        #self.python_lexer.setColor(QColor("#F9C4ED"), QsciLexerPython.FunctionMethodName)
        self.python_lexer.setFont(bold, QsciLexerPython.FunctionMethodName)
        # Operator = ., "()", "+", "=", "<", etc
        #self.python_lexer.setColor(QColor("#FFFFFF"), QsciLexerPython.Operator)
        self.python_lexer.setFont(bold, QsciLexerPython.Operator)

        #self.python_lexer.setColor(QColor("#FFD900"), QsciLexerPython.Keyword)
        self.python_lexer.setFont(bold, QsciLexerPython.Keyword)

        self.lua_lexer.setFont(bold, QsciLexerLua.Keyword)
        self.lua_lexer.setFont(bold, QsciLexerLua.Operator)

        # Identifier Foreground (Normal Text, Print, etc)
        self.lua_lexer.setColor(QColor(gold), QsciLexerLua.Identifier)

        self.setLexer(None)
        #self.setPaper(QColor("#7E53D3"))

        # Line Numbers
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "0000") # Adjust width for line numbers
        # Line Number Color
        self.setMarginsForegroundColor(QColor("#D12631"))

        # Line Number Background Color
        self.setMarginsBackgroundColor(QColor("#234EB3"))


        self.setMatchedBraceForegroundColor(QColor("#A9D6F8"))
        self.setMatchedBraceBackgroundColor(QColor("#FC8989"))
        # Auto-Close Brackets
        self.setAutoCompletionReplaceWord(False) # So it doesnt replace Existing Text
        #self.setAutoCompletionUseSingle(QsciScintilla.AutoCompletionUseSingle.AcusAlways) # Single Suggestion Only
        self.setAutoCompletionThreshold(1) # Trigger Quickly
        self.setAutoIndent(True)
        
        # AutoComplete & Brace Matching
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionUseSingle(QsciScintilla.AutoCompletionUseSingle.AcusNever)

        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        self.setAutoIndent(True)
        self.setIndentationWidth(4)
        self.setTabWidth(4)
        self.setTabIndents(True)

        self.semantic_token_types = [
            "namespace","type","class","enum","interface","struct","typeParameter",
            "parameter","variable","property","enumMember","event","function","method",
            "macro","keyword","modifier","comment","string","number","regexp","operator","decorator"
        ]

        # Assign each token type a Unique style and set its color
        self.semantic_styles = {}
        self.semantic_styles["default"] = 1
        for i, token_type in enumerate(self.semantic_token_types, start=50):
            color_hex = self.TOKEN_COLORS.get(token_type, "#FFFFFF")
            color = QColor(color_hex)

            # Build 0xBBGGRR integer for Scintilla
            fg = color.blue() << 16 | color.green() << 8 | color.red() 

            bg_color = QColor("#E31815")
            bg = bg_color.blue() << 16 | bg_color.green() << 8 | bg_color.red() 

            # Set Foreground
            self.SendScintilla(self.SCI_STYLESETFORE, i, fg)
            
            # Set Foreground
            self.SendScintilla(self.SCI_STYLESETBACK, i, bg)
            self.semantic_styles[token_type] = i


    def on_text_changed(self):
        if self.language == "python":
            highlight_python(self)
        elif self.language == "lua":
            highlight_lua(self)

    def set_language(self, language):
        self.language = language
        if language == "lua":
            self.setLexer(self.lua_lexer)
            highlight_lua(self)
        elif language == "python":
            self.setLexer(self.python_lexer)
            highlight_python(self)
        
        self.recolor()

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

    def apply_semantic_token(self, start_pos, length, token_type):
        #style = self.semantic_styles.get(token_type, 1)  # fallback style
        default_style = self.semantic_styles["default"]
        # Red Background
        bg_color = QColor("#E31815")
        bg_rgb = bg_color.blue() << 16 | bg_color.green() << 8 | bg_color.red()
        self.SendScintilla(self.SCI_STYLESETBACK, default_style, bg_rgb)

        # Apply Semantic Style for Foreground (Text Color)
        style = self.semantic_styles.get(token_type, default_style)

        # Ensure the Foreground color is correct
        token_color = QColor(self.TOKEN_COLORS.get(token_type, "#FFFFFF"))
        rgb = token_color.blue() << 16 | token_color.green() << 8 | token_color.red()
        self.SendScintilla(self.SCI_STYLESETFORE, style, rgb)

        # Apply styling: keep background as default style, foreground as semantic style
        for i in range(length):
            self.SendScintilla(self.SCI_STARTSTYLING, start_pos, 31)
            # Set each character with the semantic style
            self.SendScintilla(self.SCI_SETSTYLING, length, style)

        