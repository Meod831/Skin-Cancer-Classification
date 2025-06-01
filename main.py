import sys
import os
import csv
import matplotlib
import weakref
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime

from PyQt5 import sip
from PyQt5.QtWidgets import (QApplication, QLabel, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QDesktopWidget, QPushButton, QFrame, QFileDialog,
                             QTableWidget, QTableWidgetItem, QMenu, QAction, QMessageBox, QSizePolicy)
from PyQt5.QtCore import Qt, QRectF, QSize, QTimer, QUrl
from PyQt5.QtGui import QMovie, QPainter, QBrush, QPen, QColor, QPainterPath, QPixmap, QFont, QDesktopServices

from configs.config import MODEL_PATH, CSV_PATH, IMAGES_DIR
from utils.model_manager import ModelManager
from utils.history_manager import HistoryManager
from utils.image_processor import ImageProcessor

class disclaimerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCC App")
        self.setGeometry(100, 100, 800, 500)
        self.setMinimumSize(800, 500)
        

        self.aspect_ratio = 800 / 500
        self.centerBlock()
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.mainLayout = QVBoxLayout()
        self.centralWidget.setLayout(self.mainLayout)
        
        self.model_manager = ModelManager(MODEL_PATH)
        self.history_manager = HistoryManager(CSV_PATH)
        
        self.showDisclaimer()

    def resizeEvent(self, event):

        new_width = event.size().width()
        new_height = event.size().height()
        current_ratio = new_width / new_height
        if abs(current_ratio - self.aspect_ratio) > 0.01:
            if current_ratio > self.aspect_ratio:
                new_width = int(new_height * self.aspect_ratio)
            else:
                new_height = int(new_width / self.aspect_ratio)
            self.resize(new_width, new_height)
        super().resizeEvent(event)

        container_width = round(new_width * 0.75)
        container_height = round(new_height * 0.75)

        x = round((self.width() - container_width) / 2)
        y = round((self.height() - container_height) / 2)
        self.disclaimerContainer.setGeometry(x, y, container_width, container_height)

        margin = 10
        new_x = self.width() - self.helpButton.width() - margin
        new_y = margin
        self.helpButton.move(new_x, new_y)
        self.homeButton.move(new_x, new_y)

        design_container_width = 600  
        design_container_height = 375  


        scale_factor = min(container_width / design_container_width,
                            container_height / design_container_height)

  
        base_button_width = 100
        base_button_height = 40
        base_font_size = 13

        new_button_width = int(base_button_width * scale_factor)
        new_button_height = int(base_button_height * scale_factor)
        new_font_size = max(1, int(base_font_size * scale_factor))  

        if (hasattr(self, 'runButton') and self.runButton is not None and not sip.isdeleted(self.runButton) and 
            hasattr(self, 'recordsButtonMain') and self.recordsButtonMain is not None and not sip.isdeleted(self.recordsButtonMain)):
            self.runButton.setFixedSize(new_button_width, new_button_height)
            self.recordsButtonMain.setFixedSize(new_button_width, new_button_height)

            run_font = self.runButton.font()
            run_font.setPointSize(new_font_size)
            self.runButton.setFont(run_font)

            records_font = self.recordsButtonMain.font()
            records_font.setPointSize(new_font_size)
            self.recordsButtonMain.setFont(records_font)


        base_right_side_width = 270
        base_right_side_height = 350

        if hasattr(self, 'rightSide') and self.rightSide is not None and not sip.isdeleted(self.rightSide):
            new_right_side_width = int(base_right_side_width * scale_factor)
            new_right_side_height = int(base_right_side_height * scale_factor)
            self.rightSide.setFixedSize(new_right_side_width, new_right_side_height)

        self.updateScales()

    def showDisclaimer(self):
        self.clearLayout(self.mainLayout)
        self.setStyleSheet("background-color:rgb(213, 230, 247);")
        
        class roundWidget(QWidget):
            def paintEvent(self, event):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                margin = 2
                rect = self.rect().adjusted(margin, margin, -margin, -margin)
                rectF = QRectF(rect)
                cornerRadius = 50
                path = QPainterPath()
                path.addRoundedRect(rectF, cornerRadius, cornerRadius)
                pen = QPen(QColor(20, 80, 120), 4)
                pen.setJoinStyle(Qt.MiterJoin)
                painter.setPen(pen)
                painter.setBrush(QBrush(Qt.white))
                painter.drawPath(path)
                
        roundContainer = roundWidget(self)
        roundContainer.setGeometry(50, 60, self.width() - 100, self.height() - 120)
        
        self.disclaimerContainer = roundContainer
        containerLayout = QVBoxLayout(roundContainer)
        containerLayout.setAlignment(Qt.AlignCenter)

        label = QLabel(self)
        label.setAlignment(Qt.AlignCenter)
        label.setText("<p style='font-size:16px; background-color:white; margin-bottom:10px; text-align:center;'><b>DISCLAIMER</b><br><br>This app is for informational purposes only and<br>does not replace professional diagnosis or advice.</p>")
        button = QPushButton("I Acknowledge", self)
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(self.checkContinue)
        button.setStyleSheet("QPushButton { background-color: rgb(21, 96, 130); color: white; font-weight: bold; font-size: 15px; margin-top: 15px; min-width: 150px; min-height: 30px; } QPushButton:hover { background-color: rgb(12, 58, 78); }")

        containerLayout.addWidget(label)
        containerLayout.addWidget(button, alignment=Qt.AlignHCenter)
        self.homeButton = QPushButton("Home", self)
        self.homeButton.setCursor(Qt.PointingHandCursor)
        self.homeButton.clicked.connect(self.showHome)
        self.homeButton.setGeometry(735, 20, 37, 37)
        self.homeButton.setStyleSheet("QPushButton { background-color: rgb(21, 96, 130); border-radius: 18px; color: white; font-weight: 800; font-size: 10px; } QPushButton:hover { background-color: rgb(12, 58, 78); }")
        self.helpButton = QPushButton("?", self)
        self.helpButton.setCursor(Qt.PointingHandCursor)
        self.helpButton.clicked.connect(self.showHelp)
        self.helpButton.setGeometry(735, 20, 37, 37)
        self.helpButton.setStyleSheet("QPushButton { background-color: rgb(21, 96, 130); border-radius: 18px; color: white; font-weight: 800; font-size: 13px; } QPushButton:hover { background-color: rgb(12, 58, 78); }")
        self.homeButton.hide()
        self.helpButton.hide()

    def checkContinue(self):
        if hasattr(self, 'disclaimerContainer'):
            self.disclaimerContainer.hide()
        self.showHome()

    def showRecordContextMenu(self, position):
        if not self.recordsTable or self.recordsTable.rowCount() == 0:
            return
        
        idx = self.recordsTable.indexAt(position)
        if not idx.isValid():
            return
        self._menu_row = idx.row()

        menu = QMenu(self.recordsTable)

        deleteRecordAction = QAction("Delete Record", self)
        deleteRecordAction.triggered.connect(self.deleteRecord)

        selectedItems = self.recordsTable.selectedItems()
        if not selectedItems:
            deleteRecordAction.setEnabled(False)
        menu.addAction(deleteRecordAction)

        deleteAllAction = QAction("Delete All Records", self)
        deleteAllAction.triggered.connect(self.deleteAllRecords)
        menu.addAction(deleteAllAction)

        menu.exec_(self.recordsTable.viewport().mapToGlobal(position))

    def deleteRecord(self):
        row = getattr(self, "_menu_row", -1)
        if row < 0:
            return
        
        reply = QMessageBox.question(self, 'Confirm Deletion',
                                    'Are you sure you want to delete this record?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.history_manager.remove_record_by_index(row)
            self.loadCSVRecords(self.recordsTable)


    def deleteAllRecords(self):
        reply = QMessageBox.question(self, 'Confirm Deletion',
                                    'Are you sure you want to delete all records?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.history_manager.delete_all_records()
            self.recordsTable.setRowCount(0)
        
    def updateScales(self):
        new_width = self.width()
        new_height = self.height()
        container_width = round(new_width * 0.75)
        container_height = round(new_height * 0.75)

        design_container_width = 600  
        design_container_height = 375  

        scale_factor = min(container_width / design_container_width,
                            container_height / design_container_height)

        base_image_box_size = 270
        if hasattr(self, 'imageBox'):
            img_box = self.imageBox()  
            if img_box is not None:
                new_image_box_size = int(base_image_box_size * scale_factor)
                img_box.setFixedSize(new_image_box_size, new_image_box_size)

        base_button_width = 100
        base_button_height = 40
        base_font_size = 13

        new_button_width = int(base_button_width * scale_factor)
        new_button_height = int(base_button_height * scale_factor)
        new_font_size = max(1, int(base_font_size * scale_factor))

        if (hasattr(self, 'runButton') and self.runButton is not None and 
            not sip.isdeleted(self.runButton)):
            self.runButton.setFixedSize(new_button_width, new_button_height)
            run_font = self.runButton.font()
            run_font.setPointSize(new_font_size)
            self.runButton.setFont(run_font)

        if (hasattr(self, 'recordsButton') and self.recordsButton is not None and 
            not sip.isdeleted(self.recordsButton)):
            self.recordsButton.setFixedSize(new_button_width, new_button_height)
            rec_font = self.recordsButton.font()
            rec_font.setPointSize(new_font_size)
            self.recordsButton.setFont(rec_font)

        if (hasattr(self, 'recordsButtonMain') and 
            self.recordsButtonMain is not None and 
            not sip.isdeleted(self.recordsButtonMain)):
            self.recordsButtonMain.setFixedSize(new_button_width, new_button_height)
            records_font = self.recordsButtonMain.font()
            records_font.setPointSize(new_font_size)
            self.recordsButtonMain.setFont(records_font)


        base_right_side_width = 270
        base_right_side_height = 350

        if hasattr(self, 'rightSide') and self.rightSide is not None:
            if not sip.isdeleted(self.rightSide):
                new_right_side_width = int(base_right_side_width * scale_factor)
                new_right_side_height = int(base_right_side_height * scale_factor)
                self.rightSide.setFixedSize(new_right_side_width, new_right_side_height)

        base_help_icon_size = 70
        if (hasattr(self, 'leftTopWidget') and 
            self.leftTopWidget is not None and 
            not sip.isdeleted(self.leftTopWidget)):
            new_size = int(base_help_icon_size * scale_factor)
            self.leftTopWidget.setFixedSize(new_size, new_size)

        base_help_font_size = 10
        new_help_font_size = max(1, int(base_help_font_size * scale_factor))
        if (hasattr(self, 'leftLabel2') and 
            self.leftLabel2 is not None and 
            not sip.isdeleted(self.leftLabel2)):
            font = self.leftLabel2.font()
            font.setPointSize(new_help_font_size)
            self.leftLabel2.setFont(font)

        if (hasattr(self, 'midLabel2') and self.midLabel2 is not None and not sip.isdeleted(self.midLabel2)):
            mid_font = self.midLabel2.font()
            mid_font.setPointSize(new_help_font_size)
            self.midLabel2.setFont(mid_font)

        if (hasattr(self, 'rightLabel2') and self.rightLabel2 is not None and not sip.isdeleted(self.rightLabel2)):
            right_font = self.rightLabel2.font()
            right_font.setPointSize(new_help_font_size)
            self.rightLabel2.setFont(right_font)

        base_help_left_bottom = 200
        if (hasattr(self, 'leftBottomWidget') and 
            self.leftBottomWidget is not None and 
            not sip.isdeleted(self.leftBottomWidget)):
            new_size = int(base_help_left_bottom * scale_factor)
            self.leftBottomWidget.setFixedSize(new_size, new_size)

        if (hasattr(self, 'rightTopWidget') and 
            self.rightTopWidget is not None and 
            not sip.isdeleted(self.rightTopWidget)):
            new_size = int(base_help_icon_size * scale_factor)
            self.rightTopWidget.setFixedSize(new_size, new_size)

        if (hasattr(self, 'rightBottomWidget') and 
            self.rightBottomWidget is not None and 
            not sip.isdeleted(self.rightBottomWidget)):
            new_size = int(base_help_left_bottom * scale_factor)
            self.rightBottomWidget.setFixedSize(new_size, new_size)

        if (hasattr(self, 'midTopWidget') and 
            self.midTopWidget is not None and 
            not sip.isdeleted(self.midTopWidget)):
            new_size = int(base_help_icon_size * scale_factor)
            self.midTopWidget.setFixedSize(new_size, new_size)

        if (hasattr(self, 'midBottomWidget') and 
            self.midBottomWidget is not None and 
            not sip.isdeleted(self.midBottomWidget)):
            new_size = int(base_help_left_bottom * scale_factor)
            self.midBottomWidget.setFixedSize(new_size, new_size)

        base_help_icon_size = 70
        if (hasattr(self, 'leftTopWidget') and 
            self.leftTopWidget is not None and 
            not sip.isdeleted(self.leftTopWidget)):
            new_size = int(base_help_icon_size * scale_factor)
            self.leftTopWidget.setFixedSize(new_size, new_size)
            pic_path = os.path.join(IMAGES_DIR, "pic.png")
            pixmapLeft = QPixmap(pic_path)
            scaledPixmapLeft = pixmapLeft.scaled(self.leftTopWidget.size(),
                                                Qt.KeepAspectRatio,
                                                Qt.SmoothTransformation)
            self.leftTopWidget.setPixmap(scaledPixmapLeft)

        if (hasattr(self, 'midTopWidget') and 
            self.midTopWidget is not None and 
            not sip.isdeleted(self.midTopWidget)):
            new_size = int(base_help_icon_size * scale_factor)
            self.midTopWidget.setFixedSize(new_size, new_size)
            gear_path = os.path.join(IMAGES_DIR, "gear.png")
            pixmapMid = QPixmap(gear_path)
            scaledPixmapMid = pixmapMid.scaled(self.midTopWidget.size(),
                                            Qt.KeepAspectRatio,
                                            Qt.SmoothTransformation)
            self.midTopWidget.setPixmap(scaledPixmapMid)

        if (hasattr(self, 'rightTopWidget') and 
            self.rightTopWidget is not None and 
            not sip.isdeleted(self.rightTopWidget)):
            new_size = int(base_help_icon_size * scale_factor)
            self.rightTopWidget.setFixedSize(new_size, new_size)
            folder_path = os.path.join(IMAGES_DIR, "folder.png")
            pixmapRight = QPixmap(folder_path)
            scaled_pixmap = pixmapRight.scaled(self.rightTopWidget.size(),
                                            Qt.KeepAspectRatio,
                                            Qt.SmoothTransformation)
            self.rightTopWidget.setPixmap(scaled_pixmap)

        if hasattr(self, 'imageLabel') and self.imageLabel is not None and not sip.isdeleted(self.imageLabel):
            base_image_label_size = 270 
            new_image_label_size = int(base_image_label_size * scale_factor)
            self.imageLabel.setFixedSize(new_image_label_size, new_image_label_size)
            
            if hasattr(self.imageBox, '__call__') and self.imageBox() is not None:
                pic_path = os.path.join(IMAGES_DIR, "default_record.png")
                if os.path.exists(pic_path):
                    pixmap = QPixmap(pic_path)
                    scaledPixmap = pixmap.scaled(self.imageLabel.size(),
                                                Qt.KeepAspectRatio,
                                                Qt.SmoothTransformation)
                    self.imageLabel.setPixmap(scaledPixmap)


        if hasattr(self, 'recordsTable') and self.recordsTable is not None and not sip.isdeleted(self.recordsTable):
            base_column_width = 60 
            new_column_width = int(base_column_width * scale_factor)
            for col in range(self.recordsTable.columnCount()):
                self.recordsTable.setColumnWidth(col, new_column_width)

            base_table_font_size = 10  
            new_table_font_size = max(1, int(base_table_font_size * scale_factor))
            table_font = self.recordsTable.font()
            table_font.setPointSize(new_table_font_size)
            self.recordsTable.setFont(table_font)

        if hasattr(self, 'resultsButton') and self.resultsButton is not None and not sip.isdeleted(self.resultsButton):
            self.resultsButton.setFixedSize(new_button_width, new_button_height)
            results_font = self.resultsButton.font()
            results_font.setPointSize(new_font_size)
            self.resultsButton.setFont(results_font)

        if hasattr(self, 'recordsButtonMain') and self.recordsButtonMain is not None and not sip.isdeleted(self.recordsButtonMain):
            self.recordsButtonMain.setFixedSize(new_button_width, new_button_height)
            records_font = self.recordsButtonMain.font()
            records_font.setPointSize(new_font_size)
            self.recordsButtonMain.setFont(records_font)


        if hasattr(self, 'recordsButton') and self.recordsButton is not None and not sip.isdeleted(self.recordsButton):
            self.recordsButton.setFixedSize(new_button_width, round(new_button_height * 0.5))
            rec_font = self.recordsButton.font()
            rec_font.setPointSize(new_font_size)
            self.recordsButton.setFont(rec_font)


        if (hasattr(self, 'statsButton') and self.statsButton is not None 
            and not sip.isdeleted(self.statsButton)):
            self.statsButton.setFixedSize(new_button_width, round(new_button_height * 0.5))
            stats_font = self.statsButton.font()
            stats_font.setPointSize(new_font_size)
            self.statsButton.setFont(stats_font)







    def showHome(self):
        self.clearLayout(self.mainLayout)
        self.homeButton.hide()
        self.helpButton.show()
        hLayout = QHBoxLayout()
        self.leftSide = QVBoxLayout()
        buttonLayout = QHBoxLayout()

        self.imageBox = weakref.ref(ImageDropBox(self))

        self.recordsButtonMain = QPushButton("RECORDS", self)
        self.recordsButtonMain.setCursor(Qt.PointingHandCursor)
        self.recordsButtonMain.clicked.connect(self.showRecords)
        self.recordsButtonMain.setStyleSheet("QPushButton { background-color: white; border: 2px solid black; border-radius: 20px; font-weight: 800; font-size: 13px; } QPushButton:hover { background-color: #f0f0f0; }")
        self.recordsButtonMain.setMaximumSize(100, 40)
        self.runButton = QPushButton("RUN", self)
        self.runButton.setCursor(Qt.PointingHandCursor)
        self.runButton.clicked.connect(self.runCommand)
        self.runButton.setStyleSheet("QPushButton { background-color: rgb(21, 96, 130); border-radius: 20px; color: white; font-weight: 800; font-size: 13px; } QPushButton:hover { background-color: rgb(12, 58, 78); }")
        self.runButton.setMaximumSize(100, 40)

        buttonLayout.addWidget(self.recordsButtonMain)
        buttonLayout.addWidget(self.runButton)

        hwidget = self.imageBox()
        self.leftSide.addWidget(hwidget)
        self.leftSide.addSpacing(20)
        self.leftSide.addLayout(buttonLayout)
        self.rightSide = QFrame(self)
        self.rightSide.setStyleSheet("background-color: white; border: 4px solid rgb(20, 80, 120); border-radius: 20px")
        self.rightSide.setMinimumSize(270, 350)
        self.rightLayout = QVBoxLayout(self.rightSide)
        hLayout.addLayout(self.leftSide)
        hLayout.addWidget(self.rightSide)
        self.mainLayout.addLayout(hLayout)

        QTimer.singleShot(0, self.updateScales)

    def runCommand(self):
        if not self.imageBox().imagePath:
            layout = self.imageBox().layout()
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            error_label = QLabel("Error: Please upload an image", self.imageBox())
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red; font-size: 16px;")
            error_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            layout.addWidget(error_label)
            return
        self.imageBox().showLoading()
        prediction, confidence = self.model_manager.classify_image(self.imageBox().imagePath)
        self.lastPrediction = prediction
        self.lastConfidence = confidence
        self.showClassificationResults(prediction, confidence)
        self.imageBox().showComplete()
        currentDate = datetime.now().strftime("%m/%d/%y")
        self.history_manager.save_record(self.imageBox().imagePath, currentDate, prediction, confidence)
        self.imageBox().imagePath = None

    def showClassificationResults(self, prediction, confidence):
        self.clearLayout(self.rightLayout)
        self.addNavBar(current="results")
        
        resultsFrame = QFrame(self)
        resultsFrame.setStyleSheet("background-color: white; border: 1px solid black; border-radius: 10px; margin: 10px; padding: 10px;")
        resultsLayout = QVBoxLayout()
        resultsLayout.setAlignment(Qt.AlignCenter)
        resultsFrame.setLayout(resultsLayout)
        
        label_prediction = QLabel(f"Prediction\n{prediction}", self)
        label_prediction.setAlignment(Qt.AlignCenter)
        label_prediction.setStyleSheet("font-size: 14px; font-weight: bold; border: none;")
        resultsLayout.addWidget(label_prediction)
        
        label_confidence = QLabel(f"Confidence %\n{confidence:.2f}%", self)
        label_confidence.setAlignment(Qt.AlignCenter)
        label_confidence.setStyleSheet("font-size: 14px; font-weight: bold; border: none;")
        resultsLayout.addWidget(label_confidence)
        
        self.rightLayout.addWidget(resultsFrame, alignment=Qt.AlignHCenter)

    def showReference(self, predicted_class):
        self.clearLayout(self.rightLayout)
        self.addNavBar(current="info")
        
        titleLabel = QLabel(predicted_class, self)
        titleLabel.setAlignment(Qt.AlignCenter)
        titleLabel.setStyleSheet("font-weight: bold; font-size: 16px; border: none; margin-top: 4px")
        self.rightLayout.addWidget(titleLabel)
        
        image_files = {
            "Melanocytic nevi": os.path.join(IMAGES_DIR, "nv.png"),
            "Melanoma": os.path.join(IMAGES_DIR, "mel.png"),
            "Benign keratosis": os.path.join(IMAGES_DIR, "bkl.png"),
            "Basal cell carcinoma": os.path.join(IMAGES_DIR, "bcc.png"),
            "Actinic keratoses": os.path.join(IMAGES_DIR, "akiec.png"),
            "Vascular lesions": os.path.join(IMAGES_DIR, "vasc.png"),
            "Dermatofibroma": os.path.join(IMAGES_DIR, "df.png")
        }
        file_name = image_files.get(predicted_class, os.path.join(IMAGES_DIR, "reference_image.png"))
        imageLabel = QLabel(self)
        pixmap = QPixmap(file_name)
        if not pixmap.isNull():
            imageLabel.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            imageLabel.setStyleSheet("border: none")
        else:
            imageLabel.setText("Image Not Available")
        imageLabel.setAlignment(Qt.AlignCenter)
        self.rightLayout.addWidget(imageLabel)
        
        skin_lesion_descriptions = {
            "Melanocytic nevi": "Commonly known as moles, these are benign, pigmented growths made up of melanocytes.",
            "Melanoma": "A malignant tumor originating from melanocytes; it’s the most dangerous form of skin cancer if not detected early.",
            "Benign keratosis": "Non-cancerous skin growths that resemble keratoses with a waxy or scaly appearance.",
            "Basal cell carcinoma": "The most frequent type of skin cancer; it arises from basal cells, grows slowly, and rarely spreads, but can cause local damage.",
            "Actinic keratoses": "Rough, scaly patches caused by long-term sun exposure; considered precancerous as they can develop into squamous cell carcinoma.",
            "Vascular lesions": "Abnormalities in blood vessels that are typically benign.",
            "Dermatofibroma": "A small, firm, benign skin nodule, often found on the legs."
        }
        descriptionLabel = QLabel(self)

        descriptionText = skin_lesion_descriptions.get(predicted_class, "No description available for this lesion type.")

        descriptionLabel.setText(descriptionText)
        descriptionLabel.setWordWrap(True)
        descriptionLabel.setAlignment(Qt.AlignCenter)
        descriptionLabel.setStyleSheet("font-size: 14px; margin: 5px; border: none;")

        self.rightLayout.addWidget(descriptionLabel)
        self.rightLayout.addStretch()

    def showLinks(self):
        self.clearLayout(self.rightLayout)
        self.addNavBar(current="links")
        
        titleLabel = QLabel("Related Links", self)
        titleLabel.setAlignment(Qt.AlignCenter)
        titleLabel.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px; border: none")
        self.rightLayout.addWidget(titleLabel)
        
        mayo_links = {
            "Actinic keratoses": "https://www.mayoclinic.org/search/search-results?q=actinic%20keratoses",
            "Basal cell carcinoma": "https://www.mayoclinic.org/search/search-results?q=basal%20cell%20carcinoma",
            "Benign keratosis": "https://www.mayoclinic.org/search/search-results?q=benign%20keratosis",
            "Dermatofibroma": "https://www.mayoclinic.org/search/search-results?q=dermatofibroma",
            "Melanoma": "https://www.mayoclinic.org/search/search-results?q=melanoma",
            "Melanocytic nevi": "https://www.mayoclinic.org/search/search-results?q=melanocytic%20nevi",
            "Vascular lesions": "https://www.mayoclinic.org/search/search-results?q=vascular%20lesions"
        }
        
        acs_links = {
            "Actinic keratoses": "https://www.cancer.org/search.html?q=actinic+keratosis",
            "Basal cell carcinoma": "https://www.cancer.org/search.html?q=basal+cell+carcinoma",
            "Benign keratosis": "https://www.cancer.org/search.html?q=benign+keratosis",
            "Melanoma": "https://www.cancer.org/search.html?q=melanoma",
            "Melanocytic nevi": "https://www.cancer.org/search.html?q=melanocytic+nevi",
            "Vascular lesions": "https://www.cancer.org/search.html?q=vascular+lesions"
        }
        
        cure_links = {
            "Melanoma": "https://www.curemelanoma.org/about-melanoma"
        }
        
        current_type = self.lastPrediction 
        buttonLayout = QVBoxLayout()
        
        if current_type in acs_links:
            btnACS = QPushButton("American Cancer Society", self)
            btnACS.setCursor(Qt.PointingHandCursor)
            btnACS.setStyleSheet("""
                QPushButton {
                    font-size: 13px; 
                    padding: 5px; 
                    min-width: 180px; 
                    max-height: 50px; 
                    border: none; 
                    background-color: #FAFAFA; 
                    border: 2px solid black;
                }
                QPushButton:hover {
                    background-color: #E0E0E0;
                }
            """)
            btnACS.clicked.connect(lambda _, link=acs_links[current_type]: QDesktopServices.openUrl(QUrl(link)))
            buttonLayout.addWidget(btnACS, alignment=Qt.AlignHCenter)
        
        if current_type in mayo_links:
            btnMayo = QPushButton("Mayo Clinic", self)
            btnMayo.setCursor(Qt.PointingHandCursor)
            btnMayo.setStyleSheet("""
                QPushButton {
                    font-size: 13px; 
                    padding: 5px; 
                    min-width: 180px; 
                    max-height: 50px; 
                    border: none; 
                    background-color: #FAFAFA; 
                    border: 2px solid black;
                }
                QPushButton:hover {
                    background-color: #E0E0E0;
                }
            """)
            btnMayo.clicked.connect(lambda _, link=mayo_links[current_type]: QDesktopServices.openUrl(QUrl(link)))
            buttonLayout.addWidget(btnMayo, alignment=Qt.AlignHCenter)
        
        if current_type in cure_links:
            btnCure = QPushButton("Cure Melanoma", self)
            btnCure.setCursor(Qt.PointingHandCursor)
            btnCure.setStyleSheet("""
                QPushButton {
                    font-size: 13px; 
                    padding: 5px; 
                    min-width: 180px; 
                    max-height: 50px; 
                    border: none; 
                    background-color: #FAFAFA; 
                    border: 2px solid black;
                }
                QPushButton:hover {
                    background-color: #E0E0E0;
                }
            """)
            btnCure.clicked.connect(lambda _, link=cure_links[current_type]: QDesktopServices.openUrl(QUrl(link)))
            buttonLayout.addWidget(btnCure, alignment=Qt.AlignHCenter)
        
        buttonLayout.setSpacing(6)
        self.rightLayout.addLayout(buttonLayout)
        self.rightLayout.addStretch()

    def showStats(self):
        self.clearLayout(self.mainLayout)
        self.homeButton.hide()
        self.helpButton.show()

        statsLayout = QVBoxLayout()
        statsLayout.setAlignment(Qt.AlignCenter)

        csvFile = CSV_PATH
        if not os.path.exists(csvFile):
            noDataLabel = QLabel("No records found to generate statistics.")
            noDataLabel.setAlignment(Qt.AlignCenter)
            noDataLabel.setStyleSheet("font-size: 16px; color: gray;")
            statsLayout.addWidget(noDataLabel)
            
            backButton = QPushButton("Back to Records", self)
            backButton.setCursor(Qt.PointingHandCursor)
            backButton.setStyleSheet("""
                QPushButton {
                    background-color: rgb(21, 96, 130);
                    color: white;
                    font-size: 13px;
                    padding: 5px;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: rgb(12, 58, 78);
                }
            """)
            backButton.clicked.connect(self.showRecords)
            statsLayout.addWidget(backButton, alignment=Qt.AlignCenter)
            statsLayout.setSpacing(10)
            
            self.mainLayout.addLayout(statsLayout)
            return

        class_confidences = {}
        try:
            with open(csvFile, newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) < 4:
                        continue
                    classification = row[2]
                    try:
                        conf_value = float(row[3])
                    except ValueError:
                        conf_value = None

                    if classification and conf_value is not None:
                        class_confidences.setdefault(classification, []).append(conf_value)
        except Exception as e:
            errorLabel = QLabel(f"Error loading CSV: {e}")
            errorLabel.setAlignment(Qt.AlignCenter)
            errorLabel.setStyleSheet("font-size: 16px; color: red;")
            statsLayout.addWidget(errorLabel)
            
            backButton = QPushButton("Back to Records", self)
            backButton.setCursor(Qt.PointingHandCursor)
            backButton.setStyleSheet("""
                QPushButton {
                    background-color: rgb(21, 96, 130);
                    color: white;
                    font-size: 13px;
                    padding: 5px;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: rgb(12, 58, 78);
                }
            """)
            backButton.clicked.connect(self.showRecords)
            statsLayout.addWidget(backButton, alignment=Qt.AlignCenter)
            statsLayout.setSpacing(10)
            
            self.mainLayout.addLayout(statsLayout)
            return

        if not class_confidences:
            noDataLabel = QLabel("No valid records found to generate statistics.")
            noDataLabel.setAlignment(Qt.AlignCenter)
            noDataLabel.setStyleSheet("font-size: 16px; color: gray;")
            statsLayout.addWidget(noDataLabel)
            
            backButton = QPushButton("Back to Records", self)
            backButton.setCursor(Qt.PointingHandCursor)
            backButton.setStyleSheet("""
                QPushButton {
                    background-color: rgb(21, 96, 130);
                    color: white;
                    font-size: 13px;
                    padding: 5px;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: rgb(12, 58, 78);
                }
            """)
            backButton.clicked.connect(self.showRecords)
            statsLayout.addWidget(backButton, alignment=Qt.AlignCenter)
            statsLayout.setSpacing(10)
            
            self.mainLayout.addLayout(statsLayout)
            return


        avg_conf = {}
        for cls, conf_list in class_confidences.items():
            avg_conf[cls] = sum(conf_list) / len(conf_list)

        classifications = list(avg_conf.keys())
        confidences = [avg_conf[c] for c in classifications]


        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        bars = ax.bar(classifications, confidences, color="#008B8B")

        annot = ax.annotate(
            "",
            xy=(0,0),
            xytext=(0, -60),                 
            textcoords="offset points",
            bbox=dict(
                boxstyle="round,pad=0.3",
                fc="white",                   
                ec="black"                   
            ),
            arrowprops=dict(
                arrowstyle="->",
                color="black"                
            )
        )
        annot.set_visible(False)

        def update_annot(bar, idx):
            x = bar.get_x() + bar.get_width()/2
            y = bar.get_height()
            annot.xy = (x, y)
            cls = classifications[idx]
            avg = confidences[idx]
            count = len(class_confidences[cls])
            annot.set_text(f"{cls}\nAvg: {avg:.2f}%\nCount: {count}")
            annot.get_bbox_patch().set_alpha(0.8)

        def hover(event):
            if event.inaxes == ax:
                for idx, bar in enumerate(bars):
                    if bar.contains(event)[0]:
                        update_annot(bar, idx)
                        annot.set_visible(True)
                        fig.canvas.draw_idle()
                        return
            if annot.get_visible():
                annot.set_visible(False)
                fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", hover)

        ax.set_title("Average Confidence by Classification")
        ax.set_xlabel("Classification Type")
        ax.set_ylabel("Average Confidence (%)")
        plt.xticks(rotation=30, ha="right")


        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0,
                    height + 0.5,
                    f"{height:.2f}%",
                    ha="center", va="bottom", fontsize=9)

        fig.tight_layout()


        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        canvas.updateGeometry()
        statsLayout.addWidget(canvas)


        backButton = QPushButton("Back to Records", self)
        backButton.setCursor(Qt.PointingHandCursor)
        backButton.setStyleSheet("""
            QPushButton {
                background-color: rgb(21, 96, 130);
                color: white;
                font-size: 13px;
                padding: 5px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgb(12, 58, 78);
            }
        """)
        backButton.clicked.connect(self.showRecords)
        statsLayout.addWidget(backButton, alignment=Qt.AlignCenter)
        statsLayout.setSpacing(10)

        self.mainLayout.addLayout(statsLayout)
        self.updateScales()

    def showHelp(self):
        self.clearLayout(self.mainLayout)
        self.homeButton.show()
        self.helpButton.hide()

        self.runButton = None
        self.recordsButtonMain = None

        hLayout = QHBoxLayout()

        leftBoxWidget = QWidget(self)
        leftBox = QVBoxLayout(leftBoxWidget)
        leftBox.setSpacing(30)
        leftBox.setContentsMargins(0, 0, 0, 0)

        self.leftTopWidget = QLabel(self)
        self.leftTopWidget.setFixedSize(70, 70)
        self.leftTopWidget.setAlignment(Qt.AlignCenter) 
        pic_path = os.path.join(IMAGES_DIR, "pic.png")
        pixmapLeft = QPixmap(pic_path)
        scaledPixmapLeft = pixmapLeft.scaled(self.leftTopWidget.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.leftTopWidget.setPixmap(scaledPixmapLeft)
        leftBox.addWidget(self.leftTopWidget, 0, Qt.AlignCenter) 

        self.leftBottomWidget = QWidget(self)
        self.leftBottomWidget.setAttribute(Qt.WA_StyledBackground, True)
        self.leftBottomWidget.setStyleSheet("background-color: white; border: 2px solid rgb(21, 96, 130); border-radius: 35px;")
        self.leftBottomWidget.setFixedSize(200, 200)
        leftBottomLayout = QVBoxLayout(self.leftBottomWidget)
        leftBottomLayout.setContentsMargins(0, 0, 0, 0)
        leftBottomLayout.setSpacing(0)
        self.leftLabel2 = QLabel("Upload an image with a\ncompatible format. (JPEG, PNG)", self)
        self.leftLabel2.setWordWrap(True)
        self.leftLabel2.setAlignment(Qt.AlignCenter)
        leftBottomLayout.addWidget(self.leftLabel2)
        leftBox.addWidget(self.leftBottomWidget, 0, Qt.AlignCenter)

        rightBoxWidget = QWidget(self)
        rightBox = QVBoxLayout(rightBoxWidget)
        rightBox.setSpacing(30)
        
        self.rightTopWidget = QLabel(self) 
        self.rightTopWidget.setFixedSize(70, 70)
        self.rightTopWidget.setAlignment(Qt.AlignCenter)
        folder_path = os.path.join(IMAGES_DIR, "folder.png")
        pixmap = QPixmap(folder_path)
        scaled_pixmap = pixmap.scaled(self.rightTopWidget.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.rightTopWidget.setPixmap(scaled_pixmap)
        rightBox.addWidget(self.rightTopWidget, 0, Qt.AlignCenter)
        
        self.rightBottomWidget = QWidget(self) 
        self.rightBottomWidget.setAttribute(Qt.WA_StyledBackground, True)
        self.rightBottomWidget.setStyleSheet("background-color: white; border: 2px solid rgb(21, 96, 130); border-radius: 35px;")
        self.rightBottomWidget.setFixedSize(200,200)
        rightBottomLayout = QVBoxLayout(self.rightBottomWidget)
        rightBottomLayout.setContentsMargins(0, 0, 0, 0)
        rightBottomLayout.setSpacing(0)
        self.rightLabel2 = QLabel("Access references to\nresults or previous records", self)
        self.rightLabel2.setWordWrap(True)
        self.rightLabel2.setAlignment(Qt.AlignCenter)
        rightBottomLayout.addWidget(self.rightLabel2)
        rightBox.addWidget(self.rightTopWidget, 1, Qt.AlignHCenter)
        rightBox.addWidget(self.rightBottomWidget, 3, Qt.AlignHCenter)

        midBoxWidget = QWidget(self)
        midBox = QVBoxLayout(midBoxWidget)
        midBox.setSpacing(30)
        self.midTopWidget = QLabel(self)
        self.midTopWidget.setFixedSize(70, 70)
        self.midTopWidget.setAlignment(Qt.AlignCenter)
        gear_path = os.path.join(IMAGES_DIR, "gear.png")
        pixmapMid = QPixmap(gear_path)
        scaledPixmapMid = pixmapMid.scaled(self.midTopWidget.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.midTopWidget.setPixmap(scaledPixmapMid)
        midBox.addWidget(self.midTopWidget, 0, Qt.AlignCenter)
        self.midBottomWidget = QWidget(self) 
        self.midBottomWidget.setAttribute(Qt.WA_StyledBackground, True)
        self.midBottomWidget.setStyleSheet("background-color: white; border: 2px solid rgb(21, 96, 130); border-radius: 35px;")
        self.midBottomWidget.setFixedSize(200,200)
        midBottomLayout = QVBoxLayout(self.midBottomWidget)
        midBottomLayout.setContentsMargins(0, 0, 0, 0)
        midBottomLayout.setSpacing(0)
        self.midLabel2 = QLabel("Click run to start the\nclassification process", self)
        self.midLabel2.setWordWrap(True)
        self.midLabel2.setAlignment(Qt.AlignCenter)
        midBottomLayout.addWidget(self.midLabel2)
        midBox.addWidget(self.midTopWidget, 1, Qt.AlignHCenter)
        midBox.addWidget(self.midBottomWidget, 3, Qt.AlignHCenter)

        hLayout.addWidget(leftBoxWidget, alignment=Qt.AlignCenter)
        hLayout.addWidget(midBoxWidget, alignment=Qt.AlignCenter)
        hLayout.addWidget(rightBoxWidget, alignment=Qt.AlignCenter)
        self.mainLayout.addLayout(hLayout)

        self.updateScales()


    def addNavBar(self, current="results"):
        navWidget = QWidget(self)
        navWidget.setFixedHeight(40)

        navLayout = QHBoxLayout(navWidget)
        navLayout.setContentsMargins(2, 2, 2, 2)
        navLayout.setSpacing(5)

        self.resultsButton = QPushButton("Results", self)
        infoButton = QPushButton("Info", self)
        linksButton = QPushButton("Links", self)
        self.resultsButton.setCursor(Qt.PointingHandCursor)
        infoButton.setCursor(Qt.PointingHandCursor)
        linksButton.setCursor(Qt.PointingHandCursor)
        self.resultsButton.setFixedHeight(30)
        infoButton.setFixedHeight(30)
        linksButton.setFixedHeight(30)
        activeStyle = (
            "QPushButton { background-color: rgb(12, 58, 78); color: white; border: none; font-size: 12px; padding: 2px 6px; border-radius: 5px }"
        )
        inactiveStyle = (
            "QPushButton { background-color: rgb(21, 96, 130); color: white; border: none; font-size: 12px; padding: 2px 6px; border-radius: 5px }"
        )
        if current == "results":
            self.resultsButton.setStyleSheet(activeStyle)
            infoButton.setStyleSheet(inactiveStyle)
            linksButton.setStyleSheet(inactiveStyle)
        elif current == "info":
            self.resultsButton.setStyleSheet(inactiveStyle)
            infoButton.setStyleSheet(activeStyle)
            linksButton.setStyleSheet(inactiveStyle)
        else:
            self.resultsButton.setStyleSheet(inactiveStyle)
            infoButton.setStyleSheet(inactiveStyle)
            linksButton.setStyleSheet(activeStyle)
        self.resultsButton.clicked.connect(lambda: self.showClassificationResults(self.lastPrediction, self.lastConfidence))
        infoButton.clicked.connect(lambda: self.showReference(self.lastPrediction))
        linksButton.clicked.connect(self.showLinks)

        navLayout.addWidget(self.resultsButton)
        navLayout.addWidget(infoButton)
        navLayout.addWidget(linksButton)

        navWidget.setStyleSheet("border: none")

        self.rightLayout.addWidget(navWidget)

    def showRecords(self):
        self.clearLayout(self.mainLayout)
        self.homeButton.hide()
        self.helpButton.show()
        hLayout = QHBoxLayout()
        self.leftSide = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        self.imageLabel = QLabel(self)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setFixedSize(270, 270)
        self.imageLabel.setStyleSheet("background-color: white; border: 4px solid rgb(20, 80, 120); border-radius: 20px; color: gray")
        self.imageLabel.setText("Click on record to see image")

        self.resultsButton = QPushButton("ANALYZE", self)
        self.resultsButton.setCursor(Qt.PointingHandCursor)
        self.resultsButton.clicked.connect(self.showHome)
        self.resultsButton.setStyleSheet("QPushButton { background-color: white; border: 2px solid black; border-radius: 20px; font-weight: 800; font-size: 13px; } QPushButton:hover { background-color: #f0f0f0; }")
        self.runButton = QPushButton("RUN", self)
        self.runButton.setCursor(Qt.PointingHandCursor)
        self.runButton.setStyleSheet("QPushButton { background-color: rgb(21, 96, 130); border-radius: 20px; color: white; font-weight: 800; font-size: 13px; } QPushButton:hover { background-color: rgb(12, 58, 78); }")
        self.runButton.setMaximumSize(100, 40)

        buttonLayout.addWidget(self.resultsButton)
        self.leftSide.addWidget(self.imageLabel)
        self.leftSide.addSpacing(20)
        self.leftSide.addLayout(buttonLayout)

        self.rightSide = QFrame(self)
        self.rightSide.setStyleSheet("background-color: white; border-radius: 20px")
        self.rightSide.setFixedSize(270, 350)

        rightLayout = QVBoxLayout(self.rightSide)
        rightLayout.setContentsMargins(5, 5, 5, 5)

        navWidget = QWidget(self)
        navWidget.setFixedHeight(40)

        navLayout = QHBoxLayout(navWidget)
        navLayout.setContentsMargins(2, 2, 2, 2)
        navLayout.setSpacing(5)

        self.recordsButton = QPushButton("Records", self)
        self.statsButton = QPushButton("Stats", self)
        self.recordsButton.setCursor(Qt.PointingHandCursor)
        self.statsButton.setCursor(Qt.PointingHandCursor)

        activeStyle = ("QPushButton { background-color: rgb(12, 58, 78); color: white; border: none; font-size: 12px; padding: 2px 6px; border-radius: 5px; max-width: 80px; min-height: 20px }")
        inactiveStyle = ("QPushButton { background-color: rgb(21, 96, 130); color: white; border: none; font-size: 12px; padding: 2px 6px; border-radius: 5px; max-width: 80px; min-height: 20px }")

        self.recordsButton.setStyleSheet(activeStyle)
        self.statsButton.setStyleSheet(inactiveStyle)
        self.recordsButton.clicked.connect(self.showRecords)
        self.statsButton.clicked.connect(self.showStats)

        navLayout.addWidget(self.recordsButton)
        navLayout.addWidget(self.statsButton)

        navWidget.setStyleSheet("border: none")

        rightLayout.addWidget(navWidget)

        tableWidget = QTableWidget(self)
        tableWidget.setColumnCount(4)
        tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        tableWidget.customContextMenuRequested.connect(self.showRecordContextMenu)
        tableWidget.setHorizontalHeaderLabels(["Image", "Date", "Result", "Conf.%"])
        tableWidget.setColumnWidth(0, 60)
        tableWidget.setColumnWidth(1, 60)
        tableWidget.setColumnWidth(2, 60)
        tableWidget.setColumnWidth(3, 60)
        tableWidget.setStyleSheet("QTableWidget::corner { background-color: white; } QScrollBar:vertical { width: 10px; } QScrollBar:horizontal { height: 10px; background-color: black } QScrollBar::sub-line, QScrollBar::add-line { width: 5px; height: 5px }")
        tableWidget.cellDoubleClicked.connect(self.showClassificationFromRecord)
        tableWidget.cellClicked.connect(self.loadImageFromTable)

        self.loadCSVRecords(tableWidget)
        rightLayout.addWidget(tableWidget)
        rightLayout.setSpacing(15)
        hLayout.addLayout(self.leftSide)
        hLayout.addWidget(self.rightSide)
        self.mainLayout.addLayout(hLayout)
        self.recordsTable = tableWidget

        self.updateScales()

    def showClassificationFromRecord(self, row, column):
        if not self.recordsTable or row < 0:
            return
        item_image = self.recordsTable.item(row, 0)
        item_result = self.recordsTable.item(row, 2)
        item_conf = self.recordsTable.item(row, 3)
        if not item_result or not item_conf:
            return
        classification = item_result.text()
        try:
            confidence = float(item_conf.text())
        except ValueError:
            confidence = 0.0
        image_path = ""
        if item_image:
            image_path = item_image.data(Qt.UserRole)
        self.lastPrediction = classification
        self.lastConfidence = confidence
        self.showHome()
        if image_path and os.path.exists(image_path):
            self.imageBox().loadImage(image_path)
            image_name = os.path.basename(image_path)
            max_char = 20
            if len(image_name) > max_char:
                image_name = image_name[:max_char] + "..."
        self.showClassificationResults(classification, confidence)

    def loadCSVRecords(self, tableWidget):
        csvFile = CSV_PATH
        if not os.path.exists(csvFile):
            return
        with open(csvFile, newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)
        tableWidget.setRowCount(len(rows))
        for eachRow, row in enumerate(rows):
            fullPath = row[0] if len(row) > 0 else ""
            filename_only = os.path.basename(fullPath)
            item0 = QTableWidgetItem(filename_only)
            item0.setTextAlignment(Qt.AlignCenter)
            item0.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item0.setToolTip(f"<span style='color: black;'>{filename_only}</span>")
            item0.setData(Qt.UserRole, fullPath)
            tableWidget.setItem(eachRow, 0, item0)
            for eachCol in range(1, 4):
                cellInfo = row[eachCol] if eachCol < len(row) else ""
                item = QTableWidgetItem(cellInfo)
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                item.setToolTip(f"<span style='color: black;'>{cellInfo}</span>")
                tableWidget.setItem(eachRow, eachCol, item)

    def loadImageFromTable(self, row, column):
        if column == 0:
            item = self.recordsTable.item(row, column)
            if item:
                imagePath = item.data(Qt.UserRole)
                if os.path.exists(imagePath):
                    pixmap = QPixmap(imagePath)
                    self.imageLabel.setPixmap(pixmap.scaled(int(self.imageLabel.width() * 0.9), int(self.imageLabel.height() * 0.9), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    self.imageLabel.setText("Image Not Found")
            else:
                self.imageLabel.setText("Invalid File Path")

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def centerBlock(self):
        frame = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(center)
        self.move(frame.topLeft())

class LoadingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loading")
        self.setGeometry(100, 100, 800, 500)
        self.setFixedSize(800, 500)
        self.setStyleSheet("background-color: rgb(213, 230, 247);")
        layout = QVBoxLayout(self)
        self.loadingLabel = QLabel(self)
        self.loadingLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.loadingLabel)
        self.movie = QMovie(os.path.join(IMAGES_DIR, "loading.gif"))
        self.movie.setScaledSize(QSize(70, 70))
        self.loadingLabel.setMovie(self.movie)
        self.movie.start()
        self.centerWindow()

    def centerWindow(self):
        frameGm = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

class ImageDropBox(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self.imagePath = None
        self.setStyleSheet("background-color: white; border: 0px solid rgb(20, 80, 120); border-radius: 40px")
        self.setMaximumSize(270, 270)
        self.setMinimumSize(270, 270)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.text = QLabel("Click or drag to upload image", self)
        self.text.setAlignment(Qt.AlignCenter)
        self.text.setStyleSheet("color: gray;")
        layout.addWidget(self.text)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            if url.isLocalFile():
                filePath = url.toLocalFile()
                self.loadImage(filePath)
        event.acceptProposedAction()

    def mousePressEvent(self, event):
        filePath, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.heic *.webp *.tiff)")
        if filePath:
            self.loadImage(filePath)

    def loadImage(self, filePath):
        allowed_exts = ('.png', '.jpg', '.jpeg', '.heic', '.webp', '.tiff')
        ext = os.path.splitext(filePath)[1].lower()

        if ext not in allowed_exts:
            layout = self.layout()
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            error_label = QLabel(
                "Error: Invalid file format.\n\nAcceptable formats:\n(.png .jpg .jpeg .heic .webp .tiff)",
                self
            )
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red; font-size: 16px;")
            error_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            layout.addWidget(error_label)
            return

        self.imagePath = filePath 
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        pixmap = QPixmap(filePath)
        self.imageLabel = QLabel(self)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setPixmap(pixmap.scaled(int(self.width() * 0.9), int(self.height() * 0.9), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(self.imageLabel, alignment=Qt.AlignCenter)
        caption = QLabel(os.path.basename(filePath), self)
        caption.setAlignment(Qt.AlignCenter)
        caption.setStyleSheet("font-size: 12px; color: gray;")
        layout.addWidget(caption, alignment=Qt.AlignCenter)
        layout.addStretch()

    def showLoading(self):
        layout = self.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        loadingLabel = QLabel("Running Classification...", self)
        loadingLabel.setAlignment(Qt.AlignCenter)
        loadingLabel.setStyleSheet("color: gray; font-size: 16px")
        layout.addWidget(loadingLabel)

    def showComplete(self):
        layout = self.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        completeLabel = QLabel("Classification Complete!", self)
        completeLabel.setAlignment(Qt.AlignCenter)
        completeLabel.setStyleSheet("color: green; font-size: 16px")
        layout.addWidget(completeLabel)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet("QWidget { color: black; }")
    
    loadingWindow = LoadingWindow()
    loadingWindow.show()

    def showMainWindow():
        global mainWindow
        mainWindow = disclaimerWindow()
        mainWindow.show()
        loadingWindow.close()

    QTimer.singleShot(1000, showMainWindow)
    sys.exit(app.exec_())
