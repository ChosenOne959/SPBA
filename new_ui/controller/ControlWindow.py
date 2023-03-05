import subprocess
from Work_Place.Ui_workplace import Ui_Work_Win
import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QMessageBox, QGraphicsScene, QGraphicsPixmapItem
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer
import cv2
import os
import time
import pandas as pd
import numpy as np
import re
from new_ui.controller.keyboard_controler import keyboard_control
from new_ui.controller.Ui_Control_Window import Ui_ControlWindow
import json
import threading
from SPBA_API import Multirotor


class ControlWindow(QtWidgets.QWidget, Ui_ControlWindow):
    def __init__(self, SharedData, parent=None):
        self.SharedData = SharedData
        super(ControlWindow, self).__init__(parent)
        self.setupUi(self)
        self.set_myUI()

        self.Multirotor = Multirotor(self.SharedData)

        # self.init_timer()

    def set_myUI(self):
        """
        set_myUI : set basic signal slots
        """
        self.KeyboardCtrl.clicked.connect(self.keyboard_controler)


    def keyboard_controler(self):
        keyboard_thread = threading.Thread(target=keyboard_control)
        keyboard_thread.start()

    def init_timer(self):
        self.realtiemWindow_check_interval = QTimer(self)
        self.realtiemWindow_check_interval.timeout.connect(self.time_out)
        self.time_interval = 1500
        self.realtiemWindow_check_interval.start(self.time_interval)

    def time_out(self):

        if self.check_flag == 1:
            self.realtime_check()

    def realtime_check(self):
        if self.Realtime_Sensor_Win.isVisible() == True:
            pass
        else:
            self.pushButton_2.setEnabled(False)
            self.KeyboardCtrl.setEnabled(False)
            # self.realtiemWindow_check_interval.stop()
            self.check_flag = 0

    def mainWindow(self):
        self.close()
