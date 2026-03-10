# ------------------- OUTPUT_CONSOLE.PY----------------
from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor

from language_runner import LanguageRunner

import subprocess
import os

class CommandThread(QThread):
    output = pyqtSignal(str)

    def __init__(self, command, cwd):
        super().__init__()
        self.command = command 
        self.cwd = cwd

    def run(self):
        """Run the Command and Emit Output Line By Line"""
        proc = subprocess.Popen(
            self.command,
            shell=True,
            cwd=self.cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Capture stdout
        for line in proc.stdout:
            self.output.emit(line.rstrip())
        # Capture stderr
        for line in proc.stderr:
            self.output.emit(line.rstrip())
        proc.wait()

class OutputConsole(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(False)
        # Track Working Directory
        self.cwd = os.getcwd()
        self.setStyleSheet("background-color: #234EB3; color: #F2BC71; border: 1px solid #444; font-size: 14pt;")
        self.setMaximumHeight(100)

        # Show Initial Prompt
        self.prompt()

        # Language Runner
        self.runner = LanguageRunner()
        self.language = "lua" # Default Language
        self.runner.lua_runtime = getattr(self, "lua_runtime", None)
        self.runner.canvas = getattr(self, "lua_runtime", None)

    def prompt(self):
        """Show Terminal Prompt"""
        self.appendPlainText(f"{self.cwd} $ ")
        self.moveCursor(QTextCursor.MoveOperation.End)

    def log(self, text):
        """Append Text to the Output Console"""
        self.appendPlainText(text)
        self.moveCursor(QTextCursor.MoveOperation.End)

    def clear_console(self):
        self.clear()

    def keyPressEvent(self, event):
        """Capture Enter key to Run Commands"""

        if event.key() == 16777220: # Enter Key
            cursor = self.textCursor()
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)

            line = cursor.selectedText()

            # Remove Prompt Text
            command = line.split("$ ", 1)[-1]

            self.run_terminal_command(command.strip())
        else:
            super().keyPressEvent(event)
    
    def run_terminal_command(self, command):

        if command == "":
            self.prompt()
            return
        
        # ---- Handle CD Manually ----
        if command.startswith("cd"):

            parts = command.split()

            if len(parts) > 1:
                new_path = os.path.abspath(os.path.join(self.cwd, parts[1]))

                if os.path.isdir(new_path):
                    self.cwd = new_path
                else:
                    self.log("Directory Not Found")

            self.prompt()
            return
        
        # ---- Try Lua Execution ----
        if hasattr(self, "runner"):
            output = self.runner.execute(self.language, command, cwd=self.cwd)
            if output:
                self.log(output)   
            self.prompt()
            return
       
        # ---- Run Shell Commands (git, ls, etc) ----
        self.thread = CommandThread(command, self.cwd)
        self.thread.output.connect(self.log)
        self.thread.finished.connect(self.prompt)
        self.thread.start()