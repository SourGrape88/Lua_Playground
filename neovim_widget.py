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

        self.cols = 60
        self.rows = 20

        self.grids = {}
        self.active_grid = 1 # Default to Main Grid
        self.hl_attrs = {}

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
        ])

        start = time.time()
        timeout = 10

        while not os.path.exists(self.pipe_name):
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

            if event_name == "hl_attr_define":

                for attr in event_args:
                    hl_id, info = attr[0], attr[1]

                    fg = QColor(*info.get("foreground_rgb", (220,220,220)))
                    bg = QColor(*info.get("background_rgb", (30,30,30)))

                    self.hl_attrs[hl_id] = (fg, bg)


            elif event_name == "grid_resize":
                self.handle_grid_resize(event_args)

            elif event_name == "grid_line":
                self.handle_grid_line(event_args)

            elif event_name == "grid_cursor_goto":
                grid, row, col = event_args[0]
                self.active_grid = grid
                self.cursor_row = row
                self.cursor_col = col

            elif event_name == "grid_scroll":
                self.handle_grid_scroll(event_args)

            elif event_name == "win_pos":

                grid, win, row, col, width, height = event_args[0]

                if grid in self.grids:
                    self.grids[grid]["row"] = row
                    self.grids[grid]["col"] = col
            
            elif event_name == "win_float_pos":

                grid, win, anchor, row, col, focusable, zindex = event_args[0]

                if grid in self.grids:
                    self.grids[grid]["row"] = int(row)
                    self.grids[grid]["col"] = int(col)

            elif event_name == "grid_clear":
                for grid_id in event_args[0]:
                    grid = self.grids.get(grid_id)
                    if not grid:
                        continue
                    
                    for r in range(grid["height"]):
                        for c in range(grid["width"]):
                            grid["chars"][r][c] = " "

        QMetaObject.invokeMethod(self, "update")


    def handle_grid_resize(self, args):

        for grid_id, width, height in args:

            chars = [[" "] * width for _ in range(height)]

            hl = [[(QColor(220,220,220), QColor(30,30,30))
                  for _ in range(width)] for _ in range(height)]

            self.grids[grid_id] = {
                "chars": chars,
                "hl": hl,
                "width": width,
                "height": height,
                "row": 0,
                "col": 0
            }


    def handle_grid_line(self, args):

        for line in args:

            if len(line) < 4:
                continue

            grid_id, row, col, cells = line[:4]

            grid = self.grids.get(grid_id)
            if not grid:
                continue

            chars = grid["chars"]
            hl = grid["hl"]

            for cell in cells:

                char = cell[0] if len(cell) > 0 else " "
                hl_id = cell[1] if len(cell) > 1 else None
                repeat = cell[2] if len(cell) > 2 else 1

                fg, bg = self.hl_attrs.get(
                    hl_id,
                    (QColor(220,220,220), QColor(30,30,30))
                )

                for _ in range(repeat):

                    if 0 <= row < grid["height"] and 0 <= col < grid["width"]:
                        chars[row][col] = char
                        hl[row][col] = (fg, bg)

                    col += 1


    def handle_grid_scroll(self, args):

        for grid_id, top, bottom, left, right, rows, cols in args:

            grid = self.grids.get(grid_id)
            if not grid:
                continue

            chars = grid["chars"]
            hl = grid["hl"]

            if rows > 0:

                for r in range(bottom-1, top-1, -1):
                    src = r - rows
                    if src >= top:
                        chars[r][left:right] = chars[src][left:right]
                        hl[r][left:right] = hl[src][left:right]

            elif rows < 0:

                for r in range(top, bottom):
                    src = r - rows
                    if src < bottom:
                        chars[r][left:right] = chars[src][left:right]
                        hl[r][left:right] = hl[src][left:right]


    def paintEvent(self, event):

        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(30,30,30))
        painter.setFont(QFont("Cascadia Code", 11))
        metrics = painter.fontMetrics()
        cell_w = metrics.horizontalAdvance("M")
        cell_h = metrics.height()

        for grid in self.grids.values():
            chars = grid["chars"]
            hl = grid["hl"]
            grid_row = grid["row"]
            grid_col = grid["col"]

            # Draw the Text Grid
            for r in range(grid["height"]):
                for c in range(grid["width"]):

                    fg, bg = hl[r][c]

                    x = (grid_col + c) * cell_w
                    y = (grid_row + r) * cell_h
                    painter.fillRect(x, y, cell_w, cell_h, bg)

                    ch = chars[r][c]
                    if ch.strip():
                        painter.setPen(fg)
                        painter.drawText(x, y + cell_h, ch)

            if grid is self.grids.get(self.active_grid):
                painter.fillRect(
                    (grid_col + self.cursor_col) * cell_w,
                    (grid_row + self.cursor_row) * cell_h,
                    cell_w,
                    cell_h,
                    QColor(200,200,255,120)
                )


    def keyPressEvent(self, event):

        key = event.key()
        text = event.text()

        seq = text

        if key in [
            Qt.Key.Key_Backspace,
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter,
            Qt.Key.Key_Tab,
            Qt.Key.Key_Escape
        ]:

            seq = {
                Qt.Key.Key_Backspace: "<BS>",
                Qt.Key.Key_Return: "<CR>",
                Qt.Key.Key_Enter: "<CR>",
                Qt.Key.Key_Tab: "<Tab>",
                Qt.Key.Key_Escape: "<Esc>",
            }[key]

        if hasattr(self, "nvim"):
            self.nvim.async_call(lambda: self.nvim.input(seq))


    def resizeEvent(self, event):

        metrics = self.fontMetrics()

        cell_w = metrics.horizontalAdvance("M")
        cell_h = metrics.height()

        cols = max(10, self.width() // cell_w)
        rows = max(5, self.height() // cell_h)

        if hasattr(self, "nvim") and (cols != self.cols or rows != self.rows):

            self.cols = cols
            self.rows = rows

            self.nvim.async_call(
                lambda: self.nvim.ui_try_resize(cols, rows)
            )

        return super().resizeEvent(event)