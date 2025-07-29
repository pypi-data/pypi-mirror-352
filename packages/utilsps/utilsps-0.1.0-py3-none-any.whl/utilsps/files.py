"""
utilsps.files module: File utilities
"""

import os

def list_all_files(base_path):
    """
    Recursively list all files from base_path.

    Example usage:

    >>> list(list_all_files('/tmp'))
    ['/tmp/file1', '/tmp/dir/file2']

    Args:
        base_path (str): Folder to scan.

    Yields:
        str: Full path to each file found.
    """
    for dirpath, _, filenames in os.walk(base_path):
        for file in filenames:
            yield os.path.join(dirpath, file)
