from pulp import *
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import (QFont, QTextCharFormat, QTextCursor, QTextFrameFormat,
        QTextLength, QTextTableFormat)
from PyQt5.QtWidgets import (QApplication, QCheckBox, QDialog, QDoubleSpinBox,
        QDialogButtonBox, QGridLayout, QLabel, QLineEdit, QMainWindow, QPushButton,
        QMessageBox, QMenu, QTableWidget, QTableWidgetItem, QTabWidget, QComboBox,
        QTextEdit, QItemDelegate, QHBoxLayout, QSpinBox, QRadioButton, QGroupBox, QVBoxLayout)

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

        newAction.triggered.connect(self.openDialog)
        quitAction.triggered.connect(self.close)

        self.setCentralWidget(self.solvers)
        self.setWindowTitle("Pulppy Software")

    def createSample(self):
        self.createTabSolver()

    def openDialog(self):
        inputProblemDialog = InputProblem(self)
        if inputProblemDialog.exec_() == QDialog.Accepted:
            inputTable = InputTableModel(inputProblemDialog.title, inputProblemDialog.numVar, inputProblemDialog.numCons, inputProblemDialog.typeVar, inputProblemDialog.objCrit, self)
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
        referenceFrameFormat.setWidth(700)
        cursor.insertFrame(referenceFrameFormat)

        #-------------------------------------------------------------------------------------------------------
        mip=1
        cursor.insertText("Title Problem: ", boldFormat)
        cursor.insertText(problem.name+"\n", textFormat)
        cursor.insertBlock()
        if problem.sense == 1:
            cursor.insertText("Minimize\n",boldFormat)
        else:
            cursor.insertText("Maximize\n",boldFormat)
        cursor.insertBlock()
        WasNone, dummyVar = problem.fixObjective()
        cursor.insertText("Objective\n")
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
                #set this dummyvar to zero so infeasible problems are not made feasible
                cursor.insertText((dummyVar == 0.0).asCplexLpConstraint("_dummy"), textFormat)
                cursor.insertBlock()
            cursor.insertText(str(k)+" : ", boldFormat)
            cursor.insertText(str(constraint), textFormat)
            cursor.insertBlock()
        vs = problem.variables()
        # Bounds on non-"positive" variables
        # Note: XPRESS and CPLEX do not interpret integer variables without
        # explicit bounds
        if mip:
            vg = [v for v in vs if not (v.isPositive() and v.cat == LpContinuous) \
                and not v.isBinary()]
        else:
            vg = [v for v in vs if not v.isPositive()]
        if vg:
            cursor.insertText("Bounds\n", boldFormat)
            for v in vg:
                cursor.insertText("%s\n" % v.asCplexLpVariable(), textFormat)
                cursor.insertBlock()
        # Integer non-binary variables
        if mip:
            vg = [v for v in vs if v.cat == LpInteger and not v.isBinary()]
            if vg:
                cursor.insertText("Generals\n", boldFormat)
                cursor.insertBlock()
                for v in vg:
                    cursor.insertText("%s\n" % v.name, textFormat)
                    cursor.insertBlock()
            # Binary variables
            vg = [v for v in vs if v.isBinary()]
            if vg:
                cursor.insertText("Binaries\n",boldFormat)
                cursor.insertBlock()
                for v in vg:
                    cursor.insertText("%s, " % v.name, textFormat)
        cursor.insertText("End\n")
        cursor.insertBlock()
        #-------------------------------------------------------------------------------------------------------
        cursor.setPosition(topFrame.lastPosition())
        cursor.insertBlock()

        bodyFrameFormat = QTextFrameFormat()
        bodyFrameFormat.setWidth(QTextLength(QTextLength.PercentageLength, 100))
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
        cursor.insertText("Valor", boldFormat)

        for v in problem.variables():
            row = orderTable.rows()

            orderTable.insertRows(row, 1)
            cursor = orderTable.cellAt(row, 0).firstCursorPosition()
            cursor.insertText(v.name, textFormat)
            cursor = orderTable.cellAt(row, 1).firstCursorPosition()
            cursor.insertText(str(v.varValue), textFormat)
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
        cursor.insertText("Restriccion", boldFormat)
        cursor = orderTable.cellAt(0, 1).firstCursorPosition()
        cursor.insertText("Slack", boldFormat)
        cursor = orderTable.cellAt(0, 2).firstCursorPosition()
        cursor.insertText("Precio sombra", boldFormat)

        for m in range(problem.numConstraints()):
            row = orderTable.rows()
            orderTable.insertRows(row, 1)
            cursor = orderTable.cellAt(row, 0).firstCursorPosition()
            cursor.insertText("C"+ str(m+1), textFormat)
            cursor = orderTable.cellAt(row, 1).firstCursorPosition()
            cursor.insertText(str(problem.constraints.get("_C"+str(m+1)).pi), textFormat)
            cursor = orderTable.cellAt(row, 2).firstCursorPosition()
            cursor.insertText(str(problem.constraints.get("_C"+str(m+1)).slack), textFormat)

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
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
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
            else:
                self.typeVar = 4

            if self.maxRadioButton.isChecked():
                self.objCrit = True
            else:
                self.objCrit = False

            self.accept()
            return

        answer = QMessageBox.warning(self, "Incomplete Input Problem",
                "Dont contain all the necessary information.\n"
                "Do you want to discard it?",
                QMessageBox.Yes, QMessageBox.No)

        if answer == QMessageBox.Yes:
            self.reject()
