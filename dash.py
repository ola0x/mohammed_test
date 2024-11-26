import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, \
    QLabel, QGridLayout, QScrollArea, QSizePolicy
from PyQt5.QtGui import QPixmap, QIcon, QImage, QPalette
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QEvent, QObject
from PyQt5 import QtCore
import sys
import logging

from sp.config import get_config

STORE_NAME = "PREMIER"
config = get_config(STORE_NAME)
RTSP_URL_1 = config["RTSP_URL_1"]
RTSP_URL_2 = config["RTSP_URL_2"]
RTSP_URL_3 = config["RTSP_URL_3"]
RTSP_URL_4 = config["RTSP_URL_4"]


class CaptureIpCameraFramesWorker(QThread):
    ImageUpdated = pyqtSignal(QImage)

    def __init__(self, url) -> None:
        super(CaptureIpCameraFramesWorker, self).__init__()
        self.url = url
        self.__thread_active = True
        self.fps = 0
        self.__thread_pause = False
        self.retry_limit = 5

    def run(self) -> None:
        retry_count = 0
        while self.__thread_active:
            cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
            self.fps = cap.get(cv2.CAP_PROP_FPS)
            if not cap.isOpened():
                logging.error(f"Failed to open the stream {self.url}")
                cap.release()
                continue

            while self.__thread_active and cap.isOpened():
                if self.__thread_pause:
                    self.msleep(100)
                    continue
                
                ret, frame = cap.read()
                if ret:
                    retry_count = 0
                    self.process_frame(frame)
                else:
                    retry_count += 1
                    logging.warning("Frame read failed, retrying...")
                    if retry_count >= self.retry_limit:
                        logging.error("Maximum retry limit reached, attempting to reconnect...")
                        break
                    self.msleep(1000)

            if self.__thread_active:
                logging.info("Attempting to reconnect to the camera...")
                cap.release()
                self.msleep(5000)
        cap.release()

    def process_frame(self, frame):
        height, width, channels = frame.shape
        bytes_per_line = width * channels
        cv_rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qt_rgb_image = QImage(cv_rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        qt_rgb_image_scaled = qt_rgb_image.scaled(1280, 720, Qt.KeepAspectRatio)
        self.ImageUpdated.emit(qt_rgb_image_scaled)

    def stop(self) -> None:
        self.__thread_active = False

    def pause(self) -> None:
        self.__thread_pause = True

    def unpause(self) -> None:
        self.__thread_pause = False

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()

        self.url_1 = RTSP_URL_1
        self.url_2 = RTSP_URL_2
        self.url_3 = RTSP_URL_3
        self.url_4 = RTSP_URL_4

        self.list_of_cameras_state = {}

        self.camera_1 = QLabel()
        self.camera_1.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_1.setScaledContents(True)
        self.camera_1.installEventFilter(self)
        self.camera_1.setObjectName("Camera_1")
        self.list_of_cameras_state["Camera_1"] = "Normal"

        self.QScrollArea_1 = QScrollArea()
        self.QScrollArea_1.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_1.setWidgetResizable(True)
        self.QScrollArea_1.setWidget(self.camera_1)

        self.camera_2 = QLabel()
        self.camera_2.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_2.setScaledContents(True)
        self.camera_2.installEventFilter(self)
        self.camera_2.setObjectName("Camera_2")
        self.list_of_cameras_state["Camera_2"] = "Normal"

        self.QScrollArea_2 = QScrollArea()
        self.QScrollArea_2.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_2.setWidgetResizable(True)
        self.QScrollArea_2.setWidget(self.camera_2)

        self.camera_3 = QLabel()
        self.camera_3.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_3.setScaledContents(True)
        self.camera_3.installEventFilter(self)
        self.camera_3.setObjectName("Camera_3")
        self.list_of_cameras_state["Camera_3"] = "Normal"

        self.QScrollArea_3 = QScrollArea()
        self.QScrollArea_3.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_3.setWidgetResizable(True)
        self.QScrollArea_3.setWidget(self.camera_3)

        self.camera_4 = QLabel()
        self.camera_4.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_4.setScaledContents(True)
        self.camera_4.installEventFilter(self)
        self.camera_4.setObjectName("Camera_4")
        self.list_of_cameras_state["Camera_4"] = "Normal"

        self.QScrollArea_4 = QScrollArea()
        self.QScrollArea_4.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_4.setWidgetResizable(True)
        self.QScrollArea_4.setWidget(self.camera_4)

        self.__SetupUI()

        self.CaptureIpCameraFramesWorker_1 = CaptureIpCameraFramesWorker(self.url_1)
        self.CaptureIpCameraFramesWorker_1.ImageUpdated.connect(lambda image: self.ShowCamera1(image))

        self.CaptureIpCameraFramesWorker_2 = CaptureIpCameraFramesWorker(self.url_2)
        self.CaptureIpCameraFramesWorker_2.ImageUpdated.connect(lambda image: self.ShowCamera2(image))

        self.CaptureIpCameraFramesWorker_3 = CaptureIpCameraFramesWorker(self.url_3)
        self.CaptureIpCameraFramesWorker_3.ImageUpdated.connect(lambda image: self.ShowCamera3(image))

        self.CaptureIpCameraFramesWorker_4 = CaptureIpCameraFramesWorker(self.url_4)
        self.CaptureIpCameraFramesWorker_4.ImageUpdated.connect(lambda image: self.ShowCamera4(image))

        self.CaptureIpCameraFramesWorker_1.start()
        self.CaptureIpCameraFramesWorker_2.start()
        self.CaptureIpCameraFramesWorker_3.start()
        self.CaptureIpCameraFramesWorker_4.start()

    def __SetupUI(self) -> None:
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.addWidget(self.QScrollArea_1, 0, 0)
        grid_layout.addWidget(self.QScrollArea_2, 0, 1)
        grid_layout.addWidget(self.QScrollArea_3, 1, 0)
        grid_layout.addWidget(self.QScrollArea_4, 1, 1)

        self.widget = QWidget(self)
        self.widget.setLayout(grid_layout)

        self.setCentralWidget(self.widget)
        self.setMinimumSize(800, 600)
        self.showMaximized()
        self.setStyleSheet("QMainWindow {background: 'black';}")
        self.setWindowIcon(QIcon(QPixmap("rai.ico")))
        self.setWindowTitle(f"Retail AI CCTV System - {STORE_NAME}")

    @QtCore.pyqtSlot()
    def ShowCamera1(self, frame: QImage) -> None:
        self.camera_1.setPixmap(QPixmap.fromImage(frame))

    @QtCore.pyqtSlot()
    def ShowCamera2(self, frame: QImage) -> None:
        self.camera_2.setPixmap(QPixmap.fromImage(frame))

    @QtCore.pyqtSlot()
    def ShowCamera3(self, frame: QImage) -> None:
        self.camera_3.setPixmap(QPixmap.fromImage(frame))

    @QtCore.pyqtSlot()
    def ShowCamera4(self, frame: QImage) -> None:
        self.camera_4.setPixmap(QPixmap.fromImage(frame))

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if event.type() == QtCore.QEvent.MouseButtonDblClick:
            if source.objectName() == 'Camera_1':
                if self.list_of_cameras_state["Camera_1"] == "Normal":
                    self.QScrollArea_2.hide()
                    self.QScrollArea_3.hide()
                    self.QScrollArea_4.hide()
                    self.list_of_cameras_state["Camera_1"] = "Maximized"
                else:
                    self.QScrollArea_2.show()
                    self.QScrollArea_3.show()
                    self.QScrollArea_4.show()
                    self.list_of_cameras_state["Camera_1"] = "Normal"
            elif source.objectName() == 'Camera_2':
                if self.list_of_cameras_state["Camera_2"] == "Normal":
                    self.QScrollArea_1.hide()
                    self.QScrollArea_3.hide()
                    self.QScrollArea_4.hide()
                    self.list_of_cameras_state["Camera_2"] = "Maximized"
                else:
                    self.QScrollArea_1.show()
                    self.QScrollArea_3.show()
                    self.QScrollArea_4.show()
                    self.list_of_cameras_state["Camera_2"] = "Normal"
            elif source.objectName() == 'Camera_3':
                if self.list_of_cameras_state["Camera_3"] == "Normal":
                    self.QScrollArea_1.hide()
                    self.QScrollArea_2.hide()
                    self.QScrollArea_4.hide()
                    self.list_of_cameras_state["Camera_3"] = "Maximized"
                else:
                    self.QScrollArea_1.show()
                    self.QScrollArea_2.show()
                    self.QScrollArea_4.show()
                    self.list_of_cameras_state["Camera_3"] = "Normal"
            elif source.objectName() == 'Camera_4':
                if self.list_of_cameras_state["Camera_4"] == "Normal":
                    self.QScrollArea_1.hide()
                    self.QScrollArea_2.hide()
                    self.QScrollArea_3.hide()
                    self.list_of_cameras_state["Camera_4"] = "Maximized"
                else:
                    self.QScrollArea_1.show()
                    self.QScrollArea_2.show()
                    self.QScrollArea_3.show()
                    self.list_of_cameras_state["Camera_4"] = "Normal"
            else:
                return super(MainWindow, self).eventFilter(source, event)
            return True
        else:
            return super(MainWindow, self).eventFilter(source, event)

    def closeEvent(self, event) -> None:
        if self.CaptureIpCameraFramesWorker_1.isRunning():
            self.CaptureIpCameraFramesWorker_1.quit()
        if self.CaptureIpCameraFramesWorker_2.isRunning():
            self.CaptureIpCameraFramesWorker_2.quit()
        if self.CaptureIpCameraFramesWorker_3.isRunning():
            self.CaptureIpCameraFramesWorker_3.quit()
        event.accept()


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()