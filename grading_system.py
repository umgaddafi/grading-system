from PyQt6.QtCore import QTimer
import sys
from welcome import SplashScreen
from grader import StudentManagementSystem
from login import LoginDialog
from PyQt6.QtWidgets import QApplication

main_window = None

def run_login_flow():
    login = LoginDialog()
    if login.exec():
        global main_window
        username = login.logged_in_user
        main_window = StudentManagementSystem(username)
        main_window.logout_requested.connect(run_login_flow)  # reconnect signal
        main_window.show()
    else:
        sys.exit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()

    def start_main_app():
        splash.close()
        run_login_flow()

    def update():
        current = splash.progress.value()
        if current < 100:
            splash.update_progress(current + 5)
        else:
            timer.stop()
            start_main_app()

    timer = QTimer()
    timer.timeout.connect(update)
    timer.start(500)

    sys.exit(app.exec())

