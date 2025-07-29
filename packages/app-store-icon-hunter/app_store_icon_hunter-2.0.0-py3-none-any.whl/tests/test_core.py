"""
Tests for core functionality
"""

import pytest
from app_store_icon_hunter.core.app_store import AppStoreAPI
from app_store_icon_hunter.core.google_play import GooglePlayAPI
from app_store_icon_hunter.utils.helpers import (
    validate_icon_size, validate_store_name, clean_filename, format_app_name
)


class TestAppStoreAPI:
    """Test App Store API functionality"""
    
    def test_init(self):
        """Test API initialization"""
        api = AppStoreAPI()
        assert api.BASE_URL == "https://itunes.apple.com/search"
        assert hasattr(api, 'session')
    
    def test_search_apps_empty_term(self):
        """Test search with empty term"""
        api = AppStoreAPI()
        results = api.search_apps("")
        # Should return empty list for empty search term
        assert isinstance(results, list)


class TestGooglePlayAPI:
    """Test Google Play API functionality"""
    
    def test_init_without_key(self):
        """Test initialization without API key"""
        api = GooglePlayAPI()
        assert api.api_key is None
    
    def test_init_with_key(self):
        """Test initialization with API key"""
        api = GooglePlayAPI("test_key")
        assert api.api_key == "test_key"


class TestUtilityFunctions:
    """Test utility helper functions"""
    
    def test_validate_icon_size(self):
        """Test icon size validation"""
        assert validate_icon_size(64) is True
        assert validate_icon_size(128) is True
        assert validate_icon_size(999) is False
        assert validate_icon_size(0) is False
    
    def test_validate_store_name(self):
        """Test store name validation"""
        assert validate_store_name("appstore") is True
        assert validate_store_name("googleplay") is True
        assert validate_store_name("both") is True
        assert validate_store_name("invalid") is False
    
    def test_clean_filename(self):
        """Test filename cleaning"""
        assert clean_filename("Test App") == "Test App"
        assert clean_filename("Test/App") == "Test_App"
        assert clean_filename("Test:App*") == "Test_App_"
        assert "..." not in clean_filename("A" * 200)  # Should be truncated
    
    def test_format_app_name(self):
        """Test app name formatting"""
        assert format_app_name("test app") == "Test App"
        assert format_app_name("TEST APP") == "TEST APP"
        assert format_app_name("") == "Unknown App"
        assert format_app_name("  spaced  ") == "Spaced"


if __name__ == "__main__":
    pytest.main([__file__])
