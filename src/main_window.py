import sys
import os
import json
import pymysql
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QMessageBox,
                             QAction, QDesktopWidget)

from settings_window import LeadsSettingsWindow, TicketSettingsWindow
from leads_window import LeadsWindow

CONFIG_PATH = os.path.expanduser('~/.config/mariadb_login.json')
TICKET_CONFIG_PATH = os.path.expanduser('~/.config/ticket_system_config.json')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.CONFIG_PATH = os.path.expanduser('~/.config/mariadb_login.json')
        self.setWindowTitle('Modular GUI Application')
        self.setGeometry(100, 100, 800, 600)
        self.text_edit = QTextEdit(self)
        self.setCentralWidget(self.text_edit)
        self.createMenu()
        self.leads_db_config = None
        self.ticket_db_config = None
        self.checkConfigAndConnect()
        self.moveToFirstScreen()

    def createMenu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu('File')
        settings_action = QAction('Einstellungen', self)
        settings_action.triggered.connect(self.openSettings)
        file_menu.addAction(settings_action)

        about_action = QAction('About', self)
        about_action.triggered.connect(self.showAbout)
        file_menu.addAction(about_action)

        open_menu = menubar.addMenu('Open')
        load_leads_action = QAction('Lade Leads', self)
        load_leads_action.triggered.connect(self.loadLeads)
        open_menu.addAction(load_leads_action)

        ticket_system_action = QAction('Ticket System', self)
        ticket_system_action.triggered.connect(self.openTicketSystem)
        open_menu.addAction(ticket_system_action)

    def checkConfigAndConnect(self):
        self.loadLeadsConfig()
        self.loadTicketConfig()
        if not self.leads_db_config:
            self.promptForLeadsCredentials()
        if not self.ticket_db_config:
            self.promptForTicketCredentials()
        self.verifyDatabaseConnections()


    def loadConfig(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as file:
                self.leads_db_config = json.load(file)
        if os.path.exists(TICKET_CONFIG_PATH):
            with open(TICKET_CONFIG_PATH, 'r') as file:
                self.ticket_db_config = json.load(file)

    def verifyDatabaseConnections(self):
        self.verifyLeadsDatabaseConnection()
        self.verifyTicketDatabaseConnection()

    def verifyLeadsDatabaseConnection(self):
        if not self.leads_db_config:
            QMessageBox.critical(self, 'Error', 'Leads database configuration is missing.')
            return
        try:
            connection = pymysql.connect(**self.leads_db_config, charset='utf8mb4',
                                         cursorclass=pymysql.cursors.DictCursor)
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            connection.close()
            print("Leads database connection verified successfully.")
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to connect to leads database: {str(e)}')

    def verifyTicketDatabaseConnection(self):
        if not self.ticket_db_config:
            QMessageBox.critical(self, 'Error', 'Ticket system database configuration is missing.')
            return
        try:
            connection = pymysql.connect(**self.ticket_db_config, charset='utf8mb4',
                                         cursorclass=pymysql.cursors.DictCursor)
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            connection.close()
            print("Ticket system database connection verified successfully.")
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to connect to ticket system database: {str(e)}')

    def promptForDatabaseCredentials(self):
        settings_window = SettingsWindow(self)
        settings_window.exec_()
        
    def openSettings(self):
        self.promptForLeadsCredentials()
        self.promptForTicketCredentials()


    def loadLeads(self):
        if self.leads_db_config:
            leads_window = LeadsWindow(self.leads_db_config)
            leads_window.exec_()
        else:
            QMessageBox.critical(self, 'Error', 'Leads database configuration is missing.')

    def openTicketSystem(self):
        if self.ticket_db_config:
            from ticket_window import TicketWindow
            ticket_window = TicketWindow(self.ticket_db_config)
            ticket_window.exec_()
        else:
            QMessageBox.critical(self, 'Error', 'Ticket system database configuration is missing.')

    def showAbout(self):
        QMessageBox.information(self, "About", "This is a modular GUI application for MySQL/MariaDB.")

    def moveToFirstScreen(self):
        desktop = QDesktopWidget()
        primary_screen = desktop.primaryScreen()
        screen_geometry = desktop.screenGeometry(primary_screen)
        self.move(screen_geometry.left(), screen_geometry.top())
    
    def loadLeadsConfig(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as file:
                self.leads_db_config = json.load(file)

    def loadTicketConfig(self):
        if os.path.exists(TICKET_CONFIG_PATH):
            with open(TICKET_CONFIG_PATH, 'r') as file:
                self.ticket_db_config = json.load(file)

    def promptForLeadsCredentials(self):
        leads_settings = LeadsSettingsWindow(self)
        leads_settings.exec_()

    def promptForTicketCredentials(self):
        ticket_settings = TicketSettingsWindow(self)
        ticket_settings.exec_()


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
