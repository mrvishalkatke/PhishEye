# PhishEye: AI-Driven Phishing Analyzer Tool

PhishEye is an AI-driven phishing email detection tool that helps users analyze their emails and detect any malicious links or attachments. The tool alerts the user if any phishing attempts are detected and advises them to delete the phishing email to prevent harm. The system is built using Python and incorporates machine learning to identify suspicious or dangerous emails.

## Features

- **Email Authentication:** Users can log in using their email and password (supports Gmail).
- **Inbox Access:** After logging in, users can view their inbox emails in a list.
- **Phishing Detection:** The tool analyzes emails for malicious links and attachments.
- **Alerts:** If a phishing email is detected, users are notified with an alert to delete it.
- **Multi-tab Interface:** Each email can be opened in a separate tab for detailed inspection.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/mrvishalkatke/PhishEye.git
cd PhishEye
```

### 2. Set up a Python Virtual Environment

Create a virtual environment for the project:

```bash
python3 -m venv phisheyenv
```

Activate the virtual environment:

```bash
source phisheyenv/bin/activate  # On Windows use `phisheyenv\Scripts\activate`
```

### 3. Install dependencies

Install the required libraries

```bash
pip install PyQt5
```

### 4. Run the application

Run the PhishEye tool:

```bash
python main.py
```

## Usage

1. Launch the application and log in with your email and password (Note: For Gmail users, an app password is recommended).
2. After logging in, you will be redirected to your inbox view where you can see the list of emails.
3. The tool will analyze each email for phishing links and attachments.
4. If a malicious email is found, the tool will display an alert asking you to delete the email.
5. You can open any email in a detailed view to examine its content and headers.

## Technologies Used

- **Python 3:** The primary language for building the tool.
- **PyQt5:** For the graphical user interface (GUI).
- **IMAP:** For connecting and fetching emails from the mail server (supports Gmail).
- **Machine Learning:** For detecting phishing content in emails (for future updates).

## Contributing

We welcome contributions to improve **PhishEye**! If you have suggestions, improvements, or bug fixes, feel free to open an issue or submit a pull request.

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature-name`).
6. Open a pull request.

## Acknowledgments

- **PyQt5:** For building the graphical user interface.
- **Python:** For providing the base language for this tool.
- **Gmail IMAP:** For fetching emails from Gmail accounts.
