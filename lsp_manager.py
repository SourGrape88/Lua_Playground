# --------LSP_MANAGER.PY---------------------
import subprocess
import json
import threading
import queue
import os

class LSPClient:
    """
    A lightweight JSON-RPC client for interacting with a Language Server (LSP).
    Supports async reads from stdout and sending requests to the server.
    """

    def __init__(self, cmd):
        """
        cmd: list[str] - command to start the LSP server, e.g.,
        ["lua-language-server", "-E", "main.lua"] or ["pyright-langserver", "--stdio"]
        """
        self.cmd = cmd
        self.proc = None
        self.msg_id = 0
        self.pending = {}
        self.queue = queue.Queue()
        self.lock = threading.Lock()

    def start(self):
        """Start the LSP Server as a Subprocess"""
        print("Starting LSP:", self.cmd)
        self.proc = subprocess.Popen(
            self.cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0
        )
        threading.Thread(target=self._read_loop, daemon=True).start()
        self.initialize()

    def _read_loop(self):
        """Read LSP Server Output Asynchronously and Push Response to Queue"""
        while True:
            line = self.proc.stdout.readline()
            if not line:
                break
            line = line.decode("utf-8").strip()
            if line.startswith("Content-Length:"):
                length = int(line.split(":")[1])
                self.proc.stdout.read(2) # Skip \r\n
                body = self.proc.stdout.read(length).decode("utf-8")
                data = json.loads(body)
                
                print("LSP Message:", data)
                
                self.queue.put(data)

    def initialize(self):
        """Send the 'initialize' request to the LSP Server"""
        req = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "processId": os.getpid(),
                "rootUri": None,
                "capabilities": {},
            }
        }
        self.send(req)

    def _next_id(self):
        with self.lock:
            self.msg_id += 1
            return self.msg_id
        
    def send(self, msg):
        """Send A JSON-RPC Message to the LSP Server"""
        body = json.dumps(msg)
        content = f"Content-Length: {len(body)}\r\n\r\n{body}"
        self.proc.stdin.write(content.encode("utf-8"))
        self.proc.stdin.flush()

    def request_completion(self, text, line, character):
        """Send a Completion Request"""
        req = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "textDocument/completion",
            "params": {
                "textDocument": {"uri": "file://dummy.lua"},
                "position": {"line": line, "character": character},
                "context": {"triggerKind": 1}
            }
        }
        self.send(req)

    def get_response(self, timeout=0.1):
        """Non-Blocking get from the Response Queue"""
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None
