"""
API communication utilities.
"""
import os
import requests

DEFAULT_API_URL = "https://tag-factory.vercel.app/api/cli/"

def join_url(base: str, *paths: str) -> str:
    """
    base와 여러 path를 슬래시(/) 중복 없이 안전하게 이어붙임
    예: join_url("http://localhost:9987/api", "cli", "upload") → "http://localhost:9987/api/cli/upload"
    """
    from urllib.parse import urlparse, urlunparse

    # base에서 scheme, netloc, path만 분리
    parsed = urlparse(base)
    base_path = parsed.path.rstrip('/')

    # 나머지 path들 정리
    clean_paths = [p.strip('/') for p in paths]
    full_path = '/'.join([base_path] + clean_paths)

    # 새 URL 구성
    new_parsed = parsed._replace(path=full_path)
    return urlunparse(new_parsed)


class APIClient:
    """API client for Tag Factory."""

    def __init__(self):
        """Initialize API client using environment variables."""
        self.api_key = os.environ.get("TAG_FACTORY_API_KEY")
        self.api_url = os.environ.get("TAG_FACTORY_API_URL", DEFAULT_API_URL)

        if not self.api_key:
            raise ValueError("API key is required. Set TAG_FACTORY_API_KEY environment variable.")

    def _get_headers(self):
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def get(self, path, params=None):
        """Send GET request to API.
        
        Args:
            path: API path
            params: Request parameters
            
        Returns:
            Response data
        """
        url = join_url(self.api_url, path)
        response = requests.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()
        return response.json()

    def post(self, path, data):
        """Send POST request to API.
        
        Args:
            path: API path
            data: Request data
            
        Returns:
            Response data
        """
        url = join_url(self.api_url, path)
        response = requests.post(url, headers=self._get_headers(), json=data)
        response.raise_for_status()
        return response.json()
