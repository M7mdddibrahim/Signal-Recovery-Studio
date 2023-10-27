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
    QSlider,
    QLabel
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
import scipy.signal
from scipy import signal
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
        self.actionRemove_all.triggered.connect(self.remove)
        self.SamplingSlider = self.findChild(QSlider,"verticalSlider")
        self.SamplingLabel = self.findChild(QLabel,"SamplingNumber")
        self.NoiseSlider = self.findChild(QSlider,"verticalSlider_2")
        self.NoiseLabel = self.findChild(QLabel,"NoiseNumber")
        self.SamplingSlider.valueChanged.connect(self.SamplingSliderfunc)
        self.NoiseSlider.valueChanged.connect(self.NoiseSliderfunc)
        self.SamplingSlider.setMinimum(1)
        self.SamplingSlider.setMaximum(100)
        self.NoiseSlider.setMinimum(1)
        self.NoiseSlider.setMaximum(100)

    def SamplingSliderfunc(self, value):
        self.SamplingLabel.setText(str(value))
        self.enteredsampledfreq = int(value)
        self.updatefunction()
        return value
    def NoiseSliderfunc(self, value):
        self.NoiseLabel.setText(str(value))
        self.EnterNewNoise = int(value)
        self.updatefunction()
        return value

    def AddSin(self):
        newplot = PlotLine()
        newplot.signaltype=1
        newplot.Frequency = 5
        newplot.magnitude = 10
        num_points = 1000
        newplot.signaltime = np.linspace(0, 1, num_points)
        newplot.signal = (np.sin(2 * np.pi * newplot.Frequency *  newplot.signaltime)) * newplot.magnitude
        PlotLines.append(newplot)
        self.graphWidget1.plot( newplot.signaltime, newplot.signal)
        self.sampling()

    def Reconstruction(self):
        newplot=PlotLines[-1]
        if(newplot.islouded==1):
            num_samples = len(newplot.sampledSignalAmplitude)
            sampling_interval = 1.0 / newplot.Samplingfrequency
        # Initialize the reconstructed signal
            reconstructed_signal = np.zeros(len( newplot.sampledSignalTime))
            for n in range(num_samples):
              reconstructed_signal += newplot.sampledSignalAmplitude[n] * np.sinc(( newplot.sampledSignalTime-(n*sampling_interval))/sampling_interval)
            self.graphWidget2.clear()
            self.graphWidget2.plot( newplot.sampledSignalTime, reconstructed_signal)
            pass
        num_samples = len(newplot.sampledSignal)
        
        # Calculate the sampling interval
        sampling_interval = 1.0 / newplot.Samplingfrequency

        # Create a time vector based on the original duration

        # Initialize the reconstructed signal
        reconstructed_signal = np.zeros(len( newplot.signaltime))
        
        # Perform signal reconstruction using sinc interpolation
        for n in range(num_samples):
            reconstructed_signal += newplot.sampledSignal[n] * np.sinc(( newplot.signaltime-(n*sampling_interval))/sampling_interval)
        # Plot the reconstructed signal
        self.graphWidget2.clear()
        self.graphWidget2.plot( newplot.signaltime, reconstructed_signal)

    def sampling(self):
        newplot=PlotLines[-1]
        newplot.Samplingfrequency = (2*newplot.Frequency)
        if (self.enteredsampledfreq != None):
            newplot.Samplingfrequency = 2*self.enteredsampledfreq

        newplot.SamplingInterval = 1 / newplot.Samplingfrequency
        if (self. EnterNewNoise == 0):
            t2 = np.arange(0, 1, newplot.SamplingInterval)
            if (newplot.signaltype==1):
                newplot.sampledSignal = (np.sin(2 * np.pi * newplot.Frequency * t2)) * newplot.magnitude
            elif(newplot.signaltype==2):
                newplot.sampledSignal = (np.cos(2 * np.pi * newplot.Frequency * t2)) * newplot.magnitude
            elif(newplot.islouded==1):
                newplot.sampledSignalAmplitude,newplot.sampledSignalTime=scipy.signal.resample(newplot.data['amplitude'],int(len(newplot.data))*2,newplot.data['time'])
        else:
            t2 = np.arange(0, 1, newplot.SamplingInterval)
            if (newplot.signaltype==1):
                newplot.sampledSignal = (np.sin(2 * np.pi * newplot.Frequency * t2)) * newplot.magnitude + (np.random.randn(len(t2)) * self.EnterNewNoise) 
            elif(newplot.signaltype==2):
                newplot.sampledSignal = (np.cos(2 * np.pi * newplot.Frequency * t2)) * newplot.magnitude + (np.random.randn(len(t2)) * self.EnterNewNoise) 
            elif(newplot.islouded==1):
                newplot.sampledSignalAmplitude,newplot.sampledSignalTime=scipy.signal.resample(newplot.data['amplitude'],int(len(newplot.data))*2,newplot.data['time'])

            print('lookat')
            print(len(newplot.sampledSignalAmplitude),len(newplot.sampledSignalTime))
            self.graphWidget1.plot(newplot.sampledSignalTime, newplot.sampledSignalAmplitude, symbol='+')
            self.Reconstruction()
            pass
        self.graphWidget1.plot(t2, newplot.sampledSignal, symbol='+')
        self.Reconstruction()

    def AddCos(self):
        newplot=PlotLine()
        newplot.signaltype=2
        newplot.Frequency=10
        newplot.magnitude=10
        num_points = 1000
        newplot.signaltime = np.linspace(0, 1, num_points)
        newplot.signal = (np.cos(2*np.pi*newplot.Frequency* newplot.signaltime))*newplot.magnitude
        PlotLines.append(newplot)
        self.graphWidget1.plot( newplot.signaltime,newplot.signal)
        self.sampling()

    def EnterFrequency(self):
        
          dialog = InputDialog(self)
          result = dialog.exec_()  # This will block until the user closes the dialog

          if result == QtWidgets.QDialog.Accepted:
             user_input = dialog.input_text.text()
             PlotLines[-1].Frequency=int(user_input)
             self.updatefunction()

    def remove(self):
        self.graphWidget1.clear()
        self.graphWidget2.clear()
        self.graphWidget3.clear()

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
         newplot=PlotLines[-1]

         t = np.linspace(0, 1, 1000)
         if (newplot.signaltype==1):
            newplot.signal=(np.sin(2*np.pi* newplot.Frequency*t))* newplot.magnitude
         elif (newplot.signaltype==2):
              newplot.signal=(np.cos(2*np.pi* newplot.Frequency*t))* newplot.magnitude
              self.graphWidget1.plot(t,PlotLines[-1].signal)
         self.sampling()
         self.Reconstruction()

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
                    newplot.islouded=1

                else:
                    newplot = PlotLine()
                    newplot.data = pd.read_csv(path, usecols=["time", "amplitude"])
                    self.graphWidget1.plot(newplot.data['time'],newplot.data['amplitude'])
                    newplot.islouded=1
                    PlotLines.append(newplot)
                    # Compute spectrogram
                    fs = 1000  # Sampling frequency
                    f, t, Sxx = signal.spectrogram(newplot.data['amplitude'], fs)

                    # Find maximum frequency across entire signal
                    max_index = np.argmax(np.amax(Sxx, axis=1))
                    max_frequency = f[max_index]
                    newplot.Frequency=max_frequency
                    self.sampling()
            
            else:
                    self.ErrorMsg("You can only load .txt or .csv files.")





 
