import requests
import os
from typing import Optional, Dict, Any

class APIClient:
    """HTTP client calling FastAPI Backend (backend1)"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.user: Optional[Dict] = None
        self.role: Optional[str] = None

    def set_auth(self, token: str, user: Dict, role: str):
        self.token = token
        self.user = user
        self.role = role

    def clear_auth(self):
        self.token = None
        self.user = None
        self.role = None

    def get_headers(self) -> Dict:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def login(self, role: str, username: str, password: str) -> Dict:
        """Special login handler for FastAPI OAuth2 Form Data"""
        url = f"{self.base_url}/auth/login/{role}"
        try:
            # FastAPI OAuth2PasswordRequestForm expects data as form-data
            data = {"username": username, "password": password}
            response = requests.post(url, data=data, timeout=10)
            token_data = response.json()
            
            if response.status_code == 200:
                # Map 'access_token' to 'token' for internal consistency
                self.set_auth(
                    token_data.get("access_token"),
                    token_data.get("user"),
                    token_data.get("role")
                )
                return {
                    "success": True,
                    "token": self.token,
                    "user": self.user,
                    "role": self.role
                }
            else:
                return {
                    "success": False,
                    "error": token_data.get("error", "Unauthorized"),
                    "message": token_data.get("detail", token_data.get("error", "Đăng nhập thất bại"))
                }
        except Exception as e:
            return {"success": False, "error": "Connection Error", "message": str(e)}

    def get(self, endpoint: str) -> Dict:
        try:
            url = f"{self.base_url}{endpoint}"
            print(f"DEBUG_API: Calling GET {url}")
            response = requests.get(url, headers=self.get_headers(), timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def post(self, endpoint: str, data: Dict = None) -> Dict:
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.post(url, json=data or {}, headers=self.get_headers(), timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def put(self, endpoint: str, data: Dict) -> Dict:
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.put(url, json=data, headers=self.get_headers(), timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def delete(self, endpoint: str) -> Dict:
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.delete(url, headers=self.get_headers(), timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# Global instance
api = APIClient()
