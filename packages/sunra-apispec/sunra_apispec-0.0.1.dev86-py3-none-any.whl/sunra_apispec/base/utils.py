import os
import mimetypes
from urllib.parse import urlparse, unquote
from typing import Tuple


def get_url_extension_and_content_type(url: str) -> Tuple[str, str]:
    """
    Extract file extension and corresponding content_type from a URL
    
    Args:
        url (str): The URL to parse
        
    Returns:
        Tuple[str, str]: (extension, content_type)
            - extension: File extension (including dot, e.g., '.jpg')
            - content_type: MIME type (e.g., 'image/jpeg')
    
    Examples:
        >>> get_url_extension_and_content_type("https://example.com/image.jpg")
        ('.jpg', 'image/jpeg')
        
        >>> get_url_extension_and_content_type("https://example.com/video.mp4")
        ('.mp4', 'video/mp4')
        
        >>> get_url_extension_and_content_type("https://example.com/file")
        (None, None)
    """
    try:
        # Parse the URL
        parsed_url = urlparse(url)
        # URL decode the path part
        path = unquote(parsed_url.path)
        
        # Extract filename
        filename = os.path.basename(path)
        
        # Get file extension
        _, extension = os.path.splitext(filename)
        
        # If no extension, return None
        if not extension:
            return None, None
        
        # Guess content_type based on extension
        content_type, _ = mimetypes.guess_type(filename)
        
        return extension, content_type
        
    except Exception:
        raise ValueError(f"Failed to parse file {url}")

