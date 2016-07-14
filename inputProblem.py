import sys

from PyQt5.QtWidgets import *

class InputProblem(QDialog):
    def __init__(self,parent=None):

        super(InputProblem, self).__init__(parent)

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

        numVariablesSpinBox = QSpinBox()
        numVariablesSpinBox.setMinimum(2)
        numVariablesSpinBox.setValue(2)
        numVariablesLabel = QLabel("&Number of Variables")
        numVariablesLabel.setBuddy(numVariablesSpinBox)

        leftLayout = QHBoxLayout()
        leftLayout.addWidget(numVariablesLabel)
        leftLayout.addWidget(numVariablesSpinBox)

        numConstraintsSpinBox = QSpinBox()
        numConstraintsSpinBox.setMinimum(1)
        numConstraintsSpinBox.setValue(1)
        numConstraintsLabel = QLabel("&Number of Constraints")
        numConstraintsLabel.setBuddy(numConstraintsSpinBox)

        rightLayout = QHBoxLayout()
        rightLayout.addWidget(numConstraintsLabel)
        rightLayout.addWidget(numConstraintsSpinBox)

        topBelowLayout.addLayout(leftLayout)
        topBelowLayout.addLayout(rightLayout)

        ##--GroupLayout--##
        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()

        ##--Buttons--##
        hbox = QHBoxLayout()
        okButton = QPushButton("Ok")
        okButton.clicked.connect(self.accept)
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.cancelButton)

        hbox.addWidget(okButton)
        hbox.addWidget(cancelButton)

        ##--MainLayout--##
        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addLayout(topBelowLayout, 1, 0, 1, 2)
        mainLayout.addWidget(self.topLeftGroupBox, 2, 0)
        mainLayout.addWidget(self.topRightGroupBox, 2, 1)
        mainLayout.addLayout(hbox, 3, 1)

        self.setLayout(mainLayout)
        self.setWindowTitle("Problem Specification")

    def createTopLeftGroupBox(self):
        self.topLeftGroupBox = QGroupBox("Objetive Criterion")
        maxRadioButton = QRadioButton("Maximization")
        minRadioButton = QRadioButton("Minimization")
        maxRadioButton.setChecked(True)
        layout = QVBoxLayout()
        layout.addWidget(maxRadioButton)
        layout.addWidget(minRadioButton)

        self.topLeftGroupBox.setLayout(layout)

    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox("Default Variable Type")
        nonNegConRadioButton = QRadioButton("Non Negative Continuous")
        nonNegIntRadioButton = QRadioButton("Non Negative Integer")
        binaryRadioButton = QRadioButton("Binary(0,1)")
        unrestrictedRadioButton = QRadioButton("Unrestricted")
        unrestrictedRadioButton.setChecked(True)

        layout = QVBoxLayout()
        layout.addWidget(nonNegConRadioButton)
        layout.addWidget(nonNegIntRadioButton)
        layout.addWidget(binaryRadioButton)
        layout.addWidget(unrestrictedRadioButton)

        self.topRightGroupBox.setLayout(layout)

    def accept(self):
        print self.nameProblemEdit.text()
        print "Accept"

    def cancelButton(self):
        print "cancelButton"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = InputProblem()
    dialog.show()
    sys.exit(app.exec_())
