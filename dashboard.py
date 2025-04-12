import sys, os, subprocess, threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QPushButton, QHBoxLayout, QVBoxLayout,
    QLabel, QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPalette, QBrush
from PyQt5.QtCore import Qt, QSize

# Paths to your game scripts
CAR_GAME = os.path.join(os.path.dirname(__file__), 'main.py')
PED_GAME = os.path.join(os.path.dirname(__file__), 'pedestrain.py')

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Window setup
        self.setWindowTitle("Traffic Rules Games Dashboard")
        self.showMaximized()

        # Background image (place 'background.jpg' in ./assets/)
        bg_path = os.path.join(os.path.dirname(__file__), 'assets', 'background.jpg')
        if os.path.exists(bg_path):
            bg = QPixmap(bg_path)
            palette = QPalette()
            palette.setBrush(QPalette.Window, QBrush(bg.scaled(
                self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
            self.setPalette(palette)

        # Central widget
        central = QWidget(self)
        self.setCentralWidget(central)

        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Title label
        title = QLabel("Select Game Mode", self)
        title.setFont(QFont('Segoe UI', 36, QFont.Bold))
        title.setStyleSheet("color: white; text-shadow: 2px 2px 4px #000;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Buttons layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(100)

        # Car Mode button
        car_btn = QPushButton("Car Mode", self)
        car_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'assets', 'car_icon.png')))
        car_btn.setIconSize(QSize(128, 128))
        car_btn.setFixedSize(300, 300)
        car_btn.setFont(QFont('Segoe UI', 18))
        car_btn.setStyleSheet(
            "QPushButton { background: rgba(0,123,255,0.8); border-radius: 20px; color: white; }"
            "QPushButton:hover { background: rgba(0,123,255,1.0); }"
        )
        car_btn.clicked.connect(lambda: self.launch_game(CAR_GAME))
        btn_layout.addWidget(car_btn)

        # Pedestrian Mode button
        ped_btn = QPushButton("Pedestrian Mode", self)
        ped_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'assets', 'ped_icon.png')))
        ped_btn.setIconSize(QSize(128, 128))
        ped_btn.setFixedSize(300, 300)
        ped_btn.setFont(QFont('Segoe UI', 18))
        ped_btn.setStyleSheet(
            "QPushButton { background: rgba(40,167,69,0.8); border-radius: 20px; color: white; }"
            "QPushButton:hover { background: rgba(40,167,69,1.0); }"
        )
        ped_btn.clicked.connect(lambda: self.launch_game(PED_GAME))
        btn_layout.addWidget(ped_btn)

        layout.addLayout(btn_layout)
        central.setLayout(layout)

    def launch_game(self, script_path):
        if not os.path.exists(script_path):
            QMessageBox.critical(self, "Error", f"Script not found:\n{script_path}")
            return
        def run():
            subprocess.Popen([sys.executable, script_path])
        threading.Thread(target=run, daemon=True).start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    sys.exit(app.exec_())
