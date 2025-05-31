import os
import json
import hashlib
import pathlib
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFormLayout, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QTimer

from register_dialog import RegisterDialog
from reset_dialog import ResetDialog


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setFixedSize(350, 300)
        self.setWindowIcon(QIcon("images/login.png"))
        self.USER_FILE = self.get_gradesys_path() / "users.json"
        self.logged_in_user = None
        self.failed_attempts = 0
        self.locked_out = False
        self.remaining_time = 30
        self.lockout_timer = QTimer()
        self.countdown_label = QLabel()
        self.init_ui()

    def get_gradesys_path(self):
        documents_dir = pathlib.Path.home() / "Documents"
        gradesys_dir = documents_dir / "GradeSys"
        gradesys_dir.mkdir(parents=True, exist_ok=True)
        return gradesys_dir

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Welcome, please login")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        main_layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setStyleSheet("padding: 5px;")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("padding: 5px;")

        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)

        main_layout.addLayout(form_layout)

        # Countdown label
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setStyleSheet("color: red;")
        main_layout.addWidget(self.countdown_label)

        # Login button
        button_layout = QHBoxLayout()
        button_layout.addItem(QSpacerItem(20, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.login_button = QPushButton("Login")
        self.login_button.setFixedWidth(100)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.login_button.clicked.connect(self.check_credentials)

        button_layout.addWidget(self.login_button)
        button_layout.addItem(QSpacerItem(20, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        main_layout.addLayout(button_layout)

        # Combined Register + Forgot Password Label
        action_label = QLabel('<a href="register">Not registered?</a> | <a href="reset">Forgot password?</a>')
        action_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        action_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        action_label.setOpenExternalLinks(False)
        action_label.linkActivated.connect(self.handle_link_clicked)
        main_layout.addWidget(action_label)

        self.setLayout(main_layout)
        self.valid = False

        # Timer setup
        self.lockout_timer.setInterval(1000)
        self.lockout_timer.timeout.connect(self.update_countdown)
    def clear_input(self):
        self.username_input.setText("")
        self.password_input.setText("")
    def check_credentials(self):
        if self.locked_out:
            QMessageBox.warning(self, "Locked Out", "Please wait before trying again.")
            return

        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not os.path.exists(self.USER_FILE):
            QMessageBox.warning(self, "Login Failed", "No users registered yet.")
            return

        with open(self.USER_FILE, "r") as f:
            users = json.load(f)

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if username in users and users[username] == hashed_password:
            self.valid = True
            self.logged_in_user = username
            self.accept()
        else:
            self.clear_input()
            self.failed_attempts += 1
            if self.failed_attempts >= 3:
                self.start_lockout()
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password")

    def start_lockout(self):
        self.locked_out = True
        self.remaining_time = 30
        self.login_button.setEnabled(False)
        self.update_countdown()
        self.lockout_timer.start()

    def update_countdown(self):
        if self.remaining_time > 0:
            self.countdown_label.setText(f"Too many attempts. Try again in {self.remaining_time} seconds.")
            self.remaining_time -= 1
        else:
            self.failed_attempts = 0
            self.locked_out = False
            self.login_button.setEnabled(True)
            self.countdown_label.clear()
            self.lockout_timer.stop()

    def handle_link_clicked(self, link):
        if link == "register":
            dialog = RegisterDialog()
            if dialog.exec():
                QMessageBox.information(self, "Success", "Registered successfully! Please login.")
        elif link == "reset":
            dialog = ResetDialog()
            dialog.exec()


