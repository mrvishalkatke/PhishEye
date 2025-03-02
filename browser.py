import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QLineEdit, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineSettings
from PyQt5.QtCore import QUrl

class SecureWebBrowser(QMainWindow):
    def __init__(self, url):
        super().__init__()
        self.setWindowTitle("Secure Web Browser")
        self.setGeometry(100, 100, 1200, 800)

        # Secure Web Profile
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        self.profile.setCachePath("")
        self.profile.setPersistentStoragePath("")
        self.profile.clearHttpCache()
        self.profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)

        # Web Engine
        self.browser = QWebEngineView()
        self.browser.setPage(self.create_page())
        self.browser.urlChanged.connect(self.update_address_bar)

        # Back Button
        self.back_button = QPushButton("◀")
        self.back_button.clicked.connect(self.browser.back)
        self.back_button.setFixedWidth(40)

        # Address Bar
        self.address_bar = QLineEdit()
        self.address_bar.setText(url)
        self.address_bar.returnPressed.connect(self.load_url)

        # Top Layout with Back Button and Address Bar
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.back_button)
        top_layout.addWidget(self.address_bar)

        # Main Layout
        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(self.browser)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Load the initial URL
        self.browser.setUrl(QUrl(url))

    def create_page(self):
        """Create a web page with custom security settings."""
        page = self.browser.page()
        settings = page.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, False)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, False)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, False)
        settings.setAttribute(QWebEngineSettings.DnsPrefetchEnabled, False)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, False)
        settings.setAttribute(QWebEngineSettings.XSSAuditingEnabled, True)

        # Block automatic downloads
        self.profile.downloadRequested.connect(self.handle_download)
        return page

    def handle_download(self, download):
        """Show a popup warning when an automatic download is detected."""
        QMessageBox.critical(self, "Warning", "⚠️ Malicious Activity Detected: A site attempted to download a file automatically!")
        download.cancel()
    
    def update_address_bar(self, url):
        """Update the address bar when the URL changes."""
        self.address_bar.setText(url.toString())
    
    def load_url(self):
        """Load the URL entered in the address bar."""
        url = self.address_bar.text()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        self.browser.setUrl(QUrl(url))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.google.com"
    window = SecureWebBrowser(url)
    window.show()
    sys.exit(app.exec_())
