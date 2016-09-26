from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtWidgets, QtCore
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid
import numpy as np
from matplotlib.figure import Figure


class CanvasPlot():
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, data, path):
        self.fig = plt.figure(5)
        coulter_data, manual_data, patient_indexes = data
        count = 1
        for key, value in coulter_data.iteritems():
            #ax1 = self.fig.add_subplot(111)
            plt.subplot(3, 2, count)
            #self.fig.add_subplot(blah)
            count += 1
            length = max(max(manual_data[key]), max(coulter_data[key]))
            plt.axis([0, length, 0, length])
            plt.scatter(manual_data[key], coulter_data[key])
            plt.title(key)
            plt.ylabel('Coulter Counter')
            plt.xlabel('Manual Labeled')
            for i, index in enumerate(patient_indexes[key]):
                plt.annotate(str(index), xy=(manual_data[key][i], coulter_data[key][i]), xytext=(-20, 20),
                             textcoords='offset points', ha='right', va='bottom',
                             bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                             arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

        plt.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, wspace=0.6, hspace=0.6)
        #self.fig.tight_layout()
        ######plt.show()
        self.fig.savefig(path, dpi=100)
        #x1 = np.linspace(0.0, 5.0)
        #x2 = np.linspace(0.0, 2.0)

        #y1 = np.cos(2 * np.pi * x1) * np.exp(-x1)
        #y2 = np.cos(2 * np.pi * x2)

        # plt.subplot(2, 1, 2)
        # plt.plot(x2, y2, 'r.-')
        # plt.xlabel('time (s)')
        # plt.ylabel('Undamped')


def main():
    test=[]
    test.append({'blah': [11, 2, 3], 'blah2': [5, 2, 3], 'blah3': [7, 2, 3], 'blah4': [4, 5, 6]})
    test.append({'blah': [1, 2, 3], 'blah2': [1, 2, 3], 'blah3': [1, 2, 3], 'blah4': [1, 2, 3]})
    test.append({'blah': [1, 2, 3], 'blah2': [1, 2, 3], 'blah3': [1, 2, 3], 'blah4': [1, 2, 3]})
    p = CanvasPlot(test)

if __name__ == "__main__":
    main()
