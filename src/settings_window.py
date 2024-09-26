from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QMessageBox
import os
import json

CONFIG_PATH = os.path.expanduser('~/.config/mariadb_login.json')

class SettingsWindow(QDialog):
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
