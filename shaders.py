# ----SHADER.PY------------------------------------
from PyQt6.QtGui import QColor, QPainter

class ShaderSystem:
    def __init__(self):
        self.effects = []

    def clear(self):
        self.effects.clear()

    def add(self, effect_name, *args):

        if len(args) >= 2:
            *real_args, duration = args
        else:
            real_args = args
            duration = 1.0

        self.effects.append({
            "name": effect_name,
            "args": real_args,
            "time": duration,
            "max_time": duration})

    def apply(self, painter, rect):
        """Apply All Effects AFTER World is Drawn"""

        new_effects = []

        for effect in self.effects:
            name = effect["name"]
            args = effect["args"]
            time = effect["time"]
            max_time = effect["max_time"]

            life = time / max_time if max_time > 0 else 0

            if name == "darken":
                #intensity = args[0] # 0 to 1

                intensity = max(0.0, min(1.0, args[0])) * life

                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

                color = QColor(0, 0, 0, int(255 * intensity))
                painter.fillRect(rect, color)

                painter.setPen(QColor(255, 255, 0))
                painter.drawRect(rect)

            elif name == "flash":
                # args: intensity (0-1), optional RGB color
                intensity = max(0.0, min(1.0, args[0])) * life

                if len(args) >= 4:
                    r, g, b = args[1], args[2], args[3]
                else:
                    r, g, b = 255, 255, 255 # Default to white Flash

                # Set Blending Mode
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

                color = QColor(r, g, b, int(255 * intensity))
                painter.fillRect(rect, color)

            # UPDATE TIME ----------------------

            effect["time"] -= 1/60 # 60 FPS

            if effect["time"] > 0:
                new_effects.append(effect)

        self.effects = new_effects


