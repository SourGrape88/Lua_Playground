# ----SHADER.PY------------------------------------
from PyQt6.QtGui import QColor, QPainter

class ShaderSystem:
    def __init__(self):
        self.effects = []

    def clear(self):
        self.effects.clear()

    def add(self, effect_name, *args):
        self.effects.append((effect_name, args))

    def apply(self, painter, rect):
        """Apply All Effects AFTER World is Drawn"""
        for effect_name, args in self.effects:
            print("Shader:", effect_name, args)

            if effect_name == "darken":
                #intensity = args[0] # 0 to 1

                intensity = max(0.0, min(1.0, args[0]))

                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

                color = QColor(0, 0, 0, int(255 * intensity))
                painter.fillRect(rect, color)

                painter.setPen(QColor(255, 255, 0))
                painter.drawRect(rect)
