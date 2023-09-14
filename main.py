import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QCheckBox
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
import pandas as pd

class DatabaseApp(QWidget):
    def __init__(self):
        super().__init__()
        try:
            self.conn = sqlite3.connect("mydb.db")
            print("Database connection established successfully")
        except sqlite3.Error as e:
            print(f"Error connecting to the database: {e}")
        self.initUI()
    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def initUI(self):
        # Setting up window

        self.setWindowTitle('Electronic Parts Storage')
        self.setWindowIcon(QIcon('icon.ico'))

        # Connecting database

        
        
        # Creating widgets

        self.type_label = QLabel('Type:')
        self.type_input = QComboBox()
        self.number_label = QLabel('Part number:')
        self.number_input = QLineEdit()
        self.value_label = QLabel('Value:')
        self.value_input = QLineEdit()
        self.quantity_label = QLabel('Quantity:')
        self.quantity_input = QLineEdit()
        self.note_label = QLabel('Note:')
        self.note_input = QLineEdit()
        self.action_label = QLabel('Action:')
        self.action_input = QComboBox()
        self.add_button = QPushButton('Do choosen action')
        self.search_label = QLabel('Search in:')
        self.search_list = QComboBox()
        self.search_word = QLineEdit()
        self.search_button = QPushButton('Show content')
        self.table = QTableWidget()
        
        # Setting up layout

        layout = QGridLayout()
        layout.addWidget(self.type_label, 0, 0)
        layout.addWidget(self.number_label, 0, 1)
        layout.addWidget(self.value_label, 0, 2)
        layout.addWidget(self.quantity_label, 0, 3)
        layout.addWidget(self.note_label, 0, 4)
        layout.addWidget(self.action_label, 0, 5)
        layout.addWidget(self.type_input, 1, 0)
        layout.addWidget(self.number_input, 1, 1)
        layout.addWidget(self.value_input, 1, 2)
        layout.addWidget(self.quantity_input, 1, 3)
        layout.addWidget(self.note_input, 1, 4)
        layout.addWidget(self.action_input, 1, 5)
        layout.addWidget(self.add_button, 2, 0, 1 , 6)
        layout.addWidget(self.search_label, 3, 0)
        layout.addWidget(self.search_list, 3, 1, 1, 1)
        layout.addWidget(self.search_word, 3, 2, 1, 3)
        layout.addWidget(self.search_button, 3, 5)
        layout.addWidget(self.table, 4, 0, 6, 6)
        
        # Managing widgets

        self.action_input.addItem('Add element')
        self.action_input.addItem('Delete element')
        cursor = self.conn.cursor()
        cursor.execute('SELECT DISTINCT type from electronics')
        element_types = [row[0] for row in cursor.fetchall()]
        self.type_input.addItems(element_types)
        self.search_list.addItems(['Wszystkie'] + element_types)
        self.type_input.setEditable(True)

        # Adding functions for widgets

        self.add_button.clicked.connect(self.click)
        self.search_button.clicked.connect(self.show_content)


        # Setting up layout
        self.setLayout(layout)

    # Defining functions

    def addElement(self):
        type_value = self.type_input.currentText()
        number_value = self.number_input.text()
        value = self.value_input.text()
        quantity_value = self.quantity_input.text()
        note_value = self.note_input.text()
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID, quantity FROM electronics WHERE type = ? AND part_number = ? AND value = ?",
                   (type_value, number_value, value))
        existing_item = cursor.fetchone()

        if existing_item:
            # Item already exists, update the quantity
            existing_id, existing_quantity = existing_item
            new_quantity = int(existing_quantity) + int(quantity_value)
            cursor.execute("UPDATE electronics SET quantity = ? WHERE ID = ?", (new_quantity, existing_id))
        else:
            cursor.execute("INSERT INTO electronics (type, part_number, value, quantity, note) VALUES (?, ?, ?, ?, ?)",
                       (type_value, number_value, value, quantity_value, note_value))

        # Commit transaction and clo

        self.conn.commit()
        
        
        # Clear the input fields after adding to the database

        self.type_input.clear()
        self.number_input.clear()
        self.value_input.clear()
        self.quantity_input.clear()
        self.note_input.clear()
        
    def deleteElement(self):
        type_value = self.type_input.currentText()
        number_value = self.number_input.text()
        value = self.value_input.text()
        quantity = self.quantity_input.text()
        note = self.note_input.text()
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID, quantity FROM electronics WHERE type = ? AND part_number = ? AND value = ?",
                   (type_value, number_value, value))
        existing_item = cursor.fetchone()
        if existing_item:
            pass
        else:
            pass
        
    def click(self):
        action = self.action_input.currentText()
        if 'Add' in action:
            self.addElement()
        else:
            self.delete_selected_items()
        cursor = self.conn.cursor()
        cursor.execute('SELECT DISTINCT type from electronics')
        element_types = [row[0] for row in cursor.fetchall()]
        self.type_input.addItems(element_types)
        
    def show_content(self):
        search_type = self.search_list.currentText()
        search_word = self.search_word.text()
        cursor = self.conn.cursor()

        if search_type == 'Wszystkie' and not search_word:  # Show entire table when "Wszystkie" and empty search word
            cursor.execute("SELECT * FROM electronics")
        elif search_type == 'Wszystkie':  # Handle "Wszystkie" with a search word
            cursor.execute("SELECT * FROM electronics WHERE part_number LIKE ? OR value LIKE ? OR quantity LIKE ? OR note LIKE ?",
                        ('%' + search_word + '%', '%' + search_word + '%', '%' + search_word + '%', '%' + search_word + '%'))
        else:
            cursor.execute("SELECT * FROM electronics WHERE type = ? AND (part_number LIKE ? OR value LIKE ? OR quantity LIKE ? OR note LIKE ?)",
                        (search_type, '%' + search_word + '%', '%' + search_word + '%', '%' + search_word + '%', '%' + search_word + '%'))
        data = cursor.fetchall()
        columns = ['ID', 'Type', 'Part Number', 'Value', 'Quantity' , 'Note']
        df = pd.DataFrame(data, columns = columns)
        df = df.drop(df.columns[0], axis = 1)
        self.table.setRowCount(df.shape[0])
        self.table.setColumnCount(df.shape[1])
        self.table.setHorizontalHeaderLabels(df.columns.insert(0, 'Check'))
        for i, row in enumerate(range(df.shape[0])):
            checkbox = QCheckBox()
            self.table.setCellWidget(i, 0, checkbox)
            for col in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iat[row, col]))
                self.table.setItem(row, col + 1, item)

        self.table.resizeColumnsToContents()
            


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DatabaseApp()
    window.show()
    sys.exit(app.exec_())