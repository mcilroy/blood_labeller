#!/usr/bin/env python

# simple program to help experts label blood cells and store in a sqlite3 database

from __future__ import unicode_literals
import sys
from PyQt4 import QtGui, QtCore
import db
import constants
from image_grid import StaticImageGridCanvas
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import math
from label_single_cell import MyPopup
import numpy as np


class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        # General layout and window
        self.setStyleSheet('font-size: 16pt; font-family: Courier;')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Label Cells 0.2")
        self.setMinimumSize((150*6)+50, 840)
        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Load Data', self.load_and_display_data,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_L)
        self.file_menu.addAction('&Quit', self.file_quit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)
        self.help_menu.addAction('&Documentation', self.about)
        self.statusBar().showMessage('Ready')
        self.main_widget = None
        # db layer
        self.the_db = None
        self.entries = []
        self.neutro = []
        self.lymph = []
        self.mono = []
        self.eosin = []
        self.baso = []
        self.unsure = []
        self.no_cell = []

        self.display_opening_menu('Welcome. To load data go to : Options -> Load Data')

    def display_opening_menu(self, instructions):
        self.main_widget = QtGui.QWidget(self)
        label = QtGui.QLabel(instructions)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setWordWrap(True)
        vbox = QtGui.QVBoxLayout(self.main_widget)

        hbox = QtGui.QVBoxLayout()
        hbox.addWidget(label)
        vbox.addLayout(hbox)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def file_quit(self):
        self.close()

    def closeEvent(self, ce):
        self.file_quit()

    def about(self):
        QtGui.QMessageBox.about(self, "Documentation", '''0) Load Data from File Menu.\n 1) Select a cell to re-label.
        \n 2) label cell.\n 3) move between pages.\n 4) select different cell types to display them\n 5) Click Save to
             save.\n 6) Re-sort button re-sorts the re-labeled cells into their proper categories.''')

    def display_cell_grid_ui(self, images):
        self.main_widget = QtGui.QWidget(self)

        vbox = QtGui.QVBoxLayout(self.main_widget)

        label = QtGui.QLabel("""Click on cells to re-label them. Click on previous and next buttons to see more cells. Click on buttons with cell names to see cells of that type. Click re-sort button to move re-labelled cells to their proper category """)
        label.setWordWrap(True)
        hbox_label = QtGui.QHBoxLayout()
        hbox_label.addWidget(label)
        vbox.addLayout(hbox_label)

        #self.pop_up = MyPopup(self.entries[0], self.the_db)
        #vbox.addWidget(self.pop_up)
        self.sc = StaticImageGridCanvas(self, int(math.ceil(float(images.shape[0])/7)), 7, images, self.main_widget)
        #self.sc.show_images(images)
        vbox.addWidget(self.sc)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def load_and_display_data(self):
        #file_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home/hallab/AlanFine')
        file_path = '/home/hallab/AlanFine/monocytes_neutrophils.npz'
        self.the_db = db.DB(file_path)
        self.cur_cell_type = constants.NEUTROPHIL
        self.cur_pg = 0
        self.entries = self.the_db.get_entries()
        self.get_neutrophils()
        self.cur_images = images = self.set_current_entries()
        self.display_cell_grid_ui(images)

    def display_pop_up(self, image):
        for x in xrange(self.cur_images.shape[0]):
            if np.array_equal(self.cur_images[x, :, :, :], image):
                print("display image")
                self.pop_up = MyPopup(self.current_entries[x], self.the_db)
                self.pop_up.show()
                #vbox.addWidget(self.pop_up)

    def get_neutrophils(self):
        self.neutro = []
        for entry in self.entries:
            if entry.cell_type == constants.NEUTROPHIL:
                self.neutro.append(entry)

    def set_current_entries(self):
        if self.cur_cell_type == constants.NEUTROPHIL:
            if self.cur_pg == 0:
                self.current_entries = self.entries[0:10]
            return self.the_db.get_currently_displayed_images(self.current_entries, self.the_db.offset_neutro)
        else:
            return None

qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()
aw.show()
sys.exit(qApp.exec_())

# def button_back_clicked(self):
#     sender = self.sender()
#     if self.the_db.more_entries_available(reverse=True):
#         self.the_db.unprocess_previous()
#         self.change_cell(self.the_db.get_previous_entry())
#         self.statusBar().showMessage('Previous action: ' + sender.text() + ' was pressed')
#     else:
#         self.statusBar().showMessage("No previous entry.")
#     self.the_db.print_entries()

# def change_cell(self, entry):
#     self.ckb_cut_off.setChecked(False)
#     self.ckb_more_than_one.setChecked(False)
#     self.ckb_obstructions.setChecked(False)
#     vbox = self.main_widget.findChild(QtGui.QVBoxLayout)
#     fc = self.main_widget.findChild(FigureCanvas)
#     fc.deleteLater()
#     try:
#         vbox.removeItem(fc)
#     except TypeError:
#         pass
#
#     self.sc = StaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
#     self.sc.show_image(self.the_db.get_entries_array(entry))
#     vbox.insertWidget(1, self.sc)

