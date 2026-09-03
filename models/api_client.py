# models/api_client.py - HTTP Client for FastAPI Backend

import requests
import os
import time
import hashlib

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")


class ApiClient:
    """Centralized HTTP client for communicating with the FastAPI backend."""

    _instance = None
    _api_key = None
    _username = None
    _user_id = None
    _role = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.session = requests.Session()
            cls._instance.session.headers.update({"Content-Type": "application/json"})
        return cls._instance

    def set_api_key(self, api_key, user_id=None, username=None, role=None):
        self._api_key = api_key
        self._user_id = user_id
        self._username = username
        self._role = role
        self.session.headers["X-API-Key"] = api_key

    def clear_api_key(self):
        self._api_key = None
        self._user_id = None
        self._username = None
        self._role = None
        self.session.headers.pop("X-API-Key", None)

    def login(self, username, password):
        """Login and store API key."""
        try:
            resp = self.session.post(
                f"{API_BASE_URL}/auth/login",
                json={"username": username, "password": password},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                self.set_api_key(
                    data["api_key"],
                    user_id=data["id"],
                    username=data["username"],
                    role=data["role"],
                )
                return data
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ API login error: {e}")
            return None

    def logout(self):
        try:
            self.session.post(f"{API_BASE_URL}/auth/logout", timeout=10)
        except:
            pass
        self.clear_api_key()

    def get(self, path, params=None):
        try:
            resp = self.session.get(f"{API_BASE_URL}{path}", params=params, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            print(f"❌ GET {path} failed: {resp.status_code} - {resp.text[:200]}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ API GET error ({path}): {e}")
            return None

    def post(self, path, data=None):
        try:
            resp = self.session.post(f"{API_BASE_URL}{path}", json=data, timeout=30)
            if resp.status_code in (200, 201):
                return resp.json()
            print(f"❌ POST {path} failed: {resp.status_code} - {resp.text[:200]}")
            return {"error": resp.text}
        except requests.exceptions.RequestException as e:
            print(f"❌ API POST error ({path}): {e}")
            return None

    def put(self, path, data=None, params=None):
        try:
            resp = self.session.put(
                f"{API_BASE_URL}{path}", json=data, params=params, timeout=30
            )
            if resp.status_code == 200:
                return resp.json()
            print(f"❌ PUT {path} failed: {resp.status_code} - {resp.text[:200]}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ API PUT error ({path}): {e}")
            return None

    def delete(self, path):
        try:
            resp = self.session.delete(f"{API_BASE_URL}{path}", timeout=30)
            if resp.status_code == 200:
                return resp.json()
            print(f"❌ DELETE {path} failed: {resp.status_code} - {resp.text[:200]}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ API DELETE error ({path}): {e}")
            return None


# Singleton instance
api = ApiClient()
