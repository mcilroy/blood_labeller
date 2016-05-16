#!/usr/bin/env python

# embedding_in_qt4.py --- Simple Qt4 application embedding matplotlib canvases
#
# Copyright (C) 2005 Florent Rougon
#               2006 Darren Dale
#
# This file is an example program for matplotlib. It may be used and
# modified with no restriction; raw copies as well as modified versions
# may be distributed without limitation.

from __future__ import unicode_literals
import sys
import os
from PyQt4 import QtGui, QtCore
import data
import numpy as np

from numpy import arange, sin, pi
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""
    def show_image(self, img):
        self.axes.imshow(img)


class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Label Cells 0.1")
        self.setMinimumSize(150*6+50, 600)
        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Load Data', self.load_data,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_L)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&Documentation', self.about)
        self.label = QtGui.QLabel('Welcome. To load data go to : Options -> Load Data')
        self.main_widget = QtGui.QWidget(self)
        l = QtGui.QVBoxLayout(self.main_widget)
        l.addWidget(self.label)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)


        self.entries = []

    def load_data(self):
        self.the_data = data.Data()
        self.the_data.create_table_if_not_exists()
        self.the_data.check_if_data_seen_before()
        self.entries = self.the_data.get_unprocessed_entries()
        if len(self.entries) <= 1:
            self.label.setText("You've already processed that file 100%. If you are think you haven't try renaming the "
                               "file")
        else:
            self.the_data.available(self.entries)
            entry = self.the_data.get_next_entry(self.entries)
            self.display(entry)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtGui.QMessageBox.about(self, "Documentation", """0) Load Data from File Menu. 1) Select problems with the
        cells. You can select more than one. 2) click on a button with the name of the cell you believe the image
        represents. If you are unsure. Select the button 'Un sure'. Note: you can click the previous cell to relabel a
        previous cell. You can quit at anytime. Your progress is saved.""")

    def display(self, entry):
        self.main_widget = QtGui.QWidget(self)

        l = QtGui.QVBoxLayout(self.main_widget)

        label = QtGui.QLabel("You can quit at any time. Your progress is saved. The program will notify you when no "
                             "more cells exist to label.")
        l.addWidget(label)

        sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        sc.show_image(self.the_data.get_entries_array(entry))
        l.addWidget(sc)
        label = QtGui.QLabel("Problems with image. Check if applicable. Can leave blank.")
        l.addWidget(label)

        hbox1 = QtGui.QHBoxLayout()
        ck1 = QtGui.QCheckBox("Cut off")
        ck2 = QtGui.QCheckBox("More than one cell")
        ck4 = QtGui.QCheckBox("Obstruction")
        hbox1.addWidget(ck1)
        hbox1.addWidget(ck2)
        hbox1.addWidget(ck4)
        l.addLayout(hbox1)

        label = QtGui.QLabel("Select which cell category best fits the image.")
        l.addWidget(label)

        hbox2 = QtGui.QHBoxLayout()
        self.button_neutrophil = QtGui.QPushButton("Neutrophil")
        self.button_neutrophil.setMinimumSize(150, 75)
        hbox2.addWidget(self.button_neutrophil)
        self.button_monocyte = QtGui.QPushButton("Monocyte")
        self.button_monocyte.setMinimumSize(150, 75)
        hbox2.addWidget(self.button_monocyte)
        self.button_eosinophil = QtGui.QPushButton("Eosinophil")
        self.button_eosinophil.setMinimumSize(150, 75)
        hbox2.addWidget(self.button_eosinophil)
        self.basophil = QtGui.QPushButton("Basophil")
        self.basophil.setMinimumSize(150, 75)
        hbox2.addWidget(self.basophil)
        self.button_not_sure = QtGui.QPushButton("Not Sure")
        self.button_not_sure.setMinimumSize(150, 75)
        hbox2.addWidget(self.button_not_sure)
        self.button_no_cell = QtGui.QPushButton("No Cell")
        self.button_no_cell.setMinimumSize(150, 75)
        hbox2.addWidget(self.button_no_cell)
        l.addLayout(hbox2)

        label = QtGui.QLabel("Select to go back to the previous cell to relabel it.")
        l.addWidget(label)

        hbox3 = QtGui.QHBoxLayout()
        self.button_back = QtGui.QPushButton("Previous cell")
        self.button_back.setMinimumSize(150, 100)
        self.button_back.setMaximumSize(400, 200)
        hbox3.addWidget(self.button_back)
        l.addLayout(hbox3)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()
aw.show()
sys.exit(qApp.exec_())