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


class ResetDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reset Password")
        self.setFixedSize(350, 300)
        self.USER_FILE = self.get_gradesys_path() / "users.json"
        self.init_ui()

    def get_gradesys_path(self):
        documents_dir = pathlib.Path.home() / "Documents"
        gradesys_dir = documents_dir / "GradeSys"
        gradesys_dir.mkdir(parents=True, exist_ok=True)
        return gradesys_dir

    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Reset Your Password")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.main_layout.addWidget(title)

        self.form_layout = QFormLayout()
        self.main_layout.addLayout(self.form_layout)

        # Username input and check button
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.check_button = QPushButton("Check Username")
        self.check_button.clicked.connect(self.check_username)

        self.form_layout.addRow(self.username_label, self.username_input)
        self.form_layout.addRow("", self.check_button)

        # New password and confirm password fields
        self.new_password_label = QLabel("New Password:")
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setPlaceholderText("Enter new password")

        self.confirm_label = QLabel("Confirm:")
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("Confirm new password")

        # Reset button
        self.reset_button = QPushButton("Reset Password")
        self.reset_button.clicked.connect(self.reset_password)

        # Add but initially hide password fields and reset button
        for widget in [
            self.new_password_label, self.new_password_input,
            self.confirm_label, self.confirm_input,
            self.reset_button
        ]:
            widget.hide()

        self.setLayout(self.main_layout)

    def check_username(self):
        username = self.username_input.text().strip()

        if not username:
            QMessageBox.warning(self, "Error", "Please enter a username.")
            return

        if not os.path.exists(self.USER_FILE):
            QMessageBox.warning(self, "Error", "No user data found.")
            return

        with open(self.USER_FILE, "r") as f:
            users = json.load(f)

        if username not in users:
            QMessageBox.warning(self, "Error", "Username not found.")
        else:
            QMessageBox.information(self, "Verified", "Username found. Please reset your password.")
            self.clear_to_reset_only()

    def clear_to_reset_only(self):
        # Remove all widgets in form layout
        while self.form_layout.rowCount() > 0:
            self.form_layout.removeRow(0)

        # Add only password reset fields
        self.form_layout.addRow(self.new_password_label, self.new_password_input)
        self.form_layout.addRow(self.confirm_label, self.confirm_input)
        self.main_layout.addWidget(self.reset_button)

        # Show the fields
        self.new_password_label.show()
        self.new_password_input.show()
        self.confirm_label.show()
        self.confirm_input.show()
        self.reset_button.show()

        self.new_password_input.setFocus()

    def reset_password(self):
        username = self.username_input.text().strip()
        new_pass = self.new_password_input.text()
        confirm_pass = self.confirm_input.text()

        if not new_pass or not confirm_pass:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        if new_pass != confirm_pass:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return

        with open(self.USER_FILE, "r") as f:
            users = json.load(f)

        hashed_password = hashlib.sha256(new_pass.encode()).hexdigest()
        users[username] = hashed_password

        with open(self.USER_FILE, "w") as f:
            json.dump(users, f)

        QMessageBox.information(self, "Success", "Password reset successfully.")
        self.accept()

