# ---- App.Py (The Entry Point)

import sys
from PyQt6.QtWidgets import QApplication
from styling import apply_style
from window import MainWindow

app = QApplication(sys.argv)
apply_style(app)
window = MainWindow()
window.show()
sys.exit(app.exec())
