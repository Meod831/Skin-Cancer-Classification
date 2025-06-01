import os
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class ImageProcessor:
    @staticmethod
    def load_and_scale_image(file_path, width, height):
        if os.path.exists(file_path):
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                return None
            return pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return None
