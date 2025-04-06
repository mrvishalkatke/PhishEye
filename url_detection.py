import sys
import xgboost as xgb
import numpy as np
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTextEdit, QGroupBox, QProgressBar)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QColor, QPalette
import re
from openai import OpenAI

# Configuration - Set your OpenAI API key here
client = OpenAI(api_key="0U4bHUVTyhEbfmZ99-_NL9SXNaLwd8OE-lECdjeJxdN2-VkdqGc1BCQ4E9jr_tN4b2QWNuwYNoT3BlbkFJCb9dJHiiRruIjW9jEK2NdE1wPBrnt1-ix22_5rJoSeg4LpZVai-h6m8rSnphhPRo6wUCpedCcA")

# Load the XGBoost model
model = xgb.Booster()
model.load_model("Model/XGBoostClassifier.json")

def extract_features(url):
    """
    Extract 30 features from the URL as expected by the model.
    Some features are computed from the URL; others are set as dummy values.
    Replace dummy values with real extraction logic if available.
    """
    features = {}
    # 1. having_IP_Address: 1 if URL contains an IP address, else 0.
    features["having_IP_Address"] = 1 if re.search(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', url) else 0
    # 2. URL_Length: length of the URL.
    features["URL_Length"] = len(url)
    # 3. Shortining_Service: 1 if URL contains a known shortener.
    shorteners = ["bit.ly", "tinyurl.com", "goo.gl", "ow.ly", "is.gd"]
    features["Shortining_Service"] = 1 if any(s in url for s in shorteners) else 0
    # 4. having_At_Symbol: 1 if '@' is in URL.
    features["having_At_Symbol"] = 1 if "@" in url else 0
    # 5. double_slash_redirecting: 1 if '//' occurs in the URL path (after protocol).
    try:
        path = url.split("://")[1]
        features["double_slash_redirecting"] = 1 if path.find("//") != -1 else 0
    except IndexError:
        features["double_slash_redirecting"] = 0
    # 6. Prefix_Suffix: 1 if '-' is in the domain part.
    try:
        domain = url.split("://")[1].split("/")[0]
        features["Prefix_Suffix"] = 1 if "-" in domain else 0
    except:
        features["Prefix_Suffix"] = 0
    # 7. having_Sub_Domain: 1 if domain contains more than one dot.
    try:
        domain = url.split("://")[1].split("/")[0]
        features["having_Sub_Domain"] = 1 if domain.count(".") > 1 else 0
    except:
        features["having_Sub_Domain"] = 0
    # 8. SSLfinal_State: 1 if URL starts with 'https', else 0.
    features["SSLfinal_State"] = 1 if url.startswith("https") else 0
    # 9. Domain_registeration_length: dummy value (replace with real registration length if available).
    features["Domain_registeration_length"] = 0
    # 10. Favicon: dummy value.
    features["Favicon"] = 0
    # 11. port: dummy value.
    features["port"] = 0
    # 12. HTTPS_token: 1 if "https" appears in the domain part improperly.
    try:
        domain = url.split("://")[1].split("/")[0]
        features["HTTPS_token"] = 1 if "https" in domain else 0
    except:
        features["HTTPS_token"] = 0
    # 13. URL_of_Anchor: dummy value.
    features["URL_of_Anchor"] = 0
    # 14. Links_in_tags: dummy value.
    features["Links_in_tags"] = 0
    # 15. SFH: dummy value.
    features["SFH"] = 0
    # 16. Submitting_to_email: dummy value.
    features["Submitting_to_email"] = 0
    # 17. Abnormal_URL: dummy value.
    features["Abnormal_URL"] = 0
    # 18. Redirect: dummy value.
    features["Redirect"] = 0
    # 19. on_mouseover: dummy value.
    features["on_mouseover"] = 0
    # 20. RightClick: dummy value.
    features["RightClick"] = 0
    # 21. popUpWidnow: dummy value.
    features["popUpWidnow"] = 0
    # 22. Iframe: 1 if 'iframe' in URL, else 0.
    features["Iframe"] = 1 if "iframe" in url.lower() else 0
    # 23. age_of_domain: dummy value.
    features["age_of_domain"] = 0
    # 24. DNSRecord: dummy value.
    features["DNSRecord"] = 0
    # 25. web_traffic: dummy value.
    features["web_traffic"] = 0
    # 26. Page_Rank: dummy value.
    features["Page_Rank"] = 0
    # 27. Google_Index: dummy value.
    features["Google_Index"] = 0
    # 28. Links_pointing_to_page: dummy value.
    features["Links_pointing_to_page"] = 0
    # 29. Statistical_report: dummy value.
    features["Statistical_report"] = 0
    # 30. Request_URL_part_0: We'll take the first part after splitting the URL by comma.
    parts = url.split(',')
    features["Request_URL_part_0"] = len(parts[0]) if parts else len(url)
    
    # Define the order as specified in the JSON model
    order = [
        "having_IP_Address", "URL_Length", "Shortining_Service", "having_At_Symbol",
        "double_slash_redirecting", "Prefix_Suffix", "having_Sub_Domain", "SSLfinal_State",
        "Domain_registeration_length", "Favicon", "port", "HTTPS_token", "URL_of_Anchor",
        "Links_in_tags", "SFH", "Submitting_to_email", "Abnormal_URL", "Redirect",
        "on_mouseover", "RightClick", "popUpWidnow", "Iframe", "age_of_domain", "DNSRecord",
        "web_traffic", "Page_Rank", "Google_Index", "Links_pointing_to_page", "Statistical_report",
        "Request_URL_part_0"
    ]
    feature_vector = [features[key] for key in order]
    return np.array([feature_vector])

# Define the expected feature names (order must match training)
feature_names = [
    "having_IP_Address", "URL_Length", "Shortining_Service", "having_At_Symbol",
    "double_slash_redirecting", "Prefix_Suffix", "having_Sub_Domain", "SSLfinal_State",
    "Domain_registeration_length", "Favicon", "port", "HTTPS_token", "URL_of_Anchor",
    "Links_in_tags", "SFH", "Submitting_to_email", "Abnormal_URL", "Redirect",
    "on_mouseover", "RightClick", "popUpWidnow", "Iframe", "age_of_domain", "DNSRecord",
    "web_traffic", "Page_Rank", "Google_Index", "Links_pointing_to_page", "Statistical_report",
    "Request_URL_part_0"
]

class EnhancedPhishingDetector(QWidget):
    def __init__(self, url=None):
        super().__init__()
        self.predefined_url = url
        self.dark_mode = False
        self.initUI()
        self.apply_theme()

        if self.predefined_url:
            QTimer.singleShot(100, self.start_scan)

    def initUI(self):
        self.setWindowTitle("AI Phishing URL Analyzer")
        self.setGeometry(200, 200, 600, 500)
        self.center_window()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header Section
        header = QLabel("Phishing URL Detection System")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        # URL Display Group
        url_group = QGroupBox("Scan Details")
        url_layout = QVBoxLayout()
        
        self.url_label = QLabel(f"<b>Target URL:</b> {self.predefined_url or 'Not specified'}")
        self.url_label.setWordWrap(True)
        url_layout.addWidget(self.url_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(False)
        url_layout.addWidget(self.progress)

        url_group.setLayout(url_layout)
        main_layout.addWidget(url_group)

        # Results Group
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout()
        
        self.result_header = QLabel("Result: Scanning...")
        self.result_header.setFont(QFont("Arial", 12, QFont.Bold))
        results_layout.addWidget(self.result_header)

        self.confidence_label = QLabel("Confidence: Calculating...")
        results_layout.addWidget(self.confidence_label)

        self.detail_label = QLabel("Feature Analysis:")
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        results_layout.addWidget(self.detail_label)
        results_layout.addWidget(self.detail_text)

        self.ai_reason_label = QLabel("AI Threat Assessment:")
        self.ai_reason_text = QTextEdit()
        self.ai_reason_text.setReadOnly(True)
        results_layout.addWidget(self.ai_reason_label)
        results_layout.addWidget(self.ai_reason_text)

        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)

        self.setLayout(main_layout)

    def start_scan(self):
        self.progress.setValue(0)
        QTimer.singleShot(100, self.perform_analysis)

    def perform_analysis(self):
        try:
            self.progress.setValue(30)
            url = self.predefined_url.strip()
            features = extract_features(url)
            dmatrix = xgb.DMatrix(features, feature_names=feature_names)
            prediction = model.predict(dmatrix)[0]
            confidence = round(prediction * 100, 2)

            self.progress.setValue(60)
            feature_analysis = self.get_feature_analysis(features[0])
            ai_reason = self.generate_ai_reason(url, prediction, feature_analysis)

            self.progress.setValue(90)
            self.display_results(confidence, feature_analysis, ai_reason)
            self.progress.setValue(100)

        except Exception as e:
            self.result_header.setText("Error in analysis")
            self.detail_text.setText(str(e))

    def get_feature_analysis(self, features):
        analysis = []
        feature_descriptions = {
            'having_IP_Address': 'Uses IP address instead of domain name',
            'Shortining_Service': 'Uses URL shortening service',
            'having_At_Symbol': 'Contains @ symbol',
            'double_slash_redirecting': 'Contains double slash redirect',
            'Prefix_Suffix': 'Uses hyphens in domain name',
            'having_Sub_Domain': 'Has multiple subdomains',
            'HTTPS_token': 'Contains HTTPS in domain',
            'Iframe': 'Contains iframe reference'
        }
        
        for name, value in zip(feature_names, features):
            if value != 0 and name in feature_descriptions:
                analysis.append(f"• {feature_descriptions[name]}")
        
        return "\n".join(analysis) if analysis else "No strong security indicators detected"

    def generate_ai_reason(self, url, prediction, features):
        try:
            # Check for valid API key structure
            if not client.api_key.startswith("sk-") or len(client.api_key) < 30:
                return self.get_fallback_analysis(prediction, features)
            
            prompt = f"""Analyze this URL for phishing risk: {url}
            Model confidence: {prediction:.2f}
            Key features: {features}
            Provide a professional security assessment in 3-4 bullet points:"""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return self.get_fallback_analysis(prediction, features)

    def get_fallback_analysis(self, prediction, features):
        analysis = []
        risk_level = "High risk" if prediction >= 0.7 else \
                    "Moderate risk" if prediction >= 0.5 else \
                    "Low risk"
        
        analysis.append(f"Automated Security Assessment ({risk_level}):")
        
        if features:
            analysis.append("Key indicators found:")
            analysis.extend(features.split("\n"))
        else:
            analysis.append("No strong security indicators detected")
        
        analysis.append("\nRecommendation: " + 
            ("Avoid visiting this site" if prediction >= 0.5 
            else "Exercise caution when visiting" if prediction >= 0.3 
            else "Likely safe to visit"))
        
        return "\n".join(analysis)

    def display_results(self, confidence, features, ai_reason):
        color = QColor(200, 50, 50) if confidence >= 50 else QColor(50, 150, 50)
        result_text = "Malicious URL" if confidence >= 50 else "Safe URL"
        
        self.result_header.setText(f"Result: {result_text}")
        self.result_header.setStyleSheet(f"color: {color.name()};")
        
        self.confidence_label.setText(f"Confidence Level: {confidence}%")
        self.detail_text.setText(features)
        self.ai_reason_text.setText(ai_reason)

    def center_window(self):
        """Center the window on the screen."""
        screen = QApplication.primaryScreen().geometry()
        window = self.frameGeometry()
        center_point = screen.center()
        window.moveCenter(center_point)
        self.move(window.topLeft())

    def apply_theme(self):
        """Apply dark mode theme based on PhishEye settings."""
        if self.dark_mode:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: white;
                }
                QLabel {
                    color: #ffffff;
                    font-weight: bold;
                }
                QTextEdit {
                    background-color: #3c3f41;
                    color: #ffffff;
                    border: 1px solid #555;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #ffffff;
                    color: black;
                }
                QLabel {
                    color: #000000;
                    font-weight: bold;
                }
                QTextEdit {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #aaa;
                }
            """)

    def scan_url(self):
        """Scan the predefined URL directly without user input."""
        if not self.predefined_url:
            self.result_label.setText("Result: No URL provided.")
            return

        url = self.predefined_url.strip()
        features = extract_features(url)
        print("Extracted Features:", features)
        dmatrix = xgb.DMatrix(features, feature_names=feature_names)
        prediction = model.predict(dmatrix)
        print("Prediction:", prediction)

        # Display result
        if prediction[0] >= 0.5:
            self.result_label.setText("Result: Malicious URL")
            self.reason_text.setText("Reasons:\n- Suspicious patterns detected.\n- Review URL structure and content.")
        else:
            self.result_label.setText("Result: Safe URL")
            self.reason_text.setText("Reasons:\n- URL structure appears normal.\n- No alarming patterns detected.")

    # Rest of existing methods (center_window, apply_theme) remain similar...
    # Feature extraction function and feature_names list remain unchanged...

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    url_argument = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--url" else None
    window = EnhancedPhishingDetector(url_argument)
    window.show()
    sys.exit(app.exec_())
    