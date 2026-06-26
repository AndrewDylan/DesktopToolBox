import sys
import subprocess, base64, threading

from PyQt6.QtCore import pyqtSlot, QObject
from PyQt6.QtWidgets import QApplication

class ActionLogic(QObject):
    def __init__(self, ui):
        super().__init__(ui)
        self.ui = ui #store reference to the MainWindow
        self.ps = None
        self._lock = threading.Lock()

    @pyqtSlot(bool)
    def file_exit_action(self, checked=False):
        QApplication.instance().quit()

    @pyqtSlot(bool)
    def comp_searchBtn_pressed(self, checked=False):
        script = r".\PS Scripts\Get-ADComputer.ps1"
        comp = self.ui.input_computer.text().strip()

        cmd = fr"& '{script}' -computer '{comp}'"
        out = self.run_ps(cmd)
        self.ui.ad_output.setText(out)


    def start_ps_session(self, username: str, password: str):
        """
        Spawn a persistent PowerShell and create $creds inside that session.
        """
        if self.ps and self.ps.poll() is None:
            return  # already running

        # Start persistent PS with an interactive loop
        self.ps = subprocess.Popen(
            ["powershell", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-NoExit"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1
        )

        # Safely inject username/password.
        # Use base64 to avoid quoting/escaping pitfalls; decode inside PS.
        u_b64 = base64.b64encode(username.encode("utf-16le")).decode("ascii")
        p_b64 = base64.b64encode(password.encode("utf-16le")).decode("ascii")

        bootstrap = rf"""
            $u = [Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('{u_b64}'))
            $pwdPlain = [Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('{p_b64}'))
            $sec = ConvertTo-SecureString -String $pwdPlain -AsPlainText -Force
            $creds = New-Object System.Management.Automation.PSCredential ($u, $sec)
            # optionally clear transient variables
            Remove-Variable u,pwdPlain,sec -ErrorAction SilentlyContinue
            Write-Output '[IOT] $creds initialized'
        """
        _ = self.run_ps(bootstrap)  # initialize $creds

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
        """
        Send a command to the persistent PS and read until a marker.
        Synchronous example; move to a worker thread for non-blocking UI.
        """
        if not self.ps or self.ps.poll() is not None:
            raise RuntimeError("PowerShell session is not running.")

        marker = "[IOT-END]"
        wrapped = f"{cmd}; Write-Output '[IOT-FLUSH]'; Write-Output '{marker}'\n"
        flush_seen = False

        # Write command safely
        with self._lock:
            self.ps.stdin.write(wrapped)
            self.ps.stdin.flush()

        # Read until marker
        lines = []
        while True:
            line = self.ps.stdout.readline()
            if "[IOT-FLUSH]" in line:
                flush_seen = True
                continue
            if marker in line and flush_seen:
                break
            lines.append(line.rstrip())

        output = "\n".join(lines)
        # forward stderr (best-effort)
        err = ""
        try:
            while self.ps.stderr.readable():
                # non-blocking best-effort read; may not return all immediately
                break
        except Exception:
            pass

        return output
