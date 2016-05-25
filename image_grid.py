from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from PyQt4 import QtGui, QtCore
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid
from matplotlib.image import AxesImage
import numpy as np


class MplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, main, rows, cols, images, parent=None):
        self.main = main
        self.rows = rows
        self.cols = cols
        self.images = images
        self.pop_up = None

        fig = plt.figure()

        self.grid = ImageGrid(fig, 111, nrows_ncols=(rows, cols), label_mode="1", axes_pad=0.1,)

        #self.grid2 = ImageGrid(fig, 111, nrows_ncols=(rows, cols), axes_pad=0.1,)
        self.axes = fig

        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        FigureCanvas.__init__(self, fig)
        #self.setMinimumSize(800, 700)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        fig.canvas.mpl_connect('pick_event', self.on_pick)
        #fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.show_images()
        for ax in fig.axes:
            ax.set_xticklabels([])
            ax.set_yticklabels([])
        # count = 0
        # for ax, im_title in zip(self.grid, ["(a)", "(b)", "(c)", "(d)"]):
        #     if count == 0:
        #         t = add_inner_title(ax, im_title, loc=2)
        #         t.patch.set_ec("none")
        #         t.patch.set_alpha(0.5)
        #     else:
        #         pass
        #t = add_inner_title(self.grid.axes_all[0], "(a)", loc=2)

    # def on_release(self, event):
    #     t = add_inner_title(event.inaxes, "bbbb", loc=2)
    #     t.patch.set_ec("none")
    #     t.patch.set_alpha(0.5)

    def on_pick(self, event):
        modifiers = QtGui.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            mouseevent = event.mouseevent
            ax = mouseevent.inaxes
            if len(ax.artists) > 0:
                ax.artists.pop()
            else:
                t = add_inner_title(ax, "*", loc=2)
                t.patch.set_ec("none")
                t.patch.set_alpha(0.5)
            self.draw()
        else:
            artist = event.artist
            if isinstance(artist, AxesImage):
                im = artist
                a = im.get_array()
                self.main.display_pop_up(a)

    def show_images(self):
        for x in xrange(self.rows):
            for y in xrange(self.cols):
                if self.images.shape[0] > (x*self.cols)+y:
                    img = self.images[(x*self.cols)+y, :, :, :]
                    #img2 = np.zeros([3, 3, 3])
                    #self.grid2[(x*self.cols)+y].imshow(img2, picker=True)
                    self.grid[(x*self.cols)+y].imshow(img, picker=True)


def add_inner_title(ax, title, loc, size=None, **kwargs):
    from matplotlib.offsetbox import AnchoredText
    from matplotlib.patheffects import withStroke
    if size is None:
        size = dict(size=plt.rcParams['legend.fontsize'])
    at = AnchoredText(title, loc=loc, prop=size,
                      pad=0., borderpad=0.5,
                      frameon=False, **kwargs)
    ax.add_artist(at)
    at.txt._text.set_path_effects([withStroke(foreground="w", linewidth=3)])
    at.txt._text.set_color("red")
    #at.txt._text.set_backgroundcolor("green")
    return at