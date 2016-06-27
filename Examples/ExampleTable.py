import sys
from PyQt5.QtWidgets import QApplication, QTableWidget, QWidget, QTableWidgetItem


if __name__ == '__main__':

    app = QApplication(sys.argv)

    w = QWidget()
    w.resize(400, 400)
    w.move(300, 300)
    w.setWindowTitle('Simple')
    #Crear una tabla con cantidad de columnas y filas, y ventana en la q aparece
    table = QTableWidget(3,3,w)
    #inserta columna, similar en filas
    table.insertColumn(1)
    #tamano de la tabla en pixeles
    table.resize(400, 300)
    #inserta elemento en fila-columna determinada
    table.setItem(0,0, QTableWidgetItem("Text"))
    table.setItem(1,1, QTableWidgetItem(30))
    w.show()
    #interesante, se puede mostrar u ocultar la tabla de la ventana
    #table.show()

    sys.exit(app.exec_())
