import pynvim
import subprocess
import threading
import os
import time

class NvimClient:

    def __init__(self, pipe_name, notification_cb):

        self.pipe_name = pipe_name
        self.notification_cb = notification_cb

        self.nvim = None

    def start(self, cols, rows, init_lua):
        self.cols = cols
        self.rows = rows


        nvim_exe = r"C:\Users\Owner\scoop\apps\neovim\current\bin\nvim.exe"
        #init_lua = r"C:\Users\Owner\Desktop\Projects\Lua_Playground\nvim_config\init_min.lua"

        subprocess.Popen([
            nvim_exe,
            "--headless",
            "--listen", self.pipe_name,
            "-u", init_lua
        ])

        start = time.time()
        timeout = 10

        while not os.path.exists(self.pipe_name):
            if time.time() - start > timeout:
                raise RuntimeError("Neovim pipe not created in time!")
            time.sleep(0.05)

        self.nvim = pynvim.attach("socket", path=self.pipe_name)

        self.nvim.ui_attach(
            cols,
            rows,
            rgb=True,
            ext_linegrid=True,
            ext_hlstate=True
        )

        threading.Thread(
            target=lambda: self.nvim.run_loop(
                request_cb=None,
                notification_cb=self.notification_cb
            ),
            daemon=True
        ).start()

    def input(self, seq):
        if self.nvim:
            self.nvim.async_call(lambda: self.nvim.input(seq))

    def resize(self, cols, rows):
        if self.nvim:
            self.nvim.async_call(lambda: self.nvim.ui_try_resize(cols, rows)) 