from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from PyQt4 import QtGui, QtCore
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid
from matplotlib.image import AxesImage
import numpy as np


class MplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, main, rows, cols, parent=None):
        self.main = main
        self.rows = rows
        self.cols = cols
        self.fig = plt.figure()
        self.grid = ImageGrid(self.fig, 111, nrows_ncols=(rows, cols), label_mode="1", axes_pad=0.1,)
        self.axes = self.fig
        self.axes.hold(False)  # We want the axes cleared every time plot() is called
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)

    def on_pick(self, event):
        modifiers = QtGui.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            mouseevent = event.mouseevent
            ax = mouseevent.inaxes
            if len(ax.artists) > 0:
                if ax.artists[0].txt._text._text == "":
                    ax.artists[0].txt._text._text = "*"
                elif ax.artists[0].txt._text._text == "*":
                    artist = event.artist
                    if isinstance(artist, AxesImage):
                        a = artist
                        im = a.get_array()
                        idx = self.main.get_index_current_image(im)
                        if idx in self.main.current_modified_indexes:
                            found = False
                            for mod in self.main.modified:
                                if mod.file_name == self.main.current_entries[idx].file_name and mod.index_in_array == self.main.current_entries[idx].index_in_array:
                                    self.grid.axes_all[idx].artists[0].txt._text._text = mod.cell_type
                                    found = True
                                    break
                            if not found:
                                self.grid.axes_all[idx].artists[0].txt._text._text = self.main.current_entries[idx].cell_type
                        else:
                            ax.artists[0].txt._text._text = ""
                else:
                    ax.artists[0].txt._text._text = "*"
            else:
                t = add_inner_title(ax, "*", loc=2)
                t.patch.set_ec("none")
                t.patch.set_alpha(0.5)
            self.draw()
        else:
            artist = event.artist
            if isinstance(artist, AxesImage):
                a = artist
                im = a.get_array()
                self.main.display_pop_up(im)

    def show_images(self):

        self.grid = ImageGrid(self.fig, 111, nrows_ncols=(self.rows, self.cols), label_mode="1", axes_pad=0.1,)

        for ax in self.fig.axes:
            ax.set_xticklabels([])
            ax.set_yticklabels([])

        for x in xrange(self.rows):
            for y in xrange(self.cols):
                if self.images.shape[0] > (x*self.cols)+y:
                    img = self.images[(x*self.cols)+y, :, :, :]
                    self.grid[(x*self.cols)+y].imshow(img, picker=True)

    def change_images(self, images, current_entries, current_modified_indexes):
        self.images = images
        self.show_images()
        for ax in self.grid.axes_all:
            if len(ax.artists) > 0:
                ax.artists[0].txt._text._text = ""
            else:
                t = add_inner_title(ax, "", loc=2)
                t.patch.set_ec("none")
                t.patch.set_alpha(0.5)
        for idx in current_modified_indexes:
            if len(self.grid.axes_all[idx].artists) > 0:
                found = False
                for mod in self.main.modified:
                    if mod.file_name == current_entries[idx].file_name and mod.index_in_array == current_entries[idx].index_in_array:
                        self.grid.axes_all[idx].artists[0].txt._text._text = mod.cell_type
                        found = True
                        break
                if not found:
                    self.grid.axes_all[idx].artists[0].txt._text._text = current_entries[idx].cell_type
        self.draw()

    def deselect(self, current_entries, current_modified_indexes):
        for i, ax in enumerate(self.grid.axes_all):
            if len(ax.artists) > 0:
                if ax.artists[0].txt._text._text == "*":
                    if i in current_modified_indexes:
                        found = False
                        for mod in self.main.modified:
                            if mod.file_name == current_entries[i].file_name and mod.index_in_array == current_entries[i].index_in_array:
                                ax.artists[0].txt._text._text = mod.cell_type
                                found = True
                                break
                        if not found:
                            ax.artists[0].txt._text._text = current_entries[i].cell_type
                    else:
                        ax.artists[0].txt._text._text = ""
        self.draw()


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