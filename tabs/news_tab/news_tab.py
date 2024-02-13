from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class NewsTab(QWidget):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("This is the News Tab")

        layout.addWidget(label)

        self.show()

