# -----------Code Editor-----------------

from PyQt6.Qsci import QsciScintilla, QsciLexerLua 
from PyQt6.QtGui import QFont, QColor

class LuaEditor(QsciScintilla):
    def __init__(self):
        super().__init__()

        red = "#E31815"
        gold = "#FFC02D"
        blue = "#234EB3"
        #color = "#FFCC5D"

        # Font
        font = QFont("DepartureMono Nerd Font", 16)
        bold = QFont("DepartureMono Nerd Font", 16)
        bold.setBold(True)
        self.setFont(font)
        #self.setMarginsForegroundColor(QColor("#ECA0BE"))
        #self.setMarginsBackgroundColor(QColor("#3C6774"))
        self.setMarginsFont(QFont("FiraMono Nerd Font", 16, QFont.Weight.Bold))

        # Selection Highlight Color
        self.setSelectionBackgroundColor(QColor("#EA7674"))
        self.setSelectionForegroundColor(QColor("#FFFFFF"))

        # Syntax Highlighting
        #editor = QsciScintilla()
        
        # Lexer
        lexer = QsciLexerLua() # Lua Syntax
        lexer.setDefaultFont(font)

        for style in range(128):
            lexer.setFont(font, style)
            lexer.setPaper(QColor(red), style)

        lexer.setFont(bold, QsciLexerLua.Keyword)
        lexer.setFont(bold, QsciLexerLua.Operator)


        self.setPaper(QColor(red))
        # Text Editor Background Color
        
        #lexer.setDefaultPaper(QColor("#E31815"))

        # Text Editor Font Color 
        lexer.setColor(QColor(gold), QsciLexerLua.Default)
        

        # Comments
        lexer.setColor(QColor("#851764"), QsciLexerLua.Comment)
        
        lexer.setColor(QColor("#C5EBCA"), QsciLexerLua.LineComment)
        
        lexer.setColor(QColor("#B0D2F3"), QsciLexerLua.Number)

        #Numbers
        lexer.setColor(QColor("#00BBFF"), QsciLexerLua.Keyword)

        # Strings
        # "for, if, while, etc"
        lexer.setColor(QColor("#FFFFFF"), QsciLexerLua.String)
        #Inside Quotes
        lexer.setColor(QColor("#000000"), QsciLexerLua.Character)
        lexer.setColor(QColor("#CE9178"), QsciLexerLua.LiteralString)
        lexer.setColor(QColor("#FFFFFF"), QsciLexerLua.UnclosedString)

        # Operators
        lexer.setColor(QColor(blue), QsciLexerLua.Operator)

        # Identifiers

        # Identifier Foreground (Normal Text, Print, etc)
        lexer.setColor(QColor(gold), QsciLexerLua.Identifier)

        self.setLexer(lexer)
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