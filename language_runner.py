# ---- LANGUAGE_RUNNER.PY -----
import subprocess
import os
import io
import contextlib

class LanguageRunner:
    def __init__(self):
        self.languages = {
            "lua": self.run_lua,
            "python": self.run_python,
        }
        self.lua_runtime = None
        self.canvas = None

    def execute(self, language: str, code: str, cwd: str = None):
        """Run Code in Given Language and Return Output"""
        if language in self.languages:
            return self.languages[language](code, cwd)
        else:
            return f"Language '{language}' not supported."
        
    # --- Lua Execution ---
    def run_lua(self, code: str, cwd: str = None):
        if self.lua_runtime is None:
            return "Lua runtime not initialized."
        try:
            self.lua_runtime.execute(
                'package.path = package.path .. ";C:/Users/Owner/Desktop/Projects/Lua_Playground/?.lua"')
            result = self.lua_runtime.execute(code)
            return str(result) if result else ""
        except Exception as e:
            return f"Lua Error: {e}"
        
    # -- Python Execution ---
    def run_python(self, code: str, cwd: str = None):
        local_namespace = {"canvas": self.canvas}
        stdout = io.StringIO()
        stderr = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exec(code, {}, local_namespace)
        except Exception as e:
            stderr.write(f"Python Error: {e}\n")
        return stdout.getvalue() + stderr.getvalue()


