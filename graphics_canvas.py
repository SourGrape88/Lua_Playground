# ---------CANVAS (GRAPHICS) ------------------------------------

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import QTimer

class Canvas(QWidget):

    def __init__(self, lua):
        super().__init__()
        self.lua = lua
        # Position of the animated circle
        self.x = 300
        # Speed of the Circle
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

    # -------------DRAW COMMAND FUNCTIONS ------------------
    def draw_circle(self, x, y, r, color=(100, 200, 255)):
        """Add a Circle Command to the Draw List"""
        if color is None:
            color = (100, 200, 255)
        elif hasattr(color, 'values'):
            color = tuple(color.values())
        self.lua_draw_commands.append(("circle", x, y, r, color))

    def draw_rect(self, x, y, w, h, color=(150, 70, 100)):
        """Add a Rectangle Command to the Draw List"""
        if color is None:
            color = (255, 20, 50)
        elif hasattr(color, 'values'):
            color = tuple(color.values())
        self.lua_draw_commands.append(("rect", x, y, w, h, color))

    # ------------------------------------------------------------

    def update_frame(self):

        """The Update Function"""

        # Demo Animation (moving circle)
        self.x += self.dx
        # Bounce if it hits left or right edge of screen
        if self.x < 200 or self.x > 500:
          self.dx = -self.dx

        # Clear Previous Frame's Commands
        self.draw_commands.clear()
        #self.lua_draw_commands.clear()

        # --- Call Lua Update() If it Exists -------
        lua_update = getattr(self.lua.globals(), "update", None)
        if lua_update:
            try:
                lua_update()
            except Exception as e:
                print(f"Lua Update Error: {e}")

        # Add Python Demo Shapes
        self.draw_commands.append(("circle", self.x, 200, 40, (100, 200, 255)))
        self.draw_commands.append(("rect", 100, 300, 60, 60, (150, 70, 100)))

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
            # If the first command in line is Circle...
            if cmd[0] == "circle":
                _, x, y, r, color = cmd
                painter.setBrush(QColor(*color))
                painter.drawEllipse(x, y, r, r)

            elif cmd[0] == "rect":
                _, x, y, w, h, color = cmd
                painter.setBrush(QColor(*color))
                painter.drawRect(x, y, w, h)