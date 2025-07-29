"""
Utility helper functions
"""

import re
import os
from typing import List, Optional
from pathlib import Path


def format_app_name(name: str) -> str:
    """
    Format app name for display
    
    Args:
        name: Raw app name
        
    Returns:
        Formatted app name
    """
    if not name:
        return "Unknown App"
    
    # Remove extra whitespace
    formatted = " ".join(name.split())
    
    # Capitalize first letter if all lowercase
    if formatted.islower():
        formatted = formatted.title()
    
    return formatted


def clean_filename(filename: str) -> str:
    """
    Clean filename for filesystem compatibility
    
    Args:
        filename: Raw filename
        
    Returns:
        Clean filename safe for filesystem
    """
    # Remove or replace invalid characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    cleaned = cleaned.strip(' .')
    
    # Replace multiple underscores with single
    cleaned = re.sub(r'_+', '_', cleaned)
    
    # Limit length
    if len(cleaned) > 100:
        name, ext = os.path.splitext(cleaned)
        cleaned = name[:100-len(ext)] + ext
    
    return cleaned or "file"


def validate_icon_size(size: int) -> bool:
    """
    Validate if icon size is supported
    
    Args:
        size: Icon size in pixels
        
    Returns:
        True if size is valid
    """
    VALID_SIZES = [16, 32, 48, 64, 128, 256, 512, 1024]
    return size in VALID_SIZES


def validate_icon_sizes(sizes: List[int]) -> List[int]:
    """
    Validate and filter list of icon sizes
    
    Args:
        sizes: List of icon sizes
        
    Returns:
        List of valid icon sizes
    """
    return [size for size in sizes if validate_icon_size(size)]


def validate_store_name(store: str) -> bool:
    """
    Validate store name
    
    Args:
        store: Store identifier
        
    Returns:
        True if store is valid
    """
    VALID_STORES = ["appstore", "googleplay", "both"]
    return store.lower() in VALID_STORES


def validate_country_code(country: str) -> bool:
    """
    Validate country code (basic validation)
    
    Args:
        country: Two-letter country code
        
    Returns:
        True if country code appears valid
    """
    return len(country) == 2 and country.isalpha()


def ensure_directory(path: str) -> Path:
    """
    Ensure directory exists, create if necessary
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Truncate text to specified length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def format_price(price: str) -> str:
    """
    Format price string consistently
    
    Args:
        price: Raw price string
        
    Returns:
        Formatted price
    """
    if not price or price.lower() in ['free', '0', '0.00']:
        return "Free"
    
    # Handle different price formats
    price = price.strip()
    if price.startswith('$'):
        return price
    elif price.replace('.', '').replace(',', '').isdigit():
        return f"${price}"
    else:
        return price


def format_rating(rating: Optional[float]) -> str:
    """
    Format app rating for display
    
    Args:
        rating: Rating value
        
    Returns:
        Formatted rating string
    """
    if rating is None:
        return "No rating"
    
    try:
        rating_float = float(rating)
        if 0 <= rating_float <= 5:
            return f"{rating_float:.1f}/5.0"
        else:
            return "Invalid rating"
    except (ValueError, TypeError):
        return "No rating"


def extract_bundle_id_from_url(url: str) -> Optional[str]:
    """
    Extract bundle ID from App Store URL
    
    Args:
        url: App Store URL
        
    Returns:
        Bundle ID if found
    """
    # Pattern for App Store URLs: https://apps.apple.com/app/id123456789
    import re
    pattern = r'/id(\d+)'
    match = re.search(pattern, url)
    return match.group(1) if match else None
