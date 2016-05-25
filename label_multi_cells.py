#!/usr/bin/env python

# simple program to help experts label blood cells and store in a sqlite3 database

from __future__ import unicode_literals
import sys
from PyQt4 import QtGui, QtCore
import db
import constants
from image_grid import MplCanvas
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
        self.neutros = []
        self.lymph = []
        self.mono = []
        self.eosin = []
        self.baso = []
        self.unsure = []
        self.no_cell = []
        self.pop_up = None
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

    def load_and_display_data(self):
        #file_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home/hallab/AlanFine')
        file_path = '/home/hallab/AlanFine/monocytes_neutrophils.npz'
        self.the_db = db.DB(file_path, restart=True)
        self.cur_cell_type = constants.NEUTROPHIL
        self.cur_pg = dict()
        self.num_pages = dict()
        self.cur_pg[constants.NEUTROPHIL] = 0
        self.cur_pg[constants.MONOCYTE] = 0
        self.cell_per_pg = 3
        self.rows = 1
        self.cols = 3
        assert(self.rows*self.cols == self.cell_per_pg)
        self.entries = self.the_db.get_entries()
        self.split_cells()
        self.num_pages[constants.NEUTROPHIL] = int(math.ceil(len(self.neutros)/self.cell_per_pg))
        self.num_pages[constants.MONOCYTE] = int(math.ceil(len(self.monos)/self.cell_per_pg))
        self.set_current_entries()
        self.cur_images = self.the_db.get_currently_displayed_images(self.current_entries)
        self.modified = []
        self.display_cell_grid_ui()

    def split_cells(self):
        self.neutros = []
        self.monos = []
        for entry in self.entries:
            if entry.cell_type == constants.NEUTROPHIL:
                self.neutros.append(entry)
            elif entry.cell_type == constants.MONOCYTE:
                self.monos.append(entry)

    def set_current_entries(self):
        if self.cur_cell_type == constants.NEUTROPHIL:
            blah = self.neutros
        elif self.cur_cell_type == constants.MONOCYTE:
            blah = self.monos
        if self.cur_pg[self.cur_cell_type] > len(blah)/self.cell_per_pg:
            return []
        if (self.cur_pg[self.cur_cell_type]+1) * self.cell_per_pg > len(blah):
            self.current_entries = blah[self.cur_pg[self.cur_cell_type] * self.cell_per_pg: len(blah)]
        else:
            self.current_entries = blah[self.cur_pg[self.cur_cell_type] * self.cell_per_pg: (self.cur_pg[self.cur_cell_type]+1) * self.cell_per_pg]

    def display_cell_grid_ui(self):
        self.main_widget = QtGui.QWidget(self)
        vbox = QtGui.QVBoxLayout(self.main_widget)
        label = QtGui.QLabel("""Click on cells to re-label them. Click on previous and next buttons to see more cells. Click on buttons with cell names to see cells of that type. Click re-sort button to move re-labelled cells to their proper category """)
        label.setWordWrap(True)
        vbox.addWidget(label)
        btn_neutrophils = QtGui.QPushButton("Neutrophils")
        btn_neutrophils.clicked.connect(self.btn_neutrophils_clicked)
        btn_neutrophils.setMaximumSize(150, 75)
        btn_monocytes = QtGui.QPushButton("Monocytes")
        btn_monocytes.clicked.connect(self.btn_monocytes_clicked)
        btn_monocytes.setMaximumSize(150, 75)
        spacer = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(btn_neutrophils)
        hbox.addItem(spacer)
        hbox.addWidget(btn_monocytes)
        vbox.addLayout(hbox)
        self.label_cell_type = QtGui.QLabel("Current Cell Type: " + self.cur_cell_type)
        vbox.addWidget(self.label_cell_type)
        self.label_cur_page = QtGui.QLabel("Current Page: " + str(self.cur_pg[self.cur_cell_type]+1) + " of " + str(self.num_pages[self.cur_cell_type]))
        vbox.addWidget(self.label_cur_page)
        self.sc = MplCanvas(self, self.rows, self.cols, self.cur_images, self.main_widget)
        vbox.addWidget(self.sc)
        self.btn_previous = QtGui.QPushButton("Previous")
        self.btn_previous.clicked.connect(self.btn_previous_clicked)
        self.btn_previous.setMaximumSize(150, 75)
        self.btn_previous.setVisible(False)
        self.btn_next = QtGui.QPushButton("Next")
        self.btn_next.clicked.connect(self.btn_next_clicked)
        self.btn_next.setMaximumSize(150, 75)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.btn_previous)
        hbox.addItem(spacer)
        hbox.addWidget(self.btn_next)
        vbox.addLayout(hbox)
        btn_resort = QtGui.QPushButton("Re-sort")
        btn_resort.clicked.connect(self.btn_resort_clicked)
        btn_resort.setMaximumSize(150, 75)
        btn_save = QtGui.QPushButton("Save")
        btn_save.clicked.connect(self.btn_save_clicked)
        btn_save.setMaximumSize(150, 75)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(btn_resort)
        hbox.addWidget(btn_save)
        vbox.addLayout(hbox)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def btn_neutrophils_clicked(self):
        self.cur_cell_type = constants.NEUTROPHIL
        self.label_cell_type.setText("Current Cell Type: " + self.cur_cell_type)
        self.label_cur_page.setText("Current Page: " + str(self.cur_pg[self.cur_cell_type]+1) + " of " + str(self.num_pages[self.cur_cell_type]))
        if self.cur_pg[self.cur_cell_type] == 0:
            self.btn_previous.setVisible(False)
        else:
            self.btn_previous.setVisible(True)
        if self.cur_pg[self.cur_cell_type]-1 == self.num_pages[self.cur_cell_type]:
            self.btn_next.setVisible(False)
        else:
            self.btn_next.setVisible(True)
        self.change_cell_type()

    def btn_monocytes_clicked(self):
        self.cur_cell_type = constants.MONOCYTE
        self.label_cell_type.setText("Current Cell Type: " + self.cur_cell_type)
        self.label_cur_page.setText("Current Page: " + str(self.cur_pg[self.cur_cell_type]+1) + " of " + str(self.num_pages[self.cur_cell_type]))
        if self.cur_pg[self.cur_cell_type] == 0:
            self.btn_previous.setVisible(False)
        else:
            self.btn_previous.setVisible(True)
        if self.cur_pg[self.cur_cell_type]-1 == self.num_pages[self.cur_cell_type]:
            self.btn_next.setVisible(False)
        else:
            self.btn_next.setVisible(True)
        self.change_cell_type()

    def change_cell_type(self):
        self.set_current_entries()
        self.cur_images = self.the_db.get_currently_displayed_images(self.current_entries)
        # find mplcanvas, remove it, remake it, then insert into UI
        vbox = self.main_widget.findChild(QtGui.QVBoxLayout)
        fc = self.main_widget.findChild(FigureCanvas)
        fc.deleteLater()
        try:
            vbox.removeItem(fc)
        except TypeError:
            pass
        self.sc = MplCanvas(self, self.rows, self.cols, self.cur_images, self.main_widget)
        vbox.insertWidget(4, self.sc)

    def btn_previous_clicked(self):
        self.cur_pg[self.cur_cell_type] -= 1
        self.label_cur_page.setText("Current Page: " + str(self.cur_pg[self.cur_cell_type]+1) + " of " + str(self.num_pages[self.cur_cell_type]))
        if self.cur_pg[self.cur_cell_type] <= 0:
            self.btn_previous.setVisible(False)
        else:
            self.btn_previous.setVisible(True)
        self.btn_next.setVisible(True)
        self.change_cell_type()

    def btn_next_clicked(self):
        self.cur_pg[self.cur_cell_type] += 1
        self.label_cur_page.setText("Current Page: " + str(self.cur_pg[self.cur_cell_type]+1) + " of " + str(self.num_pages[self.cur_cell_type]))
        if self.cur_pg[self.cur_cell_type]-1 >= self.num_pages[self.cur_cell_type]:
            self.btn_next.setVisible(False)
        else:
            self.btn_next.setVisible(True)
        self.btn_previous.setVisible(True)
        self.change_cell_type()

    def display_pop_up(self, image):
        for x in xrange(self.cur_images.shape[0]):
            if np.array_equal(self.cur_images[x, :, :, :], image):
                self.pop_up = MyPopup(self, self.current_entries[x], self.the_db)
                self.pop_up.show()
                break

    def modify_entry(self, entry):
        for i, an_entry in enumerate(self.current_entries):
            if an_entry.file_name == entry.file_name and an_entry.index_in_array == entry.index_in_array:
                if an_entry.cell_type == entry.cell_type:
                    # set label blank
                    self.modified.remove(entry)
                else:
                    # set label to entry.cell_type
                    #self.current_entries[i] = entry
                    self.modified.append(entry)

    def btn_save_clicked(self):
        self.the_db.save_entries(self.modified)

    def btn_resort_clicked(self):
        self.btn_save_clicked()
        #file_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home/hallab/AlanFine')
        file_path = '/home/hallab/AlanFine/monocytes_neutrophils.npz'
        self.the_db = db.DB(file_path, restart=False)
        self.cur_cell_type = constants.NEUTROPHIL
        self.cur_pg = dict()
        self.num_pages = dict()
        self.cur_pg[constants.NEUTROPHIL] = 0
        self.cur_pg[constants.MONOCYTE] = 0
        self.cell_per_pg = 3
        self.rows = 1
        self.cols = 3
        assert(self.rows*self.cols == self.cell_per_pg)
        self.entries = self.the_db.get_entries()
        self.split_cells()
        self.num_pages[constants.NEUTROPHIL] = int(math.ceil(len(self.neutros)/self.cell_per_pg))
        self.num_pages[constants.MONOCYTE] = int(math.ceil(len(self.monos)/self.cell_per_pg))
        self.set_current_entries()
        self.cur_images = self.the_db.get_currently_displayed_images(self.current_entries)
        self.modified = []
        self.label_cell_type.setText("Current Cell Type: " + self.cur_cell_type)
        self.label_cur_page.setText("Current Page: " + str(self.cur_pg[self.cur_cell_type]+1) + " of " + str(self.num_pages[self.cur_cell_type]))
        if self.cur_pg[self.cur_cell_type] == 0:
            self.btn_previous.setVisible(False)
        else:
            self.btn_previous.setVisible(True)
        if self.cur_pg[self.cur_cell_type]-1 == self.num_pages[self.cur_cell_type]:
            self.btn_next.setVisible(False)
        else:
            self.btn_next.setVisible(True)
        self.change_cell_type()

qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()
aw.show()
sys.exit(qApp.exec_())
