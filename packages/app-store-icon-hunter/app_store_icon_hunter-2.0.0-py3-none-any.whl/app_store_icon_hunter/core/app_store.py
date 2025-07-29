"""
App Store API integration using iTunes Search API
"""

import requests
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class AppStoreAPI:
    """Interface for iTunes Search API"""
    
    BASE_URL = "https://itunes.apple.com/search"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'App-Store-Icon-Hunter/2.0'
        })
    
    def search_apps(self, term: str, country: str = "us", limit: int = 10) -> List[Dict]:
        """
        Search for apps in the App Store using iTunes Search API
        
        Args:
            term: Search term
            country: Country code (default: "us")
            limit: Maximum number of results (default: 10)
            
        Returns:
            List of app dictionaries with standardized format
        """
        params = {
            "term": term,
            "media": "software",
            "entity": "software", 
            "country": country,
            "limit": limit
        }
        
        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Standardize the format
            apps = []
            for result in data.get("results", []):
                app = {
                    "name": result.get("trackName", ""),
                    "bundle_id": result.get("bundleId", ""),
                    "icon_url": self._get_best_icon_url(result),
                    "store": "appstore",
                    "price": result.get("formattedPrice", "Free"),
                    "rating": result.get("averageUserRating"),
                    "description": result.get("description", ""),
                    "developer": result.get("artistName", ""),
                    "category": result.get("primaryGenreName", ""),
                    "url": result.get("trackViewUrl", "")
                }
                apps.append(app)
            
            return apps
            
        except requests.RequestException as e:
            logger.error(f"Error searching App Store: {e}")
            return []
    
    def _get_best_icon_url(self, result: Dict) -> str:
        """Extract the best quality icon URL from iTunes result"""
        # iTunes provides artworkUrl60, artworkUrl100, artworkUrl512
        icon_url = (
            result.get("artworkUrl512") or 
            result.get("artworkUrl100") or 
            result.get("artworkUrl60") or 
            ""
        )
        
        # Try to get higher resolution by modifying URL
        if icon_url and "100x100" in icon_url:
            icon_url = icon_url.replace("100x100", "512x512")
        elif icon_url and "60x60" in icon_url:
            icon_url = icon_url.replace("60x60", "512x512")
            
        return icon_url
    
    def get_app_details(self, bundle_id: str, country: str = "us") -> Optional[Dict]:
        """
        Get detailed information about a specific app by bundle ID
        
        Args:
            bundle_id: App bundle identifier
            country: Country code
            
        Returns:
            App details dictionary or None if not found
        """
        params = {
            "bundleId": bundle_id,
            "media": "software",
            "entity": "software",
            "country": country,
            "limit": 1
        }
        
        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results", [])
            if results:
                return results[0]
            return None
            
        except requests.RequestException as e:
            logger.error(f"Error getting app details: {e}")
            return None
