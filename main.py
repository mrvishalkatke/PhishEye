from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QVBoxLayout, QLabel, QWidget, QPushButton, QLineEdit, QHBoxLayout, QScrollArea, QListWidget, QListWidgetItem, QTextBrowser, QTabWidget, QFrame, QGridLayout, QSplitter, QDesktopWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
import imaplib
import email
from email.header import decode_header
from datetime import datetime

class PhishEye(QMainWindow):
    def __init__(self):
        super().__init__()
        self.email = None
        self.password = None
        self.imap = None  # IMAP connection object
        self.init_login_ui()
        
    def center_window(self):
        # Get screen geometry and window geometry
        screen = QDesktopWidget().screenGeometry()
        window = self.frameGeometry()
        center = screen.center()
        window.moveCenter(center)
        self.move(window.topLeft())

    def init_login_ui(self):
        self.setWindowTitle("PhishEye - Login")
        self.setGeometry(200, 200, 800, 300)

        layout = QVBoxLayout()

        # Logo Label
        self.logo_label = QLabel(self)
        self.logo_pixmap = QPixmap("logo.png")  # Specify the path to your logo image
        self.logo_label.setPixmap(self.logo_pixmap.scaled(550, 454, Qt.KeepAspectRatio))
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)

        # Create a container layout for centering input fields
        input_layout = QVBoxLayout()
        input_layout.setAlignment(Qt.AlignCenter)
        
        # Email Input Field with Rounded Corners
        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("Email")
        self.email_input.setStyleSheet("""
            QLineEdit {
                border-radius: 15px;
                border: 2px solid #ccc;
                padding: 10px;
            }
        """)
        self.email_input.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.email_input)

        # Password Input Field with Rounded Corners
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border-radius: 15px;
                border: 2px solid #ccc;
                padding: 10px;
            }
        """)
        self.password_input.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.password_input)

        # Login Button
        self.login_button = QPushButton("Login", self)
        self.login_button.clicked.connect(self.login)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 15px;
                padding: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(self.login_button)

        # Set the layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.center_window()  # Call the center window method

    def init_email_ui(self):
        self.setWindowTitle("PhishEye - Inbox")
        self.setGeometry(200, 200, 1200, 700)

        main_layout = QVBoxLayout()

        self.inbox_widget = QWidget(self)
        self.inbox_layout = QVBoxLayout()

        self.email_list = QListWidget()
        self.email_list.itemClicked.connect(self.display_split_view)
        self.inbox_layout.addWidget(self.email_list)

        self.clear_button = QPushButton("Clear", self)
        self.clear_button.setStyleSheet("background-color: black; color: white;")
        self.clear_button.clicked.connect(self.confirm_clear)
        self.inbox_layout.addWidget(self.clear_button)

        self.inbox_widget.setLayout(self.inbox_layout)
        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.addTab(self.inbox_widget, "Inbox")

        logout_layout = QHBoxLayout()
        logout_layout.addStretch()
        self.logout_button = QPushButton("Logout")
        self.logout_button.setStyleSheet("background-color: red; color: white;")
        self.logout_button.clicked.connect(self.confirm_logout)
        logout_layout.addWidget(self.logout_button)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.clear_button)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.logout_button)

        main_layout.addWidget(self.tabs)
        main_layout.addLayout(bottom_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        self.center_window()  # Call the center window method

    def login(self):
        self.email = self.email_input.text()
        self.password = self.password_input.text()

        if not self.email or not self.password:
            QMessageBox.warning(self, "Input Error", "Please enter both email and password.")
            return

        try:
            self.imap = imaplib.IMAP4_SSL("imap.gmail.com")
            self.imap.login(self.email, self.password)

            self.statusBar().showMessage(f"Logged in as {self.email}")
            self.init_email_ui()
            self.fetch_emails()

        except imaplib.IMAP4.error:
            QMessageBox.critical(self, "Login Failed", "Invalid email or app password.\nEnsure you are using an app password.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def confirm_logout(self):
        reply = QMessageBox.question(self, 'Logout Confirmation', 'Are you sure you want to logout?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.logout()

    def logout(self):
        try:
            if self.imap:
                self.imap.logout()
            self.imap = None
            self.statusBar().showMessage("Logged out.")
        
            # Clear email and password references before initializing login UI
            self.email_input = None
            self.password_input = None

            self.tabs.clear()
            self.init_login_ui()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred during logout: {e}")

    def confirm_clear(self):
        reply = QMessageBox.question(self, 'Clear Confirmation', 'Are you sure you want to clear all opened emails?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.clear_all_tabs()

    def clear_all_tabs(self):
        # Loop through and remove all tabs except for the first one (Inbox)
        for i in range(self.tabs.count() - 1, 0, -1):
            self.tabs.removeTab(i)

    def fetch_emails(self):
        if not self.imap:
            QMessageBox.critical(self, "Error", "You are not logged in.")
            return

        try:
            self.imap.select("INBOX")
            status, messages = self.imap.search(None, "ALL")
            if status != "OK":
                QMessageBox.warning(self, "Error", "Failed to fetch emails.")
                return

            email_ids = messages[0].split()[::-1]  # Reverse to show latest emails first
            self.email_list.clear()

            for email_id in email_ids:
                status, msg_data = self.imap.fetch(email_id, "(RFC822)")
                if status != "OK":
                    continue

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                        sender = msg.get("From")
                        date = msg.get("Date")
                        formatted_date, formatted_time = self.format_datetime(date)

                        email_item_widget = QWidget(self)
                        email_layout = QVBoxLayout()

                        email_details_layout = QGridLayout()
                        subject_label = QLabel(f"Subject: {subject}")
                        email_details_layout.addWidget(subject_label, 0, 0)
                        sender_label = QLabel(f"From: {sender}")
                        email_details_layout.addWidget(sender_label, 1, 0)
                        date_label = QLabel(f"Date: {formatted_date}")
                        date_label.setAlignment(Qt.AlignRight)
                        email_details_layout.addWidget(date_label, 0, 1)
                        time_label = QLabel(f"Time: {formatted_time}")
                        time_label.setAlignment(Qt.AlignRight)
                        email_details_layout.addWidget(time_label, 1, 1)

                        email_layout.addLayout(email_details_layout)

                        email_item_widget.setLayout(email_layout)

                        email_item = QListWidgetItem()
                        email_item.setSizeHint(email_item_widget.sizeHint())
                        self.email_list.addItem(email_item)
                        self.email_list.setItemWidget(email_item, email_item_widget)
                        email_item.setData(Qt.UserRole, (email_id, subject))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch emails: {e}")

    def format_datetime(self, raw_date):
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(raw_date)
            formatted_date = dt.strftime("%a, %d %B %Y")
            formatted_time = dt.strftime("%I:%M:%S %p")
            return formatted_date, formatted_time
        except Exception:
            return "Invalid Date", "Invalid Time"

    def display_split_view(self, item):
        email_id, subject = item.data(Qt.UserRole)
        status, msg_data = self.imap.fetch(email_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        body = None
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    body = part.get_payload(decode=True).decode()

        if body is None:
            body = "No email content available."

        self.display_email_content(subject, body)

    def display_email_content(self, subject, body):
        # Create the main widget for the split view
        split_view_widget = QWidget(self)
        split_view_layout = QHBoxLayout()

        # Left side: Display email content (subject, body, sender, date, etc.)
        left_panel_widget = QWidget(self)
        left_panel_layout = QVBoxLayout()

        # Subject, Sender, Date, and Time
        email_details_layout = QGridLayout()
        subject_label = QLabel(f"<b>Subject:</b> {subject}")
        sender_label = QLabel(f"<b>From:</b> {self.sender}")
        date_label = QLabel(f"<b>Date:</b> {self.format_datetime(datetime.now())[0]}")
        time_label = QLabel(f"<b>Time:</b> {self.format_datetime(datetime.now())[1]}")
        
        email_details_layout.addWidget(subject_label, 0, 0)
        email_details_layout.addWidget(sender_label, 1, 0)
        email_details_layout.addWidget(date_label, 0, 1)
        email_details_layout.addWidget(time_label, 1, 1)

        left_panel_layout.addLayout(email_details_layout)

        # Email Body
        email_body_browser = QTextBrowser(self)
        email_body_browser.setHtml(f"<h3>{subject}</h3><p>{body}</p>")
        left_panel_layout.addWidget(email_body_browser)

        left_panel_widget.setLayout(left_panel_layout)

        # Right side: Display email meta details (IP address, server details, etc.)
        right_panel_widget = QWidget(self)
        right_panel_layout = QVBoxLayout()

        # Create a table for meta data (e.g., Source IP, forwarded server, etc.)
        metadata_table = QGridLayout()

        # Example data (replace with actual extracted details)
        metadata = [
            ("Source IP Address", "192.168.1.1"),
            ("Received From", "mailserver.example.com"),
            ("Forwarded From", "smtp.example.com"),
            ("Server IP", "203.0.113.5"),
            ("Email Size", "2 MB"),
            ("SPF Status", "Pass"),
            ("DKIM Status", "Pass"),
            ("DMARC Status", "Pass"),
            ("X-Mailer", "Microsoft Outlook 16.0"),
            ("Received Date", "2025-01-19 14:25:00"),
        ]

        for row, (key, value) in enumerate(metadata):
            key_label = QLabel(f"<b>{key}:</b>")
            value_label = QLabel(value)
            metadata_table.addWidget(key_label, row, 0)
            metadata_table.addWidget(value_label, row, 1)

        right_panel_layout.addLayout(metadata_table)
        right_panel_widget.setLayout(right_panel_layout)
        
        # Analyse Button to open a new window
        self.analyse_button = QPushButton("Analyse", self)
        self.analyse_button.setStyleSheet("""
            QPushButton {
                background-color: #1e64fe;
                color: white;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #1e64fe;
            }
        """)
        self.analyse_button.clicked.connect(self.open_analysis_window)
        right_panel_layout.addWidget(self.analyse_button)

        # Add both panels (left and right) to the split view layout
        split_view_layout.addWidget(left_panel_widget, 2)  # Adjust the weight for proper splitting
        split_view_layout.addWidget(right_panel_widget, 1)

        split_view_widget.setLayout(split_view_layout)

        # Add the split view as a new tab
        self.tabs.addTab(split_view_widget, subject)
    
    def open_analysis_window(self):
        # Open a new window for analysis (to be expanded later)
        self.analysis_window = QMainWindow(self)
        self.analysis_window.setWindowTitle("Email Analysis")
        self.analysis_window.setGeometry(200, 200, 500, 400)

        # Central widget for analysis window
        central_widget = QWidget()
        self.analysis_window.setCentralWidget(central_widget)

        # Add a label as placeholder for analysis window
        analysis_layout = QVBoxLayout()
        analysis_label = QLabel("Email Analysis will be implemented here.", central_widget)
        analysis_label.setAlignment(Qt.AlignCenter)
        analysis_layout.addWidget(analysis_label)

        central_widget.setLayout(analysis_layout)
        self.analysis_window.show()

    def close_tab(self, index):
        self.tabs.removeTab(index)

# Run the application
if __name__ == "__main__":
    app = QApplication([])
    window = PhishEye()
    window.show()
    app.exec_()
