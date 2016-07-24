#!/usr/bin/env python
# PuLP : Python LP Modeler

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

from pulp import *
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import (QFont, QTextCharFormat, QTextCursor, QTextFrameFormat,
        QTextLength, QTextTableFormat)
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (QApplication, QCheckBox, QDialog, QDoubleSpinBox,
        QDialogButtonBox, QGridLayout, QLabel, QLineEdit, QMainWindow,
        QPushButton, QMessageBox, QMenu, QTableWidget, QTableWidgetItem,
        QTabWidget, QComboBox, QTextEdit, QItemDelegate, QHBoxLayout, QSpinBox
        , QRadioButton, QGroupBox, QVBoxLayout, QSizePolicy)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        fileMenu = QMenu("&File", self)
        newAction = fileMenu.addAction("&New...")
        newAction.setShortcut("Ctrl+N")
        quitAction = fileMenu.addAction("&Exit")
        quitAction.setShortcut("Ctrl+Q")
        self.menuBar().addMenu(fileMenu)

        self.solvers = QTabWidget()
        self.solvers.setTabsClosable(True)
        self.solvers.tabCloseRequested.connect(self.closeTab)

        newAction.triggered.connect(self.openDialog)
        quitAction.triggered.connect(self.close)

        self.setCentralWidget(self.solvers)
        self.setWindowTitle("Pulppy Software")

    def createSample(self):
        self.createTabSolver()

    def closeTab (self, currentIndex):
        currentQWidget = self.solvers.widget(currentIndex)
        currentQWidget.deleteLater()
        self.solvers.removeTab(currentIndex)

    def openDialog(self):
        inputProblemDialog = InputProblem(self)
        if inputProblemDialog.exec_() == QDialog.Accepted:
            inputTable = InputTableModel(inputProblemDialog.title
            , inputProblemDialog.numVar, inputProblemDialog.numCons
            , inputProblemDialog.typeVar, inputProblemDialog.objCrit, self)
            if inputTable.exec_() == QDialog.Accepted:
                self.createTabSolver(inputTable.problem)

    def createTabSolver(self, problem):
        editor = QTextEdit()
        tabIndex = self.solvers.addTab(editor, problem.name)
        self.solvers.setCurrentIndex(tabIndex)

        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        topFrame = cursor.currentFrame()
        topFrameFormat = topFrame.frameFormat()
        topFrameFormat.setPadding(16)
        topFrame.setFrameFormat(topFrameFormat)

        textFormat = QTextCharFormat()
        boldFormat = QTextCharFormat()
        boldFormat.setFontWeight(QFont.Bold)

        referenceFrameFormat = QTextFrameFormat()
        referenceFrameFormat.setBorder(1)
        referenceFrameFormat.setPadding(8)
        referenceFrameFormat.setPosition(QTextFrameFormat.FloatLeft)
        referenceFrameFormat.setWidth(QTextLength(QTextLength.PercentageLength, 100))
        cursor.insertFrame(referenceFrameFormat)

        cursor.insertText("Title Problem: ", boldFormat)
        cursor.insertText(problem.name+"\n", textFormat)
        cursor.insertText("Criterion: ", boldFormat)
        if problem.sense == 1:
            cursor.insertText("Minimize\n",textFormat)
        else:
            cursor.insertText("Maximize\n",textFormat)

        WasNone, dummyVar = problem.fixObjective()
        cursor.insertText("Status: ", boldFormat)
        cursor.insertText(str(LpStatus[problem.status])+"\n", textFormat)
        cursor.insertText("Value Function Objetive: ", boldFormat)
        cursor.insertText(str(value(problem.objective))+"\n", textFormat)
        cursor.insertBlock()
        cursor.insertText("Objective\n", boldFormat)
        cursor.insertText(str(problem.objective)+"\n", textFormat)
        cursor.insertBlock()
        cursor.insertText("Subject To\n", boldFormat)
        ks = list(problem.constraints.keys())
        ks.sort()
        for k in ks:
            constraint = problem.constraints[k]
            print constraint
            if not list(constraint.keys()):
                #empty constraint add the dummyVar
                dummyVar = problem.get_dummyVar()
                constraint += dummyVar
                #set this dummyvar to zero so infeasible problems are not made
                #feasible
                cursor.insertText((dummyVar == 0.0).asCplexLpConstraint("_dummy")
                                    , textFormat)
                cursor.insertBlock()
            cursor.insertText(str(k)+" : ", boldFormat)
            cursor.insertText(str(constraint), textFormat)
            cursor.insertBlock()
        vs = problem.variables()
        cursor.insertBlock()
        # Bounds on non-"positive" variables
        # Note: XPRESS and CPLEX do not interpret integer variables without
        # explicit bounds
        mip=1
        if mip:
            vg=[v for v in vs if not (v.isPositive() and v.cat==LpContinuous) \
                and not v.isBinary()]
        else:
            vg = [v for v in vs if not v.isPositive()]
        if vg:
            cursor.insertText("Bounds\n", boldFormat)
            for v in vg:
                cursor.insertText("%s, " % v.asCplexLpVariable(), textFormat)
        # Integer non-binary variables
        if mip:
            vg = [v for v in vs if v.cat == LpInteger and not v.isBinary()]
            if vg:
                cursor.insertText("Generals\n", boldFormat)
                for v in vg:
                    cursor.insertText("%s, " % v.name, textFormat)
            # Binary variables
            vg = [v for v in vs if v.isBinary()]
            if vg:
                cursor.insertText("Binaries\n",boldFormat)
                for v in vg:
                    cursor.insertText("%s, " % v.name, textFormat)
        cursor.setPosition(topFrame.lastPosition())

        bodyFrameFormat = QTextFrameFormat()
        bodyFrameFormat.setWidth(QTextLength(QTextLength.PercentageLength, 100))
        cursor.insertBlock()
        cursor.insertFrame(bodyFrameFormat)

        orderTableFormat = QTextTableFormat()
        orderTableFormat.setAlignment(Qt.AlignHCenter)
        orderTable = cursor.insertTable(1, 3, orderTableFormat)

        orderFrameFormat = cursor.currentFrame().frameFormat()
        orderFrameFormat.setBorder(1)
        cursor.currentFrame().setFrameFormat(orderFrameFormat)

        cursor = orderTable.cellAt(0, 0).firstCursorPosition()
        cursor.insertText("Variable", boldFormat)
        cursor = orderTable.cellAt(0, 1).firstCursorPosition()
        cursor.insertText("Value", boldFormat)
        cursor = orderTable.cellAt(0, 2).firstCursorPosition()
        cursor.insertText("Reduced Cost", boldFormat)

        for v in problem.variables():
            row = orderTable.rows()
            orderTable.insertRows(row, 1)
            #Name variable
            cursor = orderTable.cellAt(row, 0).firstCursorPosition()
            cursor.insertText(v.name, textFormat)
            #Value variable
            cursor = orderTable.cellAt(row, 1).firstCursorPosition()
            cursor.insertText(str(v.varValue), textFormat)
            #Cost Reduced variable
            cursor = orderTable.cellAt(row, 2).firstCursorPosition()
            cursor.insertText(str(v.dj), textFormat)

        cursor.setPosition(topFrame.lastPosition())
        cursor.insertBlock()

        orderTableFormat = QTextTableFormat()
        orderTableFormat.setAlignment(Qt.AlignHCenter)
        orderTable = cursor.insertTable(1, 3, orderTableFormat)

        orderFrameFormat = cursor.currentFrame().frameFormat()
        orderFrameFormat.setBorder(1)
        cursor.currentFrame().setFrameFormat(orderFrameFormat)

        cursor = orderTable.cellAt(0, 0).firstCursorPosition()
        cursor.insertText("Constraint", boldFormat)
        cursor = orderTable.cellAt(0, 1).firstCursorPosition()
        cursor.insertText("Slack", boldFormat)
        cursor = orderTable.cellAt(0, 2).firstCursorPosition()
        cursor.insertText("Shadow Price", boldFormat)

        for m in range(problem.numConstraints()):
            row = orderTable.rows()
            orderTable.insertRows(row, 1)
            #Name Constraint
            cursor = orderTable.cellAt(row, 0).firstCursorPosition()
            cursor.insertText("C"+ str(m+1), textFormat)
            #Slack Constraint
            cursor = orderTable.cellAt(row, 1).firstCursorPosition()
            cursor.insertText(str(problem.constraints.get("_C"+str(m+1)).slack)
            , textFormat)
            cursor = orderTable.cellAt(row, 2).firstCursorPosition()
            cursor.insertText(str(problem.constraints.get("_C"+str(m+1)).pi)
                                    , textFormat)

