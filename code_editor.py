# -----------Code Editor-----------------

from PyQt6.Qsci import QsciScintilla, QsciLexerLua, QsciLexerPython
from PyQt6.QtGui import QFont, QColor

class CodeEditor(QsciScintilla):
    def __init__(self):
        super().__init__()

        red = "#E31815"
        gold = "#FFC02D"
        blue = "#234EB3"
        #color = "#FFCC5D"

        # Font
        font = QFont("FiraMono Nerd Font", 16)
        bold = QFont("FiraMono Nerd Font", 16)
        bold.setBold(True)
        self.setFont(font)

        margin_font = QFont("FiraMono Nerd Font", 16)
        margin_font.setBold(True)
        self.setMarginsFont(margin_font)

        # Selection Highlight Color
        self.setSelectionBackgroundColor(QColor("#EA7674"))
        self.setSelectionForegroundColor(QColor("#FFFFFF"))

        # Syntax Highlighting
        #editor = QsciScintilla()
        
        # Lua Lexer
        self.lua_lexer = QsciLexerLua() # Lua Syntax
        self.lua_lexer.setDefaultFont(font)

        # Python Lexer
        self.python_lexer = QsciLexerPython()
        self.python_lexer.setDefaultFont(font)

        for style in range(128):
            self.lua_lexer.setFont(font, style)
            self.lua_lexer.setPaper(QColor(red), style)

        self.lua_lexer.setDefaultPaper(QColor(red))

        for style in range(128):
            self.python_lexer.setFont(font, style)
            self.python_lexer.setPaper(QColor(red), style)

        self.python_lexer.setDefaultPaper(QColor(red))

        self.python_lexer.setColor(QColor("#00FF77"), QsciLexerPython.Default)

        self.python_lexer.setColor(QColor(blue), QsciLexerPython.Comment)
        self.python_lexer.setFont(bold, QsciLexerPython.Comment)

        # Identifier = Default Words
        self.python_lexer.setColor(QColor("#00CCFF"), QsciLexerPython.Identifier)
        #self.python_lexer.setFont(bold, QsciLexerPython.Identifier)

        self.python_lexer.setColor(QColor(gold), QsciLexerPython.DoubleQuotedString)
        self.python_lexer.setColor(QColor("#FCB5D6"), QsciLexerPython.Number)
        self.python_lexer.setColor(QColor("#09FF00"), QsciLexerPython.ClassName)

        self.python_lexer.setColor(QColor("#F9C4ED"), QsciLexerPython.FunctionMethodName)
        self.python_lexer.setFont(bold, QsciLexerPython.FunctionMethodName)
        # Operator = ., "()", "+", "=", "<", etc
        self.python_lexer.setColor(QColor("#FFFFFF"), QsciLexerPython.Operator)
        self.python_lexer.setFont(bold, QsciLexerPython.Operator)

        self.python_lexer.setColor(QColor("#FFD900"), QsciLexerPython.Keyword)
        self.python_lexer.setFont(bold, QsciLexerPython.Keyword)

        self.lua_lexer.setFont(bold, QsciLexerLua.Keyword)
        self.lua_lexer.setFont(bold, QsciLexerLua.Operator)


        self.setPaper(QColor(red))
        # Text Editor Background Color
        
        #lexer.setDefaultPaper(QColor("#E31815"))

        # Text Editor Font Color 
        self.lua_lexer.setColor(QColor(gold), QsciLexerLua.Default)
        

        # Comments
        self.lua_lexer.setColor(QColor("#851764"), QsciLexerLua.Comment)
        
        self.lua_lexer.setColor(QColor("#C5EBCA"), QsciLexerLua.LineComment)
        
        self.lua_lexer.setColor(QColor("#B0D2F3"), QsciLexerLua.Number)

        #Numbers
        self.lua_lexer.setColor(QColor("#00BBFF"), QsciLexerLua.Keyword)

        # Strings
        # "for, if, while, etc"
        self.lua_lexer.setColor(QColor("#FFFFFF"), QsciLexerLua.String)
        #Inside Quotes
        self.lua_lexer.setColor(QColor("#000000"), QsciLexerLua.Character)
        self.lua_lexer.setColor(QColor("#CE9178"), QsciLexerLua.LiteralString)
        self.lua_lexer.setColor(QColor("#FFFFFF"), QsciLexerLua.UnclosedString)

        # Operators
        self.lua_lexer.setColor(QColor(blue), QsciLexerLua.Operator)

        # Identifiers

        # Identifier Foreground (Normal Text, Print, etc)
        self.lua_lexer.setColor(QColor(gold), QsciLexerLua.Identifier)

        self.setLexer(self.lua_lexer)
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
        self.setAutoCompletionUseSingle(QsciScintilla.AutoCompletionUseSingle.AcusAlways) # Single Suggestion Only
        self.setAutoCompletionThreshold(1) # Trigger Quickly
        self.setAutoIndent(True)
        
        # AutoComplete & Brace Matching
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionThreshold(1) # Trigger After 1 Characters

        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        self.setAutoIndent(True)
        self.setIndentationWidth(4)
        self.setTabWidth(4)
        self.setTabIndents(True)

    def set_language(self, language):
        if language == "lua":
            self.setLexer(self.lua_lexer)
        elif language == "python":
            self.setLexer(self.python_lexer)
        
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