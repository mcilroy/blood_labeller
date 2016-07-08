#!/usr/bin/env python

# simple program to help experts label blood cells and store in a sqlite3 database

from __future__ import unicode_literals, division

import math
import sys
from PyQt5 import QtCore, QtWidgets
import numpy as np
import os
import constants
import db
from entry import Entry
from image_grid import MplCanvas, add_inner_title
from label_single_cell import MyPopup
import compare_coulter_counter
import plot_canvas

DATA_FILE_PATH = "data"
DB_NAME = 'cell_labeled1_paul.db'


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        # General layout and window
        self.setStyleSheet('font-size: 16pt; font-family: Courier;')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Label Cells 0.4")
        self.setMinimumSize((150*6)+50, 840)
        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Load Data', self.load_and_display_data, QtCore.Qt.CTRL + QtCore.Qt.Key_L)
        self.file_menu.addAction('&Quit', self.file_quit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)
        self.help_menu.addAction('&Documentation', self.about)

        self.stats_menu = QtWidgets.QMenu('&Stats', self)
        self.stats_menu.addAction('&Export graph of patient statistics', self.plot_patient_stats)
        self.stats_menu.addAction('&Display current patient statistics', self.display_patient_stats)
        self.stats_menu.addAction('&Display global patient statistics', self.display_global_patient_stats)
        self.stats_menu.addAction('&Export global patient statistics', self.export_global_patient_stats)
        self.stats_menu.addAction('&Export raw labeled amounts per patient', self.export_raw_global_patient_stats)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.stats_menu)
        self.stats = compare_coulter_counter.Stats(DATA_FILE_PATH, DB_NAME)
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
        self.unlabeled = []
        self.pop_up = None
        self.display_opening_menu('Welcome. To load data go to : File -> Load Data')
        self.cur_patient = 0

    def display_opening_menu(self, instructions):
        self.main_widget = QtWidgets.QWidget(self)
        label = QtWidgets.QLabel(instructions)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setWordWrap(True)
        vbox = QtWidgets.QVBoxLayout(self.main_widget)
        hbox = QtWidgets.QVBoxLayout()
        hbox.addWidget(label)
        vbox.addLayout(hbox)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def file_quit(self):
        self.close()

    def closeEvent(self, ce):
        self.file_quit()

    def about(self):
        msbBox = QtWidgets.QMessageBox()
        msbBox.setText("\nCommands:\nLoad:\nLoad data from filemenu, select file where cells located\n"
                       "Save:\nSave the current labels.\nRe-sort:\nSaves and then resorts all the cells into their respective categories\n"
                        "Cell buttons (top of page):\nClick to display cells of that type\nCell buttons (bottom page):\n"
                        "Click to modify cell type of currently selected cells.\nCell image:\nClick to open larger version\n"
                        "SHIFT+click cells:\nSelect multiple cells at once, then you can click bottom cell buttons to modify in bulk.\n"
                        "Page naviation:\nSelect specific pages or use the previous/next buttons to switch pages.\n"
                        "Select/Deselect all:\nClick to select all cells. Can then SHIFT+click to deselect what you don't want selected.\n"
                        "Patient Selection:\nSelect current patient's cells\n"
                        "Display stats by accessing the stats file menu.\n"
                        "Export stats by assessing the file menu")
        msbBox.setWindowTitle("Documentation")
        retval = msbBox.exec_()

    def display_patient_stats(self):
        if len(self.entries) > 0:
                self.statusBar().showMessage('Calculating...')
                self.stats.re_calculate(self.file_path)
                msg = self.stats.display_single_patient(self.cur_patient)
                msbBox = QtWidgets.QMessageBox()
                msbBox.setText(msg)
                msbBox.setWindowTitle("Stats for patient: " + str(self.cur_patient))
                retval = msbBox.exec_()
                self.statusBar().showMessage('Ready')
        else:
            self.statusBar().showMessage('No data')

    def plot_patient_stats(self):
        if len(self.entries) > 0:
            self.statusBar().showMessage('Calculating...')
            self.stats.re_calculate(self.file_path)
            path = QtWidgets.QFileDialog.getSaveFileName(self, 'PNG file', '.', '(*.png)')[0]
            data = self.stats.get_counts()
            #self.plot_popup = canvas_plot_popup.CanvasPlotPopup(self, data)
            #self.plot_popup.show()
            plotpopup = plot_canvas.CanvasPlot(data, path)
            #plotpopup.compute_initial_figure(None)
            self.statusBar().showMessage('Ready')
        else:
            self.statusBar().showMessage('No data')

    def display_global_patient_stats(self):
        if len(self.entries) > 0:
                self.statusBar().showMessage('Calculating...')
                self.stats.re_calculate(self.file_path)
                msg = self.stats.display_global_patient_stats()
                msbBox = QtWidgets.QMessageBox()
                msbBox.setText(msg)
                msbBox.setWindowTitle("R-squared values for each cell-type")
                retval = msbBox.exec_()
                self.statusBar().showMessage('Ready')
        else:
            self.statusBar().showMessage('No data')

    def export_global_patient_stats(self):
        if len(self.entries) > 0:
                self.statusBar().showMessage('Calculating...')
                self.stats.re_calculate(self.file_path)
                path = QtWidgets.QFileDialog.getSaveFileName(self, 'CSV file', '.', '(*.csv)')[0]
                self.stats.export_computed_global_patient_stats(path)
                self.statusBar().showMessage('Ready')
        else:
            self.statusBar().showMessage('No data')

    def export_raw_global_patient_stats(self):
        if len(self.entries) > 0:
                self.statusBar().showMessage('Calculating...')
                self.stats.re_calculate(self.file_path)
                path = QtWidgets.QFileDialog.getSaveFileName(self, 'CSV file', '.', '(*.csv)')[0]
                self.stats.export_raw_global_patient_stats(path, zip(self.neutros, self.lymph, self.mono, self.eosin,
                                                                     self.baso, self.unsure, self.no_cell,
                                                                     self.unlabeled))
                self.statusBar().showMessage('Ready')
        else:
            self.statusBar().showMessage('No data')

    def load_and_display_data(self):
        self.load()
        self.display_cell_grid_ui()
        self.statusBar().showMessage('Ready')

    def load(self):
        self.file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '.')[0]
        self.statusBar().showMessage('Initializing...')
        #file_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home/hallab/AlanFine')
        #file_path = '/home/hallab/AlanFine/monocytes_neutrophils.npz'
        self.the_db = db.DB(os.path.join(DATA_FILE_PATH, DB_NAME), self.file_path, restart=False)
        self.initialize(self.cur_patient)

    def initialize(self, cur_patient=0):
        self.cur_patient = cur_patient
        self.num_patients = self.the_db.num_patients()
        self.cur_cell_type = constants.UNLABELED
        self.cur_pg = dict()
        self.num_pages = dict()
        self.cur_pg[constants.NEUTROPHIL] = 0
        self.cur_pg[constants.LYMPHOCYTE] = 0
        self.cur_pg[constants.MONOCYTE] = 0
        self.cur_pg[constants.EOSINOPHIL] = 0
        self.cur_pg[constants.BASOPHIL] = 0
        self.cur_pg[constants.NO_CELL] = 0
        self.cur_pg[constants.NOT_SURE] = 0
        self.cur_pg[constants.UNLABELED] = 0
        self.cell_per_pg = 51
        self.rows = 3
        self.cols = 17
        #assert(self.rows*self.cols == self.cell_per_pg)
        self.entries = self.the_db.get_entries()
        self.split_cells()
        self.num_pages[constants.NEUTROPHIL] = int(math.ceil(len(self.neutros[self.cur_patient]) / self.cell_per_pg))
        self.num_pages[constants.MONOCYTE] = int(math.ceil(len(self.mono[self.cur_patient]) / self.cell_per_pg))
        self.num_pages[constants.LYMPHOCYTE] = int(math.ceil(len(self.lymph[self.cur_patient]) / self.cell_per_pg))
        self.num_pages[constants.EOSINOPHIL] = int(math.ceil(len(self.eosin[self.cur_patient]) / self.cell_per_pg))
        self.num_pages[constants.BASOPHIL] = int(math.ceil(len(self.baso[self.cur_patient]) / self.cell_per_pg))
        self.num_pages[constants.NO_CELL] = int(math.ceil(len(self.no_cell[self.cur_patient]) / self.cell_per_pg))
        self.num_pages[constants.NOT_SURE] = int(math.ceil(len(self.unsure[self.cur_patient]) / self.cell_per_pg))
        self.num_pages[constants.UNLABELED] = int(math.ceil(len(self.unlabeled[self.cur_patient]) / self.cell_per_pg))
        self.set_current_entries()
        self.cur_images = self.the_db.get_currently_displayed_images(self.current_entries)
        self.modified = []
        self.current_modified_indexes = []

    def split_cells(self):
        self.neutros = [[] for w in range(self.num_patients)]
        self.lymph = [[] for w in range(self.num_patients)]
        self.mono = [[] for w in range(self.num_patients)]
        self.eosin = [[] for w in range(self.num_patients)]
        self.baso = [[] for w in range(self.num_patients)]
        self.unsure = [[] for w in range(self.num_patients)]
        self.no_cell = [[] for w in range(self.num_patients)]
        self.unlabeled = [[] for w in range(self.num_patients)]
        for entry in self.entries:
            if entry.cell_type == constants.NEUTROPHIL:
                self.neutros[entry.patient_index].append(entry)
            elif entry.cell_type == constants.MONOCYTE:
                self.mono[entry.patient_index].append(entry)
            elif entry.cell_type == constants.LYMPHOCYTE:
                self.lymph[entry.patient_index].append(entry)
            elif entry.cell_type == constants.EOSINOPHIL:
                self.eosin[entry.patient_index].append(entry)
            elif entry.cell_type == constants.BASOPHIL:
                self.baso[entry.patient_index].append(entry)
            elif entry.cell_type == constants.NO_CELL:
                self.no_cell[entry.patient_index].append(entry)
            elif entry.cell_type == constants.NOT_SURE:
                self.unsure[entry.patient_index].append(entry)
            elif entry.cell_type == constants.UNLABELED:
                self.unlabeled[entry.patient_index].append(entry)

    def set_current_entries(self):
        if self.cur_cell_type == constants.NEUTROPHIL:
            blah = self.neutros[self.cur_patient]
        elif self.cur_cell_type == constants.MONOCYTE:
            blah = self.mono[self.cur_patient]
        elif self.cur_cell_type == constants.LYMPHOCYTE:
            blah = self.lymph[self.cur_patient]
        elif self.cur_cell_type == constants.BASOPHIL:
            blah = self.baso[self.cur_patient]
        elif self.cur_cell_type == constants.NOT_SURE:
            blah = self.unsure[self.cur_patient]
        elif self.cur_cell_type == constants.NO_CELL:
            blah = self.no_cell[self.cur_patient]
        elif self.cur_cell_type == constants.EOSINOPHIL:
            blah = self.eosin[self.cur_patient]
        elif self.cur_cell_type == constants.UNLABELED:
            blah = self.unlabeled[self.cur_patient]
        if self.cur_pg[self.cur_cell_type] > len(blah)/self.cell_per_pg:
            return []
        if (self.cur_pg[self.cur_cell_type]+1) * self.cell_per_pg > len(blah):
            self.current_entries = blah[self.cur_pg[self.cur_cell_type] * self.cell_per_pg: len(blah)]
        else:
            self.current_entries = blah[self.cur_pg[self.cur_cell_type] * self.cell_per_pg: (self.cur_pg[self.cur_cell_type]+1) * self.cell_per_pg]

    def display_cell_grid_ui(self):
        self.main_widget = QtWidgets.QWidget(self)
        vbox = QtWidgets.QVBoxLayout(self.main_widget)
        btn_neutrophils = QtWidgets.QPushButton("Neutrophils")
        btn_neutrophils.clicked.connect(self.btn_neutrophils_clicked)
        btn_neutrophils.setMaximumSize(150, 75)
        self.lbl_neutro_count = QtWidgets.QLabel(str(len(self.neutros[self.cur_patient])))
        btn_lymphocyte = QtWidgets.QPushButton("Lymphocyte")
        btn_lymphocyte.clicked.connect(self.btn_lymphocyte_clicked)
        btn_lymphocyte.setMaximumSize(150, 75)
        self.lbl_lymph_count = QtWidgets.QLabel(str(len(self.lymph[self.cur_patient])))
        btn_monocytes = QtWidgets.QPushButton("Monocytes")
        btn_monocytes.clicked.connect(self.btn_monocytes_clicked)
        btn_monocytes.setMaximumSize(150, 75)
        self.lbl_monocytes_count = QtWidgets.QLabel(str(len(self.mono[self.cur_patient])))
        btn_eosinophil = QtWidgets.QPushButton("Eosinophil")
        btn_eosinophil.clicked.connect(self.btn_eosinophil_clicked)
        btn_eosinophil.setMaximumSize(150, 75)
        self.lbl_eosinophil_count = QtWidgets.QLabel(str(len(self.eosin[self.cur_patient])))
        btn_basophil = QtWidgets.QPushButton("Basophil")
        btn_basophil.clicked.connect(self.btn_basophil_clicked)
        btn_basophil.setMaximumSize(150, 75)
        self.lbl_basophil_count = QtWidgets.QLabel(str(len(self.baso[self.cur_patient])))
        btn_unsure = QtWidgets.QPushButton("Unsure")
        btn_unsure.clicked.connect(self.btn_unsure_clicked)
        btn_unsure.setMaximumSize(150, 75)
        self.lbl_unsure_count = QtWidgets.QLabel(str(len(self.unsure[self.cur_patient])))
        btn_nocell = QtWidgets.QPushButton("No cell")
        btn_nocell.clicked.connect(self.btn_nocell_clicked)
        btn_nocell.setMaximumSize(150, 75)
        self.lbl_nocell_count = QtWidgets.QLabel(str(len(self.no_cell[self.cur_patient])))
        btn_unlabeled = QtWidgets.QPushButton("Unlabeled")
        btn_unlabeled.clicked.connect(self.btn_unlabeled_clicked)
        btn_unlabeled.setMaximumSize(150, 75)
        self.lbl_unlabeled_count = QtWidgets.QLabel(str(len(self.unlabeled[self.cur_patient])))
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(btn_neutrophils)
        hbox.addWidget(self.lbl_neutro_count)
        hbox.addWidget(btn_lymphocyte)
        hbox.addWidget(self.lbl_lymph_count)
        hbox.addWidget(btn_monocytes)
        hbox.addWidget(self.lbl_monocytes_count)
        vbox.addLayout(hbox)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(btn_eosinophil)
        hbox.addWidget(self.lbl_eosinophil_count)
        hbox.addWidget(btn_basophil)
        hbox.addWidget(self.lbl_basophil_count)
        hbox.addWidget(btn_unsure)
        hbox.addWidget(self.lbl_unsure_count)
        hbox.addWidget(btn_nocell)
        hbox.addWidget(self.lbl_nocell_count)
        hbox.addWidget(btn_unlabeled)
        hbox.addWidget(self.lbl_unlabeled_count)
        vbox.addLayout(hbox)
        self.label_cell_type = QtWidgets.QLabel("Current Cell Type: " + self.cur_cell_type)
        self.label_cell_type.setStyleSheet('font-size: 18pt; font-weight: bold;')
        vbox.addWidget(self.label_cell_type)
        hbox_temp = QtWidgets.QHBoxLayout(self.main_widget)
        hbox_temp.setContentsMargins(0, 0, 0, 0)
        hbox_temp.setSpacing(0)
        self.label_cur_page = QtWidgets.QLabel("Current Page: " + str(self.cur_pg[self.cur_cell_type]+1) + " of " + str(self.num_pages[self.cur_cell_type]))
        self.label_cur_page.setStyleSheet('font-size: 16pt; font-weight: bold;')
        hbox_temp.addWidget(self.label_cur_page)
        self.line_edit_cur_page = QtWidgets.QLineEdit()
        self.line_edit_cur_page.setMaximumSize(75, 75)
        hbox_temp.addWidget(self.line_edit_cur_page)
        self.btn_set_page = QtWidgets.QPushButton("Set page")
        self.btn_set_page.setMaximumSize(150, 75)
        self.btn_set_page.clicked.connect(self.btn_set_page_clicked)
        hbox_temp.addWidget(self.btn_set_page)
        vbox.addLayout(hbox_temp)
        self.sc = MplCanvas(self, self.rows, self.cols, self.main_widget)
        self.sc.change_images(self.cur_images, self.current_entries, self.current_modified_indexes)
        vbox.addWidget(self.sc)
        self.btn_previous = QtWidgets.QPushButton("Previous Pg.")
        self.btn_previous.clicked.connect(self.btn_previous_clicked)
        self.btn_previous.setMaximumSize(150, 42)
        self.btn_previous.setEnabled(False)
        self.btn_next = QtWidgets.QPushButton("Next Pg.")
        self.btn_next.clicked.connect(self.btn_next_clicked)
        self.btn_next.setMaximumSize(150, 42)
        self.btn_deselect = QtWidgets.QPushButton("De-select")
        self.btn_deselect.clicked.connect(self.btn_deselect_clicked)
        self.btn_deselect.setMaximumSize(150, 75)
        self.btn_select_all = QtWidgets.QPushButton("Select All")
        self.btn_select_all.clicked.connect(self.btn_select_all_clicked)
        self.btn_select_all.setMaximumSize(150, 75)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.btn_previous)
        hbox.addItem(spacer)
        hbox.addWidget(self.btn_next)
        vbox.addLayout(hbox)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.btn_deselect)
        hbox.addWidget(self.btn_select_all)
        vbox.addLayout(hbox)
        vbox.addWidget(QtWidgets.QLabel("Bulk Change"))
        pop_up = MyPopup(self, None, self.the_db)
        vbox.addWidget(pop_up)

        btn_resort = QtWidgets.QPushButton("Re-sort")
        btn_resort.clicked.connect(self.btn_resort_clicked)
        btn_resort.setMaximumSize(150, 75)
        btn_save = QtWidgets.QPushButton("Save")
        btn_save.clicked.connect(self.btn_save_clicked)
        btn_save.setMaximumSize(150, 75)
        btn_export = QtWidgets.QPushButton("Export")
        btn_export.clicked.connect(self.btn_export_clicked)
        btn_export.setMaximumSize(150, 75)

        dropdown_patient = QtWidgets.QComboBox()
        for x in range(self.num_patients):
            dropdown_patient.addItem("Patient "+str(x))
        dropdown_patient.activated[str].connect(self.dropdown_patient_clicked)
        dropdown_patient.setMaximumSize(180, 75)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(btn_resort)
        hbox.addWidget(btn_save)
        hbox.addWidget(dropdown_patient)
        vbox.addLayout(hbox)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def btn_neutrophils_clicked(self):
        self.cur_cell_type = constants.NEUTROPHIL
        self.update_ui()
        self.change_cell_type()

    def btn_lymphocyte_clicked(self):
        self.cur_cell_type = constants.LYMPHOCYTE
        self.update_ui()
        self.change_cell_type()

    def btn_monocytes_clicked(self):
        self.cur_cell_type = constants.MONOCYTE
        self.update_ui()
        self.change_cell_type()

    def btn_eosinophil_clicked(self):
        self.cur_cell_type = constants.EOSINOPHIL
        self.update_ui()
        self.change_cell_type()

    def btn_basophil_clicked(self):
        self.cur_cell_type = constants.BASOPHIL
        self.update_ui()
        self.change_cell_type()

    def btn_unsure_clicked(self):
        self.cur_cell_type = constants.NOT_SURE
        self.update_ui()
        self.change_cell_type()

    def btn_nocell_clicked(self):
        self.cur_cell_type = constants.NO_CELL
        self.update_ui()
        self.change_cell_type()

    def btn_unlabeled_clicked(self):
        self.cur_cell_type = constants.UNLABELED
        self.update_ui()
        self.change_cell_type()

    def dropdown_patient_clicked(self, text):
        num = int(text.split(" ", 1)[1])
        self.cur_patient = num
        self.initialize(self.cur_patient)
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
        self.lbl_neutro_count.setText(str(len(self.neutros[self.cur_patient])))
        self.lbl_monocytes_count.setText(str(len(self.mono[self.cur_patient])))
        self.lbl_lymph_count.setText(str(len(self.lymph[self.cur_patient])))
        self.lbl_eosinophil_count.setText(str(len(self.eosin[self.cur_patient])))
        self.lbl_basophil_count.setText(str(len(self.baso[self.cur_patient])))
        self.lbl_nocell_count.setText(str(len(self.no_cell[self.cur_patient])))
        self.lbl_unlabeled_count.setText(str(len(self.unlabeled[self.cur_patient])))
        self.lbl_unsure_count.setText(str(len(self.unsure[self.cur_patient])))

    def change_cell_type(self):
        self.set_current_entries()
        self.current_modified_indexes = []
        for i, cur in enumerate(self.current_entries):
            for mod in self.modified:
                if cur.file_name == mod.file_name and cur.patient_index == mod.patient_index and cur.index_in_array == mod.index_in_array:
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
        self.sc.select_all()

    def display_pop_up(self, image):
        for x in xrange(self.cur_images.shape[0]):
            if np.array_equal(self.cur_images[x, :, :, :], image):
                self.pop_up = MyPopup(self, self.current_entries[x], self.the_db)
                self.pop_up.show()
                break

    def modify_entry(self, entry):
        for i, an_entry in enumerate(self.current_entries):
            if an_entry.file_name == entry.file_name and an_entry.patient_index == entry.patient_index and an_entry.index_in_array == entry.index_in_array:  # find the entry in current entries
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
                        self.modified = [s for s in self.modified if not (s.file_name == entry.file_name and s.patient_index == entry.patient_index and s.index_in_array == entry.index_in_array)]
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
        self.initialize(self.cur_patient)
        self.update_ui()
        self.change_cell_type()
    
    def btn_export_clicked(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'CSV file', '.', '(*.csv)')[0]
        if not path: return
        with open(path, 'w') as f:
            f.write('Patient, Neutrophils, Lymphocytes, Monocytes, Eosinophils, Basophils, Unsure, No Cell, Unlabelled\n')
            for i, x in enumerate(zip(self.neutros, self.lymph, self.mono, self.eosin, self.baso, self.unsure, self.no_cell, self.unlabeled)):
                f.write(','.join(['%i' % (i+1)] + ['%i' % len(xi) for xi in x]) + '\n')

    def modify_bulk_entries(self, cell_type, cut_off, more_than_one, obstructions):
        for i, an_entry in enumerate(self.current_entries):
            if len(self.sc.grid.axes_all[i].artists) > 0:
                if self.sc.grid.axes_all[i].artists[0].txt._text._text == "*":
                    # make label blank
                    self.sc.grid.axes_all[i].artists[0].txt._text._text = ""
                    if an_entry.cell_type == cell_type:  # did the cell_type stay the same?
                        # remove entry from modified list because they are the same
                        try:
                            self.modified = [s for s in self.modified if not (s.file_name == an_entry.file_name and s.patient_index == an_entry.patient_index and s.index_in_array == an_entry.index_in_array)]
                            #self.modified.remove(an_entry)
                            self.current_modified_indexes.remove(i)
                        except ValueError:
                            pass
                    else:
                        self.sc.grid.axes_all[i].artists[0].txt._text._text = cell_type  # set label to modified cell type label
                        self.modified.append(Entry(an_entry.file_name, an_entry.patient_index, an_entry.index_in_array, cell_type,
                                         cut_off, more_than_one, obstructions, processed=False, modified=False))
                        self.current_modified_indexes.append(i)
        self.sc.draw()

    def get_index_current_image(self, image):
        for x in xrange(self.cur_images.shape[0]):
            if np.array_equal(self.cur_images[x, :, :, :], image):
                return x

    def btn_set_page_clicked(self):
        self.cur_pg[self.cur_cell_type] = int(self.line_edit_cur_page.text())-1
        self.update_ui()
        self.change_cell_type()

qApp = QtWidgets.QApplication(sys.argv)

aw = ApplicationWindow()
aw.show()
sys.exit(qApp.exec_())
