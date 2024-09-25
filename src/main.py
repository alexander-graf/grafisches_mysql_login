import sys
import os
import json
import pymysql
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QTextEdit, QPushButton, QMessageBox,
                             QMenuBar, QAction, QFormLayout, QLineEdit, QDialog)

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
                    print(f"DB Config: {self.db_config}")  # Debugging output
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
        settings_window.exec_()  # Use exec_() for modal dialog

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
                cursor.execute("SELECT 1")  # Simple query to verify connection
                result = cursor.fetchone()
                print(f"Connection verification result: {result}")

            connection.close()  # Close the connection after use
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
        settings_window.exec_()  # Use exec_() for modal dialog

    def loadLeads(self):
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
                cursor.execute("SELECT * FROM leads")  # Fetch all records from leads table
                leads = cursor.fetchall()

                if leads:
                    for lead in leads:
                        print(lead)  # Print each lead record to console
                else:
                    print("No records found in leads table.")

            connection.close()  # Close the connection after use
            print("Connection closed.")

        except pymysql.MySQLError as e:
            QMessageBox.critical(self, 'Database Error', f'Failed to connect to the database: {str(e)}')
            print(f"Database Connection Error: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred while fetching leads: {str(e)}')
            print(f"Error in loadLeads: {str(e)}")

    def showAbout(self):
         QMessageBox.information(self, "About", "This is a modular GUI application for MySQL/MariaDB.")


class SettingsWindow(QDialog):  # Change QWidget to QDialog
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
        self.password_input.setEchoMode(QLineEdit.Password)  # Hide password input
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
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)  # Create directory if it doesn't exist
            with open(CONFIG_PATH, 'w') as config_file:
                json.dump(config_data, config_file)
                print(f"Configuration saved to {CONFIG_PATH}")

            # Load and verify database connection after saving config
            self.main_window.loadConfig()  # Reload config after saving
            
            QMessageBox.information(self, 'Success', 'Configuration saved successfully.')
            
            # Verify connection after saving new credentials
            self.main_window.verifyDatabaseConnection()

            print("Configuration saved successfully.")
            
            self.close()  # Close settings window after saving

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save configuration: {str(e)}')
            print(f"Error saving configuration: {str(e)}")


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
