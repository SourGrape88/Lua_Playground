import pynvim
import threading
import subprocess
import os
import time

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QMetaObject


class NeovimWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.rows = 20
        self.cols = 60

        self.grid = [[" "] * self.cols for _ in range(self.rows)]

        self.cursor_row = 0
        self.cursor_col = 0

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.pipe_name = r"\\.\pipe\my_nvim" + str(os.getpid())

        self._start_nvim()

    def _start_nvim(self):

        nvim_exe = r"C:\Users\Owner\scoop\apps\neovim\current\bin\nvim.exe"
        init_lua = r"C:\Users\Owner\Desktop\Projects\Lua_Playground\nvim_config\init_min.lua"
        subprocess.Popen([
            nvim_exe,
            "--headless",
            "--listen", self.pipe_name,
            "-u", init_lua
        ]) #creationflags=subprocess.CREATE_NEW_CONSOLE)

        start = time.time()
        timeout = 10
        while not os.path.exists(rf"\\.\pipe\my_nvim{os.getpid()}"):
            if time.time() - start > timeout:
                raise RuntimeError("Neovim pipe not created in time!")
            time.sleep(0.05)

        self.nvim = pynvim.attach("socket", path=self.pipe_name)

        self.nvim.ui_attach(
            self.cols,
            self.rows,
            rgb=True,
            ext_linegrid=True,
            ext_hlstate=True
        )

        # Run_loop in a seperaet thread
        threading.Thread(
            target=lambda: self.nvim.run_loop(
            request_cb=None,
            notification_cb=self.nvim_notification
        ),
        daemon=True
        ).start()

    def nvim_notification(self, name, args):

        if name != "redraw":
            return

        for event in args:

            event_name = event[0]
            event_args = event[1:]
            
            if event_name not in ("grid_line", "hl_attr_define", "grid_cursor_goto", "grid_clear"):
                #print("Event:", event_name, event_args)
                pass
            if event_name == "grid_line":
                self.handle_grid_line(event_args)

            elif event_name == "grid_cursor_goto":
                grid, row, col = event_args[0]
                self.cursor_row = row
                self.cursor_col = col

            elif event_name == "grid_clear":
                self.grid = [[" "] * self.cols for _ in range(self.rows)]

            else:
                pass  # e.g., hl_attr_define, option_set, default_colors_set, etc.

        QMetaObject.invokeMethod(self, "update")

    def handle_grid_line(self, args):

       for line in args:  # each line is [grid, row, col, cells]
            if len(line) < 4:
                continue  # skip malformed lines 
            
            
            grid_id, row, col, cells = line[:4]

            for cell in cells:

                char = str(cell[0]) if len(cell) > 0 else " "
                repeat = cell[2] if len(cell) > 2 else 1

                for _ in range(repeat):

                    if 0 <= row < self.rows and 0 <= col < self.cols:
                        self.grid[row][col] = char

                    col += 1

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(30,30,30))  # background
        font = QFont("Cascadia Code", 11)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        cell_w = metrics.horizontalAdvance("M")
        cell_h = metrics.height()

        for r in range(self.rows):
            for c in range(self.cols):
                char = self.grid[r][c]
                if char.strip() != "":
                    painter.setPen(QColor(220,220,220))
                    painter.drawText(c*cell_w, (r+1)*cell_h, char)

        # cursor
        painter.fillRect(self.cursor_col*cell_w, self.cursor_row*cell_h, cell_w, cell_h, QColor(200,200,255,120))

    def keyPressEvent(self, event):
        key = event.key()
        text = event.text()
        seq = text  # basic
        if key in [Qt.Key.Key_Backspace, Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Tab, Qt.Key.Key_Escape]:
            seq = {
                Qt.Key.Key_Backspace: "<BS>",
                Qt.Key.Key_Return: "<CR>",
                Qt.Key.Key_Enter: "<CR>",
                Qt.Key.Key_Tab: "<Tab>",
                Qt.Key.Key_Escape: "<Esc>",
            }[key]
        if hasattr(self, 'nvim'):
            self.nvim.async_call(lambda seq=seq: self.nvim.input(seq))


    def resizeEvent(self, event):
        font = QFont("Cascadia Code", 11)
        metrics = self.fontMetrics()
        cell_w = metrics.horizontalAdvance("M")
        cell_h = metrics.height()

        # calculate new cols/rows
        new_cols = max(10, min(200, self.width() // cell_w))
        new_rows = max(5, min(100, self.height() // cell_h))

        # only resize Neovim if it actually changed
        if hasattr(self, "nvim") and (new_cols != self.cols or new_rows != self.rows):
            self.cols = new_cols
            self.rows = new_rows
            
            # Resize the grid to avoid IndexError
            old_grid =self.grid

            self.grid = [[" "] * self.cols for _ in range(self.rows)]
            for r in range(min(len(old_grid), self.rows)):
                for c in range(min(len(old_grid[0]), self.cols)):
                    self.grid[r][c] = old_grid[r][c]
            
            try:
                def resize_and_redraw():
                    self.nvim.ui_try_resize(self.cols, self.rows)
                    self.nvim.redraw()  # <-- force immediate redraw
                self.nvim.async_call(resize_and_redraw)
            except Exception as e:
                print("Resize failed:", e)

        return super().resizeEvent(event)
