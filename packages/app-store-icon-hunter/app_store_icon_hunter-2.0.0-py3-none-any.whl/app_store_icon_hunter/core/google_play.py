"""
Google Play Store API integration via SerpApi
"""

import requests
import os
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class GooglePlayAPI:
    """Interface for Google Play Store via SerpApi"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        self.base_url = "https://serpapi.com/search"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'App-Store-Icon-Hunter/2.0'
        })
    
    def search_apps(self, term: str, country: str = "us", limit: int = 10) -> List[Dict]:
        """
        Search for apps in Google Play Store
        
        Args:
            term: Search term
            country: Country code (default: "us")
            limit: Maximum number of results (default: 10)
            
        Returns:
            List of app dictionaries with standardized format
        """
        if not self.api_key:
            logger.warning("Google Play search requires SerpApi key. Set SERPAPI_KEY environment variable.")
            return []
        
        params = {
            "engine": "google_play",
            "q": term,
            "gl": country,
            "num": limit,
            "api_key": self.api_key
        }
        
        try:
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Standardize the format
            apps = []
            for result in data.get("organic_results", []):
                app = {
                    "name": result.get("title", ""),
                    "bundle_id": result.get("product_id", ""),
                    "icon_url": result.get("thumbnail", ""),
                    "store": "googleplay",
                    "price": result.get("price", "Free"),
                    "rating": result.get("rating"),
                    "description": result.get("description", ""),
                    "developer": result.get("developer", ""),
                    "category": result.get("genre", ""),
                    "url": result.get("link", "")
                }
                apps.append(app)
            
            return apps
            
        except requests.RequestException as e:
            logger.error(f"Error searching Google Play: {e}")
            return []
    
    def get_app_details(self, app_id: str, country: str = "us") -> Optional[Dict]:
        """
        Get detailed information about a specific app by ID
        
        Args:
            app_id: Google Play app ID
            country: Country code
            
        Returns:
            App details dictionary or None if not found
        """
        if not self.api_key:
            logger.warning("Google Play details require SerpApi key.")
            return None
        
        params = {
            "engine": "google_play_product",
            "product_id": app_id,
            "gl": country,
            "api_key": self.api_key
        }
        
        try:
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return data.get("product_result", {})
            
        except requests.RequestException as e:
            logger.error(f"Error getting Google Play app details: {e}")
            return None
