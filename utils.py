"""
Utility functions for Chess.com Helper
"""

import os
import sys
import platform
from typing import Optional


def get_platform_info() -> dict:
    """Get platform information"""
    return {
        "system": platform.system(),
        "machine": platform.machine(),
        "python_version": sys.version,
    }


def find_executable(name: str) -> Optional[str]:
    """Find executable in PATH or common locations"""
    import shutil
    
    # Try PATH first
    path = shutil.which(name)
    if path:
        return path
    
    # Platform-specific common locations
    common_paths = []
    
    if platform.system() == "Darwin":  # macOS
        common_paths.extend([
            f"/usr/local/bin/{name}",
            f"/opt/homebrew/bin/{name}",
            f"/Applications/{name.title()}.app/Contents/MacOS/{name}",
        ])
    elif platform.system() == "Linux":
        common_paths.extend([
            f"/usr/bin/{name}",
            f"/usr/local/bin/{name}",
            f"/snap/bin/{name}",
        ])
    elif platform.system() == "Windows":
        common_paths.extend([
            f"C:\\Program Files\\{name.title()}\\{name}.exe",
            f"C:\\Program Files (x86)\\{name.title()}\\{name}.exe",
        ])
    
    for path in common_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    
    return None


def format_time(seconds: float) -> str:
    """Format time in a human-readable way"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"


def format_score(score) -> str:
    """Format chess engine score"""
    if not score:
        return "N/A"
    
    if score.is_mate():
        mate_in = score.mate()
        if mate_in > 0:
            return f"Mate in {mate_in}"
        else:
            return f"Mate in {abs(mate_in)} (opponent)"
    else:
        cp_score = score.score()
        if cp_score is None:
            return "N/A"
        return f"{cp_score/100.0:+.2f}"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."