class InputProblem(QDialog):
    def __init__(self,parent=None):
        super(InputProblem, self).__init__(parent)
        self.title = ""
        self.numVar = 0
        self.numCons = 0
        self.typeVar = 0
        self.objCrit = True
        ##--topLayout--##
        topLayout = QHBoxLayout()

        self.nameProblemEdit = QLineEdit()
        nameProblemLabel = QLabel("&Problem Title")
        #Pone al Label como companero del EditText
        nameProblemLabel.setBuddy(self.nameProblemEdit)

        topLayout.addWidget(nameProblemLabel)
        topLayout.addWidget(self.nameProblemEdit)
        ##--TopBelowLayout--##
        topBelowLayout = QHBoxLayout()

        self.numVariablesSpinBox = QSpinBox()
        self.numVariablesSpinBox.setMinimum(2)
        self.numVariablesSpinBox.setValue(2)
        numVariablesLabel = QLabel("&Number of Variables")
        numVariablesLabel.setBuddy(self.numVariablesSpinBox)

        leftLayout = QHBoxLayout()
        leftLayout.addWidget(numVariablesLabel)
        leftLayout.addWidget(self.numVariablesSpinBox)

        self.numConstraintsSpinBox = QSpinBox()
        self.numConstraintsSpinBox.setMinimum(1)
        self.numConstraintsSpinBox.setValue(1)
        numConstraintsLabel = QLabel("&Number of Constraints")
        numConstraintsLabel.setBuddy(self.numConstraintsSpinBox)

        rightLayout = QHBoxLayout()
        rightLayout.addWidget(numConstraintsLabel)
        rightLayout.addWidget(self.numConstraintsSpinBox)

        topBelowLayout.addLayout(leftLayout)
        topBelowLayout.addLayout(rightLayout)

        ##--GroupLayout--##
        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()

        ##--Buttons--##
        buttonBox=QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.verify)
        buttonBox.rejected.connect(self.reject)

        ##--MainLayout--##
        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addLayout(topBelowLayout, 1, 0, 1, 2)
        mainLayout.addWidget(self.topLeftGroupBox, 2, 0)
        mainLayout.addWidget(self.topRightGroupBox, 2, 1)
        mainLayout.addWidget(buttonBox, 3, 1)

        self.setLayout(mainLayout)
        self.setWindowTitle("Problem Specification")

    def createTopLeftGroupBox(self):
        self.topLeftGroupBox = QGroupBox("Objetive Criterion")
        self.maxRadioButton = QRadioButton("Maximization")
        self.minRadioButton = QRadioButton("Minimization")
        self.maxRadioButton.setChecked(True)
        layout = QVBoxLayout()
        layout.addWidget(self.maxRadioButton)
        layout.addWidget(self.minRadioButton)

        self.topLeftGroupBox.setLayout(layout)

    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox("Default Variable Type")
        self.nonNegConRadioButton = QRadioButton("Non Negative Continuous")
        self.nonNegIntRadioButton = QRadioButton("Non Negative Integer")
        self.binaryRadioButton = QRadioButton("Binary(0,1)")
        self.unrestrictedRadioButton = QRadioButton("Unrestricted")
        self.unrestrictedRadioButton.setChecked(True)

        layout = QVBoxLayout()
        layout.addWidget(self.nonNegConRadioButton)
        layout.addWidget(self.nonNegIntRadioButton)
        layout.addWidget(self.binaryRadioButton)
        layout.addWidget(self.unrestrictedRadioButton)

        self.topRightGroupBox.setLayout(layout)

    def verify(self):
        if self.nameProblemEdit.text():
            self.title = self.nameProblemEdit.text()
            self.numVar = self.numVariablesSpinBox.value()
            self.numCons = self.numConstraintsSpinBox.value()

            if self.nonNegConRadioButton.isChecked():
                self.typeVar = 1
            elif self.nonNegIntRadioButton.isChecked():
                self.typeVar = 2
            elif self.binaryRadioButton.isChecked():
                self.typeVar = 3
            else:#Unrestricted
                self.typeVar = 4

            if self.maxRadioButton.isChecked():
                self.objCrit = True#Maximitation
            else:
                self.objCrit = False#Minimization

            self.accept()
            return

        answer = QMessageBox.warning(self, "Incomplete Input Problem",
                "Dont contain all the necessary information.\n"
                "Do you want to discard it?",
                QMessageBox.Yes, QMessageBox.No)

        if answer == QMessageBox.Yes:
            self.reject()
    def setupItemsTable(self):
        self.itemsTable = QTableWidget(len(self.items), 2)

        for row, item in enumerate(self.items):
            name = QTableWidgetItem(item)
            name.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.itemsTable.setItem(row, 0, name)
            quantity = QTableWidgetItem('1')
            self.itemsTable.setItem(row, 1, quantity)

class Delegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        spinBox = QDoubleSpinBox(parent)
        spinBox.setRange(-9999999999999999, 9999999999999999)
        spinBox.setDecimals(2)
        return spinBox


class InputTableModel(QDialog):
    def __init__(self, title, numVar, numCons, typeVar, objCrit, parent=None):
        super(InputTableModel, self).__init__(parent)
        self.problem = None
        self.problemTitle = title
        self.numVariables = numVar
        self.numConstraints = numCons
        self.objCriterion = objCrit
        self.typeVariable = typeVar
        self.tableModel = QTableWidget(self.numConstraints+1, self.numVariables+2)
        self.tableModel.setItemDelegate(Delegate(self))

        listVariables = []
        for m in range(self.numVariables):
            listVariables.append("X"+str(m))

        listVariables.extend(["Direction","R.H.S"])

        #Generar Filas
        listConstraints = ["Objetive"]
        for m in range(self.numConstraints):
            listConstraints.append("C"+str(m))
            combo = QComboBox()
            combo.addItem('<')
            combo.addItem('<=')
            combo.addItem('=')
            combo.addItem('>=')
            combo.addItem('>')
            self.tableModel.setCellWidget(m+1, self.numVariables, combo)

        #listConstraints.extend(["LowerBound","UpperBound", "VariableType"])

        self.tableModel.setCellWidget(0, self.numVariables, QLabel(""))

        self.tableModel.setHorizontalHeaderLabels(listVariables)
        self.tableModel.setVerticalHeaderLabels(listConstraints)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.verify)
        buttonBox.rejected.connect(self.reject)

        f = "Problem Title: "
        if self.objCriterion == True:
            f = f + self.problemTitle + " - Objetive: Maximitation"
        else:
            f = f + self.problemTitle + " - Objetive: Minimization"
        t = QLabel(f)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(t)
        mainLayout.addWidget(self.tableModel)
        mainLayout.addWidget(buttonBox)

        width = self.tableModel.columnWidth(1)*(self.tableModel.columnCount()+1)
        height = self.tableModel.rowHeight(0)*(self.tableModel.rowCount()+4)

        self.resize(QSize(width, height))
        self.setWindowTitle("Input Problem Model")
        self.setLayout(mainLayout)

    def verify(self):
        self.accept()

        #Matix Values
        matrix = []
        for f in range(self.tableModel.rowCount()):
            row = []
            for c in range(self.tableModel.columnCount()):
                if c == self.numVariables:
                    item = self.tableModel.cellWidget(f,c)
                    if type(item) == QComboBox:
			            row.append(item.currentText())
                else:
                    item = self.tableModel.item(f,c)
                    if item == None:
                        row.append(0)
                    else:
                        row.append(float(item.text()))
            if f == 0:
                row.pop(-1)
            matrix.append(row)

        #Title and Criterion
        if self.objCriterion:
            self.problem = LpProblem(self.problemTitle, LpMaximize)
        else:
            self.problem = LpProblem(self.problemTitle, LpMinimize)

        #Non Negative Continuous
        if self.typeVariable == 1:
            x = LpVariable.matrix("x", list(range(self.numVariables)), 0, None)
            print "Non Negative Continuous"
        #Non Negative Integer
        elif self.typeVariable == 2:
            x = LpVariable.matrix("x", list(range(self.numVariables)), 0, None
                                    , LpInteger)
            print "Non Negative Integer"
        #Binary
        elif self.typeVariable == 3:
            x = LpVariable.matrix("x", list(range(self.numVariables)), 0, 1
                                    , LpInteger)
            print "Binary"
        #Unrestricted
        else:
            x = LpVariable.matrix("x", list(range(self.numVariables)), None
                                    , None)
            print "Unrestricted"

        for i in range(len(matrix)):
            if i == 0:
                #Function Objetive
                weight = lpDot(matrix[i], x)
                self.problem += weight
            else:
                b = matrix[i].pop(-1)
                sign = matrix[i].pop(-1)
                constraint = lpDot(matrix[i], x)
                if sign == u'>':
                    self.problem += constraint > b
                elif sign == u'>=':
                    self.problem += constraint >= b
                elif sign == u'=':
                    self.problem += constraint == b
                elif sign == u'<=':
                    self.problem += constraint <= b
                else:
                    self.problem += constraint < b

        #Resolve Cmpl (<Coliop|Coin> Mathematical Programming Language)
        self.problem.solve(COIN())
        return

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
