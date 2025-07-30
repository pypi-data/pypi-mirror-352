import os
from pathlib import Path

ABS_PATH = os.getcwd()
HOME_DIR = os.environ.get("KOZMOCHAIN_CONFIG_DIR", str(Path.home()))
CONFIG_DIR = os.path.join(HOME_DIR, ".kozmochain")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
SQLITE_PATH = os.path.join(CONFIG_DIR, "kozmochain.db")

# Set the environment variable for the database URI
os.environ.setdefault("KOZMOCHAIN_DB_URI", f"sqlite:///{SQLITE_PATH}")
