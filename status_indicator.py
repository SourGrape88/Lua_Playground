# --------- STATUS_INDICATOR.PY ------------
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QMovie

class StatusIndicator(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create Status Indicator
        self.setMinimumWidth(80)
        self.setFixedSize(64, 64)
        self.setScaledContents(True)
        
        self.idle_icon = QMovie("assets/status_light/Idle_Status_Light.gif") # Idle GIF
        self.run_icon = QMovie("assets/status_light/Running_Status_Light.gif") # Running GIF
        self.run_icon.setSpeed(50)
        self.finished_icon = QMovie("assets/status_light/Finished_Status_Light.gif") # Finished GIF
        self.error_icon = QMovie("assets/status_light/Error_Status_Light.gif")
        
        # Start with Idle Animation
        self.setMovie(self.idle_icon)
        self.idle_icon.start()

    def set_idle(self):
        self.setMovie(self.idle_icon)
        self.idle_icon.start()

    def set_running(self):
        self.setMovie(self.run_icon)
        self.run_icon.start()

    def set_finished(self):
        self.setMovie(self.finished_icon)
        self.finished_icon.start()

    def set_error(self):
        self.setMovie(self.error_icon)
        self.error_icon.start()