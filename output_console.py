# ------------------- OUTPUT_CONSOLE.PY----------------
from PyQt6.QtWidgets import QPlainTextEdit

class OutputConsole(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumHeight(100)

    def log(self, text):
        self.appendPlainText(text)