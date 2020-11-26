import sys
import sqlite3

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5 import uic


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)

        self.connection = sqlite3.connect('coffee.sqlite')
        self.cursor = self.connection.cursor()

        self.titles = ['ID', 'Название сорта', 'Степень обжарки',
                       'Молотый/в зернах', 'Описание вкуса', 'Цена', 'Объем упаковки']

        query = """SELECT m.id, m.title, r.title, t.title, m.description, m.price, m.volume
                   FROM main as m, roasts as r, type as t
                    WHERE m.roast_id = r.id AND m.type_id = t.id
                     ORDER BY m.title"""
        self.loadTable(query)

    def loadTable(self, query):
        data = self.cursor.execute(query).fetchall()

        self.table.setColumnCount(len(self.titles))
        self.table.setHorizontalHeaderLabels(self.titles)
        self.table.setRowCount(len(data))

        for i, row in enumerate(data):
            for j, elem in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(elem)))

        self.table.resizeColumnsToContents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
