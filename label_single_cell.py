from PyQt4.Qt import *
from PyQt4 import QtGui
import constants
from mpl_canvas import StaticMplCanvas
from entry import Entry


class MyPopup(QWidget):

    def __init__(self, main, entry, the_db):
        QWidget.__init__(self)
        if entry is None:
            self.bulk_add = True
        else:
            self.bulk_add = False
        self.main_widget = QtGui.QWidget(self)
        self.the_db = the_db
        self.display_cell_ui(entry)
        self.entry = entry
        self.main = main

    def display_cell_ui(self, entry):
        vbox = QtGui.QVBoxLayout(self.main_widget)
        if not self.bulk_add:
            self.sc = StaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
            self.sc.show_image(self.the_db.get_entries_array(entry))
            vbox.addWidget(self.sc)
        label = QtGui.QLabel("Problems with image. Check if applicable. Can leave blank.")
        label.setWordWrap(True)
        vbox.addWidget(label)

        hbox1 = QtGui.QHBoxLayout()
        self.ckb_cut_off = QtGui.QCheckBox("Cut off")
        if not self.bulk_add and entry.cutoff:
            self.ckb_cut_off.setChecked(True)
        self.ckb_more_than_one = QtGui.QCheckBox("More than one cell")
        if not self.bulk_add and entry.more_than_one:
            self.ckb_more_than_one.setChecked(True)
        self.ckb_obstructions = QtGui.QCheckBox("Obstruction")
        if not self.bulk_add and entry.obstructions:
            self.ckb_obstructions.setChecked(True)
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
        self.setLayout(vbox)

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
        if self.bulk_add:
            self.main.modify_bulk_entries(cell_type, self.ckb_cut_off.isChecked(), self.ckb_more_than_one.isChecked(),
                                          self.ckb_obstructions.isChecked())
        else:
            self.main.modify_entry(Entry(self.entry.file_name, self.entry.index_in_array, cell_type,
                                         self.ckb_cut_off.isChecked(), self.ckb_more_than_one.isChecked(),
                                         self.ckb_obstructions.isChecked(), processed=True, modified=True))
            self.close()
