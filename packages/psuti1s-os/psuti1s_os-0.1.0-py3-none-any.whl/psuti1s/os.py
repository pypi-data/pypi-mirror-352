"""
psuti1s.os
---------
This module contains some helper functions OS-related functionality.
"""

import os

def list_files(path):
    """List all files in the given directory."""
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def get_file_size(filepath):
    """Return the size of a file in bytes."""
    return os.path.getsize(filepath)
