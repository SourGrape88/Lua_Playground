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

        self.default_fg = QColor(20, 20, 220)
        self.default_bg = QColor(140, 30, 30)

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
                    hl_id = attr[0]
                    rgb_attr = attr[1]

                    fg_val = rgb_attr.get("foreground")
                    bg_val = rgb_attr.get("background")

                    fg = self.rgb_int_to_qcolor(fg_val) if fg_val is not None else self.default_fg
                    bg = self.rgb_int_to_qcolor(bg_val) if bg_val is not None else self.default_bg

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

            elif event_name == "default_colors_set":

                fg, bg, sp, *_ = event_args[0]

                if fg is not None:
                    self.default_fg = self.rgb_int_to_qcolor(fg)

                if bg is not None:
                    self.default_bg = self.rgb_int_to_qcolor(bg)
                
            elif event_name == "hl_group_set":

                for group in event_args:
                    name = group[0]
                    hl_id = group[1]

                    # Optional but useful for debugging
                    # print("HL group:", name, "->", hl_id)

            elif event_name == "grid_clear":
                for grid_id in event_args[0]:
                    grid = self.grids.get(grid_id)
                    if not grid:
                        continue
                    
                    for r in range(grid["height"]):
                        for c in range(grid["width"]):
                            grid["chars"][r][c] = " "

        QMetaObject.invokeMethod(self, "update")


    def rgb_int_to_qcolor(self, value):
        if value is None:
            return None
        r = (value >> 16) & 0xFF
        g = (value >> 8) & 0xFF
        b = value & 0xFF
        return QColor(r, g, b)

    def handle_grid_resize(self, args):

        for grid_id, width, height in args:

            chars = [[" "] * width for _ in range(height)]

            hl = [[(self.default_fg, self.default_bg)
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
            #if len(line) < 4:
                #continue

            grid_id, row, col, cells = line[:4]
            grid = self.grids.get(grid_id)
            if not grid:
                continue

            chars = grid["chars"]
            hl = grid["hl"]

            current_col = col
            last_hl_id = None

            for cell in cells:
                char = cell[0] if len(cell) > 0 else " "
                hl_id = cell[1] if len(cell) > 1 else last_hl_id
                repeat = cell[2] if len(cell) > 2 else 1

                last_hl_id = hl_id
                fg, bg = self.hl_attrs.get(
                    hl_id,
                    (self.default_fg, self.default_bg)
                )

                for i in range(repeat):
                    c_pos = current_col + i
                    if 0 <= row < grid["height"] and 0 <= c_pos < grid["width"]:
                        #display_char = char if char else " "
                        chars[row][c_pos] = char
                        hl[row][c_pos] = (fg, bg)

                current_col += repeat
                print("HL ID:", hl_id)

    def handle_grid_scroll(self, args):
       for grid_id, top, bottom, left, right, rows, cols in args:
        grid = self.grids.get(grid_id)
        if not grid:
            continue

        chars = grid["chars"]
        hl = grid["hl"]

        width = right - left
        height = bottom - top

        # Scroll Rows
        if rows > 0:  # scroll down
            for r in range(bottom - 1, top - 1, -1):
                src = r - rows
                if top <= src < bottom:
                    chars[r][left:right] = chars[src][left:right].copy()
                    hl[r][left:right] = hl[src][left:right].copy()
                else:
                    chars[r][left:right] = [" "] * width
                    hl[r][left:right] = [(self.default_fg, self.default_bg)] * width

        elif rows < 0:  # scroll up
            for r in range(top, bottom):
                src = r - rows
                if top <= src < bottom:
                    chars[r][left:right] = chars[src][left:right].copy()
                    hl[r][left:right] = hl[src][left:right].copy()
                else:
                    chars[r][left:right] = [" "] * width
                    hl[r][left:right] = [(self.default_fg, self.default_bg)] * width 
    
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.default_bg)
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
                    char = chars[r][c]
                    fg, bg = hl[r][c]
                    x = (grid_col + c) * cell_w
                    y = (grid_row + r) * cell_h
                    painter.fillRect(x, y, cell_w, cell_h, bg)
                    painter.setPen(fg)
                    painter.drawText(x, y + cell_h, char)   

            # Draw cursor
            if grid is self.grids.get(self.active_grid):
                painter.fillRect(
                    (grid_col + self.cursor_col) * cell_w,
                    (grid_row + self.cursor_row) * cell_h,
                    cell_w,
                    cell_h,
                    QColor(200, 200, 255, 120)
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