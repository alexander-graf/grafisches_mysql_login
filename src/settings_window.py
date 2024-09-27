from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QPushButton, QMessageBox, QGroupBox)

import os
import json

CONFIG_PATH = os.path.expanduser('~/.config/mariadb_login.json')
TICKET_CONFIG_PATH = os.path.expanduser('~/.config/ticket_system_config.json')

class LeadsSettingsWindow(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle('Leads Database Settings')
        layout = QFormLayout()

        self.host_input = QLineEdit()
        layout.addRow('Host:', self.host_input)
        self.user_input = QLineEdit()
        layout.addRow('User:', self.user_input)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addRow('Password:', self.password_input)
        self.db_input = QLineEdit()
        layout.addRow('Database:', self.db_input)

        save_button = QPushButton('Save')
        save_button.clicked.connect(self.saveConfig)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def saveConfig(self):
        host = self.host_input.text().strip()
        user = self.user_input.text().strip()
        password = self.password_input.text().strip()
        db = self.db_input.text().strip()

        if not (host and user and password and db):
            QMessageBox.warning(self, 'Warning', 'All fields must be filled out.')
            return

        config_data = {
            'host': host,
            'user': user,
            'password': password,
            'db': db
        }

        try:
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, 'w') as config_file:
                json.dump(config_data, config_file)
            print(f"Leads configuration saved to {CONFIG_PATH}")

            self.main_window.loadConfig()
            QMessageBox.information(self, 'Success', 'Leads configuration saved successfully.')
            self.main_window.verifyLeadsDatabaseConnection()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save leads configuration: {str(e)}')
            print(f"Error saving leads configuration: {str(e)}")

class TicketSettingsWindow(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle('Ticket System Database Settings')
        layout = QFormLayout()

        self.host_input = QLineEdit()
        layout.addRow('Host:', self.host_input)
        self.user_input = QLineEdit()
        layout.addRow('User:', self.user_input)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addRow('Password:', self.password_input)
        self.db_input = QLineEdit()
        layout.addRow('Database:', self.db_input)

        save_button = QPushButton('Save')
        save_button.clicked.connect(self.saveConfig)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def saveConfig(self):
        host = self.host_input.text().strip()
        user = self.user_input.text().strip()
        password = self.password_input.text().strip()
        db = self.db_input.text().strip()

        if not (host and user and password and db):
            QMessageBox.warning(self, 'Warning', 'All fields must be filled out.')
            return

        config_data = {
            'host': host,
            'user': user,
            'password': password,
            'db': db
        }

        try:
            os.makedirs(os.path.dirname(TICKET_CONFIG_PATH), exist_ok=True)
            with open(TICKET_CONFIG_PATH, 'w') as config_file:
                json.dump(config_data, config_file)
            print(f"Ticket configuration saved to {TICKET_CONFIG_PATH}")

            self.main_window.loadTicketConfig()
            QMessageBox.information(self, 'Success', 'Ticket configuration saved successfully.')
            self.main_window.verifyTicketDatabaseConnection()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save ticket configuration: {str(e)}')
            print(f"Error saving ticket configuration: {str(e)}")
