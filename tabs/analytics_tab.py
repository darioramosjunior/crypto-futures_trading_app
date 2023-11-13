from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel, QPushButton


class AnalyticsTab(QWidget):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("This is the Analytics Tab")
        button = QPushButton("Refresh")
        layout.addWidget(label)
        layout.addWidget(button)

        self.show()
