from PyQt6.QtGui import QColor 

class GridModel:

    def __init__(self):
        self.default_fg = QColor(20, 20, 220)
        self.default_bg = QColor(140, 30, 30)

        self.grids = {}
        self.active_grid = 1 # Default to Main Grid
        self.hl_attrs = {}

        self.cursor_row = 0
        self.cursor_col = 0


    def rgb_int_to_qcolor(self, value):
        if value is None:
            return None
        r = (value >> 16) & 0xFF
        g = (value >> 8) & 0xFF
        b = value & 0xFF
        return QColor(r, g, b)
    
    