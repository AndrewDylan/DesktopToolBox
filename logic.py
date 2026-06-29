import sys
import subprocess, base64, threading, time, queue

from PyQt6.QtCore import pyqtSlot, QObject
from PyQt6.QtWidgets import QApplication

class ActionLogic(QObject):
    def __init__(self, ui):
        super().__init__(ui)
        self.ui = ui #store reference to the MainWindow
        self.ps = None
        self._lock = threading.Lock()
        #Build threading and queue
        self.cmd_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    @pyqtSlot(bool)
    def file_exit_action(self, checked=False):
        QApplication.instance().quit()

    ###### SEARCH LOGIC ######
    @pyqtSlot(bool)
    def comp_searchBtn_pressed(self, checked=False):
        script = r".\PS_Scripts\Get-ADComputer.ps1"
        comp = self.ui.input_computer.text().strip()

        cmd = fr"& '{script}' -computer '{comp}'"
        self.cmd_queue.put(cmd)
    
    ###### ACTIVE DIRECTORY LOGIC ######
    @pyqtSlot(bool)
    def btn_disableComp_pressed(self, checked=False):
        script = r".\PS_Scripts\DisableComputer.ps1"
        comp = self.ui.input_computer.text().strip()

        cmd = fr"& '{script}' -computer '{comp}'"
        self.cmd_queue.put(cmd)

    @pyqtSlot(bool)
    def btn_updateBilling_pressed(self, checked=False):
        script = r".\PS_Scripts\UpdateBilling.ps1"
        comp = self.ui.input_computer.text().strip()
        bill = self.ui.input_billing.text().strip()

        cmd = fr"& '{script}' -computer '{comp}' -billCode '{bill}'"
        self.cmd_queue.put(cmd)

    @pyqtSlot(bool)
    def btn_removeComp_pressed(self, checked=False):
        script = r".\PS_Scripts\RemoveComputer.ps1"
        comp = self.ui.input_computer.text().strip()

        cmd = fr"& '{script}' -computer '{comp}'"
        self.cmd_queue.put(cmd)

    ###### Worker Loop ######
    def _worker_loop(self):
        while True:
            try:
                cmd = self.cmd_queue.get() #Wait for command
                if cmd is None:
                    break                  #clean shutdown
                if isinstance(cmd, tuple) and cmd[0] == "bootstrap":
                    result = self.run_ps(cmd[1])
                    self.result_queue.put(("bootstrap", result))
                else:
                    result = self.run_ps(cmd)
                    self.result_queue.put(("normal", result))
            except Exception as e:
                self.result_queue.put(("error", f"[Worker Error] {e}"))

    ###### POWERSHELL SESSION ######
    def start_ps_session(self, username: str, password: str):
        """
        Spawn a persistent PowerShell and create $creds inside that session.
        """
        if self.ps and self.ps.poll() is None:
            return True# already running

        # Start persistent PS with an interactive loop
        try:
            self.ps = subprocess.Popen(
                ["powershell", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-NoExit"],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, bufsize=1
            )
        except Exception as e:
            print(f"ERROR: Failed to start PowerShell: {e}")
            self.ps = None
            return False
        
        #If PS died instantly, abort
        if self.ps.poll() is not None:
            print("ERROR: PowerShell process terminated immediately.")
            self.ps=None
            return False
        
        try:
            u_b64 = base64.b64encode(username.encode("utf-16le")).decode("ascii")
            p_b64 = base64.b64encode(password.encode("utf-16le")).decode("ascii")
        except Exception as e:
            print(f"ERROR: Failed to base64-encode credentials: {e}")
            return False

        bootstrap = rf"""
$u = [Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('{u_b64}'))
$pwdPlain = [Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('{p_b64}'))
$sec = ConvertTo-SecureString -String $pwdPlain -AsPlainText -Force
$creds = New-Object System.Management.Automation.PSCredential ($u, $sec)
Remove-Variable u,pwdPlain,sec -ErrorAction SilentlyContinue
Write-Output '[IOT] creds initialized'
"""
        try:
            self.cmd_queue.put(("bootstrap",bootstrap))
        except Exception as e:
            print(f"ERROR: run_ps() failed during bootstrap: {e}")
            return False
        
        print("PowerShell session initialized successfully.")
        return True

    def stop_ps_session(self):
        """
        Clear $creds and terminate the PowerShell session.
        """
        if not self.ps:
            return
        try:
            self.run_ps("$creds = $null; Remove-Variable creds -ErrorAction SilentlyContinue; [GC]::Collect(); [GC]::WaitForPendingFinalizers(); Write-Output '[IOT] creds cleared'")
            with self._lock:
                self.ps.stdin.write("Exit\n")
                self.ps.stdin.flush()
        except Exception:
            pass
        finally:
            try:
                self.ps.terminate()
            except Exception:
                pass
            self.ps = None

    
    def run_ps(self, cmd: str, timeout: float = 30.0) -> str:
        if not self.ps or self.ps.poll() is not None:
            raise RuntimeError("PowerShell session is not running.")

        marker = "[IOT-END]"
        wrapped = f"{cmd} 2>&1; Write-Output '[IOT-FLUSH]'; Write-Output '{marker}'\n"

        flush_seen = False
        start_time = time.time()

        # Write the command
        with self._lock:
            try:
                self.ps.stdin.write(wrapped)
                self.ps.stdin.flush()
            except Exception as e:
                return f"[stdin error] {e}"

        # ---- READ STDOUT UNTIL MARKER ----
        stdout_lines = []
        while True:
            #Timeout protection
            if time.time() - start_time > timeout:
                return "[timeout] PowerShell command took too long."
            
            line = self.ps.stdout.readline()
            if not line:
                return "[error] PowerShell process closed the pipe"
            
            line = line.rstrip()

            if "[IOT-FLUSH]" in line:
                flush_seen = True
                continue

            if marker in line and flush_seen:
                break

            stdout_lines.append(line)

        stdout_text = "\n".join(stdout_lines)

        return stdout_text

