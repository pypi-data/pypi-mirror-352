# pgstudio/utils.py

import os
import json
import uuid
import logging
import subprocess
import platform

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def ensure_folder(path: str):
    """make sure a folder exists (create if missing)."""
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)

def load_json(path: str):
    """load JSON from file, return None if not exists or invalid."""
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.warning(f"couldn't load JSON from {path}: {e}")
        return None

def save_json(path: str, data):
    """save data (list/dict) as pretty JSON to file."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logging.error(f"couldn't save JSON to {path}: {e}")

def sanitize_name(name: str):
    """strip whitespace, replace spaces with underscores, remove weird chars."""
    clean = name.strip().replace(" ", "_")
    return "".join(ch for ch in clean if ch.isalnum() or ch in "_-")

def gen_id() -> str:
    """generate a short unique id."""
    return uuid.uuid4().hex

def open_in_editor(filepath: str):
    """
    open a file in the default system editor.
    works on Windows/Mac/Linux.
    """
    try:
        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(("open", filepath))
        else:  # assume linux
            subprocess.call(("xdg-open", filepath))
    except Exception as e:
        logging.error(f"error opening file {filepath} in editor: {e}")
