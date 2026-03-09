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
        
        # Store animations in dictionary
        self.gifs = {
        "idle": QMovie("assets/status_light/Idle_Status_Light.gif"), # Idle GIF
        "running": QMovie("assets/status_light/Running_Status_Light.gif"), # Running GIF
        "finished": QMovie("assets/status_light/Finished_Status_Light.gif"), # Finished GIF
        "error": QMovie("assets/status_light/Error_Status_Light.gif")
        }
        
        self.gifs["running"].setSpeed(50)

        self.current_gif = None

        self.set_status("idle")

    def set_status(self, state):
        """This is the Animation Switcher"""

        # Stop the Current Gif
        if self.current_gif:
            self.current_gif.stop()
        
        gif = self.gifs[state]
        self.setMovie(gif)
        gif.start()

        self.current_gif = gif

    def set_idle(self):
        self.set_status("idle")

    def set_running(self):
        self.set_status("running")

    def set_finished(self):
        self.set_status("finished")

    def set_error(self):
        self.set_status("error")