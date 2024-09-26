import sys
import os
import json
import pymysql
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QTextEdit, QPushButton, QMessageBox,
                             QMenuBar, QAction, QFormLayout, QLineEdit, QDialog, QGridLayout,
                             QLabel, QScrollArea, QHBoxLayout)
from PyQt5.QtCore import Qt


CONFIG_PATH = os.path.expanduser('~/.config/mariadb_login.json')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Modular GUI Application')
        self.setGeometry(100, 100, 800, 600)
        self.text_edit = QTextEdit(self)
        self.setCentralWidget(self.text_edit)
        self.createMenu()
        self.db_config = None
        self.checkConfigAndConnect()

    def createMenu(self):
        menubar = self.menuBar()
        # Creating menu items
        file_menu = menubar.addMenu('File')
        settings_action = QAction('Einstellungen', self)
        settings_action.triggered.connect(self.openSettings)
        file_menu.addAction(settings_action)
        load_leads_action = QAction('Lade Leads', self)
        load_leads_action.triggered.connect(self.loadLeads)
        file_menu.addAction(load_leads_action)
        about_action = QAction('About', self)
        about_action.triggered.connect(self.showAbout)
        file_menu.addAction(about_action)

    def checkConfigAndConnect(self):
        if os.path.exists(CONFIG_PATH):
            print(f"Loading configuration from {CONFIG_PATH}")
            with open(CONFIG_PATH, 'r') as file:
                try:
                    self.db_config = json.load(file)
                    print("Configuration loaded successfully.")
                    print(f"DB Config: {self.db_config}") # Debugging output
                    # Attempt to connect to the database and verify
                    self.verifyDatabaseConnection()
                except json.JSONDecodeError as e:
                    print(f"JSON Decode Error: {str(e)}")
                    QMessageBox.critical(self, 'Error', 'Failed to parse configuration file.')
                except Exception as e:
                    print(f"Error loading configuration: {str(e)}")
                    QMessageBox.critical(self, 'Error', 'An error occurred while loading the configuration.')
        else:
            print(f"No configuration file found at {CONFIG_PATH}. Prompting for database credentials...")
            self.promptForDatabaseCredentials()

    def promptForDatabaseCredentials(self):
        settings_window = SettingsWindow(self)
        settings_window.exec_() # Use exec_() for modal dialog

    def loadConfig(self):
        """Load database configuration from JSON file."""
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as file:
                try:
                    self.db_config = json.load(file)
                    print("Configuration loaded successfully.")
                except json.JSONDecodeError as e:
                    print(f"JSON Decode Error: {str(e)}")
                except Exception as e:
                    print(f"Error loading configuration: {str(e)}")

    def verifyDatabaseConnection(self):
        if not self.db_config:
            QMessageBox.critical(self, 'Error', 'Database configuration is missing.')
            return
        try:
            host = self.db_config['host']
            user = self.db_config['user']
            password = self.db_config['password']
            db = self.db_config['db']
            print(f"Attempting to connect to database '{db}' at '{host}' with user '{user}'...")
            connection = pymysql.connect(host=host,
                                         user=user,
                                         password=password,
                                         db=db,
                                         charset='utf8mb4',
                                         cursorclass=pymysql.cursors.DictCursor)
            print("Connected to the database successfully.")
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1") # Simple query to verify connection
                result = cursor.fetchone()
                print(f"Connection verification result: {result}")
            connection.close() # Close the connection after use
            print("Connection closed.")
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, 'Database Error', f'Failed to connect to the database: {str(e)}')
            print(f"Database Connection Error: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred while verifying database connection: {str(e)}')
            print(f"Error in verifyDatabaseConnection: {str(e)}")

    def openSettings(self):
        print("Opening settings window...")
        settings_window = SettingsWindow(self)
        settings_window.exec_() # Use exec_() for modal dialog

    def loadLeads(self):
        if not self.db_config:
            QMessageBox.critical(self, 'Error', 'Database configuration is missing.')
            return

        try:
            connection = pymysql.connect(**self.db_config, charset='utf8mb4',
                                        cursorclass=pymysql.cursors.DictCursor)
            print("Connected to the database successfully.")

            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM leads")
                leads = cursor.fetchall()

            connection.close()
            print("Connection closed.")

            if leads:
                leads_window = LeadsWindow(leads)
                leads_window.exec_()
            else:
                print("No records found in leads table.")
                QMessageBox.information(self, 'Info', 'No leads found in the database.')

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred while fetching leads: {str(e)}')
            print(f"Error in loadLeads: {str(e)}")

    def showAbout(self):
        QMessageBox.information(self, "About", "This is a modular GUI application for MySQL/MariaDB.")

class SettingsWindow(QDialog): # Change QWidget to QDialog
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle('Einstellungen')
        layout = QFormLayout()
        # Input fields for MySQL credentials
        self.host_input = QLineEdit()
        layout.addRow('Host:', self.host_input)
        self.user_input = QLineEdit()
        layout.addRow('User:', self.user_input)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password) # Hide password input
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
            # Save configuration to JSON file
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True) # Create directory if it doesn't exist
            with open(CONFIG_PATH, 'w') as config_file:
                json.dump(config_data, config_file)
            print(f"Configuration saved to {CONFIG_PATH}")
            # Load and verify database connection after saving config
            self.main_window.loadConfig() # Reload config after saving
            QMessageBox.information(self, 'Success', 'Configuration saved successfully.')
            # Verify connection after saving new credentials
            self.main_window.verifyDatabaseConnection()
            print("Configuration saved successfully.")
            self.close() # Close settings window after saving
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save configuration: {str(e)}')
            print(f"Error saving configuration: {str(e)}")


class LeadsWindow(QDialog):
    def __init__(self, leads):
        super().__init__()
        self.leads = leads
        self.current_index = 0
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Leads')
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()

        # Scroll area for lead fields
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.form_layout = QVBoxLayout()
        scroll_widget.setLayout(self.form_layout)
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
        for i in reversed(range(self.form_layout.count())): 
            self.form_layout.itemAt(i).widget().setParent(None)

        lead = self.leads[self.current_index]
        for key, value in lead.items():
            label = QLabel(f"{key}:")
            text_edit = QTextEdit()
            text_edit.setPlainText(str(value))
            self.form_layout.addWidget(label)
            self.form_layout.addWidget(text_edit)

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



class LeadsWindow(QDialog):
    def __init__(self, leads):
        super().__init__()
        self.leads = leads
        self.current_index = 0
        self.initUI()

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
            text_edit = QTextEdit()
            text_edit.setPlainText(str(value))
            text_edit.setFixedHeight(30)  # Set a fixed height for normal row height
            text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable vertical scrollbar
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

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
