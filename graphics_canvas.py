# ---------CANVAS (GRAPHICS) ------------------------------------

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import QTimer, Qt

class Canvas(QWidget):

    def __init__(self, lua):
        super().__init__()
        self.lua = lua
        
        # For Print Output
        self.messages = []

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

    # -------------DRAW COMMAND FUNCTIONS ------------------
    # Circle() Function
    def draw_circle(self, x, y, r, color=(100, 200, 255)):
        """Add a Circle Command to the Draw List"""
        if color is None:
            color = (100, 200, 255)
        elif hasattr(color, 'values'):
            color = tuple(color.values())
        self.lua_draw_commands.append(("circle", x, y, r, color))

    # Rect() Function
    def draw_rect(self, x, y, w, h, color=(150, 70, 100)):
        """Add a Rectangle Command to the Draw List"""
        if color is None:
            color = (255, 20, 50)
        elif hasattr(color, 'values'):
            color = tuple(color.values())
        self.lua_draw_commands.append(("rect", x, y, w, h, color))

    # Cls() (Clear Screen) Function
    def cls(self):
        """Clear All draw commands for the next frame"""
        self.draw_commands.clear()
        self.lua_draw_commands.clear()

    def print_to_canvas(self, text, color=Qt.GlobalColor.white):
        """Display messages on the canvas"""
        # You can maintain a list of strings for display
        self.messages.append((str(text), color))
        # optionally store color for each line
        self.update()  # trigger paintEvent

    def update_frame(self):

        """The Update Function"""

        # Demo Animation (moving circle)
        #self.x += self.dx
        # Bounce if it hits left or right edge of screen
        #if self.x < 200 or self.x > 500:
          #self.dx = -self.dx

        # Game Loop Functions
        lua_globals = self.lua.globals()
        lua_init = getattr(self.lua.globals(), "_init", None)
        lua_update = getattr(self.lua.globals(), "_update", None)
        lua_draw = getattr(self.lua.globals(), "_draw", None)

        # Run _init() if it exists
        if not hasattr(self, "_init_ran") and lua_init:
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

        # Add Python Demo Shapes
        #self.draw_commands.append(("circle", self.x, 200, 40, (100, 200, 255)))
        #self.draw_commands.append(("rect", 100, 300, 60, 60, (150, 70, 100)))

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

        # Draw printed messages
        y = 20
        for msg, color in self.messages[-20:]:  # show last 20 lines
            painter.setPen(QColor(color))
            painter.drawText(10, y, msg)
            y += 20