import os

def ensure_directory(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory, mode=0o755, exist_ok=True)

def ensure_directory_for_file(file):
    d = os.path.dirname(file)
    ensure_directory(d)
