from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from PyQt4 import QtGui
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid
import numpy as np
from matplotlib.image import AxesImage
from label_single_cell import MyPopup


class MplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, main, rows, cols, images, parent=None):
        self.main = main
        self.rows = rows
        self.cols = cols
        self.images = images
        self.pop_up = None
        fig = plt.figure()
        #self.grid2 = ImageGrid(fig, 111, nrows_ncols=(rows, cols), axes_pad=0.1,)
        self.grid = ImageGrid(fig, 111, nrows_ncols=(rows, cols), axes_pad=0.1,)

        self.axes = fig

        # We want the axes cleared every time plot() is called
        self.axes.hold(False)
        FigureCanvas.__init__(self, fig)
        self.setMinimumSize(500, 400)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        fig.canvas.mpl_connect('pick_event', self.onpick4)

    # def display_pop_up(self, image):
    #     for x in xrange(self.images.shape[0]):
    #         if np.array_equal(self.images[x, :, :, :], image):
    #             print("display image")
    #             self.pop_up = MyPopup(image, self.the_db)
    #             self.pop_up.show()
    #             #vbox.addWidget(self.pop_up)

    def onpick4(self, event):
        artist = event.artist
        if isinstance(artist, AxesImage):
            im = artist
            a = im.get_array()
            print('onpick4 image', a.shape)
            #self.display_pop_up(A)
            self.main.display_pop_up(a)

class StaticImageGridCanvas(MplCanvas):
    def __init__(self, main, rows, cols, images, parent=None):
        MplCanvas.__init__(self, main, rows, cols, images, parent)
        self.show_images()

    def show_images(self):
        for x in xrange(self.rows):
            for y in xrange(self.cols):
                if self.images.shape[0] > (x*self.cols)+y:
                    img = self.images[(x*self.cols)+y, :, :, :]
                    self.grid[(x*self.cols)+y].imshow(img, picker=True)
                    #blah = np.zeros([81, 81, 3])
                    #blah[:, :, :] = (x*self.cols)+y
                    #self.grid2[(x*self.cols)+y].imshow(blah, picker=True, visible=False)

