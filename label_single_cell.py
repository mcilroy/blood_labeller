from PyQt5 import QtWidgets

from PyQt5.Qt import QWidget

import constants
from entry import Entry
from mpl_canvas import StaticMplCanvas


class MyPopup(QWidget):

    def __init__(self, main, entry, the_db):
        QWidget.__init__(self)
        if entry is None:
            self.bulk_add = True
        else:
            self.bulk_add = False
        self.main_widget = QtWidgets.QWidget(self)
        self.the_db = the_db
        self.display_cell_ui(entry)
        self.entry = entry
        self.main = main

    def display_cell_ui(self, entry):
        vbox = QtWidgets.QVBoxLayout(self.main_widget)
        if not self.bulk_add:
            self.sc = StaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
            self.sc.show_image(self.the_db.get_entries_array(entry))
            vbox.addWidget(self.sc)

        label = QtWidgets.QLabel("Select which cell category best fits the image.")
        label.setWordWrap(True)
        vbox.addWidget(label)

        hbox2 = QtWidgets.QHBoxLayout()
        self.button_neutrophil = QtWidgets.QPushButton("Neutrophil")
        self.button_neutrophil.setMaximumSize(150, 75)
        self.button_neutrophil.clicked.connect(self.button_neutrophil_clicked)
        hbox2.addWidget(self.button_neutrophil)

        self.button_lymphocyte = QtWidgets.QPushButton("Lymphocyte")
        self.button_lymphocyte.setMaximumSize(150, 75)
        self.button_lymphocyte.clicked.connect(self.button_lymphocyte_clicked)
        hbox2.addWidget(self.button_lymphocyte)

        self.button_monocyte = QtWidgets.QPushButton("Monocyte")
        self.button_monocyte.setMaximumSize(150, 75)
        self.button_monocyte.clicked.connect(self.button_monocyte_clicked)
        hbox2.addWidget(self.button_monocyte)

        self.button_eosinophil = QtWidgets.QPushButton("Eosinophil")
        self.button_eosinophil.setMaximumSize(150, 75)
        self.button_eosinophil.clicked.connect(self.button_eosinophil_clicked)
        hbox2.addWidget(self.button_eosinophil)

        self.button_basophil = QtWidgets.QPushButton("Basophil")
        self.button_basophil.setMaximumSize(150, 75)
        self.button_basophil.clicked.connect(self.button_basophil_clicked)
        hbox2.addWidget(self.button_basophil)

        self.button_not_sure = QtWidgets.QPushButton("Not Sure")
        self.button_not_sure.setMaximumSize(150, 75)
        self.button_not_sure.clicked.connect(self.button_not_sure_clicked)
        hbox2.addWidget(self.button_not_sure)

        self.button_no_cell = QtWidgets.QPushButton("No Cell")
        self.button_no_cell.setMaximumSize(150, 75)
        self.button_no_cell.clicked.connect(self.button_no_cell_clicked)
        hbox2.addWidget(self.button_no_cell)

        self.button_unlabeled = QtWidgets.QPushButton("Unlabeled")
        self.button_unlabeled.setMaximumSize(150, 75)
        self.button_unlabeled.clicked.connect(self.button_unlabeled_clicked)
        hbox2.addWidget(self.button_unlabeled)

        vbox.addLayout(hbox2)
        self.setLayout(vbox)

    def button_neutrophil_clicked(self):
        cell_type = constants.NEUTROPHIL
        self.process_button_clicked(cell_type)

    def button_lymphocyte_clicked(self):
        cell_type = constants.LYMPHOCYTE
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

    def button_not_sure_clicked(self):
        cell_type = constants.NOT_SURE
        self.process_button_clicked(cell_type)

    def button_no_cell_clicked(self):
        cell_type = constants.NO_CELL
        self.process_button_clicked(cell_type)

    def button_unlabeled_clicked(self):
        cell_type = constants.UNLABELED
        self.process_button_clicked(cell_type)

    def process_button_clicked(self, cell_type):
        if self.bulk_add:
            #self.main.modify_bulk_entries(cell_type, self.ckb_cut_off.isChecked(), self.ckb_more_than_one.isChecked(), self.ckb_obstructions.isChecked())
            self.main.modify_bulk_entries(cell_type, False, False, False)
        else:
            #self.main.modify_entry(Entry(self.entry.file_name, self.entry.index_in_array, cell_type, self.ckb_cut_off.isChecked(), self.ckb_more_than_one.isChecked(), self.ckb_obstructions.isChecked(), processed=False, modified=False))
            self.main.modify_entry(Entry(self.entry.file_name, self.entry.patient_index, self.entry.index_in_array, cell_type, False, False, False, processed=False, modified=False))
            self.close()
