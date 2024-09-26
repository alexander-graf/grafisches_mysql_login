from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QMessageBox, QApplication
from settings_window import SettingsWindow
from leads_window import LeadsWindow
from config import CONFIG_PATH, load_config
from database import verify_database_connection
import json
import pymysql
import os


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
        self.moveToFirstScreen()

    def moveToFirstScreen(self):
        desktop = QApplication.desktop()
        primary_screen = desktop.primaryScreen()
        screen_geometry = desktop.screenGeometry(primary_screen)
        self.move(screen_geometry.left(), screen_geometry.top())


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
                leads_window = LeadsWindow(leads, self.db_config)  # Hier übergeben wir self.db_config
                leads_window.exec_()
            else:
                print("No records found in leads table.")
                QMessageBox.information(self, 'Info', 'No leads found in the database.')

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred while fetching leads: {str(e)}')
            print(f"Error in loadLeads: {str(e)}")


    def showAbout(self):
        QMessageBox.information(self, "About", "This is a modular GUI application for MySQL/MariaDB.")
