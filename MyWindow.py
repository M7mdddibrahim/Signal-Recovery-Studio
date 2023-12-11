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
    QLabel,
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

ext = (".txt", ".csv")

PlotLines = []
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
        self.ui = uic.loadUi("GUI-3.ui", self)
        self.graphWidget1 = pg.PlotWidget()
        self.legend1 = self.graphWidget1.addLegend()
        self.graphWidget2 = pg.PlotWidget()
        self.graphWidget3 = pg.PlotWidget()
        self.ui.verticalLayout_8.addWidget(self.graphWidget1)
        self.ui.verticalLayout_6.addWidget(self.graphWidget2)
        self.ui.verticalLayout_7.addWidget(self.graphWidget3)
        self.SinButton.clicked.connect(self.AddSin)
        self.CosButton.clicked.connect(self.AddCos)
        self.Frequency.textChanged.connect(self.EnterFrequency)
        self.Magnitude.textChanged.connect(self.EnterMagnitude)
        self.Phase.textChanged.connect(self.EnterPhase)
        self.actionLoad.triggered.connect(self.Load)
        self.ClearGraph.clicked.connect(self.remove)
        self.SamplinginFmax = self.findChild(QSlider, "verticalSlider")
        self.SamplingLabel = self.findChild(QLabel, "FMaxNum")
        self.NoiseSlider = self.findChild(QSlider, "verticalSlider_2")
        self.NoiseLabel = self.findChild(QLabel, "NoiseNum")
        self.SamplinginHz = self.findChild(QSlider, "verticalSlider_3")
        self.SamplingInHzLabel = self.findChild(QLabel, "HzNum")
        self.samplingFreqNum = self.findChild(QLabel, "label_18")
        self.Fmax = self.findChild(QLabel, "label_20")
        self.actionSampling.triggered.connect(self.SamplingTextfunc)
        self.SamplinginFmax.setMinimum(0)
        self.SamplinginFmax.setMaximum(30)
        self.NoiseSlider.setMinimum(0)
        self.NoiseSlider.setMaximum(50)
        self.SamplinginFmax.valueChanged.connect(self.samplingInFmaxFunc)
        self.NoiseSlider.valueChanged.connect(self.NoiseSliderfunc)
        self.SamplinginHz.valueChanged.connect(self.samplingInHz)
        self.enteredsampledfreq = None
        self.comboBox.addItem("Choose Signal")
        self.SinCount = 0
        self.CosCount = 0
        self.SNR = None
        self.isFmax_Text_Hz = 0

    def ErrorMsg(self, text):
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setText(text)
        msg.setIcon(QMessageBox.Warning)
        x = msg.exec_()

    def samplingInFmaxFunc(self, value):
        self.isFmax_Text_Hz = 1
        self.SamplingLabel.setText(str(value))
        self.enteredsampledfreq = int(value)
        # self.updatefunction()
        self.sampling()
        return value

    def SamplingTextfunc(self, value):
        self.isFmax_Text_Hz = 2
        dialog = InputDialog(self)
        result = dialog.exec_()  # This will block until the user closes the dialog
        if result == QtWidgets.QDialog.Accepted:
            value = dialog.input_text.text()
        # self.SamplingLabel.setText(str(value))
        self.enteredsampledfreq = int(value)
        self.sampling()
        return value

    def NoiseSliderfunc(self, value):
        self.NoiseLabel.setText(str(value))
        self.SNR = int(value)
        # self.updatefunction()
        self.sampling()

    def samplingInHz(self, value):
        self.isFmax_Text_Hz = 1
        newplot = PlotLines[-1]
        self.SamplingInHzLabel.setText(str(value))
        # self.updatefunction()
        self.sampling()

    def random_color(self):
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)

        return (red, green, blue)

    def AddSin(self):
        newplot = PlotLine()
        newplot.signaltype = 1
        newplot.Frequency = 1
        newplot.magnitude = 10
        num_points = 3000
        self.enteredsampledfreq = 2
        newplot.signaltime = np.linspace(0, 10, num_points)
        newplot.signal = (
            np.sin(2 * np.pi * newplot.Frequency * newplot.signaltime)
        ) * newplot.magnitude
        SinCos.append(newplot)
        self.SinCount += 1
        newplot.name = "Sin " + str(self.SinCount)
        self.comboBox.addItem(newplot.name)
        newplot.pen = pg.mkPen(color=self.random_color())
        # newplot.data_line = self.graphWidget1.plot(newplot.signaltime, newplot.signal,pen = newplot.pen,name = newplot.name)
        self.ComposedSignal()

    def AddCos(self):
        newplot = PlotLine()
        newplot.signaltype = 2
        newplot.Frequency = 1
        newplot.magnitude = 10
        num_points = 3000
        self.enteredsampledfreq = 2
        newplot.signaltime = np.linspace(0, 10, num_points)
        newplot.signal = (
            np.cos(2 * np.pi * newplot.Frequency * newplot.signaltime)
        ) * newplot.magnitude
        SinCos.append(newplot)
        self.CosCount += 1
        newplot.name = "Cos " + str(self.CosCount)
        self.comboBox.addItem(newplot.name)
        newplot.pen = pg.mkPen(color=self.random_color())
        # newplot.data_line = self.graphWidget1.plot( newplot.signaltime,newplot.signal,pen = newplot.pen,name = newplot.name)
        self.ComposedSignal()

    def ComposedSignal(self):
        newplot = PlotLine()
        newplot.Frequency = 1
        newplot.magnitude = 10
        num_points = 3000
        newplot.signaltime = np.linspace(0, 10, num_points)
        newplot.signal = np.zeros(num_points)
        global SinCos
        global PlotLines
        fmax = 0
        for plot in SinCos:
            # newplot.signal = np.add(newplot.signal,plot.signal)
            newplot.signal += plot.signal
            if plot.signaltype == 2:
                newplot.signaltype = 2
            print(plot.Frequency)
            if plot.Frequency > fmax:
                fmax = plot.Frequency
        newplot.Frequency = fmax
        # ampltude = np.ascontiguousarray(newplot.signal)
        # Check the data type of the data
        # if ampltude.dtype != np.float64:
        #     ampltude = ampltude.astype(np.float64)
        # magnitudes = np.abs(scipy.fft.rfft(ampltude)) / np.max(
        #     np.abs(scipy.fft.rfft(ampltude))
        # )
        # frequencies = scipy.fft.rfftfreq(
        #     len(newplot.signaltime), (newplot.signaltime[1] - newplot.signaltime[0])
        # )
        # for index, frequency in enumerate(frequencies):
        #     if magnitudes[index] >= 0.05:
        #         maximumFrequency = frequency

        # newplot.Frequency = math.ceil(maximumFrequency)
        self.graphWidget1.clear()
        PlotLines = []
        PlotLines.append(newplot)
        newplot.pen = pg.mkPen(color=self.random_color())
        newplot.name = "Composed Signal"
        newplot.data_line = self.graphWidget1.plot(
            newplot.signaltime, newplot.signal, pen=newplot.pen, name=newplot.name
        )
        # print(PlotLines)
        self.sampling()
        # self.GetChosenPlotLine()

    def GetChosenPlotLine(self):
        name = self.comboBox.currentText()
        for newplot in SinCos:
            if name == newplot.name:
                return newplot
                # Succefully found the plot
        self.ErrorMsg("No Chosen Signal")
        # Failed to find the plot

    def Reconstruction(self):
        newplot = PlotLines[-1]
        if newplot.isloaded == 1:
            num_samples = len(newplot.sampledSignalAmplitude)
            sampling_interval = 1.0 / newplot.Samplingfrequency
            # Initialize the reconstructed signal
            t = newplot.data["time"]
            reconstructed_signal = np.zeros(len(t))
            for n in range(newplot.num_samples):
                reconstructed_signal += newplot.sampledSignalAmplitude[n] * np.sinc(
                    (t - (n * sampling_interval)) / sampling_interval
                )

            newplot.reconstructed_signal = reconstructed_signal
            self.graphWidget2.clear()
            self.graphWidget2.plot(t, reconstructed_signal, pen="y")
            self.ErrorGraph()
        else:
            num_samples = len(newplot.sampledSignalAmplitude)
            sampling_interval = 1.0 / newplot.Samplingfrequency
            t = newplot.signaltime
            reconstructed_signal = np.zeros(len(t))
            for n in range(newplot.num_samples):
                reconstructed_signal += newplot.sampledSignalAmplitude[n] * np.sinc(
                    (t - (n * sampling_interval)) / sampling_interval
                )
            newplot.reconstructed_signal = reconstructed_signal
            self.graphWidget2.clear()
            self.graphWidget2.plot(t, reconstructed_signal, pen="y")
            self.ErrorGraph()

    def sampling(self):
        if len(PlotLines) > 0:
            newplot = PlotLines[-1]
            if self.isFmax_Text_Hz == 0:
                newplot.Samplingfrequency = (2 * newplot.Frequency) + 1
                newplot.SamplingInterval = 1 / newplot.Samplingfrequency
            elif self.isFmax_Text_Hz == 1 and self.enteredsampledfreq != None:
                if self.enteredsampledfreq == 1:
                    newplot.Samplingfrequency = (
                        self.enteredsampledfreq * newplot.Frequency
                    ) + self.SamplinginHz.value()
                else:
                    newplot.Samplingfrequency = (
                        self.enteredsampledfreq * newplot.Frequency
                    ) + self.SamplinginHz.value()
                newplot.SamplingInterval = 1 / newplot.Samplingfrequency
            elif (
                self.isFmax_Text_Hz == 2 or self.isFmax_Text_Hz == 3
            ) and self.enteredsampledfreq != None:
                newplot.Samplingfrequency = self.enteredsampledfreq
                newplot.SamplingInterval = 1 / newplot.Samplingfrequency
            if newplot.isloaded == 1 and self.SNR==None:
                newplot.num_samples = math.ceil(
                    newplot.Samplingfrequency * newplot.data["time"].max()
                )
                self.samplingFreqNum.setText(f"Value: {newplot.Samplingfrequency}")
                self.Fmax.setText(f"Value: {newplot.Frequency}")
                print("sampling frequency")
                print(newplot.Samplingfrequency, newplot.Frequency)
                (
                    newplot.sampledSignalAmplitude,
                    newplot.sampledSignalTime,
                ) = scipy.signal.resample(
                    newplot.data["amplitude"],
                    int(newplot.num_samples),
                    newplot.data["time"],
                )
                self.graphWidget1.clear()
                newplot.data_line = self.graphWidget1.plot(
                    newplot.data["time"],
                     newplot.data["amplitude"],
                    pen=newplot.pen,
                    name=newplot.name,
                )
                scatterPlotItem = pg.ScatterPlotItem(
                        newplot.sampledSignalTime,
                        newplot.sampledSignalAmplitude,
                        size=10,
                        pen=None,
                        symbol="o",
                    )
                self.graphWidget1.addItem(scatterPlotItem)
                self.Reconstruction()
                pass
            if newplot.isloaded == 1 and self.SNR != None and self.SNR != 0:
                    noise1 = np.random.normal(
                        0, 10 ** (-self.SNR / 20), len(newplot.data['amplitude'])
                    )
                    noise=noise1.astype(np.int32)
                    if newplot.isDat == 1:
                        newplot.modified_Amplitude += noise * 1000000
                        (
                            newplot.sampledSignalAmplitude,
                            newplot.sampledSignalTime,
                        ) = scipy.signal.resample(
                            newplot.modified_Amplitude,
                            int(newplot.num_samples),
                            newplot.modified_time,)
                        self.graphWidget1.clear()
                        newplot.data_line = self.graphWidget1.plot(
                            newplot.modified_time,
                            newplot.modified_Amplitude,
                            pen=newplot.pen,
                            name=newplot.name,
                        )
                        scatterPlotItem = pg.ScatterPlotItem(
                            newplot.sampledSignalTime,
                            newplot.sampledSignalAmplitude,
                            size=10,
                            pen=None,
                            symbol="o",
                        )
                        self.graphWidget1.addItem(scatterPlotItem)
                        print("lookat")
                        print(
                            len(newplot.sampledSignalAmplitude), len(newplot.sampledSignalTime)
                        )
                        self.Reconstruction()
                        pass
                        
                    else:
                        newplot.data['amplitude'] += noise
                        (
                            newplot.sampledSignalAmplitude,
                            newplot.sampledSignalTime,
                        ) = scipy.signal.resample(
                            newplot.data["amplitude"],
                            int(newplot.num_samples),
                            newplot.data["time"],
                        )
                        self.graphWidget1.clear()
                        newplot.data_line = self.graphWidget1.plot(
                            newplot.data["time"],
                            newplot.data["amplitude"],
                            pen=newplot.pen,
                            name=newplot.name,
                        )
                        scatterPlotItem = pg.ScatterPlotItem(
                            newplot.sampledSignalTime,
                            newplot.sampledSignalAmplitude,
                            size=10,
                            pen=None,
                            symbol="o",
                        )
                        self.graphWidget1.addItem(scatterPlotItem)
                        print("lookat")
                        print(
                            len(newplot.sampledSignalAmplitude), len(newplot.sampledSignalTime)
                        )
                        self.Reconstruction()
                        pass
                        
         
            if self.SNR == int(0):
                    newplot.num_samples = math.ceil(
                        newplot.Samplingfrequency * newplot.data["time"].max()
                    )
                    self.samplingFreqNum.setText(f"Value: {newplot.Samplingfrequency}")
                    self.Fmax.setText(f"Value: {(newplot.Samplingfrequency)/2}")
                    print("sampling frequency")
                    print(newplot.Samplingfrequency, newplot.Frequency)
                    if newplot.isDat==1:
                        (
                            newplot.sampledSignalAmplitude,
                            newplot.sampledSignalTime,
                        ) = scipy.signal.resample(
                            newplot.data["amplitude"],
                            int(newplot.num_samples),
                            newplot.data["time"],
                         )
                        self.graphWidget1.clear()
                        newplot.data_line = self.graphWidget1.plot(
                            newplot.data["time"],
                            newplot.data["amplitude"],
                            pen=newplot.pen,
                            name=newplot.name,
                        )
                        scatterPlotItem = pg.ScatterPlotItem(
                            newplot.sampledSignalTime,
                            newplot.sampledSignalAmplitude,
                            size=10,
                            pen=None,
                            symbol="o",
                        )
                        self.graphWidget1.addItem(scatterPlotItem)
                        self.Reconstruction()
                    else:
                        (
                            newplot.sampledSignalAmplitude,
                            newplot.sampledSignalTime,
                        ) = scipy.signal.resample(
                            newplot.original_Amplitude,
                            int(newplot.num_samples),
                            newplot.original_time,
                        )
                        self.graphWidget1.clear()
                        newplot.data_line = self.graphWidget1.plot(
                            newplot.original_time,
                            newplot.original_Amplitude,
                            pen=newplot.pen,
                            name=newplot.name,
                        )
                        scatterPlotItem = pg.ScatterPlotItem(
                            newplot.sampledSignalTime,
                            newplot.sampledSignalAmplitude,
                            size=10,
                            pen=None,
                            symbol="o",
                        )
                        self.graphWidget1.addItem(scatterPlotItem)
                        self.Reconstruction()
            elif newplot.isloaded != 1:
                newplot.num_samples = math.ceil(
                    newplot.Samplingfrequency * newplot.signaltime.max()
                )
                self.samplingFreqNum.setText(f"Value: {newplot.Samplingfrequency}")
                self.Fmax.setText(f"Value: {(newplot.Frequency)}")
                print("sampling frequency")
                print(newplot.Samplingfrequency, newplot.Frequency)
                ############# newplot.signaltype==2 and newplot.Samplingfrequency==newplot.Frequency
                # Specify time values for sampling
                newplot.sampledSignalTime = np.linspace(
                    0, 10, newplot.num_samples, endpoint=False
                )  #######new sampling algorthim

                # Resample the signal at the specified time values
                newplot.sampledSignalAmplitude = np.interp(
                    newplot.sampledSignalTime, newplot.signaltime, newplot.signal
                )
                # else:
                #     (
                #         newplot.sampledSignalAmplitude,
                #         newplot.sampledSignalTime,
                #     ) = scipy.signal.resample(
                #         newplot.signal, int(newplot.num_samples), newplot.signaltime
                #     )
                if self.SNR != None:
                    noise = (
                        (
                            np.random.normal(
                                0,
                                10 ** (-self.SNR / 20),
                                len(newplot.sampledSignalTime),
                            )
                        )
                        * newplot.magnitude
                        * 10
                    )
                    newplot.sampledSignalAmplitude += noise
                self.graphWidget1.clear()
                newplot.data_line = self.graphWidget1.plot(
                    newplot.signaltime,
                    newplot.signal,
                    pen=newplot.pen,
                    name=newplot.name,
                )
                scatterPlotItem = pg.ScatterPlotItem(
                    newplot.sampledSignalTime,
                    newplot.sampledSignalAmplitude,
                    size=10,
                    pen=None,
                    symbol="o",
                )
                self.graphWidget1.addItem(scatterPlotItem)
                # self.graphWidget2.plot(
                #     newplot.sampledSignalTime, newplot.sampledSignalAmplitude, symbol="+"
                # )
                self.Reconstruction()
                if self.SNR == int(0):
                    newplot.num_samples = math.ceil(
                        newplot.Samplingfrequency * newplot.signaltime.max()
                    )
                    self.samplingFreqNum.setText(f"Value: {newplot.Samplingfrequency}")
                    self.Fmax.setText(f"Value: {(newplot.Frequency)}")
                    print("sampling frequency")
                    print(newplot.Samplingfrequency, newplot.Frequency)
                    (
                        newplot.sampledSignalAmplitude,
                        newplot.sampledSignalTime,
                    ) = scipy.signal.resample(
                        newplot.signal, int(newplot.num_samples), newplot.signaltime
                    )
                self.graphWidget1.clear()
                newplot.data_line = self.graphWidget1.plot(
                    newplot.signaltime,
                    newplot.signal,
                    pen=newplot.pen,
                    name=newplot.name,
                )
                scatterPlotItem = pg.ScatterPlotItem(
                    newplot.sampledSignalTime,
                    newplot.sampledSignalAmplitude,
                    size=10,
                    pen=None,
                    symbol="o",
                )
                self.graphWidget1.addItem(scatterPlotItem)
                # self.graphWidget2.plot(
                #     newplot.sampledSignalTime, newplot.sampledSignalAmplitude, symbol="+"
                # )
                self.Reconstruction()

    def EnterFrequency(self):
        # dialog = InputDialog(self)
        # result = dialog.exec_()  # This will block until the user closes the dialog
        newplot = self.GetChosenPlotLine()
        # if result == QtWidgets.QDialog.Accepted:
        if self.Frequency.text():
            user_input = int(self.Frequency.text())
            newplot.Frequency = int(user_input)
            t = np.linspace(0, 10, 3000)
            if newplot.signaltype == 1:
                newplot.signal = (
                    np.sin(2 * np.pi * newplot.Frequency * t)
                ) * newplot.magnitude
            elif newplot.signaltype == 2:
                newplot.signal = (
                    np.cos(2 * np.pi * newplot.Frequency * t)
                ) * newplot.magnitude

        self.ComposedSignal()
        #  self.updatefunction()

    def EnterMagnitude(self):
        # This will block until the user closes the dialog
        newplot = self.GetChosenPlotLine()
        if self.Magnitude.text():
            user_input = int(self.Magnitude.text())
            newplot.magnitude = int(user_input)
            t = np.linspace(0, 10, 3000)
            if newplot.signaltype == 1:
                newplot.signal = (
                    np.sin(2 * np.pi * newplot.Frequency * t)
                ) * newplot.magnitude
            elif newplot.signaltype == 2:
                newplot.signal = (
                    np.cos(2 * np.pi * newplot.Frequency * t)
                ) * newplot.magnitude

        self.ComposedSignal()

    def EnterPhase(self):
        newplot = self.GetChosenPlotLine()
        if self.Phase.text():
            user_input = float(self.Phase.text())
            newplot.phase = (float(user_input)) * (np.pi)
            t = np.linspace(0, 10, 3000)
            if newplot.signaltype == 1:
                newplot.signal = (
                    np.sin(2 * np.pi * newplot.Frequency * t + newplot.phase)
                    * newplot.magnitude
                )
            elif newplot.signaltype == 2:
                newplot.signal = (
                    np.cos(2 * np.pi * newplot.Frequency * t + newplot.phase)
                    * newplot.magnitude
                )

        self.ComposedSignal()

    def remove(self):
        global PlotLines
        global SinCos
        self.graphWidget1.clear()
        self.graphWidget2.clear()
        self.graphWidget3.clear()
        self.SinCount = 0
        self.CosCount = 0
        self.comboBox.clear()
        self.comboBox.addItem("Choose Signal")
        PlotLines = []
        SinCos = []
        self.verticalSlider.setValue(1)
        self.verticalSlider_2.setValue(0)
        self.verticalSlider_3.setValue(1)
        self.SNR = None
        self.SNR2 = None
        self.enteredsampledfreq = None
        self.Frequency.clear()
        self.Magnitude.clear()

    # def updatefunction(self):
    #     self.graphWidget1.clear()
    #     newplot = PlotLines[-1]

    #     t = np.linspace(0, 1, 1000)
    #     if newplot.signaltype == 1:
    #         newplot.signal = (
    #             np.sin(2 * np.pi * newplot.Frequency * t)
    #         ) * newplot.magnitude
    #     elif newplot.signaltype == 2:
    #         newplot.signal = (
    #             np.cos(2 * np.pi * newplot.Frequency * t)
    #         ) * newplot.magnitude
    #         self.graphWidget1.plot(t, PlotLines[-1].signal)
    #     self.sampling()
    #     self.Reconstruction()

    def Load(self):
        filename = QtWidgets.QFileDialog.getOpenFileName()
        path = filename[0]

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
            newplot.pen = pg.mkPen(color=self.random_color())
            newplot.name = "Signal 1"
            newplot.data_line = self.graphWidget1.plot(
                newplot.data["time"],
                newplot.data["amplitude"],
                pen=newplot.pen,
                name=newplot.name,
            )
            PlotLines.append(newplot)
            newplot.isloaded = 1

            ampltude = np.ascontiguousarray(newplot.data["amplitude"])

            # Check the data type of the data
            if ampltude.dtype != np.float64:
                ampltude = ampltude.astype(np.float64)
            magnitudes = np.abs(scipy.fft.rfft(ampltude)) / np.max(
                np.abs(scipy.fft.rfft(ampltude))
            )
            frequencies = scipy.fft.rfftfreq(
                len(newplot.data["time"]),
                (newplot.data["time"][1] - newplot.data["time"][0]),
            )
            for index, frequency in enumerate(frequencies):
                if magnitudes[index] >= 0.05:
                    maximumFrequency = frequency

            newplot.Frequency = math.ceil(maximumFrequency)
            self.SamplinginHz.setMinimum(1)
            self.SamplinginHz.setMaximum(int(newplot.Frequency) - 1)
            self.SamplinginFmax.setValue(2)
            self.sampling()

        elif path.endswith(".csv"):
            newplot = PlotLine()
            newplot.data = pd.read_csv(path, usecols=["time", "amplitude"])
            newplot.name = "Signal 1"
            newplot.pen = pg.mkPen(color=self.random_color())
            newplot.data_line = self.graphWidget1.plot(
                newplot.data["time"],
                newplot.data["amplitude"],
                pen=newplot.pen,
                name=newplot.name,
            )
            newplot.isloaded = 1
            PlotLines.append(newplot)

            ampltude = np.ascontiguousarray(newplot.data["amplitude"])

            # Check the data type of the data
            if ampltude.dtype != np.float64:
                ampltude = ampltude.astype(np.float64)
            magnitudes = np.abs(scipy.fft.rfft(ampltude)) / np.max(
                np.abs(scipy.fft.rfft(ampltude))
            )
            frequencies = scipy.fft.rfftfreq(
                len(newplot.data["time"]),
                (newplot.data["time"][1] - newplot.data["time"][0]),
            )
            for index, frequency in enumerate(frequencies):
                if magnitudes[index] >= 0.05:
                    maximumFrequency = frequency

            newplot.Frequency = math.ceil(maximumFrequency)
            print("max freq", newplot.Frequency)
            self.SamplinginHz.setMinimum(1)
            self.SamplinginHz.setMaximum(int(newplot.Frequency) - 1)
            self.SamplinginFmax.setValue(2)
            newplot.original_Amplitude=newplot.data["amplitude"]
            newplot.original_time=newplot.data["time"]
            self.sampling()

        elif path.endswith(".dat"):
            string2 = ".dat"
            newpath = path.replace(string2, ".hea")
            with open(newpath, "rb") as file:
                # Read the first line which contains the data
                first_line = file.readline().strip()

                # Split the line by spaces to get columns
                columns = first_line.split()

                # Extract the integer from the second column
                fs = int(columns[2])
                print(fs)
            with open(path, "rb") as file:
                # Read binary data
                binary_data = file.read()

                # Convert binary data to a 1D array of integers
                values = np.frombuffer(binary_data, dtype=np.int32)

                # fs is already known in medical signals
                # fs = 500.0  # Sample rate in Hz
                newplot = PlotLine()
                newplot.isDat = 1
                PlotLines.append(newplot)
                # Calculate time values
                time_values = np.arange(0, len(values) / fs, 1 / fs)
                newplot.Samplingfrequency = fs
                newplot.time = time_values
                newplot.amplitude = values
                data = {}
                data["time"] = time_values[0:2000]
                data["amplitude"] = values[0:2000]
                newplot.data = data
                newplot.modified_time=data['time'].copy()
                newplot.modified_Amplitude=data['amplitude'].copy()
                newplot.isloaded = 1
                newplot.Frequency = newplot.Samplingfrequency / 2
                self.SamplinginHz.setMinimum(1)
                self.SamplinginHz.setMaximum(int(newplot.Frequency) - 1)
                self.SamplinginFmax.setValue(2)
                newplot.pen = pg.mkPen(color=self.random_color())
                newplot.data_line = self.graphWidget1.plot(
                newplot.data["time"],
                newplot.data["amplitude"],
                pen=newplot.pen,
                name=newplot.name,
            )
                self.sampling()

    def ErrorGraph(self):
        newplot = PlotLines[-1]
        self.graphWidget3.clear()
        if newplot.isloaded == 1:
            newplot.errorGraph = (
                newplot.data["amplitude"] - newplot.reconstructed_signal
            )
            self.graphWidget3.plot(newplot.data["time"], newplot.errorGraph)
        else:
            newplot.errorGraph = newplot.signal - newplot.reconstructed_signal
            self.graphWidget3.plot(newplot.signaltime, newplot.errorGraph)
