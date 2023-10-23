from PyQt5 import QtWidgets, uic, QtCore
from pyqtgraph import PlotWidget, plot
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QPushButton,
    QWidget,
    QErrorMessage,
    QMessageBox,
    QDialog,
    QScrollBar
)
from collections import deque
import pyqtgraph as pg
import pandas as pd
import sys
import os
import time
from PIL import Image
import tkinter as tk
from tkinter import colorchooser
from PyQt5.QtGui import QImage
import io
from PIL import Image as PILImage
import PIL
import tempfile
from fpdf import FPDF
import random

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("GUI.ui",self)
        self.graphWidget1 = pg.PlotWidget()
        self.graphWidget2 = pg.PlotWidget()
        self.graphWidget3 = pg.PlotWidget()
        self.ui.verticalLayout_8.addWidget(self.graphWidget1)
        self.ui.verticalLayout_6.addWidget(self.graphWidget2)
        self.ui.verticalLayout_7.addWidget(self.graphWidget3)
        self.actionLoad.triggered.connect(self.Load)

        def Load(self):
            filename = QtWidgets.QFileDialog.getOpenFileName()
            path = filename[0]
            if path.endswith(ext):
                if path.endswith(".txt"):
                    with open(path, "r") as data:
                        x = []
                        y = []
                        for line in data:
                            p = line.split()
                            x.append(float(p[0]))
                            y.append(float(p[1]))
                    newplot = PlotLine()
                    newplot.data = pd.DataFrame({"time": x, "amplitude": y})
                    PlotLines1.append(newplot)
                    newplot.ChannelNum = 1
                else:
                    newplot = PlotLine()
                    newplot.data = pd.read_csv(path, usecols=["time", "amplitude"])
                    PlotLines1.append(newplot)
                    newplot.ChannelNum = 1
            else:
                self.ErrorMsg("You can only load .txt or .csv files.")