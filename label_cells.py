#!/usr/bin/env python

# simple program to help experts label blood cells and store in a sqlite3 database

from __future__ import unicode_literals
import sys
from PyQt4 import QtGui, QtCore
import db
import constants
from mpl_canvas import StaticMplCanvas
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas


class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        # General layout and window
        self.setStyleSheet('font-size: 16pt; font-family: Courier;')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Label Cells 0.1")
        self.setMinimumSize((150*6)+50, 840)
        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Load Data', self.load_data,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_L)
        self.file_menu.addAction('&Quit', self.file_quit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)
        self.help_menu.addAction('&Documentation', self.about)
        self.statusBar().showMessage('Ready')

        # db layer
        self.the_db = None

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
        QtGui.QMessageBox.about(self, "Documentation", """0) Load Data from File Menu. 1) Select problems with the
        cells. You can select more than one. 2) click on a button with the name of the cell you believe the image
        represents. If you are unsure. Select the button 'Un sure'. Note: you can click the previous cell to relabel a
        previous cell. You can quit at anytime. Your progress is saved.""")

    def button_neutrophil_clicked(self):
        cell_type = constants.NEUTROPHIL
        self.process_button_clicked(cell_type)

    def button_monocyte_clicked(self):
        cell_type = constants.MONOCYTE
        self.process_button_clicked(cell_type)

    def button_eosinophil_clicked(self):
        cell_type = constants.EOSINOPHIL
        self.process_button_clicked(cell_type)

    def button_basophil_clicked(self):
        cell_type = constants.BASOPHIL
        self.process_button_clicked(cell_type)

    def button_lymphocyte_clicked(self):
        cell_type = constants.LYMPHOCYTE
        self.process_button_clicked(cell_type)

    def button_not_sure_clicked(self):
        cell_type = constants.NOT_SURE
        self.process_button_clicked(cell_type)

    def button_no_cell_clicked(self):
        cell_type = constants.NO_CELL
        self.process_button_clicked(cell_type)

    def process_button_clicked(self, cell_type):
        sender = self.sender()
        self.statusBar().showMessage('Previous action: ' + sender.text() + ' was pressed')
        self.the_db.save(cell_type, self.ckb_cut_off.isChecked(), self.ckb_more_than_one.isChecked(),
                         self.ckb_obstructions.isChecked(), processed=True)
        if self.the_db.more_entries_available():
            self.change_cell(self.the_db.get_next_entry())
        else:
            self.display_opening_menu('You are all done! You may exit the program now or load a new file.')
        self.the_db.print_entries()

    def button_back_clicked(self):
        sender = self.sender()
        if self.the_db.more_entries_available(reverse=True):
            self.the_db.unprocess_previous()
            self.change_cell(self.the_db.get_previous_entry())
            self.statusBar().showMessage('Previous action: ' + sender.text() + ' was pressed')
        else:
            self.statusBar().showMessage("No previous entry.")
        self.the_db.print_entries()

    def change_cell(self, entry):
        self.ckb_cut_off.setChecked(False)
        self.ckb_more_than_one.setChecked(False)
        self.ckb_obstructions.setChecked(False)
        vbox = self.main_widget.findChild(QtGui.QVBoxLayout)
        fc = self.main_widget.findChild(FigureCanvas)
        fc.deleteLater()
        try:
            vbox.removeItem(fc)
        except TypeError:
            pass

        self.sc = StaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.sc.show_image(self.the_db.get_entries_array(entry))
        vbox.insertWidget(1, self.sc)

    def display_cell_ui(self, entry):
        self.main_widget = QtGui.QWidget(self)

        vbox = QtGui.QVBoxLayout(self.main_widget)

        label = QtGui.QLabel("You can quit at any time. Your progress is saved. The program will notify you when no "
                             "more cells exist to label.")
        label.setWordWrap(True)
        hbox_label = QtGui.QHBoxLayout()
        hbox_label.addWidget(label)
        vbox.addLayout(hbox_label)
        self.sc = StaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.sc.show_image(self.the_db.get_entries_array(entry))
        vbox.addWidget(self.sc)
        label = QtGui.QLabel("Problems with image. Check if applicable. Can leave blank.")
        label.setWordWrap(True)
        vbox.addWidget(label)

        hbox1 = QtGui.QHBoxLayout()
        self.ckb_cut_off = QtGui.QCheckBox("Cut off")
        self.ckb_more_than_one = QtGui.QCheckBox("More than one cell")
        self.ckb_obstructions = QtGui.QCheckBox("Obstruction")
        hbox1.addWidget(self.ckb_cut_off)
        hbox1.addWidget(self.ckb_more_than_one)
        hbox1.addWidget(self.ckb_obstructions)
        vbox.addLayout(hbox1)

        label = QtGui.QLabel("Select which cell category best fits the image.")
        label.setWordWrap(True)
        vbox.addWidget(label)

        hbox2 = QtGui.QHBoxLayout()
        self.button_neutrophil = QtGui.QPushButton("Neutrophil")
        self.button_neutrophil.setMinimumSize(150, 75)
        self.button_neutrophil.clicked.connect(self.button_neutrophil_clicked)
        hbox2.addWidget(self.button_neutrophil)

        self.button_monocyte = QtGui.QPushButton("Monocyte")
        self.button_monocyte.setMinimumSize(150, 75)
        self.button_monocyte.clicked.connect(self.button_monocyte_clicked)
        hbox2.addWidget(self.button_monocyte)

        self.button_eosinophil = QtGui.QPushButton("Eosinophil")
        self.button_eosinophil.setMinimumSize(150, 75)
        self.button_eosinophil.clicked.connect(self.button_eosinophil_clicked)
        hbox2.addWidget(self.button_eosinophil)

        self.button_basophil = QtGui.QPushButton("Basophil")
        self.button_basophil.setMinimumSize(150, 75)
        self.button_basophil.clicked.connect(self.button_basophil_clicked)
        hbox2.addWidget(self.button_basophil)

        self.button_not_sure = QtGui.QPushButton("Not Sure")
        self.button_not_sure.setMinimumSize(150, 75)
        self.button_not_sure.clicked.connect(self.button_not_sure_clicked)
        hbox2.addWidget(self.button_not_sure)
        self.button_no_cell = QtGui.QPushButton("No Cell")
        self.button_no_cell.setMinimumSize(150, 75)
        self.button_no_cell.clicked.connect(self.button_no_cell_clicked)
        hbox2.addWidget(self.button_no_cell)
        vbox.addLayout(hbox2)

        label = QtGui.QLabel("Select to go back to the previous cell to relabel it.")
        label.setWordWrap(True)
        vbox.addWidget(label)

        hbox3 = QtGui.QHBoxLayout()
        self.button_back = QtGui.QPushButton("Previous cell")
        self.button_back.clicked.connect(self.button_back_clicked)
        self.button_back.setMinimumSize(150, 100)
        self.button_back.setMaximumSize(400, 200)
        hbox3.addWidget(self.button_back)
        vbox.addLayout(hbox3)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def load_data(self):
        file_path = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '.')
        self.the_db = db.DB(file_path)
        if not self.the_db.get_unprocessed_entries():
            self.display_opening_menu("You've already processed that file 100%. If you are think you haven't try "
                                      "renaming the file")
        else:
            if self.the_db.more_entries_available():
                entry = self.the_db.get_next_entry()
                self.display_cell_ui(entry)

qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()
aw.show()
sys.exit(qApp.exec_())