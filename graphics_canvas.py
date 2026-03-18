# ---------CANVAS (GRAPHICS) ------------------------------------

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPixmap
from PyQt6.QtCore import QTimer, Qt

class Canvas(QWidget):

    def __init__(self, lua):
        super().__init__()
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()
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

        # Store Sprites and Animations
        self.assets = {}

        # Store Animation FPS
        self.frame_count = 0

        # Key Inputs
        self.QT_KEY_MAP = {
            "a": Qt.Key.Key_A,
            "d": Qt.Key.Key_D,
            "w": Qt.Key.Key_W,
            "s": Qt.Key.Key_S,
            "space": Qt.Key.Key_Space,
            "left": Qt.Key.Key_Left,
            "right": Qt.Key.Key_Right,
            "up": Qt.Key.Key_Up,
            "down": Qt.Key.Key_Down,
        }

        self.keys_down = set()
        self.keys_pressed = set()

        self._init_ran = False

    def add_draw_command(self, cmd):
        """Called by Lua Helper Functions to Queue a Command"""
        self.lua_draw_commands.append(cmd)

    def load_sprite(self, name, file_path):
        """Load Sprite and store it in self.sprites = {}"""
        pixmap = QPixmap(file_path)
        
        if pixmap.isNull():
            print(f"Failed to load sprite: {file_path}")
            return
        
        self.assets[name] = {
            "frames": [pixmap],
            "fps": 0 # 0 = Static Image
        }
        print(f"[Load Sprite] {name} -> {file_path}")
        print("Assets now:", self.assets.keys())

    def load_anim(self, name, file_paths, fps=8):
        frames = []

        for path in file_paths:
            pixmap = QPixmap(path)
            if pixmap.isNull():
                print(f"Failed to load Frame: {path}")
                continue
            frames.append(pixmap)

        if not frames:
            print(f"Animation '{name}' has no valid frames.")
            return
        
        self.assets[name] = {
            "frames": frames,
            "fps": fps
        }
        print(f"[Load Sprite] {name} -> {file_paths}")
        print("Assets now:", self.assets.keys())

    def cls(self):
        self.draw_commands.clear()
        self.lua_draw_commands.clear()

    def btn(self, key):
        qt_key = self.QT_KEY_MAP.get(key.lower()) if isinstance(key, str) else key
        if qt_key is None:
            return False
        return qt_key in self.keys_down

    def btnp(self, key):
        qt_key = self.QT_KEY_MAP.get(key.lower()) if isinstance(key, str) else key
        if qt_key is None:
            return False
        if qt_key in self.keys_pressed:
            self.keys_pressed.remove(qt_key)
            return True
        return False

    def update_frame(self):
        """The Update Function"""

        if hasattr(self, "running_ref") and not self.running_ref():
            return

        # Clear Pressed Keys at the Start of the Frame
        self.keys_pressed.clear()

        # Game Loop Functions
        lua_globals = self.lua.globals()
        lua_init = getattr(self.lua.globals(), "_init", None)
        lua_update = getattr(self.lua.globals(), "_update", None)
        lua_draw = getattr(self.lua.globals(), "_draw", None)

        # Track FPS
        self.frame_count += 1

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

                elif kind == "sprite":
                    if len(cmd) == 4:
                        _, name, x, y = cmd
                        w, h, = -1, -1
                    else:
                        _, name, x, y, w, h = cmd
                        if w is None:
                            w = -1
                        if h is None:
                            h = -1
                    
                    if name not in self.assets:
                        print(F"Missing Asset: {name}")
                        continue

                    asset = self.assets[name]
                    frames = asset["frames"]
                    fps = asset["fps"]

                    # Determin frame
                    if fps > 0:
                        frame_index = (self.frame_count // (60 // fps)) % len(frames)
                    else:
                        frame_index = 0

                    frame_index = (self.frame_count // (60 // fps)) % len(frames) if fps > 0 else 0
                    pixmap = frames[frame_index]

                    if w > 0 and h > 0:
                        painter.drawPixmap(x, y, w, h, pixmap)
                    else:
                        painter.drawPixmap(x, y, pixmap)


            except Exception as e:
                print(f"Painter error for command {cmd}: {e}")

            finally:
                painter.restore()
            
    def mousePressEvent(self, event):
        self.setFocus()
    
    def keyPressEvent(self, event):
        qt_key = event.key() 
        
        if qt_key not in self.keys_down:
            self.keys_pressed.add(qt_key)
        self.keys_down.add(qt_key)

    def keyReleaseEvent(self, event):
        qt_key = event.key()

        self.keys_down.discard(qt_key)
        self.keys_pressed.discard(qt_key) 
