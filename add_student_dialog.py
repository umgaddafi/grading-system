from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSpinBox, QMessageBox, QStackedWidget, QWidget, QProgressBar
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt


class AddStudentDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add New Student")
        self.setWindowIcon(QIcon("./images/add.png"))
        self.setFixedSize(500, 320)
        self.setStyleSheet("""
            QDialog {
                background-color: #f4f6f9;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit, QSpinBox {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 6px;
                background-color: white;
            }
            QPushButton {
                background-color: #2f80ed;
                color: white;
                padding: 8px 18px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1c6dd0;
            }
            QPushButton:disabled {
                background-color: #bbb;
            }
            QProgressBar {
                border: 0px;
                background-color: #e0e0e0;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #2f80ed;
                border-radius: 4px;
            }
        """)

        self.current_step = 0
        self.steps = []
        self.stacked_widget = QStackedWidget()
        self.step_titles = [
            "Student Name",
            "ID Number",
            "C.A (0-30)",
            "Practical (0-20)",
            "Exam (0-50)"
        ]

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full name")
        self.name_input.textChanged.connect(self.validate_current)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("CSC/22U/XXXX")
        self.id_input.textChanged.connect(self.validate_current)

        self.ca_input = QSpinBox()
        self.ca_input.setRange(0, 30)

        self.practical_input = QSpinBox()
        self.practical_input.setRange(0, 20)

        self.exam_input = QSpinBox()
        self.exam_input.setRange(0, 50)

        inputs = [
            (self.name_input, "images/user.png"),
            (self.id_input, "images/id.png"),
            (self.ca_input, "images/ca.png"),
            (self.practical_input, "images/practical.png"),
            (self.exam_input, "images/exam.png")
        ]

        for index, (widget, icon_path) in enumerate(inputs):
            page = self.create_input_page(widget, self.step_titles[index], icon_path)
            self.steps.append(page)
            self.stacked_widget.addWidget(page)

        # Layout setup
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(self.layout)

        self.step_label = QLabel("Step 1 of 5")
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.step_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(len(self.steps) - 1)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)

        self.layout.addWidget(self.step_label)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.stacked_widget)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton("◀ Back")
        self.reset_btn = QPushButton("Reset")
        self.cancel_btn = QPushButton("Cancel")
        self.next_btn = QPushButton("Next ▶")
        self.finish_btn = QPushButton("✓ Finish")

        self.back_btn.clicked.connect(self.go_back)
        self.next_btn.clicked.connect(self.go_next)
        self.finish_btn.clicked.connect(self.finish)
        self.reset_btn.clicked.connect(self.reset_form)
        self.cancel_btn.clicked.connect(self.reject)

        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.reset_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.cancel_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        nav_layout.addWidget(self.finish_btn)

        self.layout.addLayout(nav_layout)
        self.update_ui()

    def create_input_page(self, widget, label_text, icon_path):
        page = QWidget()
        layout = QVBoxLayout()

        label = QLabel(f"{label_text}")
        label.setFont(QFont("Segoe UI", 11))

        icon = QLabel()
        icon.setPixmap(QIcon(icon_path).pixmap(24, 24))
        icon.setFixedSize(26, 26)

        input_layout = QHBoxLayout()
        input_layout.addWidget(icon)
        input_layout.addWidget(widget)

        layout.addWidget(label)
        layout.addLayout(input_layout)
        layout.addStretch()
        page.setLayout(layout)
        return page

    def validate_current(self):
        widget = self.get_current_input_widget()
        if isinstance(widget, QLineEdit):
            text = widget.text().strip()
            is_valid = bool(text)
            self.next_btn.setEnabled(is_valid)
            self.finish_btn.setEnabled(is_valid)
        else:
            self.next_btn.setEnabled(True)
            self.finish_btn.setEnabled(True)

    def get_current_input_widget(self):
        return self.steps[self.current_step].layout().itemAt(1).layout().itemAt(1).widget()

    def update_ui(self):
        self.step_label.setText(f"Step {self.current_step + 1} of {len(self.steps)}")
        self.progress_bar.setValue(self.current_step)
        self.back_btn.setEnabled(self.current_step > 0)
        self.next_btn.setVisible(self.current_step < len(self.steps) - 1)
        self.finish_btn.setVisible(self.current_step == len(self.steps) - 1)
        self.validate_current()

    def go_back(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.stacked_widget.setCurrentIndex(self.current_step)
            self.update_ui()

    def go_next(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.stacked_widget.setCurrentIndex(self.current_step)
            self.update_ui()

    def finish(self):
        if not self.name_input.text().strip() or not self.id_input.text().strip():
            QMessageBox.warning(self, "Missing Input", "Name and ID Number are required.")
            return
        self.accept()

    def reset_form(self):
        self.name_input.clear()
        self.id_input.clear()
        self.ca_input.setValue(0)
        self.practical_input.setValue(0)
        self.exam_input.setValue(0)
        self.current_step = 0
        self.stacked_widget.setCurrentIndex(self.current_step)
        self.update_ui()

    def get_student_data(self):
        return [
            self.name_input.text().strip(),
            self.id_input.text().strip(),
            self.ca_input.value(),
            self.practical_input.value(),
            self.exam_input.value()
        ]

