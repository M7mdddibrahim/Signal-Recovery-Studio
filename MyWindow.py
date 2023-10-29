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
import scipy.special as sp
import math
ext=(".txt",".csv")

PlotLines=[]
SinCos = []

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
        self.legend1 = self.graphWidget1.addLegend()
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
        self.SamplingSlider.setMinimum(1)
        self.SamplingSlider.setMaximum(30)
        self.NoiseSlider.setMinimum(1)
        self.NoiseSlider.setMaximum(100)
        self.SamplingSlider.valueChanged.connect(self.SamplingSliderfunc)
        self.NoiseSlider.valueChanged.connect(self.NoiseSliderfunc)
        self.enteredsampledfreq = None
        self.comboBox.addItem("Choose Signal")
        self.SinCount = 0
        self.CosCount = 0


    
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

    def ErrorMsg(self, text):
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setText(text)
        msg.setIcon(QMessageBox.Warning)
        x = msg.exec_()

    def SamplingSliderfunc(self, value):
        self.SamplingLabel.setText(str(value))
        self.enteredsampledfreq = int(value)
        self.updatefunction()
        return value
    
    def NoiseSliderfunc(self, value):
        self.NoiseLabel.setText(str(value))

    def random_color(self):
        red = random.randint(0,255)
        green = random.randint(0,255)
        blue = random.randint(0,255)
        
        return (red,green,blue)

    def AddSin(self):
        newplot = PlotLine()
        newplot.signaltype=1
        newplot.Frequency = 5
        newplot.magnitude = 10
        num_points = 1000
        newplot.signaltime = np.linspace(0, 1, num_points)
        newplot.signal = (np.sin(2 * np.pi * newplot.Frequency *  newplot.signaltime)) * newplot.magnitude
        SinCos.append(newplot)
        self.SinCount += 1
        newplot.name = "Sin " + str(self.SinCount)
        self.comboBox.addItem(newplot.name)
        newplot.pen = pg.mkPen(color = self.random_color())
        newplot.data_line = self.graphWidget1.plot(newplot.signaltime, newplot.signal,pen = newplot.pen,name = newplot.name)
        self.ComposedSignal()

    def AddCos(self):
        newplot=PlotLine()
        newplot.signaltype=2
        newplot.Frequency=10
        newplot.magnitude=10
        num_points = 1000
        newplot.signaltime = np.linspace(0, 1, num_points)
        newplot.signal = (np.cos(2*np.pi*newplot.Frequency* newplot.signaltime))*newplot.magnitude
        SinCos.append(newplot)
        self.CosCount += 1
        newplot.name = "Cos " + str(self.CosCount)
        self.comboBox.addItem(newplot.name)
        newplot.pen = pg.mkPen(color = self.random_color())
        newplot.data_line = self.graphWidget1.plot( newplot.signaltime,newplot.signal,pen = newplot.pen,name = newplot.name)
        self.ComposedSignal()

    def ComposedSignal(self):
        newplot = PlotLine()
        newplot.signaltype=2
        newplot.Frequency=10
        newplot.magnitude=10
        num_points = 1000
        newplot.signaltime = np.linspace(0, 1, num_points)
        newplot.signal = np.zeros(num_points)
        global SinCos
        global PlotLines
        for plot in SinCos:
                newplot.signal = np.add(newplot.signal,plot.signal)
        self.graphWidget1.clear()
        PlotLines = []
        PlotLines.append(newplot)
        newplot.pen = pg.mkPen(color = self.random_color())
        newplot.name = "Composed Signal"
        newplot.data_line = self.graphWidget1.plot(newplot.signaltime,newplot.signal,pen=newplot.pen,name=newplot.name)
        self.sampling()
        self.GetChosenPlotLine()
        
    def GetChosenPlotLine(self):
        name = self.comboBox.currentText()
        for newplot in SinCos:
            if name == newplot.name:
                return newplot
                #Succefully found the plot
        self.ErrorMsg("No Chosen Signal")
        #Failed to find the plot

    def Reconstruction(self):
        newplot=PlotLines[-1]
        if(newplot.islouded==1):
            num_samples = len(newplot.sampledSignalAmplitude)
            sampling_interval = 1.0 / newplot.Samplingfrequency
        # Initialize the reconstructed signal
            t=newplot.data['time'].values
            reconstructed_signal = np.zeros(len( t))
            for n in range(newplot.num_samples):
              reconstructed_signal += newplot.sampledSignalAmplitude[n] * np.sinc((t-(n*sampling_interval))/sampling_interval)
            # self.graphWidget2.clear()
            # print("new signal")
            # print(reconstructed_signal)
            # print("old signal")
            # print(newplot.data['amplitude'].values)
            # print('recover amplitude')
            # print(reconstructed_signal)
            self.graphWidget3.clear()
            self.graphWidget3.plot( t, reconstructed_signal)
        else:
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
        newplot.Samplingfrequency = (3*newplot.Frequency)
        if (self.enteredsampledfreq != None):
            newplot.Samplingfrequency = self.enteredsampledfreq*newplot.Frequency

        newplot.SamplingInterval = 1 / newplot.Samplingfrequency
        t2 = np.arange(0, 1, newplot.SamplingInterval)
        if (newplot.signaltype==1):
          newplot.sampledSignal = (np.sin(2 * np.pi * newplot.Frequency * t2)) * newplot.magnitude
          print(len(t2), len(newplot.sampledSignal))
          print(newplot.SamplingInterval,newplot.Samplingfrequency)
          self.graphWidget1.plot(t2, newplot.sampledSignal, symbol='+')
          self.Reconstruction()
        elif (newplot.signaltype==2):
            newplot.sampledSignal = (np.cos(2 * np.pi * newplot.Frequency * t2)) * newplot.magnitude
            self.graphWidget1.plot(t2, newplot.sampledSignal, symbol='+')
            self.Reconstruction()
        elif (newplot.islouded==1):
            # samplesize=len(np.arange(0, newplot.data['time'].max(), newplot.SamplingInterval))
            # sample_indices = np.random.choice(len(newplot.data['amplitude']), size=samplesize, replace=True)
            # newplot.sampledSignalAmplitude=newplot.data['amplitude'][sample_indices]
            # newplot.sampledSignalTime=newplot.data['time'][sample_indices]
            # print('lookat')
            # print((samplesize))
            # self.graphWidget2.plot(newplot.sampledSignalTime, newplot.sampledSignalAmplitude, symbol='+')
            # self.Reconstruction()
            # pass
            self.graphWidget1.plot(newplot.data['time'],newplot.data['amplitude'],pen=newplot.pen)
            newplot.num_samples=math.ceil(newplot.Samplingfrequency*newplot.data['time'].max())
            print('sampling frequency')
            print(newplot.Samplingfrequency,newplot.Frequency)
            newplot.sampledSignalAmplitude,newplot.sampledSignalTime=scipy.signal.resample(newplot.data['amplitude'],int(newplot.num_samples),newplot.data['time'])

            print('lookat')
            print(len(newplot.sampledSignalAmplitude),len(newplot.sampledSignalTime))
            self.graphWidget2.clear()
            self.graphWidget2.plot(newplot.sampledSignalTime, newplot.sampledSignalAmplitude, symbol='+')
            self.Reconstruction()
            pass
        # self.graphWidget1.plot(t2, newplot.sampledSignal, symbol='+')
        # self.Reconstruction()



    def EnterFrequency(self):
        
          dialog = InputDialog(self)
          result = dialog.exec_()  # This will block until the user closes the dialog

          if result == QtWidgets.QDialog.Accepted:
             user_input = dialog.input_text.text()
             PlotLines[-1].Frequency=int(user_input)
             self.updatefunction()

    def remove(self):
        global PlotLines
        self.graphWidget1.clear()
        self.graphWidget2.clear()
        self.graphWidget3.clear()
        self.SinCount = 0
        self.CosCount = 0
        self.comboBox.clear()
        self.comboBox.addItem("Choose Signal")
        PlotLines = []

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
                    newplot.pen = pg.mkPen(color = self.random_color())
                    newplot.name = "Signal 1"
                    newplot.data_line = self.graphWidget1.plot(newplot.data['time'],newplot.data['amplitude'],pen=newplot.pen,name = newplot.name)
                    PlotLines.append(newplot)
                    newplot.islouded=1
                    #method1
                     # Compute spectrogram
                    # fs = 1000  # Sampling frequency
                    # f, t, Sxx = signal.spectrogram(newplot.data['amplitude'], fs)

                    # # Find maximum frequency across entire signal
                    # max_index = np.argmax(np.amax(Sxx, axis=1))
                    # max_frequency = f[max_index]
                    # method 3
                    ampltude = np.ascontiguousarray(newplot.data['amplitude'])

                    # Check the data type of the data
                    if ampltude.dtype != np.float64:
                       ampltude = ampltude.astype(np.float64)
                    magnitudes = np.abs(scipy.fft.rfft(ampltude))/np.max(np.abs(scipy.fft.rfft(ampltude)))
                    frequencies = scipy.fft.rfftfreq(len(newplot.data['time']), (newplot.data['time'][1] - newplot.data['time'][0]))
                    for index, frequency in enumerate(frequencies):
                        if magnitudes[index] >= 0.05: maximumFrequency = frequency
                   
                    newplot.Frequency=math.ceil(maximumFrequency)
                    self.sampling()

                else:
                    newplot = PlotLine()
                    newplot.data = pd.read_csv(path, usecols=["time", "amplitude"])
                    newplot.name = "Signal 1"
                    newplot.pen = pg.mkPen(color = self.random_color())
                    newplot.data_line = self.graphWidget1.plot(newplot.data['time'],newplot.data['amplitude'],pen = newplot.pen,name = newplot.name)
                    newplot.islouded=1
                    PlotLines.append(newplot)
                    #method 1
                    # # Compute spectrogram
                    # fs = 1000  # Sampling frequency
                    # f, t, Sxx = signal.spectrogram(newplot.data['amplitude'], fs)

                    # # Find maximum frequency across entire signal
                    # max_index = np.argmax(np.amax(Sxx, axis=1))
                    # max_frequency = f[max_index]
                      #method 2
                    # fft = np.fft.fft(newplot.data['amplitude'])

                    # # Compute the frequency spectrum
                    # freq = np.fft.fftfreq(len(newplot.data['amplitude'])) * len(newplot.data['amplitude'])

                    # # Find the index of the maximum value in the frequency spectrum
                    # max_index = np.argmax(np.abs(fft))

                    # # Compute the corresponding frequency
                    # max_freq = freq[max_index]
                    # method 3
                    ampltude = np.ascontiguousarray(newplot.data['amplitude'])

                    # Check the data type of the data
                    if ampltude.dtype != np.float64:
                       ampltude = ampltude.astype(np.float64)
                    magnitudes = np.abs(scipy.fft.rfft(ampltude))/np.max(np.abs(scipy.fft.rfft(ampltude)))
                    frequencies = scipy.fft.rfftfreq(len(newplot.data['time']), (newplot.data['time'][1] - newplot.data['time'][0]))
                    for index, frequency in enumerate(frequencies):
                        if magnitudes[index] >= 0.05: maximumFrequency = frequency
      
                    newplot.Frequency=math.ceil(maximumFrequency)
                    print("max freq", newplot.Frequency)
                    self.sampling()
            
            else:
                    self.ErrorMsg("You can only load .txt or .csv files.")





 
