#!/usr/bin/env python

# Pulppy Software - Linear Programming software for optimizing various practical problems of Operations Research.

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys
import random
import matplotlib
import numpy as np
matplotlib.use("Qt5Agg")
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

#
#Pulppy Software: Graphic linear programming model
#
class MplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=8, dpi=100, matrixModel=[], title='', point=[]):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.title = title
        self.Plot(matrixModel, title, point)

        FigureCanvas.__init__(self, fig)
        self.mpl_toolbar = NavigationToolbar(self, parent)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def Plot(self, matrix, title, optime):
        s = 0
        t = 0
        for i in range(len(matrix)):
            if i != 0:
                if matrix[i][0] != 0:
                    r = matrix[i][3] / matrix[i][0]
                    if r > s:
                        s = r
                if matrix[i][1] != 0:
                    u = matrix[i][3] / matrix[i][1]
                    if u > t:
                        t = u
        
        if s != 0:
            x = np.linspace(0, s)
        else:
            x = np.linspace(0, t)
        
        listFmenor = []
        listFmayor= []
        for i in range(len(matrix)):
            if i == 0:
                y = -(matrix[i][0] / matrix[i][1])*(x-float(optime[0])) + float(optime[1])
                self.axes.plot(x, y, 'k--',linewidth=1)
            else:
                y = (matrix[i][3] - matrix[i][0]*x) / matrix[i][1]
                
                if matrix[i][2] == u'>=':
                    listFmayor.append(y)
                    self.axes.plot(x, y, linewidth=1.5, label='C'+str(i))
                    self.axes.fill_between(x, y, t, alpha=0.2)
                    
                elif matrix[i][2] == u'>':
                    listFmayor.append(y)
                    self.axes.plot(x, y, '--', linewidth=1.5, label='C'+str(i))
                    self.axes.fill_between(x, y, t, alpha=0.2)
                
                elif matrix[i][2] == u'<=':
                    listFmenor.append(y)
                    self.axes.plot(x, y, linewidth=1.5, label='C'+str(i))
                    self.axes.fill_between(x, 0, y, alpha=0.2)
                
                elif matrix[i][2] == u'<':
                    listFmenor.append(y)
                    self.axes.plot(x, y, '--', linewidth=1.5, label='C'+str(i))
                    self.axes.fill_between(x, 0, y, alpha=0.2)
                
                else:
                    self.axes.plot(x, y, linewidth=1.5, label='C'+str(i))
            
        #Functions <=, <
        j = len(listFmenor)
        if j > 1:
            ySup = np.minimum(listFmenor[0], listFmenor[1])
            for i in range(j-2):
                ySup = np.minimum(listFmenor[i+2], ySup)
        elif j == 1:
            ySup = listFmenor[0]
        else:
            ySup = t
        
        #Functions >=, >
        j = len(listFmayor)
        if j > 1:
            yInf = np.maximum(listFmayor[0], listFmayor[1])
            for i in range(j-2):
                yInf = np.maximum(listFmayor[i+2], yInf)
        elif j == 1:
            yInf = listFmayor[0]
        else:
            yInf = 0
        
        self.axes.fill_between(x, ySup, yInf, where=ySup>yInf, color='blue', alpha=0.8)
        self.axes.set_xlim(0, s)
        self.axes.set_ylim(0, t)
        self.axes.set_xlabel('x')
        self.axes.set_ylabel('y')
        self.axes.plot(optime[0], optime[1], 'go', label="%.2f"  % optime[0]+", "+"%.2f"  % optime[1])
        self.axes.set_title(title)
        self.axes.legend(fontsize=10)
        self.axes.grid(True)
