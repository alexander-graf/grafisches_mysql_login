from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTextEdit, QScrollArea, QWidget, QGridLayout, QDesktopWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
import pymysql

class CustomTextEdit(QTextEdit):
    def __init__(self, parent, key):
        super().__init__(parent)
        self.parent = parent
        self.key = key

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Tab:
            self.parent.focusNextChild()
        elif event.key() == Qt.Key_Backtab:
            self.parent.focusPreviousChild()
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event):
        self.parent.update_field(self.key, self.toPlainText())
        super().focusOutEvent(event)

from database import get_table_structure

class LeadsWindow(QDialog):
    def __init__(self, leads, db_config):
        super().__init__()
        self.leads = leads
        self.db_config = db_config
        self.table_structure = get_table_structure(self.db_config)
        self.inactive_fields = self.get_inactive_fields()
        self.current_index = 0
        self.initUI()
        self.moveToFirstScreen()

    
 
    def get_inactive_fields(self):
        inactive = []
        for column in self.table_structure:
            if column['Key'] == 'PRI' or column['Extra'] == 'auto_increment':
                inactive.append(column['Field'])
        print(f"Inactive fields: {inactive}")  # Debugging output
        return inactive


    def display_lead(self):
        # Clear previous fields
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)

        lead = self.leads[self.current_index]
        row = 0
        col = 0
        for key, value in lead.items():
            label = QLabel(f"{key}:")
            text_edit = CustomTextEdit(self, key)
            text_edit.setPlainText(str(value))
            text_edit.setFixedHeight(30)
            text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            if key in self.inactive_fields:
                text_edit.setReadOnly(True)
                text_edit.setStyleSheet("background-color: #f0f0f0;")
                print(f"Deactivated field: {key}")  # Debugging output
            
            self.grid_layout.addWidget(label, row, col * 2)
            self.grid_layout.addWidget(text_edit, row, col * 2 + 1)
            
            col += 1
            if col == 3:  # Move to next row after 3 columns
                col = 0
                row += 1

        self.update_nav_buttons()





    def initUI(self):
        self.setWindowTitle('Leads')
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout()

        # Display total number of records
        self.total_label = QLabel(f"Total records: {len(self.leads)}")
        layout.addWidget(self.total_label)

        # Scroll area for lead fields
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.grid_layout = QGridLayout()
        scroll_widget.setLayout(self.grid_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton('Previous')
        self.prev_button.clicked.connect(self.previous_lead)
        self.next_button = QPushButton('Next')
        self.next_button.clicked.connect(self.next_lead)
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)
        layout.addLayout(nav_layout)

        self.setLayout(layout)

        self.display_lead()

    def display_lead(self):
        # Clear previous fields
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)

        lead = self.leads[self.current_index]
        row = 0
        col = 0
        for key, value in lead.items():
            label = QLabel(f"{key}:")
            text_edit = CustomTextEdit(self, key)
            text_edit.setPlainText(str(value))
            text_edit.setFixedHeight(30)
            text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            if key in self.inactive_fields:
                text_edit.setReadOnly(True)
                text_edit.setStyleSheet("background-color: #f0f0f0;")
                print(f"Deactivated field: {key}")  # Debugging output
            else:
                text_edit.setReadOnly(False)
                text_edit.setStyleSheet("")
                print(f"Active field: {key}")  # Debugging output
            
            self.grid_layout.addWidget(label, row, col * 2)
            self.grid_layout.addWidget(text_edit, row, col * 2 + 1)
            
            col += 1
            if col == 3:  # Move to next row after 3 columns
                col = 0
                row += 1

        self.update_nav_buttons()


    def update_nav_buttons(self):
        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < len(self.leads) - 1)

    def previous_lead(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_lead()

    def next_lead(self):
        if self.current_index < len(self.leads) - 1:
            self.current_index += 1
            self.display_lead()

    def update_field(self, key, new_value):
        if self.leads[self.current_index][key] != new_value:
            self.leads[self.current_index][key] = new_value
            print(f"Updated field '{key}' to '{new_value}'")
            self.save_lead()

    def save_lead(self):
        lead = self.leads[self.current_index]
        try:
            connection = pymysql.connect(**self.db_config, charset='utf8mb4',
                                         cursorclass=pymysql.cursors.DictCursor)
            with connection.cursor() as cursor:
                placeholders = ', '.join(['%s = %%s' % key for key in lead.keys()])
                query = f"UPDATE leads SET {placeholders} WHERE id = %s"
                cursor.execute(query, list(lead.values()) + [lead['id']])
            connection.commit()
            connection.close()
            print(f"Lead {lead['id']} saved successfully")
        except Exception as e:
            print(f"Error saving lead: {str(e)}")

    def moveToFirstScreen(self):
        desktop = QDesktopWidget()
        primary_screen = desktop.primaryScreen()
        screen_geometry = desktop.screenGeometry(primary_screen)
        self.move(screen_geometry.left(), screen_geometry.top())
