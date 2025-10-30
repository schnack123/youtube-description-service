"""Input validation utilities"""
from typing import Dict, Any, Optional


def validate_generate_request(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate generate-descriptions request data.
    
    Args:
        data: Request JSON data
        
    Returns:
        (is_valid, error_message)
    """
    required_fields = ['novel_name', 'novel_context', 'playlist_url']
    
    for field in required_fields:
        if not data.get(field):
            return False, f"Missing required field: {field}"
    
    # Validate novel_name (no special characters in S3 path)
    novel_name = data['novel_name']
    if not novel_name or '/' in novel_name or '\\' in novel_name:
        return False, "Invalid novel_name: must not contain path separators"
    
    # Validate playlist_url format
    playlist_url = data['playlist_url']
    if not playlist_url.startswith('http'):
        return False, "Invalid playlist_url: must be a valid URL"
    
    # Validate novel_context length
    if len(data['novel_context']) > 5000:
        return False, "novel_context too long: maximum 5000 characters"
    
    # subscribe_text is now optional (AI generates it)
    # If provided, validate it (for backward compatibility or override)
    if 'subscribe_text' in data and data['subscribe_text']:
        if len(data['subscribe_text']) > 1000:
            return False, "subscribe_text too long: maximum 1000 characters"
    
    return True, None


def validate_prompt_update(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate prompt update request data.
    
    Args:
        data: Request JSON data
        
    Returns:
        (is_valid, error_message)
    """
    if 'prompt_text' not in data:
        return False, "Missing required field: prompt_text"
    
    if not data['prompt_text'] or not data['prompt_text'].strip():
        return False, "prompt_text cannot be empty"
    
    if len(data['prompt_text']) > 10000:
        return False, "prompt_text too long: maximum 10000 characters"
    
    return True, None

