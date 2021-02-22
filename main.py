import sys
import sqlite3

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from main_ui import Ui_MainWindow1
from addEditCoffeeForm import Ui_MainWindow


class AddForm(QMainWindow, Ui_MainWindow):
    submitted = pyqtSignal(tuple)
    
    def __init__(self):
        super().__init__()
        pass
        self.setupUi(self)

        self.connection = sqlite3.connect('data/coffee.sqlite')
        self.cursor = self.connection.cursor()

        self.loadRoastBox()
        self.loadTypeBox()

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.close)

    def loadRoastBox(self):
        data = self.cursor.execute("""SELECT title FROM roasts""").fetchall()
        self.roastBox.addItems(list(map(lambda x: x[0], data)))

    def loadTypeBox(self):
        data = self.cursor.execute("""SELECT title FROM type""").fetchall()
        self.typeBox.addItems(list(map(lambda x: x[0], data)))

    def accept(self):
        if self.title.text():
            self.on_submit()
        else:
            QMessageBox.warning(self, "Warning", "The data is not correct!", QMessageBox.Ok)
    
    def on_submit(self):
        title = self.title.text()
        roast = self.cursor.execute("""SELECT id FROM roasts WHERE title = ?""",
                                    (self.roastBox.currentText(),)).fetchone()[0]
        _type = self.cursor.execute("""SELECT id FROM type WHERE title = ?""",
                                    (self.typeBox.currentText(),)).fetchone()[0]
        description = self.textEdit.toPlainText()
        price = self.price.value()
        volume = self.volume.value()
        result = (title, roast, _type, description, price, volume)
        
        self.submitted.emit(result)
        self.close()
    

class EditForm(QMainWindow, Ui_MainWindow):
    submitted = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.connection = sqlite3.connect('data/coffee.sqlite')
        self.cursor = self.connection.cursor()

        self.loadRoastBox()
        self.loadTypeBox()

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.close)

    def loadRoastBox(self):
        data = self.cursor.execute("""SELECT title FROM roasts""").fetchall()
        self.roastBox.addItems(list(map(lambda x: x[0], data)))

    def loadTypeBox(self):
        data = self.cursor.execute("""SELECT title FROM type""").fetchall()
        self.typeBox.addItems(list(map(lambda x: x[0], data)))

    def setData(self, data):
        self.id = data[0]
        self.title.setText(data[1])
        self.roastBox.setCurrentText(data[2])
        self.typeBox.setCurrentText(data[3])
        self.textEdit.insertPlainText(data[4])
        self.price.setValue(int(data[5]))
        self.volume.setValue(int(data[6]))

    def accept(self):
        if self.title.text():
            self.on_submit()
        else:
            QMessageBox.warning(self, "Warning", "The data is not correct!", QMessageBox.Ok)

    def on_submit(self):
        title = self.title.text()
        roast = self.cursor.execute("""SELECT id FROM roasts WHERE title = ?""",
                                    (self.roastBox.currentText(),)).fetchone()[0]
        _type = self.cursor.execute("""SELECT id FROM type WHERE title = ?""",
                                    (self.typeBox.currentText(),)).fetchone()[0]
        description = self.textEdit.toPlainText()
        price = self.price.value()
        volume = self.volume.value()
        result = (title, roast, _type, description, price, volume, self.id)

        self.submitted.emit(result)
        self.close()


class MainWindow(QMainWindow, Ui_MainWindow1):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.connection = sqlite3.connect('data/coffee.sqlite')
        self.cursor = self.connection.cursor()

        self.titles = ['ID', 'Название сорта', 'Степень обжарки',
                       'Молотый/в зернах', 'Описание вкуса', 'Цена', 'Объем упаковки']

        self.loadTable()

        self.addButton.clicked.connect(self.add)
        self.editButton.clicked.connect(self.edit)

    def loadTable(self):
        query = """SELECT m.id, m.title, r.title, t.title, m.description, m.price, m.volume
                           FROM main as m, roasts as r, type as t
                            WHERE m.roast_id = r.id AND m.type_id = t.id
                             ORDER BY m.title"""
        data = self.cursor.execute(query).fetchall()

        self.table.setColumnCount(len(self.titles))
        self.table.setHorizontalHeaderLabels(self.titles)
        self.table.setRowCount(len(data))

        for i, row in enumerate(data):
            for j, elem in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(elem)))

        self.table.resizeColumnsToContents()

    def add(self):
        self.form = AddForm()
        self.form.submitted.connect(self.add_update)
        self.form.show()

    def edit(self):
        try:
            row = self.table.selectedItems()[0].row()
            result = []
            for i in range(self.table.columnCount()):
                result.append(self.table.item(row, i).text())

            self.form = EditForm()
            self.form.setData(result)
            self.form.submitted.connect(self.edit_update)
            self.form.show()
        except IndexError:
            QMessageBox.warning(self, "Warning", "Element is not selected!", QMessageBox.Ok)

    @pyqtSlot(tuple)
    def add_update(self, data):
        query = """INSERT INTO main(title,roast_id,type_id,description,price,volume)
                                VALUES(?,?,?,?,?,?)"""
        self.cursor.execute(query, data)
        self.connection.commit()
        self.loadTable()

    @pyqtSlot(tuple)
    def edit_update(self, data):
        query = """UPDATE main 
                    SET title = ?,
                        roast_id = ?,
                        type_id = ?,
                        description = ?,
                        price = ?,
                        volume = ? 
                    WHERE id = ?"""
        self.cursor.execute(query, data)
        self.connection.commit()
        self.loadTable()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
