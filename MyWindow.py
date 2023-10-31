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
        self.ui = uic.loadUi("GUI-2.ui", self)
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
        self.actionLoad.triggered.connect(self.Load)
        self.ClearGraph.clicked.connect(self.remove)
        self.SamplingSlider = self.findChild(QSlider, "verticalSlider")
        self.SamplingLabel = self.findChild(QLabel, "SamplingNumber")
        self.NoiseSlider = self.findChild(QSlider, "verticalSlider_2")
        self.NoiseLabel = self.findChild(QLabel, "NoiseNumber")
        self.actionSampling.triggered.connect(self.SamplingTextfunc)
        self.SamplingSlider.setMinimum(1)
        self.SamplingSlider.setMaximum(30)
        self.NoiseSlider.setMinimum(0)
        self.NoiseSlider.setMaximum(50)
        self.SamplingSlider.valueChanged.connect(self.SamplingSliderfunc)
        self.NoiseSlider.valueChanged.connect(self.NoiseSliderfunc)
        self.enteredsampledfreq = None
        self.comboBox.addItem("Choose Signal")
        self.SinCount = 0
        self.CosCount = 0
        self.SNR = None
        self.isSliderOrText = 0

    def ErrorMsg(self, text):
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setText(text)
        msg.setIcon(QMessageBox.Warning)
        x = msg.exec_()

    def SamplingSliderfunc(self, value):
        self.isSliderOrText = 1
        self.SamplingLabel.setText(str(value))
        self.enteredsampledfreq = int(value)
        # self.updatefunction()
        self.sampling()
        return value

    def SamplingTextfunc(self, value):
        self.isSliderOrText = 2
        dialog = InputDialog(self)
        result = dialog.exec_()  # This will block until the user closes the dialog
        if result == QtWidgets.QDialog.Accepted:
            value = dialog.input_text.text()
        self.SamplingLabel.setText(str(value))
        self.enteredsampledfreq = int(value)
        self.sampling()
        return value

    def NoiseSliderfunc(self, value):
        self.NoiseLabel.setText(str(value))
        self.SNR = int(value)
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
        newplot.Frequency = 5
        newplot.magnitude = 10
        num_points = 1000
        self.enteredsampledfreq = 10
        newplot.signaltime = np.linspace(0, 1, num_points)
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
        newplot.Frequency = 10
        newplot.magnitude = 10
        num_points = 1000
        self.enteredsampledfreq = 10
        newplot.signaltime = np.linspace(0, 1, num_points)
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
        newplot.signaltype = 2
        newplot.Frequency = 10
        newplot.magnitude = 10
        num_points = 1000
        newplot.signaltime = np.linspace(0, 1, num_points)
        newplot.signal = np.zeros(num_points)
        global SinCos
        global PlotLines
        for plot in SinCos:
            # newplot.signal = np.add(newplot.signal,plot.signal)
            newplot.signal += plot.signal
            print(plot.Frequency)
        ampltude = np.ascontiguousarray(newplot.signal)

        # Check the data type of the data
        if ampltude.dtype != np.float64:
            ampltude = ampltude.astype(np.float64)
        magnitudes = np.abs(scipy.fft.rfft(ampltude)) / np.max(
            np.abs(scipy.fft.rfft(ampltude))
        )
        frequencies = scipy.fft.rfftfreq(
            len(newplot.signaltime), (newplot.signaltime[1] - newplot.signaltime[0])
        )
        for index, frequency in enumerate(frequencies):
            if magnitudes[index] >= 0.05:
                maximumFrequency = frequency

        newplot.Frequency = math.ceil(maximumFrequency)
        self.graphWidget1.clear()
        PlotLines = []
        PlotLines.append(newplot)
        newplot.pen = pg.mkPen(color=self.random_color())
        newplot.name = "Composed Signal"
        newplot.data_line = self.graphWidget1.plot(
            newplot.signaltime, newplot.signal, pen=newplot.pen, name=newplot.name
        )
        print(PlotLines)
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
        if newplot.islouded == 1:
            num_samples = len(newplot.sampledSignalAmplitude)
            sampling_interval = 1.0 / newplot.Samplingfrequency
            # Initialize the reconstructed signal
            t = newplot.data["time"].values
            reconstructed_signal = np.zeros(len(t))
            for n in range(newplot.num_samples):
                reconstructed_signal += newplot.sampledSignalAmplitude[n] * np.sinc(
                    (t - (n * sampling_interval)) / sampling_interval
                )

            newplot.reconstructed_signal = reconstructed_signal
            self.graphWidget2.clear()
            self.graphWidget2.plot(t, reconstructed_signal)
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
            self.graphWidget2.plot(t, reconstructed_signal)
            self.ErrorGraph()

    def sampling(self):
        newplot = PlotLines[-1]
        if self.isSliderOrText == 0:
            newplot.Samplingfrequency = (2 * newplot.Frequency) + 1
            newplot.SamplingInterval = 1 / newplot.Samplingfrequency
        elif self.isSliderOrText == 1:
            newplot.Samplingfrequency = (
                self.enteredsampledfreq * newplot.Frequency
            ) + 1
            newplot.SamplingInterval = 1 / newplot.Samplingfrequency
        elif self.isSliderOrText == 2:
            newplot.Samplingfrequency = self.enteredsampledfreq
            newplot.SamplingInterval = 1 / newplot.Samplingfrequency

        if newplot.islouded == 1:
            newplot.num_samples = math.ceil(
                newplot.Samplingfrequency * newplot.data["time"].max()
            )
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
            if self.SNR != None:
                noise = np.random.normal(
                    0, 10 ** (-self.SNR / 20), len(newplot.sampledSignalAmplitude)
                )
                newplot.sampledSignalAmplitude += noise
            print("lookat")
            print(len(newplot.sampledSignalAmplitude), len(newplot.sampledSignalTime))
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
            if self.SNR == int(0):
                newplot.num_samples = math.ceil(
                    newplot.Samplingfrequency * newplot.data["time"].max()
                )
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
        elif newplot.islouded != 1:
            newplot.num_samples = math.ceil(
                newplot.Samplingfrequency * newplot.signaltime.max()
            )
            print("sampling frequency")
            print(newplot.Samplingfrequency, newplot.Frequency)
            (
                newplot.sampledSignalAmplitude,
                newplot.sampledSignalTime,
            ) = scipy.signal.resample(
                newplot.signal, int(newplot.num_samples), newplot.signaltime
            )
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
                newplot.signaltime, newplot.signal, pen=newplot.pen, name=newplot.name
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
                newplot.signaltime, newplot.signal, pen=newplot.pen, name=newplot.name
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
        user_input = int(self.Frequency.text())
        newplot.Frequency = int(user_input)
        t = np.linspace(0, 1, 1000)
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
        self.verticalSlider_2.setValue(1)
        self.SNR = None
        self.enteredsampledfreq = None
        self.Frequency.clear()
        self.Magnitude.clear()

    def EnterMagnitude(self):
        # This will block until the user closes the dialog
        newplot = self.GetChosenPlotLine()
        user_input = int(self.Magnitude.text())
        newplot.magnitude = int(user_input)
        t = np.linspace(0, 1, 1000)
        if newplot.signaltype == 1:
            newplot.signal = (
                np.sin(2 * np.pi * newplot.Frequency * t)
            ) * newplot.magnitude
        elif newplot.signaltype == 2:
            newplot.signal = (
                np.cos(2 * np.pi * newplot.Frequency * t)
            ) * newplot.magnitude

        self.ComposedSignal()

    def updatefunction(self):
        self.graphWidget1.clear()
        newplot = PlotLines[-1]

        t = np.linspace(0, 1, 1000)
        if newplot.signaltype == 1:
            newplot.signal = (
                np.sin(2 * np.pi * newplot.Frequency * t)
            ) * newplot.magnitude
        elif newplot.signaltype == 2:
            newplot.signal = (
                np.cos(2 * np.pi * newplot.Frequency * t)
            ) * newplot.magnitude
            self.graphWidget1.plot(t, PlotLines[-1].signal)
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
                newplot.pen = pg.mkPen(color=self.random_color())
                newplot.name = "Signal 1"
                newplot.data_line = self.graphWidget1.plot(
                    newplot.data["time"],
                    newplot.data["amplitude"],
                    pen=newplot.pen,
                    name=newplot.name,
                )
                PlotLines.append(newplot)
                newplot.islouded = 1

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
                self.sampling()

            else:
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
                newplot.islouded = 1
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
                self.sampling()

        else:
            self.ErrorMsg("You can only load .txt or .csv files.")

    def ErrorGraph(self):
        newplot = PlotLines[-1]
        self.graphWidget3.clear()
        if newplot.islouded == 1:
            newplot.errorGraph = (
                newplot.reconstructed_signal - newplot.data["amplitude"]
            )
            self.graphWidget3.plot(newplot.data["time"], newplot.errorGraph)
        else:
            newplot.errorGraph = newplot.reconstructed_signal - newplot.signal
            self.graphWidget3.plot(newplot.signaltime, newplot.errorGraph)
