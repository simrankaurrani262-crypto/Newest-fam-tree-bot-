"""
Formatting Utilities
"""
from decimal import Decimal
from datetime import datetime, timedelta


def format_money(amount: Decimal, currency: str = "$") -> str:
    """Format money amount"""
    return f"{currency}{amount:,.0f}"


def format_time(seconds: int) -> str:
    """Format time duration"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m"
    elif seconds < 86400:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours}h {mins}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"


def format_datetime(dt: datetime) -> str:
    """Format datetime"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_relative_time(dt: datetime) -> str:
    """Format relative time (e.g., '2 hours ago')"""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff < timedelta(minutes=1):
        return "just now"
    elif diff < timedelta(hours=1):
        mins = int(diff.total_seconds() // 60)
        return f"{mins} minute{'s' if mins > 1 else ''} ago"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() // 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    else:
        days = diff.days
        return f"{days} day{'s' if days > 1 else ''} ago"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
