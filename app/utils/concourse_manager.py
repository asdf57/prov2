import os
import time
import base64
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from app.utils.git import RepoHandler


CONCOURSE_USERNAME = os.getenv("CONCOURSE_USERNAME")
CONCOURSE_PASSWORD = os.getenv("CONCOURSE_PASSWORD")

CONCOURSE_OAUTH_CLIENT_ID = os.getenv("CONCOURSE_OAUTH_CLIENT_ID")
CONCOURSE_OAUTH_CLIENT_SECRET = os.getenv("CONCOURSE_OAUTH_CLIENT_SECRET")

CONCOURSE_URL = os.getenv("CONCOURSE_URL")


"""
Get OAuth token that auto refreshes
"""
class ConcourseManager:
    def __init__(self, concourse_url: str, concourse_username: str, concourse_password: str):
        self.concourse_url = concourse_url
        self.concourse_username = concourse_username
        self.concourse_password = concourse_password

        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None

        self.client_id = CONCOURSE_OAUTH_CLIENT_ID
        self.client_secret = CONCOURSE_OAUTH_CLIENT_SECRET

    def _fetch_new_token(self) -> dict:
        token_url = f"{self.concourse_url}/sky/issuer/token"

        client_auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()

        headers = {
            "Authorization": f"Basic {client_auth}"
        }

        data = {
            "grant_type": "password",
            "username": self.concourse_username,
            "password": self.concourse_password,
            "scope": "openid profile email federated:id groups"
        }

        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()

        return response.json()
    
    def get_token(self) -> str:
        now = datetime.now()

        if self._access_token is None or now >= self._token_expiry:
            token_data = self._fetch_new_token()
            self._access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self._token_expiry = now + timedelta(seconds=expires_in - 300)

        return self._access_token

    def trigger_resource_check(self, team: str, pipeline: str, resource: str) -> dict:
        """
        Trigger a resource check in Concourse.
        
        Example usage:
            manager.trigger_resource_check("main", "commands", "commands")
        """
        token = self.get_token()
        
        url = f"{self.concourse_url}/api/v1/teams/{team}/pipelines/{pipeline}/resources/{resource}/check"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.post(url, headers=headers, json={})
        response.raise_for_status()
        
        return response.json()