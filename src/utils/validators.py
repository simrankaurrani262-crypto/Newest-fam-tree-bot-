"""
Validation Utilities
"""
import re
from decimal import Decimal
from typing import Optional, Tuple


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Telegram username
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "Username cannot be empty"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 32:
        return False, "Username cannot exceed 32 characters"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, None


def validate_amount(amount_str: str) -> Tuple[bool, Optional[Decimal], Optional[str]]:
    """
    Validate and parse amount string
    
    Returns:
        Tuple of (is_valid, amount, error_message)
    """
    try:
        # Handle simple math expressions
        amount = Decimal(str(eval(amount_str)))
        
        if amount <= 0:
            return False, None, "Amount must be positive"
        
        return True, amount, None
        
    except:
        return False, None, "Invalid amount"


def validate_crop_type(crop_type: str, valid_crops: list) -> Tuple[bool, Optional[str]]:
    """
    Validate crop type
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if crop_type.lower() not in [c.lower() for c in valid_crops]:
        return False, f"Invalid crop type. Valid: {', '.join(valid_crops)}"
    
    return True, None


def validate_plot_number(plot_num: int, max_plots: int) -> Tuple[bool, Optional[str]]:
    """
    Validate plot number
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if plot_num < 1 or plot_num > max_plots:
        return False, f"Plot number must be between 1 and {max_plots}"
    
    return True, None