# class DetailsDialog(QDialog):
#     def __init__(self, title, parent):
#         super(DetailsDialog, self).__init__(parent)
#
#         self.items = ("T-shirt", "Badge", "Reference book", "Coffee cup")
#
#         nameLabel = QLabel("Name:")
#         addressLabel = QLabel("Address:")
#         addressLabel.setAlignment(Qt.AlignLeft | Qt.AlignTop)
#
#         self.nameEdit = QLineEdit()
#         self.addressEdit = QTextEdit()
#         self.offersCheckBox = QCheckBox(
#                 "Send information about products and special offers:")
#
#         self.setupItemsTable()
#
#         buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
#
#         buttonBox.accepted.connect(self.verify)
#         buttonBox.rejected.connect(self.reject)
#
#         mainLayout = QGridLayout()
#         mainLayout.addWidget(nameLabel, 0, 0)
#         mainLayout.addWidget(self.nameEdit, 0, 1)
#         mainLayout.addWidget(addressLabel, 1, 0)
#         mainLayout.addWidget(self.addressEdit, 1, 1)
#         mainLayout.addWidget(self.itemsTable, 0, 2, 2, 1)
#         mainLayout.addWidget(self.offersCheckBox, 2, 1, 1, 2)
#         mainLayout.addWidget(buttonBox, 3, 0, 1, 3)
#         self.setLayout(mainLayout)
#
#         self.setWindowTitle(title)

    def setupItemsTable(self):
        self.itemsTable = QTableWidget(len(self.items), 2)

        for row, item in enumerate(self.items):
            name = QTableWidgetItem(item)
            name.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.itemsTable.setItem(row, 0, name)
            quantity = QTableWidgetItem('1')
            self.itemsTable.setItem(row, 1, quantity)

    def orderItems(self):
        orderList = []

        for row in range(len(self.items)):
            text = self.itemsTable.item(row, 0).text()
            quantity = int(self.itemsTable.item(row, 1).data(Qt.DisplayRole))
            orderList.append((text, max(0, quantity)))

        return orderList

    def senderName(self):
        return self.nameEdit.text()

    def senderAddress(self):
        return self.addressEdit.toPlainText()

    def sendOffers(self):
        return self.offersCheckBox.isChecked()
#############################################################################
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
        self.tableModel = QTableWidget(self.numConstraints+4, self.numVariables+2)
        self.tableModel.setItemDelegate(Delegate(self))

        #Generar las Columnas
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
        listConstraints.extend(["LowerBound","UpperBound", "VariableType"])

        self.tableModel.setCellWidget(0, self.numVariables, QLabel(""))

        self.tableModel.setHorizontalHeaderLabels(listVariables)
        self.tableModel.setVerticalHeaderLabels(listConstraints)

        """for m in range(self.numConstraints + 2): #For para que no sea editable las celdas abajo de los combobox
            if m >= self.numConstraints:
                c = QLabel("")
                self.tableModel.setCellWidget(m, self.numVariables, c)

        for m in range(self.numConstraints + 2): #For para que no sea editable las celdas siguientes y abajo de los combobox
            if m >= self.numConstraints:
                c = QLabel("")
                self.tableModel.setCellWidget(m, self.numVariables + 1, c)"""


        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.verify)
        buttonBox.rejected.connect(self.reject)

        #TODO: Corregir con label's
        if self.objCriterion == True:
            f = self.problemTitle + " - Maximizacion"
        else:
            f = self.problemTitle + " - Manimizacion"

        t = QLabel(f)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(t)
        mainLayout.addWidget(self.tableModel)
        mainLayout.addWidget(buttonBox)

        self.setWindowTitle("Input Problem Model")
        self.setLayout(mainLayout)

    def verify(self):
        self.accept()
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
        print matrix

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
            x = LpVariable.matrix("x", list(range(self.numVariables)), 0, None, LpInteger)
            print "Non Negative Integer"
        #Binary
        elif self.typeVariable == 3:
            x = LpVariable.matrix("x", list(range(self.numVariables)), 0, 1, LpInteger)
            print "Binary"
        #Unrestricted
        else:
            x = LpVariable.matrix("x", list(range(self.numVariables)), None, None)
            print "Unrestricted"

        for i in range(len(matrix)-3):
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
        print self.problem.variables()
        self.problem.solve(COIN())
        print("Status:", LpStatus[self.problem.status])

        # Print the value of the variables at the optimum
        for v in self.problem.variables():
            print(v.name, "=", v.varValue)

        print("objective=", value(self.problem.objective))
        return

#############################################################################


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(640, 480)
    window.show()
    sys.exit(app.exec_())
