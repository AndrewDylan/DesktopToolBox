import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QMessageBox


def resource_path(*parts) -> str:
    """
    Returns a real filesystem path for bundled resources.
    Uses sys._MEIPASS in PyInstaller onefile builds.
    """
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return str(base.joinpath(*parts))

class ConfirmationDialog(QDialog):
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

class CredentialDialog(QDialog):
        def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Secondary Account Sign-In")
                self.setModal(True)

                self.window = parent

                self.setStyleSheet("""
                QMainWindow { background-color: #1e1e1e; color: #ddd; }
                QDialog { background-color: #1e1e1e; color: #ddd; }
                QLabel { color: #ddd; font-size: 14px; }
                QLineEdit { background: #2b2b2b; color: #ddd; padding: 6px; border: 1px solid #444; }
                QTextEdit { background: #2b2b2b; color: #ccc; border: 1px solid #444; }
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

                self.user_edit = QLineEdit()
                self.user_edit.setPlaceholderText("DOMAIN\\user")
                self.pass_edit = QLineEdit()
                self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)

                form = QFormLayout()
                form.addRow("Username:", self.user_edit)
                form.addRow("Password:", self.pass_edit)

                buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                        QDialogButtonBox.StandardButton.Cancel, parent=self)
                buttons.accepted.connect(self._on_accept)
                buttons.rejected.connect(self.reject)

                layout = QVBoxLayout(self)
                layout.addLayout(form)
                layout.addWidget(buttons)

        
        def _on_accept(self):
                if not self.user_edit.text().strip() or not self.pass_edit.text():
                        QMessageBox.warning(self, "Missing info", "Please enter both username and password.")
                        return
                u, p = self.values()
                if self.window.logic.ps and self.window.logic.ps.poll() is None:
                        self.ok = self.window.logic.verify_credentials(username = u, password = p)
                        if self.ok:
                                #Initialize Creds
                                if self.window.logic.init_credentials(username = u, password = p) == False:
                                        print("[ERROR] failed to initialize credentials")
                                        sys.exit(0)  
                else:
                        self.ok = bool(self.window.logic.start_ps_session(u, p))
                
                if self.ok:      
                        self.accept()  # close only on success
                else:
                        QMessageBox.warning(self, "Sign-in failed", "Invalid credentials. Please try again.")
                        return



        def values(self) -> tuple[str, str]:
                return self.user_edit.text().strip(), self.pass_edit.text()