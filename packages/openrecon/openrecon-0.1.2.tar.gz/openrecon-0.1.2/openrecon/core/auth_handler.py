import requests
from typing import Dict
import logging

class AuthHandler:
    def __init__(self, session: requests.Session):
        self.session = session
        self.logger = logging.getLogger(__name__)

    def set_auth(self, auth_type: str, auth_data: Dict):
        if auth_type == "basic":
            self.session.auth = (auth_data.get("username"), auth_data.get("password"))
            self.logger.info("Basic authentication configured")
            
        elif auth_type == "bearer":
            token = auth_data.get("token")
            if not token:
                token = self._refresh_bearer_token(auth_data)
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            self.logger.info("Bearer token authentication configured")
            
        elif auth_type == "apikey":
            header_name = auth_data.get("header_name", "X-API-Key")
            self.session.headers.update({header_name: auth_data.get("key")})
            self.logger.info("API key authentication configured")
            
        elif auth_type == "oauth2":
            token = auth_data.get('access_token')
            if not token:
                token = self._get_oauth_token(
                    auth_data.get('auth_url'),
                    auth_data.get('client_id'),
                    auth_data.get('client_secret')
                )
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            self.logger.info("OAuth2 authentication configured")
            
        elif auth_type == "jwt":
            token = auth_data.get('token')
            if not token:
                token = self._get_jwt_token(
                    auth_data.get('auth_url'),
                    auth_data.get('credentials')
                )
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            self.logger.info("JWT authentication configured")
            
        elif auth_type == "custom":
            auth_func = auth_data.get('auth_func')
            if auth_func and callable(auth_func):
                auth_func(self.session, **auth_data)
                self.logger.info("Custom authentication configured")
            else:
                raise ValueError("Custom authentication requires an auth_func")
        else:
            raise ValueError(f"Unsupported auth type: {auth_type}")

    def _refresh_bearer_token(self, auth_data: Dict) -> str:
        """Refresh a bearer token if it's expired"""
        refresh_url = auth_data.get('refresh_url')
        refresh_token = auth_data.get('refresh_token')
        
        if not refresh_url or not refresh_token:
            raise ValueError("Refresh URL and token required for token refresh")
            
        response = self.session.post(
            refresh_url,
            data={'refresh_token': refresh_token}
        )
        
        if response.status_code == 200:
            return response.json().get('access_token')
        raise ValueError("Failed to refresh bearer token")

    def _get_jwt_token(self, auth_url: str, credentials: Dict) -> str:
        """Get a JWT token from the authentication endpoint"""
        response = self.session.post(auth_url, json=credentials)
        
        if response.status_code == 200:
            return response.json().get('token')
        raise ValueError("Failed to get JWT token")

    def _get_oauth_token(self, auth_url: str, client_id: str, client_secret: str) -> str:
        """Get an OAuth2 token using client credentials flow"""
        response = self.session.post(
            auth_url,
            data={
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret
            }
        )
        
        if response.status_code == 200:
            return response.json().get('access_token')
        raise ValueError("Failed to get OAuth2 token") 