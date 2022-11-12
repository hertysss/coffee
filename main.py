import sqlite3

from PyQt5 import uic
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.setFixedSize(400, 300)
        self.setWindowTitle('Информация о кофе')
        self.show_records()

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