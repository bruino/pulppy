from PyQt5.QtWidgets import *
import time


def window():
    import sys
    app = QApplication(sys.argv)
    win = QDialog()

    label1 = QLabel(win)
    label1.setText('Tiempo cumplido, descansa!')
    label1.move(20, 10)

    buttonOk = QPushButton(win)
    buttonOk.setText('Ok')
    buttonOk.move(60, 50)
    buttonOk.clicked.connect(pushOk)

    win.setGeometry(100,100,250,100)
    win.setWindowTitle("Pymodoro")
    #time.sleep(1800)
    time.sleep(5)
    win.show()
    sys.exit(app.exec_())

def pushOk():
    exit()

if __name__ == '__main__':
    window()
