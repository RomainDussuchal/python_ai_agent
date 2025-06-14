# security.py

import os
from config import RESTRICTED_PATHS



def is_path_within(base_path: str, target_path: str) -> bool:
    abs_base = os.path.abspath(base_path)
    abs_target = os.path.abspath(target_path)
    return abs_target.startswith(abs_base)

def is_path_restricted(file_path: str, restricted_paths=RESTRICTED_PATHS) -> bool:
    parts = os.path.normpath(file_path).split(os.sep)
    return any(part in restricted_paths for part in parts)

def validate_access(working_directory: str, file_path: str, require_file=True) -> str | None:
    """
    Returns an error message string if access should be blocked.
    Otherwise returns None.
    """
    abs_working_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

    if not is_path_within(abs_working_dir, abs_file_path):
        return f'Error: "{file_path}" is outside the permitted working directory'

    if is_path_restricted(file_path):
        return f'Error: Access to "{file_path}" is restricted'

    if require_file and not os.path.isfile(abs_file_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    return None  # ✅ All good
