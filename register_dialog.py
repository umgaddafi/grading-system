import os 
import json
import hashlib
import pathlib
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFormLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class RegisterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register")
        self.setFixedSize(350, 250)
        self.USER_FILE = self.get_gradesys_path() / "users.json"
        self.init_ui()

    def get_gradesys_path(self):
        documents_dir = pathlib.Path.home() / "Documents"
        gradesys_dir = documents_dir / "GradeSys"
        gradesys_dir.mkdir(parents=True, exist_ok=True)
        return gradesys_dir

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Create New Account")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        form_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose a username")

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter a password")

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("Confirm your password")

        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("Confirm:", self.confirm_input)

        layout.addLayout(form_layout)

        register_button = QPushButton("Register")
        register_button.clicked.connect(self.register_user)
        layout.addWidget(register_button)

        self.setLayout(layout)
   
    def register_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not username or not password or not confirm:
            QMessageBox.warning(self, "Error", "All fields are required")
            return

        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return

        users = self.load_users()
        if username in users:
            QMessageBox.warning(self, "Error", "Username already exists")
            return

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        users[username] = hashed_password

        with open(self.USER_FILE, "w") as f:
            json.dump(users, f)

        self.accept()

    def load_users(self):
        if not os.path.exists(self.USER_FILE):
            return {}
        with open(self.USER_FILE, "r") as f:
            return json.load(f)

