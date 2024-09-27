import pymysql
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTextEdit, QScrollArea, QWidget, QGridLayout, QDesktopWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
import datetime

class CustomTextEdit(QTextEdit):
    def __init__(self, parent, key, initial_value):
        super().__init__(parent)
        self.parent = parent
        self.key = key
        self.initial_value = initial_value
        self.setPlainText(str(initial_value))

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Tab:
            self.parent.focusNextChild()
        elif event.key() == Qt.Key_Backtab:
            self.parent.focusPreviousChild()
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event):
        current_value = self.toPlainText()
        if current_value != str(self.initial_value):
            self.parent.update_field(self.key, current_value)
        super().focusOutEvent(event)

class TicketWindow(QDialog):
    def __init__(self, db_config):
        super().__init__()
        self.db_config = db_config
        self.tickets = self.fetch_tickets()
        self.table_structure = self.get_table_structure()
        self.inactive_fields = self.get_inactive_fields()
        self.current_index = 0
        self.initUI()
        self.moveToFirstScreen()

    def fetch_tickets(self):
        try:
            connection = pymysql.connect(**self.db_config, charset='utf8mb4',
                                         cursorclass=pymysql.cursors.DictCursor)
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM ost_user_email")
                tickets = cursor.fetchall()
            connection.close()
            return tickets
        except Exception as e:
            print(f"Error fetching tickets: {str(e)}")
            return []

    def get_table_structure(self):
        try:
            connection = pymysql.connect(**self.db_config, charset='utf8mb4',
                                         cursorclass=pymysql.cursors.DictCursor)
            with connection.cursor() as cursor:
                cursor.execute("DESCRIBE ost_user_email")
                columns = cursor.fetchall()
            connection.close()
            return columns
        except Exception as e:
            print(f"Error fetching table structure: {str(e)}")
            return []

    def get_inactive_fields(self):
        inactive = []
        for column in self.table_structure:
            if column['Key'] == 'PRI' or column['Extra'] == 'auto_increment':
                inactive.append(column['Field'])
        print(f"Inactive fields: {inactive}")
        return inactive

    def initUI(self):
        self.setWindowTitle('Tickets')
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout()

        self.total_label = QLabel(f"Total records: {len(self.tickets)}")
        layout.addWidget(self.total_label)

        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.grid_layout = QGridLayout()
        scroll_widget.setLayout(self.grid_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton('Previous')
        self.prev_button.clicked.connect(self.previous_ticket)
        self.next_button = QPushButton('Next')
        self.next_button.clicked.connect(self.next_ticket)
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)
        layout.addLayout(nav_layout)

        self.setLayout(layout)

        self.display_ticket()

    def display_ticket(self):
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)

        ticket = self.tickets[self.current_index]
        row = 0
        col = 0
        for key, value in ticket.items():
            label = QLabel(f"{key}:")
            text_edit = CustomTextEdit(self, key, value)
            text_edit.setFixedHeight(30)
            text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            if key in self.inactive_fields:
                text_edit.setReadOnly(True)
                text_edit.setStyleSheet("background-color: #f0f0f0;")
                print(f"Deactivated field: {key}")
            else:
                text_edit.setReadOnly(False)
                text_edit.setStyleSheet("")
                print(f"Active field: {key}")
            
            self.grid_layout.addWidget(label, row, col * 2)
            self.grid_layout.addWidget(text_edit, row, col * 2 + 1)
            
            col += 1
            if col == 3:
                col = 0
                row += 1

        self.update_nav_buttons()

    def update_nav_buttons(self):
        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < len(self.tickets) - 1)

    def previous_ticket(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_ticket()

    def next_ticket(self):
        if self.current_index < len(self.tickets) - 1:
            self.current_index += 1
            self.display_ticket()

    def update_field(self, key, new_value):
        if key == 'attribution_date':
            if new_value.strip() == '':
                new_value = None
            else:
                try:
                    datetime.datetime.strptime(new_value, '%Y-%m-%d')
                except ValueError:
                    print(f"Invalid date format for {key}. Expected format: YYYY-MM-DD")
                    return

        if self.tickets[self.current_index][key] != new_value:
            self.tickets[self.current_index][key] = new_value
            print(f"Updated field '{key}' to '{new_value}'")
            self.save_ticket()
        else:
            print(f"Field '{key}' not changed, skipping save")

    def save_ticket(self):
        ticket = self.tickets[self.current_index]
        try:
            connection = pymysql.connect(**self.db_config, charset='utf8mb4',
                                         cursorclass=pymysql.cursors.DictCursor)
            with connection.cursor() as cursor:
                placeholders = ', '.join(['%s = %%s' % key for key in ticket.keys()])
                query = f"UPDATE ost_user_email SET {placeholders} WHERE id = %s"
                print(f"Executing query: {query}")
                print(f"With values: {list(ticket.values()) + [ticket['id']]}")
                cursor.execute(query, list(ticket.values()) + [ticket['id']])
            connection.commit()
            connection.close()
            print(f"Ticket {ticket['id']} saved successfully")
        except Exception as e:
            print(f"Error saving ticket: {str(e)}")

    def moveToFirstScreen(self):
        desktop = QDesktopWidget()
        primary_screen = desktop.primaryScreen()
        screen_geometry = desktop.screenGeometry(primary_screen)
        self.move(screen_geometry.left(), screen_geometry.top())
