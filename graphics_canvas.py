# ---------CANVAS (GRAPHICS) ------------------------------------

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import QTimer, Qt

class Canvas(QWidget):

    def __init__(self, lua):
        super().__init__()
        self.lua = lua
        
        # Demo Python State
        self.x = 300
        self.dx = 2

        # List of Draw Commands
        self.draw_commands = []
        # List of Lua Commands
        self.lua_draw_commands = []

        # Create a Timer that Fires Repeatedly
        self.timer = QTimer()
        # Connect the timer to our Update Function
        self.timer.timeout.connect(self.update_frame)
        # Start Timer at ~60 FPS
        self.timer.start(16)

        self._init_ran = False

    def add_draw_command(self, cmd):
        """Called by Lua Helper Functions to Queue a Command"""
        self.lua_draw_commands.append(cmd)

    def cls(self):
        self.draw_commands.clear()
        self.lua_draw_commands.clear()

    def update_frame(self):
        """The Update Function"""

        # Game Loop Functions
        lua_globals = self.lua.globals()
        lua_init = getattr(self.lua.globals(), "_init", None)
        lua_update = getattr(self.lua.globals(), "_update", None)
        lua_draw = getattr(self.lua.globals(), "_draw", None)

        # Run _init() if it exists
        if not self._init_ran and lua_init:
            try:
                lua_init()
            except Exception as e:
                print(f"Lua _init() Error: {e}")
            self._init_ran = True

        # Clear Previous Frame's Commands
        self.cls()
        #self.lua_draw_commands.clear()

        # --- Call Lua Update() If it Exists -------
        if lua_update:
            try:
                lua_update()
            except Exception as e:
                print(f"Lua _update Error: {e}")

        # --- Call Lua Draw() If it Exists -------
        if lua_draw:
            try:
                lua_draw()
            except Exception as e:
                print(f"Lua _draw() Error: {e}")

        # Add Lua Shapes
        self.draw_commands.extend(self.lua_draw_commands)

        # Update Frame/Trigger Frame Repaint
        self.update()

    def paintEvent(self, event):
        """Draw All Commands"""
        # Called Whenever the Widget needs to Redraw
        painter = QPainter(self)

        # Draw Background
        painter.fillRect(self.rect(), QColor(30, 30, 30))

        # Loop through all Draw Commands
        for cmd in self.draw_commands:
            kind = cmd[0]
            # If the first command in line is Circle...
            
            try:
                painter.save()

                if kind == "circle":
                    _, x, y, r, color, thickness = cmd
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    pen = painter.pen()
                    pen.setColor(QColor(*color))
                    pen.setWidth(thickness)
                    painter.setPen(pen)
                    painter.drawEllipse(x, y, r, r)
                    
                elif kind == "circlefill":
                    _, x, y, r, color = cmd
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QColor(*color))
                    painter.drawEllipse(x - r, y - r,2*r,2*r)

                elif kind == "rect":
                    _, x, y, w, h, color, thickness = cmd
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    pen = painter.pen()
                    pen.setColor(QColor(*color))
                    pen.setWidth(thickness)
                    painter.setPen(pen)
                    painter.drawRect(x, y, w, h)

                elif kind == "rectfill":
                    _, x, y, w, h, color = cmd
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QColor(*color))
                    painter.drawRect(x, y, w, h)

                elif kind == "line":
                    _, x1, y1, x2, y2, color, thickness = cmd
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    pen = painter.pen()
                    pen.setColor(QColor(*color))
                    pen.setWidth(thickness)
                    painter.setPen(pen)
                    painter.drawLine(x1, y1, x2, y2)

                elif kind in ("text", "print"):
                    _, text, x, y, color, size = cmd
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    pen = painter.pen()
                    pen.setColor(QColor(*color))
                    painter.setPen(pen)
                    font = painter.font()
                    font.setPointSize(size)
                    painter.setFont(font)
                    painter.drawText(x, y, text)
                else:
                    print("Warning: invalid draw command tuple:", cmd)
            
            except Exception as e:
                print(f"Painter error for command {cmd}: {e}")

            finally:
                painter.restore()
            
            
