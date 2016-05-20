from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from PyQt4 import QtGui
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid
import numpy as np

class MplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, rows, cols, parent=None):
        self.rows = rows
        self.cols = cols
        fig = plt.figure()
        #self.grid2 = ImageGrid(fig, 111, nrows_ncols=(rows, cols), axes_pad=0.1,)
        self.grid = ImageGrid(fig, 111, nrows_ncols=(rows, cols), axes_pad=0.1,)

        self.axes = fig

        ##
        x = np.linspace(0, self.cols, self.cols)
        y = np.linspace(0, self.rows, self.rows)   # your array
        x, y = np.meshgrid(x, y)
        x = x.flatten()
        y = y.flatten()
        #self.axes = fig.add_subplot(111)
        line, = plt.plot(x, y, 'b', picker=10)
        line.set_visible(False)
        plt.pcolormesh(np.random.randn(10, 10))
        ##

        # We want the axes cleared every time plot() is called
        self.axes.hold(False)
        FigureCanvas.__init__(self, fig)
        self.setMinimumSize(500, 400)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


    def calluser(self):
        print(self.rows, self.cols)


class StaticImageGridCanvas(MplCanvas):
    def show_images(self, images):
        for x in xrange(self.rows):
            for y in xrange(self.cols):
                if images.shape[0] > (x*self.cols)+y:
                    img = images[(x*self.cols)+y, :, :, :]
                    self.grid[(x*self.cols)+y].imshow(img, picker=False)
                    blah = np.zeros([81, 81, 3])
                    blah[:, :, :] = (x*self.cols)+y
                    #self.grid2[(x*self.cols)+y].imshow(blah, picker=True, visible=False)
