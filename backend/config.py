"""Application configuration."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

POCS_DIR = BASE_DIR / "pocs"
PRESET_POCS_DIR = POCS_DIR / "preset"
CUSTOM_POCS_DIR = POCS_DIR / "custom"

RULES_DIR = BASE_DIR / "rules"
PRESET_RULES_DIR = RULES_DIR / "preset"
CUSTOM_RULES_DIR = RULES_DIR / "custom"

EVE_LOG = os.environ.get("EVE_LOG", "/var/log/suricata/eve.json")

JUICE_SHOP_URL = os.environ.get("JUICE_SHOP_URL", "http://juice-shop:3000")
SSH_HOST = os.environ.get("SSH_HOST", "ssh-server")
SSH_PORT = int(os.environ.get("SSH_PORT", "2222"))
FTP_HOST = os.environ.get("FTP_HOST", "ftp-server")
FTP_PORT = int(os.environ.get("FTP_PORT", "21"))
INTERNAL_API_URL = os.environ.get("INTERNAL_API_URL", "http://internal-api:5000")
INTERNAL_DB_HOST = os.environ.get("INTERNAL_DB_HOST", "internal-db")
INTERNAL_DB_PORT = int(os.environ.get("INTERNAL_DB_PORT", "3306"))

SURICATA_RULES_FILE = os.environ.get(
    "SURICATA_RULES_FILE", "/etc/suricata/rules/local.rules"
)

SERVICE_URLS = {
    "juice-shop": JUICE_SHOP_URL,
    "ssh-server": f"tcp://{SSH_HOST}:{SSH_PORT}",
    "ftp-server": f"tcp://{FTP_HOST}:{FTP_PORT}",
    "internal-api": INTERNAL_API_URL,
    "internal-db": f"mysql://{INTERNAL_DB_HOST}:{INTERNAL_DB_PORT}",
}
