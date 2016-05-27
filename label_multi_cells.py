#!/usr/bin/env python

# simple program to help experts label blood cells and store in a sqlite3 database

from __future__ import unicode_literals, division
import sys
from PyQt4 import QtGui, QtCore
import db
import constants
from image_grid import MplCanvas
import math
from label_single_cell import MyPopup
import numpy as np
from image_grid import add_inner_title
from entry import Entry


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
        self.load()
        self.display_cell_grid_ui()

    def load(self):
        #file_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home/hallab/AlanFine')
        file_path = '/home/hallab/AlanFine/monocytes_neutrophils.npz'
        self.the_db = db.DB(file_path, restart=False)
        self.cur_cell_type = constants.NEUTROPHIL
        self.cur_pg = dict()
        self.num_pages = dict()
        self.cur_pg[constants.NEUTROPHIL] = 0
        self.cur_pg[constants.MONOCYTE] = 0
        self.cell_per_pg = 25
        self.rows = 5
        self.cols = 5
        assert(self.rows*self.cols == self.cell_per_pg)
        self.entries = self.the_db.get_entries()
        self.split_cells()
        self.num_pages[constants.NEUTROPHIL] = int(math.ceil(len(self.neutros)/self.cell_per_pg))
        self.num_pages[constants.MONOCYTE] = int(math.ceil(len(self.monos)/self.cell_per_pg))
        self.set_current_entries()
        self.cur_images = self.the_db.get_currently_displayed_images(self.current_entries)
        self.modified = []
        self.current_modified_indexes = []

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
        self.sc = MplCanvas(self, self.rows, self.cols, self.main_widget)
        self.sc.change_images(self.cur_images, self.current_entries, self.current_modified_indexes)
        vbox.addWidget(self.sc)
        self.btn_previous = QtGui.QPushButton("Previous Pg.")
        self.btn_previous.clicked.connect(self.btn_previous_clicked)
        self.btn_previous.setMaximumSize(150, 75)
        self.btn_previous.setEnabled(False)
        self.btn_next = QtGui.QPushButton("Next Pg.")
        self.btn_next.clicked.connect(self.btn_next_clicked)
        self.btn_next.setMaximumSize(150, 75)
        self.btn_deselect = QtGui.QPushButton("De-select")
        self.btn_deselect.clicked.connect(self.btn_deselect_clicked)
        self.btn_deselect.setMaximumSize(150, 75)
        self.btn_select_all = QtGui.QPushButton("Select All")
        self.btn_select_all.clicked.connect(self.btn_select_all_clicked)
        self.btn_select_all.setMaximumSize(150, 75)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.btn_previous)
        hbox.addItem(spacer)
        hbox.addWidget(self.btn_next)
        vbox.addLayout(hbox)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.btn_deselect)
        hbox.addWidget(self.btn_select_all)
        vbox.addLayout(hbox)
        vbox.addWidget(QtGui.QLabel("Bulk Change"))
        pop_up = MyPopup(self, None, self.the_db)
        vbox.addWidget(pop_up)

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
        self.update_ui()
        self.change_cell_type()

    def btn_monocytes_clicked(self):
        self.cur_cell_type = constants.MONOCYTE
        self.update_ui()
        self.change_cell_type()

    def update_ui(self):
        self.label_cell_type.setText("Current Cell Type: " + self.cur_cell_type)
        self.label_cur_page.setText("Current Page: " + str(self.cur_pg[self.cur_cell_type]+1) + " of " + str(self.num_pages[self.cur_cell_type]))
        if self.cur_pg[self.cur_cell_type] <= 0:
            self.btn_previous.setEnabled(False)
        else:
            self.btn_previous.setEnabled(True)
        if self.cur_pg[self.cur_cell_type]+1 >= self.num_pages[self.cur_cell_type]:
            self.btn_next.setEnabled(False)
        else:
            self.btn_next.setEnabled(True)

    def change_cell_type(self):
        self.set_current_entries()
        self.current_modified_indexes = []
        for i, cur in enumerate(self.current_entries):
            for mod in self.modified:
                if cur.file_name == mod.file_name and cur.index_in_array == mod.index_in_array:
                    self.current_modified_indexes.append(i)
                    break
        self.cur_images = self.the_db.get_currently_displayed_images(self.current_entries)
        self.sc.change_images(self.cur_images, self.current_entries, self.current_modified_indexes)

    def btn_previous_clicked(self):
        self.cur_pg[self.cur_cell_type] -= 1
        self.update_ui()
        self.change_cell_type()

    def btn_next_clicked(self):
        self.cur_pg[self.cur_cell_type] += 1
        self.update_ui()
        self.change_cell_type()

    def btn_deselect_clicked(self):
        self.sc.deselect(self.current_entries, self.current_modified_indexes)

    def btn_select_all_clicked(self):
        self.sc.select_all(self.current_entries, self.current_modified_indexes)

    def display_pop_up(self, image):
        for x in xrange(self.cur_images.shape[0]):
            if np.array_equal(self.cur_images[x, :, :, :], image):
                self.pop_up = MyPopup(self, self.current_entries[x], self.the_db)
                self.pop_up.show()
                break

    def modify_entry(self, entry):
        for i, an_entry in enumerate(self.current_entries):
            if an_entry.file_name == entry.file_name and an_entry.index_in_array == entry.index_in_array:  # find the entry in current entries
                # make label blank
                if len(self.sc.grid.axes_all[i].artists) > 0:
                    self.sc.grid.axes_all[i].artists[0].txt._text._text = ""
                else:
                    t = add_inner_title(self.sc.grid.axes_all[i], "", loc=2)
                    t.patch.set_ec("none")
                    t.patch.set_alpha(0.5)
                if an_entry.cell_type == entry.cell_type:  # did the cell_type stay the same?
                    # remove entry from modified list
                    try:
                        self.modified = [s for s in self.modified if not (s.file_name == entry.file_name and s.index_in_array == entry.index_in_array)]
                        #self.modified.remove(entry)
                        self.current_modified_indexes.remove(i)
                    except ValueError:
                        pass
                else:
                    self.sc.grid.axes_all[i].artists[0].txt._text._text = entry.cell_type  # set label to modified cell type label
                    self.modified.append(entry)
                    self.current_modified_indexes.append(i)
        self.sc.draw()

    def btn_save_clicked(self):
        self.the_db.save_entries(self.modified)

    def btn_resort_clicked(self):
        self.btn_save_clicked()
        self.load()
        self.update_ui()
        self.change_cell_type()

    def modify_bulk_entries(self, cell_type, cut_off, more_than_one, obstructions):
        for i, an_entry in enumerate(self.current_entries):
            if len(self.sc.grid.axes_all[i].artists) > 0:
                if self.sc.grid.axes_all[i].artists[0].txt._text._text == "*":
                    # make label blank
                    self.sc.grid.axes_all[i].artists[0].txt._text._text = ""
                    if an_entry.cell_type == cell_type:  # did the cell_type stay the same?
                        # remove entry from modified list because they are the same
                        try:
                            self.modified = [s for s in self.modified if not (s.file_name == an_entry.file_name and s.index_in_array == an_entry.index_in_array)]
                            #self.modified.remove(an_entry)
                            self.current_modified_indexes.remove(i)
                        except ValueError:
                            pass
                    else:
                        self.sc.grid.axes_all[i].artists[0].txt._text._text = cell_type  # set label to modified cell type label
                        self.modified.append(Entry(an_entry.file_name, an_entry.index_in_array, cell_type,
                                         cut_off, more_than_one, obstructions, processed=False, modified=False))
                        self.current_modified_indexes.append(i)
        self.sc.draw()

    def get_index_current_image(self, image):
        for x in xrange(self.cur_images.shape[0]):
            if np.array_equal(self.cur_images[x, :, :, :], image):
                return x

qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()
aw.show()
sys.exit(qApp.exec_())
