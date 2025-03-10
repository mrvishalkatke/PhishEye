import sys
import xgboost as xgb
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from PyQt5.QtCore import Qt
import re

# Load the XGBoost model using its native JSON format
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

class PhishingURLDetector(QWidget):
    def __init__(self, url=None):
        super().__init__()
        # If a URL is provided, store it and later set it as read-only
        self.predefined_url = url
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Phishing URL Detector")
        self.setGeometry(200, 200, 400, 300)
        layout = QVBoxLayout()
        # Address Field: pre-fill if a URL is provided
        self.url_input = QLineEdit(self)
        if self.predefined_url:
            self.url_input.setText(self.predefined_url)
            self.url_input.setReadOnly(True)
        else:
            self.url_input.setPlaceholderText("Enter URL here...")
        layout.addWidget(self.url_input)
        # Button to check URL
        self.scan_button = QPushButton("Check if Malicious", self)
        self.scan_button.clicked.connect(self.scan_url)
        layout.addWidget(self.scan_button)
        # Result Label
        self.result_label = QLabel("Result: ", self)
        layout.addWidget(self.result_label)
        # Reason Text
        self.reason_text = QTextEdit(self)
        self.reason_text.setReadOnly(True)
        layout.addWidget(self.reason_text)
        self.setLayout(layout)

    def scan_url(self):
        # Use the URL from the input field (which may be prepopulated and read-only)
        url = self.url_input.text().strip()
        if not url:
            self.result_label.setText("Result: Please enter a valid URL.")
            return
        features = extract_features(url)
        print("Extracted Features:", features)
        dmatrix = xgb.DMatrix(features, feature_names=feature_names)
        prediction = model.predict(dmatrix)
        print("Prediction:", prediction)
        # Assuming binary classification with threshold 0.5
        if prediction[0] >= 0.5:
            self.result_label.setText("Result: Malicious URL")
            self.reason_text.setText("Reasons:\n- Suspicious patterns detected based on extracted features.\n- Review URL structure and content.")
        else:
            self.result_label.setText("Result: Safe URL")
            self.reason_text.setText("Reasons:\n- URL structure appears normal.\n- No alarming patterns detected.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # If you want to pass a URL directly, you can do so here:
    # e.g., window = PhishingURLDetector("https://example.com")
    window = PhishingURLDetector()  # or provide a URL as an argument
    window.show()
    sys.exit(app.exec_())
