from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel

class ConfimationDialog(QDialog):
    def __init__(self, text, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Confirmation")
                self.setModal(True)

                self.setStyleSheet("""
                QDialog { background-color: #1e1e1e; color: #ddd; }
                QLabel { color: #ddd; font-size: 14px; }
                QPushButton {
                        background-color: #333; 
                        color: white; 
                        padding: 8px;
                        border: 1px solid #555;
                        border-radius: 6px;
                }
                QPushButton:hover { background-color: #696969; }
                QPushButton:pressed { background-color: #696969; }
                """)

                self.text = text
                warning_label = QLabel(text)

                buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                        QDialogButtonBox.StandardButton.Cancel, parent=self)
                buttons.accepted.connect(self.accept)
                buttons.rejected.connect(self.reject)

                layout = QVBoxLayout(self)
                layout.addWidget(warning_label)
                layout.addWidget(buttons)
                self.setLayout(layout)