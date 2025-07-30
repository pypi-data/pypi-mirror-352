"""Gmail utilities."""
import os
import os.path
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def authenticate_gmail(gmail_secrets_file: str) -> Credentials:
    """Get Gmail credentials."""
    creds = None
    gmail_token_file = os.path.join(os.path.dirname(gmail_secrets_file), 'gmail_token')
    if os.path.exists(gmail_token_file):
        creds = Credentials.from_authorized_user_file(gmail_token_file, SCOPES)
    else:
        with open(gmail_token_file, 'w') as f:
            pass
        os.chmod(gmail_token_file, 0o600)
    if not creds or not creds.valid:
        refresh_creds = True
        if creds and creds.expired and creds.refresh_token:
            refresh_creds = False
            try:
                creds.refresh(Request())
            except:
                refresh_creds = True
        if refresh_creds:
            flow = InstalledAppFlow.from_client_secrets_file(gmail_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(gmail_token_file, 'w') as f:
            f.write(creds.to_json())
    return creds


def send_msg(msg: EmailMessage, gmail_secrets_file: str) -> None:
    """Send email message using Gmail API."""
    creds = authenticate_gmail(gmail_secrets_file)
    service = build('gmail', 'v1', credentials=creds)
    service.users().messages().send(userId='me', body={'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}).execute()
