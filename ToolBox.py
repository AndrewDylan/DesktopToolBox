import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QDialog, QFormLayout, QDialogButtonBox, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction

from logic import ActionLogic
import ui.dialogs as dlg

class CredentialDialog(QDialog):
        def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Secondary Account Sign-In")
                self.setModal(True)

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
                        return
                self.accept()

        def values(self) -> tuple[str, str]:
                return self.user_edit.text().strip(), self.pass_edit.text()


class MainWindow(QMainWindow):
        def __init__(self):
                super().__init__()

                self.setWindowTitle("IOT Desktop Utility App")
                self.setGeometry(200,150,1100,500)

                self.logic = ActionLogic(self) #Passes MainWindow aka self to ActionLogic to reference.
                self.bootstrap_complete = None

                # Apply a dark style (simple but effective)
                self.setStyleSheet("""
                QMainWindow { background-color: #1e1e1e; color: #ddd; }
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

                self.build_menu_bar()

                #Central widget container. Plan is to have 1 container to house all output information and have menu options for actions.
                container = QWidget()
                layout = QVBoxLayout()

                #========================================
                #Build out main information screen/window

                #Computer input/search
                computerInput = QHBoxLayout()
                computerInput.addWidget(QLabel("Computer Name / IP"))
                self.input_computer = QLineEdit()
                computerInput.addWidget(self.input_computer)

                self.comp_searchBtn = QPushButton("Search")
                self.comp_searchBtn.clicked.connect(self.logic.comp_searchBtn_pressed)
                computerInput.addWidget(self.comp_searchBtn)

                self.statusIndicator = QLabel()
                self.statusIndicator.setFixedSize(12,12)
                self.statusIndicator.setStyleSheet("background-color: #D3D3D3; border-radius: 6px;")
                self.statusLabel = QLabel("Unknown")
                computerInput.addWidget(self.statusIndicator)
                computerInput.addWidget(self.statusLabel)

                layout.addLayout(computerInput)

                #AD Billing Section
                billing_section = QHBoxLayout()
                #Box to input desired bill code
                billing_section.addWidget(QLabel("Billing Code: "))
                self.input_billing = QLineEdit()
                billing_section.addWidget(self.input_billing)
                ##############################AD ACTION BUTTONS ############################
                self.btn_updateBilling = QPushButton("Update Billing")
                self.btn_disableComp = QPushButton("Disable Computer")
                self.btn_removeComp = QPushButton("Remove Computer")
                self.btn_disableComp.clicked.connect(self.logic.btn_disableComp_pressed)
                self.btn_updateBilling.clicked.connect(self.logic.btn_updateBilling_pressed)
                self.btn_removeComp.clicked.connect(self.logic.btn_removeComp_pressed)
                billing_section.addWidget(self.btn_updateBilling)
                billing_section.addWidget(self.btn_disableComp)
                billing_section.addWidget(self.btn_removeComp)
                
                layout.addLayout(billing_section)

                #Output Areas
                layout.addWidget(QLabel("CMD Output: "))
                self.cmd_output = QTextEdit()
                self.cmd_output.setReadOnly(True)
                layout.addWidget(self.cmd_output)

                # Apply layout
                container.setLayout(layout)
                self.setCentralWidget(container)

        def build_menu_bar(self):
                menu_bar = self.menuBar()

                style_sheet = """
                        QMenuBar::item:selected {
                                background-color: #696969;
                                color: white;
                        }
                        QMenu::item:selected {
                                background-color: #696969;
                                color: white;
                        }
                        QMenuBar {background-color: #1a1a1a; color: white;}
                        QMenu {background-color: #1a1a1a; color: white;}
                """
                menu_bar.setStyleSheet(style_sheet)

                # FILE Menu
                file_menu = menu_bar.addMenu("File")
                exit_action = QAction("Exit", self)
                exit_action.triggered.connect(self.logic.file_exit_action)
                file_menu.addAction(exit_action)

                # Network Menu
                net_menu = menu_bar.addMenu("Network")

                ping_action = QAction("CMD: Ping", self)
                textConn_action = QAction("PS: Test-Connection", self)
                trace_action = QAction("CMD: Traceroute", self)
                restart_action = QAction("CMD: Restart PC", self)

                net_menu.addAction(ping_action)
                net_menu.addAction(trace_action)
                net_menu.addAction(restart_action)
                net_menu.addAction(textConn_action)

                # Action Menu
                action_menu = menu_bar.addMenu("Actions")

                ipconfig_action = QAction("Ipconfig -all", self)
                gpupdate_action = QAction("gpupdate", self)

                action_menu.addAction(ipconfig_action)
                action_menu.addAction(gpupdate_action)

        def check_worker_results(self):
                while not self.logic.result_queue.empty():
                        result_type, result_text = self.logic.result_queue.get()
                        if result_type == "bootstrap":
                                if "[IOT] creds initialized" in result_text:
                                        print("Bootstrap succeeded!")
                                        self.cmd_output.append(str(result_text))
                                else:
                                        print("Bootstrap failed:", result_text)
                                        QApplication.instance().quit()
                        elif result_type == "normal":
                                self.cmd_output.append(str(result_text))
                        elif result_type == "error":
                                self.cmd_output.append(str(result_text))

        def closeEvent(self, event):
                self.logic.stop_ps_session()
                print("Application closing - cleaning up terminals!")
                event.accept()

app = QApplication(sys.argv)

print(MainWindow.__init__)
window = MainWindow()
window.show()

cred_dlg = CredentialDialog(window)
if cred_dlg.exec() == QDialog.DialogCode.Accepted:
        u, p = cred_dlg.values()
        ok = window.logic.start_ps_session(u, p)
        if not ok:
                print("Powershell session failed to initialize.")
else:
        sys.exit(0)

window.result_timer = QTimer()
window.result_timer.timeout.connect(window.check_worker_results)
window.result_timer.start(100) #check every 100ms
# Start the event loop.
app.exec()