from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QInputDialog, QMessageBox, QLineEdit, QComboBox, QLabel, QFileDialog
)
from PyQt6.QtGui import QIcon, QTextDocument
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtCore import Qt, QMarginsF, pyqtSignal
from student import Student
import base64
import json
import csv
import pathlib
from add_student_dialog import AddStudentDialog


class StudentManagementSystem(QMainWindow):

    logout_requested = pyqtSignal()
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.logout_requested.connect(self.handle_logout)
        self.students = []

        self.setWindowTitle("Student Grading System")
        self.setWindowIcon(QIcon("images/sms.png"))
        self.setGeometry(100, 100, 900, 600)

        self.load_data()
        self.apply_styles()
        self.init_ui()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QMainWindow {
                background-color: #f7f9fc;
            }
            QLineEdit, QComboBox {
                padding: 6px;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #2f80ed;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1c6dd0;
            }
            QPushButton:pressed {
                background-color: #174ea6;
            }
            QLabel {
                font-weight: bold;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                gridline-color: #eee;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 4px;
                border: 1px solid #ddd;
            }
        """)

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()

        # Top bar with username and logout
        top_layout = QHBoxLayout()
        user_label = QLabel(f"Logged in as: {self.username}")
        user_label.setStyleSheet("font-weight: normal; color: #555;")
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        logout_btn.clicked.connect(self.logout)
        top_layout.addWidget(user_label)
        top_layout.addStretch()
        top_layout.addWidget(logout_btn)
        layout.addLayout(top_layout)

        # Search and filter
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name...")
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.refresh_table)

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("All Grades")
        self.update_filter_options()
        self.filter_combo.currentTextChanged.connect(self.refresh_table)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(QLabel("Filter by Grade:"))
        search_layout.addWidget(self.filter_combo)
        layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Name", "ID Number", "C.A", "Practical", "Exam", "Total", "Grade"])
        self.table.setColumnWidth(0, 200)
        layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()
        for label, action in [
            ("Add Student", self.add_student),
            ("Update Student", self.update_student),
            ("Delete Student", self.delete_student),
            ("Export to CSV", self.export_csv),
            ("Print Scores Sheet", self.print_report_card),
            ("Print Student", self.print_individual_card)
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(action)
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)
        self.central_widget.setLayout(layout)
        self.refresh_table()
    def logout(self):
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to logout?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()  # emit logout signal
    def handle_logout(self):
        self.close()


    def refresh_table(self):
        filter_grade = self.filter_combo.currentText()
        search_text = self.search_input.text().strip().lower()
        filtered = [
            s for s in self.students
            if (filter_grade == "All Grades" or s.grade == filter_grade) and
               (search_text in s.name.lower())
        ]
        self.table.setRowCount(len(filtered))
       
        for row, student in enumerate(filtered):
            name_item = QTableWidgetItem(student.name)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 0, name_item)

            for col, value in enumerate([
                student.id_number,
                str(student.ca),
                str(student.practical),
                str(student.exam),
                str(student.total),
                student.grade
            ], start=1):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)

    def add_student(self):
        dialog = AddStudentDialog()
        if dialog.exec():
            name, id_number, ca, practical, exam = dialog.get_student_data()
            self.students.append(Student(name, id_number, ca, practical, exam))
            self.save_data()

    
            self.update_filter_options()
            self.refresh_table()
   
    def update_student(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Warning", "Please select a student to update.")
            return

        id_number = self.table.item(row, 1).text()
        student = next((s for s in self.students if s.id_number == id_number), None)
        if not student:
            return

        # Keep ID uneditable
        QMessageBox.information(self, "Info", f"Editing student with ID: {student.id_number}")

        name, ok1 = QInputDialog.getText(self, "Update Name", "New Name:", text=student.name)
        ca, ok2 = QInputDialog.getInt(self, "Update C.A", "New C.A (0-30):", student.ca, 0, 30)
        practical, ok3 = QInputDialog.getInt(self, "Update Practical", "New Practical (0-20):", student.practical, 0, 20)
        exam, ok4 = QInputDialog.getInt(self, "Update Exam", "New Exam (0-50):", student.exam, 0, 50)

        if all([ok1, ok2, ok3, ok4]):
            student.name = name
            student.ca = ca
            student.practical = practical
            student.exam = exam
            student.total = ca + practical + exam
            student.grade = student.calculate_grade()
            self.save_data()
            self.update_filter_options()
            self.refresh_table()


    def delete_student(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Warning", "Please select a student to delete.")
            return

        id_number = self.table.item(row, 1).text()
        student = next((s for s in self.students if s.id_number == id_number), None)
        if not student:
            return

        confirm = QMessageBox.question(self, "Confirm", f"Delete student with ID: {id_number}?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.students = [s for s in self.students if s.id_number != id_number]
            self.save_data()
            self.update_filter_options()
            self.refresh_table()


    
    def export_csv(self):
        csv_path = self.get_gradesys_path() / "students.csv"
        with open(csv_path, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "ID Number", "CA", "Practical", "Exam", "Total", "Grade"])
            for s in self.students:
                writer.writerow([s.name, s.id_number, s.ca, s.practical, s.exam, s.total, s.grade])
        QMessageBox.information(self, "Exported", f"Students exported to: {csv_path}")

    def update_filter_options(self):
        current = self.filter_combo.currentText()
        self.filter_combo.clear()
        self.filter_combo.addItem("All Grades")
        grades = sorted(set(s.grade for s in self.students))
        self.filter_combo.addItems(grades)
        self.filter_combo.setCurrentText(current)
    
    def get_gradesys_path(self):
        documents_dir = pathlib.Path.home() / "Documents"
        gradesys_dir = documents_dir / "GradeSys"
        gradesys_dir.mkdir(parents=True, exist_ok=True)
        return gradesys_dir

    def save_data(self):
        file_path = self.get_gradesys_path() /  "students.json"
        with open(file_path, "w") as f:
            json.dump([s.__dict__ for s in self.students], f, indent=4)

    def load_data(self):
        file_path = self.get_gradesys_path() / "students.json"
        if file_path.exists():
            with open(file_path, "r") as f:
                for item in json.load(f):
                    name = item.get("name")
                    id_number = item.get("id_number", "")
                    ca = item.get("ca", 0)
                    practical = item.get("practical", 0)
                    exam = item.get("exam", 0)
                    self.students.append(Student(name, id_number, ca, practical, exam))
    
    
    def print_report_card(self):
        if not self.students:
            QMessageBox.warning(self, "Warning", "No student data to print.")
            return

        
        try:
            with open("images/mau.png", "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                img_tag = f'<img src="data:image/png;base64,{encoded_image}" alt="Logo" style="height: 80px;" />'
        except FileNotFoundError:
            img_tag = "<!-- Logo not found -->"

        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI'; font-size: 12pt; }}
                    h1,h2 {{ text-align: center; color: #2f80ed; margin:0px; line-height:0px; }}
                    h3 {{ text-align: center; margin:0px; line-height:0px; }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 20px;
                    }}
                    th, td {{
                        border: 1px solid #444;
                        padding: 8px;
                        text-align: center;
                    }}
                    th {{
                        background-color: #f0f0f0;
                    }}
                    .id-column {{
                        width: 180px;
                        white-space: nowrap;
                        font-size: 11pt;
                    }}
                    .s_name {{
                        text-align:left !important;
                        white-space: nowrap;  
                        font-size: 11pt;
                        min-width: 20%;     
                    }}
                </style>
            </head>
            <body>
                <div style="text-align: center; margin-bottom: 10px;">
                    {img_tag}
                </div>
                <h1>MODIBBO ADAMA UNIVERSITY YOLA</h1>
                <h2>DEPARTMENT OF COMPUTER SCIENCE</h2>
                <h3>CSC201: INTRODUCTION TO PROGRAMING USING PYTHON SCORES SHEET</h3>
                <table>
                    <tr>
                        <th>Student Name</th>
                        <th class="id_number">ID Number</th>
                        <th>C.A</th>
                        <th>Practical</th>
                        <th>Exam</th>
                        <th>Total</th>
                        <th>Grade</th>
                    </tr>
        """

        for s in self.students:
            html += f"""
                <tr>
                    <td class="s_name">{s.name}</td>
                    <td>{s.id_number}</td>
                    <td>{s.ca}</td>
                    <td>{s.practical}</td>
                    <td>{s.exam}</td>
                    <td>{s.total}</td>
                    <td>{s.grade}</td>
                </tr>
            """

        html += """
                </table>
            </body>
        </html>
        """

        filename, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if not filename:
            return
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        document = QTextDocument()
        document.setHtml(html)
        printer = QPrinter()
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(filename)
        
        printer.setPageMargins(QMarginsF(1, 0, 5, 1))
        document.print(printer)

        QMessageBox.information(self, "Success", f"PDF report saved as {filename}")
    def print_individual_card(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Warning", "Please select a student to print.")
            return

        name = self.table.item(row, 0).text()
        student = next((s for s in self.students if s.name == name), None)
        if not student:
            QMessageBox.warning(self, "Warning", "Student not found.")
            return

        try:
            with open("images/mau.png", "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                img_tag = f'<img src="data:image/png;base64,{encoded_image}" alt="Logo" style="height: 80px;" />'
        except FileNotFoundError:
            img_tag = "<!-- Logo not found -->"

        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI'; font-size: 12pt; }}
                    h1,h2 {{ text-align: center; color: #2f80ed; margin:0px; line-height:0px; }}
                    h3 {{ text-align: center; margin:0px; line-height:0px; }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 20px;
                    }}
                    th, td {{
                        border: 1px solid #444;
                        padding: 8px;
                        text-align: center;
                    }}
                    th {{
                        background-color: #f0f0f0;
                    }}
                    .s_name {{
                        text-align:left !important;
                        white-space: nowrap;  
                        font-size: 11pt;
                    }}
                </style>
            </head>
            <body>
                <div style="text-align: center; margin-bottom: 10px;">
                    {img_tag}
                </div>
                <h1>MODIBBO ADAMA UNIVERSITY YOLA</h1>
                <h2>DEPARTMENT OF COMPUTER SCIENCE</h2>
                <h3>CSC201: INTRODUCTION TO PROGRAMMING USING PYTHON</h3>
                <table>
                    <tr><th>Student Name</th><td class="s_name">{student.name}</td></tr>
                    <tr><th>ID Number</th><td>{student.id_number}</td></tr>
                    <tr><th>C.A</th><td>{student.ca}</td></tr>
                    <tr><th>Practical</th><td>{student.practical}</td></tr>
                    <tr><th>Exam</th><td>{student.exam}</td></tr>
                    <tr><th>Total</th><td>{student.total}</td></tr>
                    <tr><th>Grade</th><td>{student.grade}</td></tr>
                </table>
            </body>
        </html>
        """

        safe_id = "".join(c for c in student.id_number if c.isalnum() or c in ('-', '_'))
        output_dir = self.get_gradesys_path() / "individual_cards"
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir / f"{safe_id}.pdf"

        document = QTextDocument()
        document.setHtml(html)
        printer = QPrinter()
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(str(file_path))
        printer.setPageMargins(QMarginsF(1, 0, 5, 1))
        document.print(printer)

        QMessageBox.information(self, "Success", f"Report card saved as: {file_path}")


