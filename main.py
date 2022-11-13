import sqlite3

from PyQt5 import uic
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem


class AddEditWindow(QMainWindow):
    def __init__(self, degrees, types, type_req, mainWindow, *args):
        super().__init__()
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.setWindowTitle('Информация о кофе')
        self.price.setInputMask('00000')
        self.volume.setInputMask('00000')
        self.cb_degree.addItems(degrees)
        self.cb_type.addItems(types)
        self.type_req = type_req
        self.mainWindow = mainWindow
        self.args = args
        if type_req == 'update':
            self.fill_form()
        self.bb.accepted.connect(self.request_to_db)
        self.bb.rejected.connect(self.close)

    def request_to_db(self):
        try:
            sort, description, price, volume = (self.sort.text(), self.description.toPlainText(),
                                                self.price.text(), self.volume.text())
            if sort and price and volume:
                self.con = sqlite3.connect("coffee.sqlite")
                degree = self.con.cursor().execute('''SELECT id from degree_of_roasting
                WHERE degree=?''', (self.cb_degree.currentText(),)).fetchone()[0]
                type = self.con.cursor().execute('''SELECT id from coffee_type
                WHERE type=?''', (self.cb_type.currentText(),)).fetchone()[0]
                if self.type_req == 'insert':
                    self.insert_to_db(sort, degree, type, description, price, volume)
                else:
                    self.update_db(sort, degree, type, description, price, volume)
            else:
                return
        except Exception as e:
            print(e)
        finally:
            self.con.close()
            self.mainWindow.show_records()
            self.close()

    def insert_to_db(self, sort, degree, type, description, price, volume):
        try:
            req = """INSERT INTO coffee_info (sort_name, degree_of_roasting, type,
            description, price, volume) VALUES(?,?,?,?,?,?)"""
            self.con.cursor().execute(req, (sort, degree, type, description, price, volume))
            self.con.commit()
        except Exception as e:
            print(e)


    def update_db(self, sort, degree, type, description, price, volume):
        try:
            req = """UPDATE coffee_info SET sort_name=?, degree_of_roasting=?, type=?,
            description=?, price=?, volume=? WHERE id=?"""
            self.con.cursor().execute(req, (sort, degree, type, description, price, volume, self.args[0]))
            self.con.commit()
        except Exception as e:
            print(e)

    def fill_form(self):
        sort, degree, type, description, price, volume = self.args[1:]
        self.sort.setText(sort)
        self.cb_degree.setCurrentText(degree)
        self.cb_type.setCurrentText(type)
        self.description.setText(description)
        self.price.setText(price)
        self.volume.setText(volume)


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.setFixedSize(400, 300)
        self.setWindowTitle('Информация о кофе')
        self.show_records()
        self.btn.clicked.connect(self.insert_note)
        self.tableWidget.itemDoubleClicked.connect(self.update_note)
        self.degrees = self.get_degrees()
        self.types = self.get_types()

    def get_degrees(self):
        degrees = []
        try:
            con = sqlite3.connect("coffee.sqlite")
            result = con.cursor().execute("""SELECT degree from degree_of_roasting""").fetchall()
            degrees = [i[0] for i in result]
        except Exception as e:
            print(e)
        finally:
            con.close()
            return degrees

    def get_types(self):
        types = []
        try:
            con = sqlite3.connect("coffee.sqlite")
            result = con.cursor().execute("""SELECT type from coffee_type""").fetchall()
            types = [i[0] for i in result]
        except Exception as e:
            print(e)
        finally:
            con.close()
            return types

    def insert_note(self):
        self.w2 = AddEditWindow(self.degrees, self.types, 'insert', self)
        self.w2.show()

    def update_note(self, item):
        row = self.tableWidget.row(item)
        lst = [self.tableWidget.item(row, col).text() for col in range(self.tableWidget.columnCount())]
        self.w2 = AddEditWindow(self.degrees, self.types, 'update', self, *lst)
        self.w2.show()

    def show_records(self):
        try:
            self.con = sqlite3.connect("coffee.sqlite")
            self.tableWidget.clear()
            result = self.con.cursor().execute("""SELECT coffee_info.ID, coffee_info.sort_name,
             degree_of_roasting.degree, coffee_type.type, description, price, volume from coffee_info
             LEFT JOIN coffee_type ON coffee_type.ID = coffee_info.type
             LEFT JOIN degree_of_roasting ON coffee_info.degree_of_roasting=degree_of_roasting.ID""").fetchall()
            self.tableWidget.setColumnCount(len(result[0]))
            self.tableWidget.setRowCount(len(result))
            self.tableWidget.setHorizontalHeaderLabels(['ID', 'название сорта', 'степень обжарки', 'молотый/в зернах',
                                                        'описание вкуса', 'цена', 'объем упаковки'])
            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        except Exception as e:
            print(e)
        finally:
            self.con.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())