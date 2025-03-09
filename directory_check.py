import sys
import argparse
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QTextEdit, QProgressBar, QHBoxLayout
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class GobusterThread(QThread):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(list)
    progress_signal = pyqtSignal(int)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.results = []

    def run(self):
        try:
            gobuster_path = "/opt/homebrew/bin/gobuster" 
            wordlist_path = "directories/common.txt"      

            command = [gobuster_path, "dir", "-u", self.url, "-w", wordlist_path]

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True)

            total_progress = 0
            for line in iter(process.stdout.readline, ""):
                line = line.strip()
                if line:
                    self.output_signal.emit(line) 
                    total_progress += 1
                    progress_percentage = min(int((total_progress / 100) * 100), 100)
                    self.progress_signal.emit(progress_percentage)
                    if "Status:" in line:
                        self.results.append(line)

            process.stdout.close()
            process.wait()
            self.progress_signal.emit(100) 
            self.finished_signal.emit(self.results)

        except Exception as e:
            self.output_signal.emit(f"Error: {e}")


class DirectoryCheckWindow(QMainWindow):
    def __init__(self, url):
        super().__init__()
        self.setWindowTitle("Directory Check")
        self.setGeometry(200, 200, 800, 600)
        self.url = url

        # Layout
        layout = QVBoxLayout()
        
        # URL Label
        self.url_label = QLabel(f"Scanning URL: {url}")
        self.url_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.url_label)
        
        # Output Display
        self.output_display = QTextEdit(self)
        self.output_display.setReadOnly(True)
        layout.addWidget(self.output_display)

        # Progress Bar with Percentage
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(20)

        self.progress_label = QLabel("0%", self)
        self.progress_label.setAlignment(Qt.AlignRight)
        self.progress_label.setFixedWidth(40)

        progress_layout.addWidget(self.progress_bar, stretch=1)
        progress_layout.addWidget(self.progress_label)
        layout.addLayout(progress_layout)

        # Information label at the bottom
        self.info_label = QLabel("This process may take some time...", self)
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Automatically start scanning
        self.start_scan()

    def start_scan(self):
        self.output_display.append(f"🔍 Scanning: {self.url}\n")
        self.gobuster_thread = GobusterThread(self.url)
        self.gobuster_thread.output_signal.connect(self.update_output)
        self.gobuster_thread.progress_signal.connect(self.update_progress)
        self.gobuster_thread.finished_signal.connect(self.display_results)
        self.gobuster_thread.start()

    def update_output(self, text):
        self.output_display.append(text)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.progress_label.setText(f"{value}%")

    def display_results(self, results):
        """Open a new window to display the final results."""
        self.results_window = ResultsWindow(results)
        self.results_window.show()

class ResultsWindow(QMainWindow):
    def __init__(self, results):
        super().__init__()
        self.setWindowTitle("Scan Results")
        self.setGeometry(250, 250, 600, 400)

        layout = QVBoxLayout()
        
        self.results_display = QTextEdit(self)
        self.results_display.setReadOnly(True)
        self.results_display.append("\n".join(results))
        layout.addWidget(self.results_display)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="URL to scan for directories")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = DirectoryCheckWindow(args.url)
    window.show()
    sys.exit(app.exec_())