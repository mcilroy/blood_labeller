#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial

This program creates a skeleton of
a classic GUI application with a menubar,
toolbar, statusbar and a central widget.

author: Jan Bodnar
website: zetcode.com
last edited: September 2011
"""
import sys
from PyQt4 import QtGui
import numpy as np
import os
import pyqtgraph as pg
import pyqtgraph.examples
import matplotlib as mpl

DATA_LOCATION = '../../AlanFine'


class Example(QtGui.QMainWindow):

    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def initUI(self):
        train_val = np.load(os.path.join(DATA_LOCATION, 'monocytes_neutrophils.npz'))
        test = np.load(os.path.join(DATA_LOCATION, 'mono_neut_test.npz'))
        # stored as batch, depth, height, width. Tensorflow wants -> batch, height, width, depth
        neutrophils = np.rollaxis(train_val['neutrophils'], 1, 4)
        monocytes = np.rollaxis(train_val['monocytes'], 1, 4)


        #textEdit = QtGui.QTextEdit()
        #self.setCentralWidget(textEdit)

        exitAction = QtGui.QAction(QtGui.QIcon('House_sparrow04.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAction)

        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('Main window')
        self.show()

        label = QtGui.QLabel(self)
        image = neutrophils[12, :, :, :]










        #QI = QtGui.QImage('House_sparrow04.jpg')
        imv = pg.ImageView()
        imv.setImage(image)
        #self.setCentralWidget(imv)
        pix = QtGui.QPixmap(imv)
        #QI = pg.image(image)
        #QI = QtGui.QImage(image.data, 81, 81, QtGui.QImage.Format_RGB32)
        #pix = QtGui.QPixmap.fromImage(QI)

        label.setGeometry(75, 100, 81, 81)
        label.setPixmap(pix)
        label.show()





        # qimage = QImage(toQImage(image))
        # #image = QtGui.QImage(image, 81, 81, 3,QtGui.QImage.Format_RGB32)
        # pix = QtGui.QPixmap(qimage)
        #
        # #pixmap = QtGui.QPixmap('House_sparrow04.jpg')



def main():

    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()