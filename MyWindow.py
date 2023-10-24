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
from PlotLine import *
import numpy as np
ext=(".txt",".csv")

PlotLines=[]
class InputDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(InputDialog, self).__init__(parent)
        self.setWindowTitle("Input Dialog")

        layout = QtWidgets.QVBoxLayout(self)

        self.input_label = QtWidgets.QLabel("Enter Number:")
        self.input_text = QtWidgets.QLineEdit(self)
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_text)

        self.ok_button = QtWidgets.QPushButton("OK", self)
        layout.addWidget(self.ok_button)
        self.ok_button.clicked.connect(self.accept)

        self.cancel_button = QtWidgets.QPushButton("Cancel", self)
        layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.reject)
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
        self.actionSIN.triggered.connect(self.AddSin)
        self.actionCOSINE.triggered.connect(self.AddCos)
        self.actionEnter_Frequency.triggered.connect(self.EnterFrequency)
        self.actionEnter_Magnitude.triggered.connect(self.EnterMagnitude)
        self.actionLoad.triggered.connect(self.Load)

    
    # def AddSin(self):
    #     newplot = PlotLine()
    #     newplot.Frequency = 10
    #     newplot.magnitude = 10
    #     num_points = 1500
    #     t = np.linspace(0, 1, num_points)
    #     newplot.signal = (np.sin(2 * np.pi * newplot.Frequency * t)) * newplot.magnitude
    #     PlotLines.append(newplot)
    #     self.graphWidget1.plot(t, newplot.signal)
        
    #     newplot.Samplingfrequency = 4*newplot.Frequency
    #     newplot.SamplingInterval = 1 / newplot.Samplingfrequency
    #     t2 = np.arange(0, 1, newplot.SamplingInterval)
    #     newplot.sampledSignal = (np.sin(2 * np.pi * newplot.Frequency * t2)) * newplot.magnitude
    #     self.graphWidget1.plot(t2, newplot.sampledSignal, symbol='+')
        
    #     # Calculate the number of samples in the input signal
    #     num_samples = len(newplot.sampledSignal)
        
    #     # Calculate the sampling interval
    #     sampling_interval = 1.0 / newplot.Samplingfrequency

    #     # Create a time vector based on the original duration
    #     t_original = np.linspace(0, 1, num_samples, endpoint=False)

    #     # Initialize the reconstructed signal
    #     reconstructed_signal = np.zeros(len(t))
        
    #     # Perform signal reconstruction using sinc interpolation
    #     for n in range(num_samples):
    #         reconstructed_signal += newplot.sampledSignal[n] * np.sinc((t-(n*sampling_interval))/sampling_interval)
    #     # Plot the reconstructed signal
    #     self.graphWidget2.plot(t, reconstructed_signal)

    def AddSin(self):
        newplot = PlotLine()
        newplot.Frequency = 5
        newplot.magnitude = 10
        num_points = 1000
        t = np.linspace(0, 1, num_points)
        newplot.signal = (np.sin(2 * np.pi * newplot.Frequency * t)) * newplot.magnitude
        PlotLines.append(newplot)
        self.graphWidget1.plot(t, newplot.signal)
        
        newplot.Samplingfrequency = (2*newplot.Frequency)+2
        newplot.SamplingInterval = 1 / newplot.Samplingfrequency
        t2 = np.arange(0, 1, newplot.SamplingInterval)
        newplot.sampledSignal = (np.sin(2 * np.pi * newplot.Frequency * t2)) * newplot.magnitude
        self.graphWidget1.plot(t2, newplot.sampledSignal, symbol='+')
        
        # Calculate the number of samples in the input signal
        num_samples = len(newplot.sampledSignal)
        
        # Calculate the sampling interval
        sampling_interval = 1.0 / newplot.Samplingfrequency

        # Create a time vector based on the original duration

        # Initialize the reconstructed signal
        reconstructed_signal = np.zeros(len(t))
        
        # Perform signal reconstruction using sinc interpolation
        for n in range(num_samples):
            reconstructed_signal += newplot.sampledSignal[n] * np.sinc((t-(n*sampling_interval))/sampling_interval)
        # Plot the reconstructed signal
        self.graphWidget2.plot(t, reconstructed_signal)

    def AddCos(self):
        newplot=PlotLine()
        newplot.Frequency=10
        newplot.magnitude=10
        num_points = 1000
        t = np.linspace(0, 1, num_points)
        newplot.signal = (np.cos(2*np.pi*newplot.Frequency*t))*newplot.magnitude
        PlotLines.append(newplot)
        self.graphWidget1.plot(t,newplot.signal)
    def EnterFrequency(self):
        
          dialog = InputDialog(self)
          result = dialog.exec_()  # This will block until the user closes the dialog

          if result == QtWidgets.QDialog.Accepted:
             user_input = dialog.input_text.text()
             PlotLines[-1].Frequency=int(user_input)
             self.updatefunction()
    def EnterMagnitude(self):
        
          dialog = InputDialog(self)
          result = dialog.exec_()  # This will block until the user closes the dialog

          if result == QtWidgets.QDialog.Accepted:
             user_input = dialog.input_text.text()
             PlotLines[-1].magnitude=int(user_input)
             self.graphWidget1.clear()
             self.updatefunction()
          
            

    def updatefunction(self):
         self.graphWidget1.clear()
         t = np.linspace(0, 1, 1000)
         PlotLines[-1].signal=(np.sin(2*np.pi* PlotLines[-1].Frequency*t))* PlotLines[-1].magnitude
         self.graphWidget1.plot(t,PlotLines[-1].signal)

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
                    self.graphWidget1.plot(newplot.data['time'],newplot.data['amplitude'])
                    PlotLines.append(newplot)

                else:
                    newplot = PlotLine()
                    newplot.data = pd.read_csv(path, usecols=["time", "amplitude"])
                    self.graphWidget1.plot(newplot.data['time'],newplot.data['amplitude'])
                    PlotLines.append(newplot)
            
            else:
                    self.ErrorMsg("You can only load .txt or .csv files.")





 
