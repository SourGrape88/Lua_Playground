# ---------NEOVIM_WIDGET.PY--------------------

# Test Commit 1

import os

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QMetaObject

from grid_model import GridModel
from redraw_handler import RedrawHandler
from nvim_client import NvimClient

class NeovimWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.model = GridModel()
        self.redraw = RedrawHandler(self.model)

        self.cols = 60
        self.rows = 20

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.pipe_name = r"\\.\pipe\my_nvim" + str(os.getpid())

        self.nvim_client = NvimClient(
            self.pipe_name,
            self.nvim_notification
        )

        init_lua = r"C:\Users\Owner\Desktop\Projects\Lua_Playground\nvim_config\init_min.lua"

        self.nvim_client.start(
            self.cols,
            self.rows,
            init_lua
        )

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

                    fg = self.model.rgb_int_to_qcolor(fg_val) if fg_val is not None else self.model.default_fg
                    bg = self.model.rgb_int_to_qcolor(bg_val) if bg_val is not None else self.model.default_bg

                    self.model.hl_attrs[hl_id] = (fg, bg)


            elif event_name == "grid_resize":
                self.redraw.handle_grid_resize(event_args)

            elif event_name == "grid_line":
                self.redraw.handle_grid_line(event_args)

            elif event_name == "grid_cursor_goto":
                grid, row, col = event_args[0]
                self.model.active_grid = grid
                self.model.cursor_row = row
                self.model.cursor_col = col

            elif event_name == "grid_scroll":
                self.redraw.handle_grid_scroll(event_args)

            elif event_name == "win_pos":

                grid, win, row, col, width, height = event_args[0]

                if grid in self.model.grids:
                    self.model.grids[grid]["row"] = row
                    self.model.grids[grid]["col"] = col
            
            elif event_name == "win_float_pos":

                grid, win, anchor, row, col, focusable, zindex = event_args[0]

                if grid in self.model.grids:
                    self.model.grids[grid]["row"] = int(row)
                    self.model.grids[grid]["col"] = int(col)

            elif event_name == "default_colors_set":

                fg, bg, sp, *_ = event_args[0]

                if fg is not None:
                    self.model.default_fg = self.model.rgb_int_to_qcolor(fg)

                if bg is not None:
                    self.model.default_bg = self.model.rgb_int_to_qcolor(bg)
                
            elif event_name == "hl_group_set":

                for group in event_args:
                    name = group[0]
                    hl_id = group[1]

                    # Optional but useful for debugging
                    # print("HL group:", name, "->", hl_id)

            elif event_name == "grid_clear":
                for grid_id in event_args[0]:
                    grid = self.model.grids.get(grid_id)
                    if not grid:
                        continue
                    
                    for r in range(grid["height"]):
                        for c in range(grid["width"]):
                            grid["chars"][r][c] = " "

        QMetaObject.invokeMethod(self, "update")

    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.model.default_bg)
        painter.setFont(QFont("Cascadia Code", 11))
        metrics = painter.fontMetrics()
        cell_w = metrics.horizontalAdvance("M")
        cell_h = metrics.height()

        for grid in self.model.grids.values():
            chars = grid["chars"]
            hl = grid["hl"]
            grid_row = grid["row"]
            grid_col = grid["col"]

            # Draw the Text Grid
            for r in range(grid["height"]):
                buf_row = r
                if buf_row >= len(chars):
                    break
                for c in range(grid["width"]):
                    char = chars[buf_row][c]
                    fg, bg = hl[buf_row][c]
                    x = c * cell_w
                    y = r * cell_h
                    painter.fillRect(x, y, cell_w, cell_h, bg)
                    painter.setPen(fg)
                    painter.drawText(x, y + cell_h, char)   

            # Draw cursor
            if grid is self.model.grids.get(self.model.active_grid):
                cursor_x = self.model.cursor_col
                cursor_y = self.model.cursor_row - grid_row  # offset in viewport
                if 0 <= cursor_y < grid["height"]:
                    painter.fillRect(
                        cursor_x * cell_w,
                        cursor_y * cell_h,
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

        
        self.nvim_client.input(seq)


    def resizeEvent(self, event):

        metrics = self.fontMetrics()

        cell_w = metrics.horizontalAdvance("M")
        cell_h = metrics.height()

        cols = max(10, self.width() // cell_w)
        rows = max(5, self.height() // cell_h)

        if cols != self.cols or rows != self.rows:

            self.cols = cols
            self.rows = rows

            self.nvim_client.resize(cols, rows)

        return super().resizeEvent(event)