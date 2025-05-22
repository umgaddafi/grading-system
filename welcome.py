from PyQt6.QtWidgets import (
    QApplication,  QWidget, QVBoxLayout, QHBoxLayout,
   QLabel, QProgressBar
)
from PyQt6.QtGui import QPixmap, QFont

from PyQt6.QtCore import Qt

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(500, 350)
        self.setStyleSheet("background-color: #04364A; color: white;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        task_name = QLabel("CSC201 ASSIGNMENT: CSC/24D/4445")
        task_name.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        task_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        task_name.setStyleSheet("color: #c0c0c0;")
        # Logo
        logo = QLabel()
        pixmap = QPixmap("images/mau.png")
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        title = QLabel(" STUDENT GRADING SYSTEM")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Subtitle
        subtitle = QLabel("Ensure Accuracy, Fairness and Reliability")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #c0c0c0;")

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(20)
        self.progress.setFixedWidth(400)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #f0f0f0;
                border-radius: 5px;
                text-align: center;
                background-color: #ffffff;
                color: black;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #fc00ff, stop:1 #00dbde
                );
                border-radius: 5px;
            }
        """)

        # Footer
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(20, 0, 20, 10)
        self.status = QLabel("Starting...")
        author = QLabel("Author:- Muhammad Aliyu")
        self.status.setStyleSheet("color: #aaa;")
        author.setStyleSheet("color: #aaa;")
        footer_layout.addWidget(self.status)
        footer_layout.addStretch()
        footer_layout.addWidget(author)

        layout.addStretch()
        layout.addWidget(logo)
        layout.addSpacing(0)
        layout.addWidget(title)
        layout.addSpacing(0)
        layout.addWidget(subtitle)
        layout.addSpacing(50)
        layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addLayout(footer_layout)

        self.setLayout(layout)
        self.center_window()

    def center_window(self):
        frame_geometry = self.frameGeometry()
        screen_center = QApplication.primaryScreen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def update_progress(self, value):
        self.progress.setValue(value)
        status='Status: '
        if value < 25:
            self.status.setText(status + "Starting...")
        elif value < 50:
            self.status.setText(status + "Preparing files...")
        elif value < 75:
            self.status.setText(status + "Loading data...")
        elif value < 90:
            self.status.setText(status + "Finalizing...")
        elif value <= 100:
            self.status.setText(status + "Done.")
