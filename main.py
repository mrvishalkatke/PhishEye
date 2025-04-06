from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QVBoxLayout, QLabel, QWidget, QPushButton, QLineEdit, QHBoxLayout,
    QListWidget, QListWidgetItem, QTextBrowser, QTabWidget, QGridLayout, QDesktopWidget, QMenuBar, QMenu, QAction,
    QScrollArea, QSplitter, QFrame, QTabBar, QTableWidget, QTableWidgetItem, QDialog
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QPixmap, QColor, QPalette, QMovie, QIcon
import imaplib
import email
from email.header import decode_header
from datetime import datetime
import hashlib
import requests
from email.utils import parseaddr
import os
import subprocess
import re
import tempfile
import shutil
import tensorflow as tf
import numpy as np

class PhishEye(QMainWindow):
    def __init__(self):
        super().__init__()
        self.email = None
        self.password = None
        self.imap_server = "imap.gmail.com"
        self.imap = None
        self.url_model = None  
        self.file_model = None  
        self.dark_mode = True 
        self.toggle_dark_mode()
        self.init_login_ui()

    def center_window(self):
        """Center the window on the screen."""
        screen = QDesktopWidget().screenGeometry()
        window = self.frameGeometry()
        center = screen.center()
        window.moveCenter(center)
        self.move(window.topLeft())

    def init_login_ui(self):
        """Initialize the login UI."""
        self.setWindowTitle("PhishEye - Login")
        self.setGeometry(200, 200, 800, 300)

        # Dark mode toggle
        self.toggle_dark_mode(self.dark_mode)

        layout = QVBoxLayout()

        # Logo Label
        self.logo_label = QLabel(self)
        self.logo_pixmap = QPixmap("img/logo.png")  
        self.logo_label.setPixmap(self.logo_pixmap.scaled(550, 454, Qt.KeepAspectRatio))
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)

        # Email Input Field
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

        # Password Input Field
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

        # IMAP Server Input Field
        self.imap_input = QLineEdit(self)
        self.imap_input.setPlaceholderText("IMAP Server (e.g., imap.gmail.com)")
        self.imap_input.setText(self.imap_server) 
        self.imap_input.setStyleSheet("""
            QLineEdit {
                border-radius: 15px;
                border: 2px solid #ccc;
                padding: 10px;
            }
        """)
        self.imap_input.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.imap_input)

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

        # Loading Icon (Initially Hidden)
        self.loading_label = QLabel(self)
        self.loading_movie = QMovie("img/loading.png")  
        self.loading_movie.setScaledSize(QSize(200, 40))  
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.hide()  
        layout.addWidget(self.loading_label)

        # Set the layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Center the login screen on the screen
        self.center_on_screen()

    def login(self):
        """Handle user login by replacing the button with a loading icon."""
        # Hide the login button
        self.login_button.hide()

        # Show the loading animation
        self.loading_label.show()
        self.loading_movie.start()

        # Delay the login process slightly to show animation
        QTimer.singleShot(100, self.perform_login) 

    def perform_login(self):
        """Perform the login process after a short delay."""
        self.email = self.email_input.text()
        self.password = self.password_input.text()
        self.imap_server = self.imap_input.text()

        if not self.email or not self.password or not self.imap_server:
            QMessageBox.warning(self, "Input Error", "Please enter email, password, and IMAP server.")
            self.restore_login_button()
            return

        try:
            self.imap = imaplib.IMAP4_SSL(self.imap_server)
            self.imap.login(self.email, self.password)

            self.statusBar().showMessage(f"Logged in as {self.email}")
            self.init_email_ui()
            self.fetch_emails()

        except imaplib.IMAP4.error:
            QMessageBox.critical(self, "Login Failed", "Invalid email, password, or IMAP server.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
        finally:
            self.restore_login_button()

    def restore_login_button(self):
        """Restore the login button and hide the loading animation."""
        self.loading_movie.stop()
        self.loading_label.hide()
        self.login_button.show()

    def open_email_without_redirect(self, item):
        """Double-click: Open email in a new tab but do not switch to it."""
        email_id, subject, msg = item.data(Qt.UserRole)
        
        # Open the email using `display_email_content()`
        self.display_email_content(subject, msg)

    def open_email_and_redirect(self, pos):
        """Right-click: Open email and switch to that tab."""
        item = self.email_list.itemAt(pos)
        if item:
            email_id, subject, msg = item.data(Qt.UserRole)

            # Open email
            self.display_email_content(subject, msg)

            # Switch to the newly opened tab
            short_subject = self.get_short_subject(subject, length=15)
            for i in range(self.tabs.count()):
                if self.tabs.tabText(i) == short_subject:
                    self.tabs.setCurrentIndex(i)
                    break

    def center_on_screen(self):
        """Manually center the login screen on the screen."""
        screen = QDesktopWidget().screenGeometry() 
        window = self.geometry() 

        # Calculate the top-left corner of the window
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 5

        # Move the window to the calculated position
        self.move(x, y)
        
    def init_menu_bar(self):
        """Initialize the menu bar."""
        menubar = self.menuBar()

        # Settings Menu
        settings_menu = menubar.addMenu("Settings")
        dark_mode_action = QAction("Toggle Dark Mode", self)
        dark_mode_action.triggered.connect(self.toggle_dark_mode)
        settings_menu.addAction(dark_mode_action)

    def toggle_dark_mode(self, checked=None):
        """Toggle dark mode globally across the application and update text colors."""
        self.dark_mode = not self.dark_mode if checked is None else checked

        palette = QPalette()
        text_color = "white" if self.dark_mode else "black"

        if self.dark_mode:
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(35, 35, 35))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
        else:
            palette.setColor(QPalette.Window, Qt.white)
            palette.setColor(QPalette.WindowText, Qt.black)
            palette.setColor(QPalette.Base, Qt.white)
            palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.black)
            palette.setColor(QPalette.Text, Qt.black)
            palette.setColor(QPalette.Button, QColor(240, 240, 240))
            palette.setColor(QPalette.ButtonText, Qt.black)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.white)

        QApplication.instance().setPalette(palette)

        # Update text colors in both settings and analysis window if open
        if hasattr(self, "settings_window") and self.settings_window.isVisible():
            self.update_settings_text_color(text_color)
        if hasattr(self, "email_analysis_window") and self.email_analysis_window.isVisible():
            self.update_analysis_text_color(text_color)

    def init_email_ui(self):
        """Initialize the email UI with Inbox tab fixed at the top left."""
        self.setWindowTitle("PhishEye - Inbox")
        self.setGeometry(200, 200, 1200, 700)

        main_layout = QVBoxLayout()

        # Inbox Section
        self.inbox_widget = QWidget(self)
        self.inbox_layout = QVBoxLayout()

        self.email_list = QListWidget()
        self.email_list.setContextMenuPolicy(Qt.CustomContextMenu) 
        self.email_list.customContextMenuRequested.connect(self.open_email_and_redirect) 
        self.email_list.itemDoubleClicked.connect(self.open_email_without_redirect) 
        self.inbox_layout.addWidget(self.email_list)

        # Settings Button
        self.settings_button = QPushButton("Settings", self)
        self.settings_button.setStyleSheet("background-color: #1e64fe; color: white;")
        self.settings_button.clicked.connect(self.open_settings_window)
        self.inbox_layout.addWidget(self.settings_button)

        # Clear Button**
        self.clear_button = QPushButton("Clear", self)
        self.clear_button.setStyleSheet("background-color: black; color: white;")
        self.clear_button.clicked.connect(self.confirm_clear)
        self.inbox_layout.addWidget(self.clear_button)

        self.inbox_widget.setLayout(self.inbox_layout)

        # Tabs Setup
        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setMovable(True) 

        # Align tabs at the top left
        self.tabs.setTabPosition(QTabWidget.North)  
        self.tabs.setLayoutDirection(Qt.LeftToRight)   

        # Inbox Tab (Fixed & Non-Closable)
        self.tabs.addTab(self.inbox_widget, "📥 Inbox")
        self.tabs.tabBar().setTabButton(0, QTabBar.RightSide, None)  
        self.tabs.tabBar().setExpanding(False)  

        # Logout Button (Right Aligned)
        logout_layout = QHBoxLayout()
        logout_layout.addStretch()
        self.logout_button = QPushButton("Logout")
        self.logout_button.setStyleSheet("background-color: red; color: white;")
        self.logout_button.clicked.connect(self.confirm_logout)
        logout_layout.addWidget(self.logout_button)

        # Bottom Layout (Align Buttons Properly)
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.settings_button)
        bottom_layout.addWidget(self.clear_button)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.logout_button)

        # Final Layout
        main_layout.addWidget(self.tabs)
        main_layout.addLayout(bottom_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.center_window()

    def get_short_subject(self, subject, length=10):
        """Shorten the subject for tab display."""
        return subject if len(subject) <= length else subject[:length] + "..."

    def open_settings_window(self):
        """Open the settings window and display user account details with dynamic text color."""
        if not self.email or not self.imap:
            QMessageBox.warning(self, "Error", "You are not logged in.")
            return

        self.settings_window = QDialog(self)
        self.settings_window.setWindowTitle("Settings")
        self.settings_window.setFixedSize(400, 350)

        # Center the settings window
        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.settings_window.frameGeometry()
        center_point = screen.center()
        window_geometry.moveCenter(center_point)
        self.settings_window.move(window_geometry.topLeft())

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Determine Text Color Based on Dark Mode
        text_color = "white" if self.dark_mode else "black"

        # Profile Picture
        profile_picture = self.fetch_profile_picture(self.email)
        profile_label = QLabel(self.settings_window)
        profile_label.setPixmap(profile_picture.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        profile_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(profile_label)

        # User Name
        full_name = self.fetch_user_full_name()
        name_label = QLabel(f"<b>{full_name}</b>")
        name_label.setStyleSheet(f"font-size: 20px; color: {text_color};")
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)

        # Email ID
        email_label = QLabel(f"{self.email}")
        email_label.setStyleSheet(f"font-size: 16px; color: {text_color};")
        email_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(email_label)

        # IMAP Server (Optional)
        imap_label = QLabel(f"IMAP Server: {self.imap_server}")
        imap_label.setStyleSheet(f"font-size: 14px; color: {text_color};")
        imap_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(imap_label)

        # Dark Mode Toggle
        self.dark_mode_button = QPushButton("Toggle Dark Mode", self)
        self.dark_mode_button.clicked.connect(lambda: [self.toggle_dark_mode(), self.update_settings_text_color()])
        layout.addWidget(self.dark_mode_button, alignment=Qt.AlignCenter)

        # Close Button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.settings_window.close)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)

        self.settings_window.setLayout(layout)
        self.settings_window.exec_()

    def update_settings_text_color(self, text_color=None):
        """Update the text color of user details in the settings window."""
        if not hasattr(self, "settings_window") or not self.settings_window.isVisible():
            return  

        text_color = text_color or ("white" if self.dark_mode else "black")

        for widget in self.settings_window.findChildren(QLabel):
            widget.setStyleSheet(f"color: {text_color};")

    def fetch_user_full_name(self):
        """Fetch the user's full name from the email headers."""
        try:
            self.imap.select("INBOX")
            status, messages = self.imap.search(None, "ALL")
            if status != "OK" or not messages[0]:
                return "Unknown"

            latest_email_id = messages[0].split()[-1] 
            status, msg_data = self.imap.fetch(latest_email_id, "(RFC822)")
            if status != "OK":
                return "Unknown"

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    from_header = msg.get("From")
                    name, _ = parseaddr(from_header)
                    return name if name else "Unknown"

        except Exception as e:
            print(f"Error fetching name: {e}")
        
        return "Unknown"

    def fetch_profile_picture(self, email):
        """Fetch profile picture from Gravatar using the user's email."""
        default_avatar = QPixmap("img/default_avatar.png")   
        email_hash = hashlib.md5(email.strip().lower().encode()).hexdigest()
        gravatar_url = f"https://www.gravatar.com/avatar/{email_hash}?s=100&d=identicon"

        try:
            response = requests.get(gravatar_url, stream=True)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                return pixmap
        except Exception as e:
            print(f"Error fetching profile picture: {e}")

        return default_avatar  

    def fetch_emails(self):
        """Fetch emails from the IMAP server."""
        if not self.imap:
            QMessageBox.critical(self, "Error", "You are not logged in.")
            return

        try:
            self.imap.select("INBOX")
            status, messages = self.imap.search(None, "ALL")
            if status != "OK":
                QMessageBox.warning(self, "Error", "Failed to fetch emails.")
                return

            email_ids = messages[0].split()[::-1]   
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
                        email_item.setData(Qt.UserRole, (email_id, subject, msg))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch emails: {e}")

    def format_datetime(self, raw_date):
        """Format raw email date into a readable format."""
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(raw_date)
            formatted_date = dt.strftime("%a, %d %B %Y")
            formatted_time = dt.strftime("%I:%M:%S %p")
            return formatted_date, formatted_time
        except Exception:
            return "Invalid Date", "Invalid Time"

    def display_split_view(self, item):
        """Display email content in a split view, or switch to the existing tab if it's already open."""
        email_id, subject, msg = item.data(Qt.UserRole)

        # Check if the email is already open in a tab
        for i in range(self.tabs.count()):
            tab_title = self.tabs.tabText(i)
            if tab_title == subject:
                # If tab with the same subject is already open, switch to it
                self.tabs.setCurrentIndex(i)
                return

        # If the tab is not already open, create a new tab
        body = None
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    body = part.get_payload(decode=True).decode()

        if body is None:
            body = "No email content available."

        self.display_email_content(subject, body, msg)

    def display_email_content(self, subject, msg):
        """Display email content and metadata with proper formatting and attachments."""
        
        short_subject = self.get_short_subject(subject, length=15)

        # Check if email is already open, redirect to it instead of opening a new tab
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == short_subject:
                self.tabs.setCurrentIndex(i) 
                return

        split_view_widget = QWidget(self)
        split_view_layout = QHBoxLayout()

        # Left Panel: Email Content
        left_panel_widget = QWidget(self)
        left_panel_layout = QVBoxLayout()

        # Extract sender's email
        from_header = msg.get("From")
        sender_name, sender_email = email.utils.parseaddr(from_header)

        # Extract and format date
        raw_date = msg.get("Date")
        formatted_date, formatted_time = self.format_datetime(raw_date)

        # Email Header Details
        email_details_layout = QGridLayout()
        subject_label = QLabel(f"<b>Subject:</b> {subject}")
        email_details_layout.addWidget(subject_label, 0, 0)
        sender_label = QLabel(f"<b>From:</b> {sender_email}")
        email_details_layout.addWidget(sender_label, 1, 0)
        date_label = QLabel(f"<b>Date:</b> {formatted_date}")
        date_label.setAlignment(Qt.AlignRight)
        email_details_layout.addWidget(date_label, 0, 1)
        time_label = QLabel(f"<b>Time:</b> {formatted_time}")
        time_label.setAlignment(Qt.AlignRight)
        email_details_layout.addWidget(time_label, 1, 1)

        left_panel_layout.addLayout(email_details_layout)

        # Extract Email Body
        body = self.extract_email_body(msg)

        formatted_body = self.format_email_body(body)

        email_body_browser = QTextBrowser(self)
        email_body_browser.setHtml(formatted_body)
        left_panel_layout.addWidget(email_body_browser)

        # Display Attachments at the Bottom
        attachments = self.extract_attachments(msg)
        if attachments:
            attachments_label = QLabel("<b>Attachments:</b>")
            left_panel_layout.addWidget(attachments_label)
            for attachment in attachments:
                attachment_label = QLabel(f"📎 {attachment}")
                left_panel_layout.addWidget(attachment_label)

        left_panel_widget.setLayout(left_panel_layout)

        # Right Panel: Metadata
        right_panel_widget = QWidget(self)
        right_panel_layout = QVBoxLayout()

        metadata_table = QTableWidget(self)
        metadata_table.setColumnCount(2)
        metadata_table.setHorizontalHeaderLabels(["Key", "Value"])
        metadata_table.horizontalHeader().setStretchLastSection(True)
        metadata_table.setEditTriggers(QTableWidget.NoEditTriggers)

        received_headers = msg.get_all("Received", [])
        metadata = [("Received Header", header) for header in received_headers]
        metadata.extend([
            ("Message-ID", msg.get("Message-ID", "N/A")),
            ("Return-Path", msg.get("Return-Path", "N/A")),
            ("X-Originating-IP", msg.get("X-Originating-IP", "N/A")),
            ("X-Mailer", msg.get("X-Mailer", "N/A")),
            ("MIME-Version", msg.get("MIME-Version", "N/A")),
        ])

        metadata_table.setRowCount(len(metadata))
        for row, (key, value) in enumerate(metadata):
            metadata_table.setItem(row, 0, QTableWidgetItem(key))
            metadata_table.setItem(row, 1, QTableWidgetItem(value))

        right_panel_layout.addWidget(metadata_table)

        # Analyze Button
        self.analyse_button = QPushButton("Analyze", self)
        self.analyse_button.setStyleSheet("""
            QPushButton {
                background-color: #1e64fe;
                color: white;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #1652cc;
            }
        """)
        self.analyse_button.clicked.connect(self.open_email_analysis_window)
        right_panel_layout.addWidget(self.analyse_button)

        right_panel_widget.setLayout(right_panel_layout)

        # Add Both Panels to the Split View
        split_view_layout.addWidget(left_panel_widget, 2)
        split_view_layout.addWidget(right_panel_widget, 1)

        split_view_widget.setLayout(split_view_layout)

        # Add as a New Tab
        self.tabs.addTab(split_view_widget, short_subject)
        self.tabs.setCurrentWidget(split_view_widget) 

    def extract_email_body(self, msg):
        """Extracts the email body and ensures it is always returned as a string."""
        body = None

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
                        break  
                    except:
                        continue 
        else:
            try:
                body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8')
            except:
                body = None

        return body if body else "No email content available."  

    def format_email_body(self, body):
        """Format the email body to preserve paragraphs and line breaks."""
        
        if not isinstance(body, str):  
            return "<i>No email content available.</i>"

        formatted_body = body.replace("\n\n", "</p><p>").replace("\n", "<br>")

        return f"<p>{formatted_body}</p>"

    def open_email_analysis_window(self):
        """Open a new window for detailed email analysis with dynamic text color."""
        current_tab_index = self.tabs.currentIndex()
        if current_tab_index == 0:  
            QMessageBox.warning(self, "Error", "Please select an email to analyze.")
            return

        current_tab = self.tabs.widget(current_tab_index)
        email_body_browser = current_tab.findChild(QTextBrowser)
        if not email_body_browser:
            QMessageBox.warning(self, "Error", "No email content found.")
            return

        email_item = self.email_list.currentItem()
        if not email_item:
            QMessageBox.warning(self, "Error", "No email selected.")
            return

        email_id, subject, msg = email_item.data(Qt.UserRole)

        attachments = self.extract_attachments(msg)
        email_content = email_body_browser.toPlainText()
        urls = self.extract_urls(email_content)

        self.email_analysis_window = QMainWindow(self)
        self.email_analysis_window.setWindowTitle("Detailed Email Analysis")
        self.email_analysis_window.setFixedSize(1000, 500)

        central_widget = QWidget()
        self.email_analysis_window.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # Dynamic Text Color Based on Dark Mode
        text_color = "white" if self.dark_mode else "black"

        section_label = QLabel("<b>Attachments and URLs:</b>")
        section_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {text_color};")
        main_layout.addWidget(section_label)

        if attachments or urls:
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)

            for attachment in attachments:
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)

                attachment_label = QLabel(attachment)
                attachment_label.setStyleSheet(f"font-size: 14px; color: {text_color};")
                row_layout.addWidget(attachment_label, stretch=1)

                malware_button = QPushButton("Check for Malware")
                malware_button.setFixedSize(150, 30)
                malware_button.setStyleSheet("""
                    QPushButton {
                        background-color: #1e64fe;
                        color: white;
                        border-radius: 5px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #1652cc;
                    }
                """)
                malware_button.clicked.connect(lambda _, x=attachment: self.check_attachment_malware(x))
                row_layout.addWidget(malware_button)

                safe_env_button = QPushButton("Open in Safe File Viewer")
                safe_env_button.setFixedSize(180, 30)
                safe_env_button.setStyleSheet("""
                    QPushButton {
                        background-color: #1e64fe;
                        color: white;
                        border-radius: 5px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #1652cc;
                    }
                """)
                safe_env_button.clicked.connect(lambda _, x=attachment: subprocess.Popen(["python", "safe_file_browser.py", x]))
                row_layout.addWidget(safe_env_button)

                scroll_layout.addWidget(row_widget)

            for url in urls:
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)

                url_label = QLabel(url)
                url_label.setStyleSheet(f"font-size: 14px; color: {text_color};")
                row_layout.addWidget(url_label, stretch=1)

                dir_check_button = QPushButton("Directory Check")
                dir_check_button.setFixedSize(150, 30)
                dir_check_button.setStyleSheet("""
                    QPushButton {
                        background-color: #1e64fe;
                        color: white;
                        border-radius: 5px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #1652cc;
                    }
                """)
                dir_check_button.clicked.connect(lambda _, x=url: subprocess.Popen(["python", "directory_check.py", "--url", x]))
                row_layout.addWidget(dir_check_button)

                safe_env_button = QPushButton("Open in Safe Browser")
                safe_env_button.setFixedSize(180, 30)
                safe_env_button.setStyleSheet("""
                    QPushButton {
                        background-color: #1e64fe;
                        color: white;
                        border-radius: 5px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #1652cc;
                    }
                """)
                safe_env_button.clicked.connect(lambda _, x=url: subprocess.Popen(["python", "browser.py", x]))
                row_layout.addWidget(safe_env_button)
                
                check_malicious_button = QPushButton("Check if Malicious")
                check_malicious_button.setFixedSize(180, 30)
                check_malicious_button.setStyleSheet("""
                    QPushButton {
                        background-color: #FF8C00;
                        color: white;
                        border-radius: 5px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #FF7000;
                    }
                """)
                check_malicious_button.clicked.connect(lambda _, x=url: subprocess.Popen(["python", "url_detection.py", "--url", x, "--dark" if self.dark_mode else ""]))
                row_layout.addWidget(check_malicious_button)

                scroll_layout.addWidget(row_widget)

            scroll_area.setWidget(scroll_widget)
            main_layout.addWidget(scroll_area)
        else:
            no_items_label = QLabel("There are no attachments or URLs.")
            no_items_label.setStyleSheet(f"font-size: 14px; color: {text_color};")
            main_layout.addWidget(no_items_label)

        close_button = QPushButton("Close")
        close_button.setFixedSize(100, 30)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #1e64fe;
                color: white;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1652cc;
            }
        """)
        close_button.clicked.connect(self.email_analysis_window.close)
        main_layout.addWidget(close_button, alignment=Qt.AlignCenter)

        central_widget.setLayout(main_layout)
        self.email_analysis_window.show()
        
    def update_analysis_text_color(self, text_color=None):
        """Update the text color of user details in the analysis window."""
        if not hasattr(self, "email_analysis_window") or not self.email_analysis_window.isVisible():
            return  

        text_color = text_color or ("white" if self.dark_mode else "black")

        for widget in self.email_analysis_window.findChildren(QLabel):
            widget.setStyleSheet(f"color: {text_color};")

    def extract_attachments(self, msg):
        """Extract attachments from the email."""
        attachments = []
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_disposition() == "attachment":
                    filename = part.get_filename()
                    if filename:
                        attachments.append(filename)
        return attachments

    def extract_urls(self, email_content):
        """Extract URLs from the email body."""
        # Regular expression to find URLs
        url_pattern = re.compile(r'https?://\S+')
        urls = url_pattern.findall(email_content)
        return urls
    
    def open_attachment_safely(self, attachment_name, attachment_data):
        """Open an attached file in the Safe File Browser and ensure it launches properly."""
        safe_file_browser_path = os.path.join(os.path.dirname(__file__), "safe_file_browser.py")

        if not os.path.exists(safe_file_browser_path):
            QMessageBox.critical(self, "Error", "Safe File Browser not found!")
            return

        try:
            process = subprocess.Popen(
                ["python3", safe_file_browser_path, attachment_name], 
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            process.stdin.write(attachment_data)
            process.stdin.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open attachment safely: {e}")

    def open_url_safely(self, url):
        """Open a URL in the Secure Web Browser."""
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        
        try:
            # Launch the Secure Web Browser
            subprocess.Popen(["python", "browser.py", url])
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open URL in safe environment: {e}")

    def get_attachment_from_email(self, msg):
        """Extract the first attachment from an email without saving it to disk."""
        if not isinstance(msg, email.message.Message):  
            QMessageBox.critical(self, "Error", "Invalid email format.")
            return None, None

        for part in msg.walk():
            content_disposition = part.get("Content-Disposition", "")

            # Check if the part is an attachment
            if "attachment" in content_disposition:
                attachment_name = part.get_filename()
                attachment_data = part.get_payload(decode=True)

                if attachment_name and attachment_data:
                    return attachment_data, attachment_name   

        return None, None  

    def check_attachment_malware(self, attachment):
        """Scan the attachment for malware and display the analysis results."""
        if not attachment:
            QMessageBox.warning(self, "Error", "No file selected.")
            return

        # Create Analyzing Window
        self.analyzing_window = QDialog(self)
        self.analyzing_window.setWindowTitle(f"Analyzing {attachment}")
        self.analyzing_window.setFixedSize(500, 400)

        layout = QVBoxLayout()

        # File Type-Based Threats
        file_ext = os.path.splitext(attachment)[1].lower()
        threats = self.get_potential_threats(file_ext)
        threat_label = QLabel("<b>Potential Threats:</b>")
        threat_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(threat_label)

        threats_text = QTextBrowser()
        threats_text.setPlainText("\n".join(threats) if threats else "No specific threats detected for this file type.")
        layout.addWidget(threats_text)

        # Perform Malware Scan
        scan_result = self.scan_for_malware(attachment) 
        QMessageBox.information(self, "Malware Scan Result", scan_result)

        # Display Scan Results
        result_label = QLabel("<b>Scan Results:</b>")
        result_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(result_label)

        result_text = QTextBrowser()
        result_text.setPlainText(scan_result)
        layout.addWidget(result_text)

        # Close Button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.analyzing_window.close)
        layout.addWidget(close_button)

        self.analyzing_window.setLayout(layout)
        self.analyzing_window.exec_()

    def extract_attachment(self, email_msg, attachment_name):
        """Extract an attachment from an email message and return its data."""
        for part in email_msg.walk():
            content_disposition = part.get("Content-Disposition", "")

            if "attachment" in content_disposition:
                filename = part.get_filename()
                if filename and filename == attachment_name:
                    return part.get_payload(decode=True), filename  

        return None, None  

    def get_potential_threats(self, file_ext):
        """Return common threats based on file extension."""
        threats_dict = {
            ".exe": ["Trojan horses", "Ransomware", "Backdoors"],
            ".docx": ["Macro viruses", "Embedded scripts"],
            ".pdf": ["Malicious JavaScript", "Exploit payloads"],
            ".xlsm": ["Excel Macro Malware"],
            ".zip": ["Packed malware", "Hidden executables"],
            ".js": ["Obfuscated JavaScript", "Malicious redirects"],
        }
        return threats_dict.get(file_ext, ["Unknown threats or safe file type."])

    def preprocess_url(self, url):
        """Preprocess the URL to match the AI model's expected input shape (1, 16)."""
        url = url.lower()  
        url = re.sub(r"[^a-zA-Z0-9./:?=]", "", url)  # Remove special characters

        # Convert URL to ASCII numeric values
        url_vector = np.array([ord(c) for c in url if ord(c) < 128])[:16]  # Limit to 16 chars

        # Pad with zeros if it's shorter than 16 chars
        if len(url_vector) < 16:
            url_vector = np.pad(url_vector, (0, 16 - len(url_vector)), 'constant')

        return np.expand_dims(url_vector, axis=0)  # Ensure it has shape (1, 16)

    def scan_for_malware(self, input_data, email_msg=None):
        """Scan a file or URL for malware using AI models and ClamAV."""
        try:
            # Check URLs using the AI model (`url.h5`)
            if input_data.startswith("http://") or input_data.startswith("https://"):
                if self.url_model:
                    url_input = self.preprocess_url(input_data)
                    prediction = self.url_model.predict(url_input)[0][0]  # Output probability

                    if prediction > 0.5:
                        return f"⚠️ Malicious URL Detected: {input_data}"
                    else:
                        return f"✅ Safe URL: {input_data}"
                else:
                    return "❌ AI Model not loaded for URL scanning."

            # Extract Attachments and Scan Using `file_model.h5`
            if email_msg:
                attachment_data, attachment_name = self.extract_attachment(email_msg, input_data)
                if attachment_data:
                    return self.scan_attachment_ai(attachment_data, attachment_name)  # Use AI Model
                else:
                    return f"❌ Error: Attachment '{input_data}' not found in the email."

            # Use ClamAV if `file_model.h5` is unavailable
            if os.path.exists(input_data):
                result = subprocess.run(["clamscan", input_data], capture_output=True, text=True)
                if "FOUND" in result.stdout:
                    return f"⚠️ Malware Detected: {result.stdout.split(':')[-1].strip()}"
                else:
                    return f"✅ {os.path.basename(input_data)} is safe to open."

            return f"❌ Error: File not found - {input_data}"

        except Exception as e:
            return f"❌ Error scanning input: {e}"
    
    def scan_attachment_ai(self, file_data, filename):
        """Use AI to scan an email attachment for malware."""
        if not self.file_model:
            return "❌ AI Model not loaded for file scanning."

        # Convert file data into a format suitable for AI model
        file_vector = self.preprocess_file(file_data)

        # Make AI prediction
        prediction = self.file_model.predict(file_vector)[0][0]  # Output probability

        if prediction > 0.5:
            return f"⚠️ Malicious File Detected: {filename}"
        else:
            return f"✅ Safe File: {filename}"

    def preprocess_file(self, file_data):
        """Convert a file's raw binary data into a numerical format suitable for the AI model."""
        import numpy as np

        # Convert raw bytes to numerical features
        byte_array = np.frombuffer(file_data, dtype=np.uint8)[:1000]  # Limit to 1000 bytes

        # Pad with zeros if shorter
        if len(byte_array) < 1000:
            byte_array = np.pad(byte_array, (0, 1000 - len(byte_array)), 'constant')

        return np.expand_dims(byte_array, axis=0)  # Ensure correct input shape

    def scan_attachment_memory(self, file_data, filename):
        """Scan an attachment directly from memory without saving it to disk."""
        try:
            with tempfile.NamedTemporaryFile(delete=True) as temp_file:
                temp_file.write(file_data)
                temp_file.flush() 

                # Scan the temporary file
                result = subprocess.run(["clamscan", temp_file.name], capture_output=True, text=True)
                
                if "FOUND" in result.stdout:
                    return f"⚠️ Malware Detected in {filename}"
                else:
                    return f"✅ {filename} is safe to open."

        except Exception as e:
            return f"❌ Error scanning attachment: {e}"
    
    def check_url_safe_env(self, url):
        """Placeholder for checking a URL in a safe environment."""
        QMessageBox.information(self, "Safe Environment Check", f"Checking {url} in a safe environment...")

    def check_url_malware(self, url):
        """Placeholder for checking a URL for malware."""
        safe = False 
        if safe:
            QMessageBox.information(self, "Malware Check", f"{url} is safe.")
        else:
            QMessageBox.warning(self, "Malware Check", f"{url} is potentially harmful!")

    def logout(self):
        """Logout the user safely and return to the login screen."""
        try:
            if self.imap:
                try:
                    # Properly close the IMAP connection
                    self.imap.shutdown()
                    self.imap.logout()
                except Exception as e:
                    print(f"Clean logout failed: {e}")
                finally:
                    self.imap = None

            # Add small delay for connection cleanup
            QTimer.singleShot(500, self.clear_ui)
            
        except Exception as e:
            QMessageBox.critical(self, "Logout Error", 
                f"An unexpected error occurred during logout:\n{str(e)}")

    def clear_ui(self):
        """Final cleanup after logout delay"""
        try:
            # Close all open email windows
            for i in range(self.tabs.count() - 1, 0, -1):
                self.tabs.removeTab(i)

            # Reset UI
            self.clear_ui()
            self.init_login_ui()
            
            # Force garbage collection
            import gc
            gc.collect()
            
        except Exception as e:
            QMessageBox.critical(self, "Cleanup Error", 
                f"Post-logout cleanup failed:\n{str(e)}")

    def confirm_logout(self):
        """Confirm logout action."""
        reply = QMessageBox.question(
            self, 'Logout Confirmation', 'Are you sure you want to logout?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.logout()

    def clear_all_tabs(self):
        """Clear all opened email tabs."""
        for i in range(self.tabs.count() - 1, 0, -1):
            self.tabs.removeTab(i)

    def confirm_clear(self):
        """Confirm clearing all opened email tabs."""
        reply = QMessageBox.question(self, 'Clear Confirmation', 'Are you sure you want to clear all opened emails?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.clear_all_tabs()

    def close_tab(self, index):
        """Close a specific tab."""
        if index != 0:  # Prevent closing the Inbox tab
            self.tabs.removeTab(index)

# Run the application
if __name__ == "__main__":
    app = QApplication([])
    window = PhishEye()
    window.show()
    app.exec_()