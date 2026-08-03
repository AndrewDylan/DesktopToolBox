# Desktop Tool Box

The Desktop Utility App is a PyQt6-based desktop aapplication designed to streamline network and Active Directory (AD) management task for IT professionals.

## Features

- Computer Search: Enter a computer naem or IP address to query AD and check online status.
- AD Actions: Updating billing codes, disable computers, or remove computers from AD with confirmation dialogs for safety.
- Network Tools: Access common network diagnostics via menu options.
- Command Output: View results and logs in a dedicated, read-only output area.
- Persistent PowerShell Session: Secure credential handling and session management for executing PowerShell scripts.
- Threaded Command Execution: Responsive UI with background worker threads for running commands and scripts.

## Installation

1. Requirements
  - Python 3.8+
  - PyQt6
  - Windows OS (for PowerShell integration)
2. Setup
  - Clone or download repository
  - Install dependencies:
    - ```python
      pip install PyQt6
      ```
  - Running the App:
    - Launch the application:
      - ```python
        python ToolBox.py
        ```

## Usage

- Search for a Computer: Enter the name or IP, then click "Search"
- Update Billing: Input the billing code and click "Update Billing"
- Disable/Remove Computer: Use the respective button; confirmation dialogs will appear.
- Network Diagnostics: Use the Network menu for Ping, Traceroute, or Test-Connection
- View Output: All command results are displayed in the CMD Output area.
