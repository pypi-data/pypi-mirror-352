import pickle
import os
from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


google_services = {
    "sheets": {
        "scopes": ["https://www.googleapis.com/auth/spreadsheets"],
        "versions": "v4",
    },
    "gmail": {
        "scopes": ["https://mail.google.com/"],
        "versions": "v1",
    },
    "drive": {
        "scopes": ["https://www.googleapis.com/auth/drive"],
        "versions": "v3",
    },
    "slides": {
        "scopes": ["https://www.googleapis.com/auth/presentations"],
        "versions": "v1",
    },
}


class GoogleAuthentication:
    def __init__(self, service_type: str):
        """
        get google credentials
        :param service_type: 'sheets', 'gmail or 'drive' services
        :return: google credential
        """
        # check if the service is valid
        creds = None
        service_info = google_services[service_type]
        scopes, version = service_info["scopes"], service_info["versions"]

        # check if the json file exists
        json_path = Path(os.getenv("CRED_GG_API"))
        if not json_path.exists():
            raise Exception(
                "Set your 'client_secret.json' file path to CRED_GG_API env"
            )

        # check if the token file exists
        token_dir = json_path.parent / "token"
        token_file = token_dir / f"token_{service_type}.pickle"
        token_dir.mkdir(parents=True, exist_ok=True)
        if token_file.exists():
            with open(token_file, "rb") as f:
                creds = pickle.load(f)

        # if the token is not valid, get a new one
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(json_path), scopes)
                creds = flow.run_local_server(port=0, open_browser=False)

            # save the token
            with open(token_file, "wb") as f:
                pickle.dump(creds, f)
        self.service = build(service_type, version, credentials=creds)
