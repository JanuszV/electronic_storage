import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QCheckBox, QMessageBox, QTextBrowser, QStyledItemDelegate
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import pandas as pd
import re
import webbrowser
import os

class DatabaseApp(QWidget):
    def __init__(self):
        super().__init__()
        # Get the path to the directory where the script is located
        current_directory = os.path.dirname(os.path.abspath(__file__))
        database_path = os.path.join(current_directory, "mydb.db")  # Replace with your database file name
        try:
            self.conn = sqlite3.connect(database_path)
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
        self.showMaximized()

        # Creating widgets

        self.type_label = QLabel('Type:')
        self.type_input = QComboBox()
        self.number_label = QLabel('Part number:')
        self.number_input = QLineEdit()
        self.value_label = QLabel('Value:')
        self.value_input = QLineEdit()
        self.quantity_label = QLabel('Quantity:')
        self.quantity_input = QLineEdit('1')
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
        
        # Set fixed height for header labels
        header_labels = [self.type_label, self.number_label, self.value_label, self.quantity_label, self.note_label, self.action_label]
        for label in header_labels:
            label.setFixedHeight(25)  # Adjust the height as needed

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
        self.quantity_input.textChanged.connect(self.update_add_button_state)
        self.action_input.currentTextChanged.connect(self.update_add_button_state)

        # Setting up layout
        self.setLayout(layout)
        self.show_content()  # Load the content initially
        

    # Defining functions
    def open_link(self, link):
        webbrowser.open(link)
    def update_add_button_state(self):
        # Enable the add_button if quantity_input is not empty, disable it otherwise
        if 'Add' in self.action_input.currentText():
            if self.quantity_input.text():
                self.add_button.setEnabled(True)
            else:
                self.add_button.setEnabled(False)
        else: 
            self.add_button.setEnabled(True)
    def addElement(self):
        type_value = self.type_input.currentText()
        number_value = self.number_input.text()
        value = self.value_input.text()
        quantity_value = self.quantity_input.text()
        note_value = self.note_input.text()
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID, quantity, note FROM electronics WHERE type = ? AND part_number = ? AND value = ?",
                   (type_value, number_value, value))
        existing_item = cursor.fetchone()

        if existing_item:
            # Item already exists, update the quantity
            existing_id, existing_quantity, existing_note = existing_item
            new_quantity = int(existing_quantity) + int(quantity_value)
            print(existing_note)
            if existing_note == '':
                existing_note = note_value
            cursor.execute("UPDATE electronics SET quantity = ?, note = ? WHERE ID = ?", (new_quantity, existing_note, existing_id))
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"Quantity updated successfully. New quantity: {new_quantity}")
            msg.setWindowTitle("Success")
            msg.exec_()
        else:
            cursor.execute("INSERT INTO electronics (type, part_number, value, quantity, note) VALUES (?, ?, ?, ?, ?)",
                       (type_value, number_value, value, quantity_value, note_value))
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("New item added successfully.")
            msg.setWindowTitle("Success")
            msg.exec_()
        # Commit transaction and clo
        self.conn.commit()
        
        
        
        # Clear the input fields after adding to the database

        self.type_input.clear()
        self.number_input.clear()
        self.value_input.clear()
        self.quantity_input.clear()
        self.note_input.clear()
        
    def decreaseElement(self):
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
            existing_id, existing_quantity = existing_item
            new_quantity = int(existing_quantity) - int(quantity) if quantity else int(existing_quantity)
            if new_quantity < 0:
                # Show a popup message that the quantity cannot be decreased further
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error: Quantity cannot be decreased further.")
                msg.setWindowTitle("Error")
                msg.exec_()
            else:
                cursor.execute("UPDATE electronics SET quantity = ? WHERE ID = ?", (new_quantity, existing_id))
                self.conn.commit()
                # Show a success message
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText(f"Quantity decreased successfully. New quantity: {new_quantity}")
                msg.setWindowTitle("Success")
                msg.exec_()
        else:
            # Show a popup message that the element doesn't exist
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Error: The element does not exist.")
            msg.setWindowTitle("Error")
            msg.exec_()
    def are_checkboxes_checked(self):
        column_index = 1  # Replace with the actual index of the checkbox column
        for row in range(self.table.rowCount()):
            item = self.table.item(row, column_index)
            if item is not None and isinstance(item, QTableWidgetItem):
                checkbox = self.table.cellWidget(row, column_index)
                if checkbox is not None and isinstance(checkbox, QCheckBox):
                    if checkbox.isChecked():
                        return True
        return False
    def click(self):
        action = self.action_input.currentText()
        if 'Add' in action:
            self.addElement()
        else:
            if self.are_checkboxes_checked():
                self.delete_selected_items()
            else:
                self.decreaseElement()
        cursor = self.conn.cursor()
        cursor.execute('SELECT DISTINCT type from electronics')
        element_types = [row[0] for row in cursor.fetchall()]
        self.type_input.addItems(element_types)
    # Implement the method to delete an item by ID
    def delete_items_by_ids(self, ids):
        cursor = self.conn.cursor()
        try:
            for item_id in ids:
                cursor.execute("DELETE FROM electronics WHERE ID = ?", (item_id,))
            self.conn.commit()
            print(f"{len(ids)} item(s) deleted successfully")
        except Exception as e:
            print(f"Error deleting items: {e}")
    def delete_selected_items(self):
        # Create a list to store the IDs of selected items
        ids_to_delete = []

        # Iterate through the rows and check if the checkbox is selected
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 1)
            if checkbox.isChecked():
                # Get the ID of the item in the first column (assuming it's the ID)
                item_id = self.table.item(row, 0).text()  # Assuming the ID is in the second column
                ids_to_delete.append(item_id)

        # Delete selected items from the database
        self.delete_items_by_ids(ids_to_delete)

        # Refresh the table after deleting items
        self.show_content()     
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
        df.insert(1, 'Check', '')
        self.table.setRowCount(df.shape[0])
        self.table.setColumnCount(df.shape[1])
        self.table.setHorizontalHeaderLabels(df.columns)
        for i, row in enumerate(range(df.shape[0])):
            checkbox = QCheckBox()
            self.table.setCellWidget(i, 1, checkbox)
            for j ,col in enumerate(range(df.shape[1])):
                value = str(df.iat[row, col])
                if j == 6 and re.match(r'https?://', value):
                    link_label = QLabel('<a href="{0}">{0}</a>'.format(value))
                    link_label.setOpenExternalLinks(True)
                    link_label.linkActivated.connect(self.open_link)
                    self.table.setCellWidget(i, j, link_label)
                else:
                    item = QTableWidgetItem(value)
                    self.table.setItem(row, col, item)
        self.table.resizeColumnsToContents()
            


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DatabaseApp()
    window.show()
    sys.exit(app.exec_())