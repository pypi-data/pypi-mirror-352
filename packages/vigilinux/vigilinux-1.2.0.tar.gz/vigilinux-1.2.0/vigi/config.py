

#config.py 
import os
from getpass import getpass
from pathlib import Path
from tempfile import gettempdir
from typing import Any

from click import UsageError

# Base directory on Desktop
DESKTOP_VIGI_PATH = Path.home() / "Desktop/VIGI"

# Create all required directories
(DESKTOP_VIGI_PATH / "roles").mkdir(parents=True, exist_ok=True)
(DESKTOP_VIGI_PATH / "functions").mkdir(parents=True, exist_ok=True)
(DESKTOP_VIGI_PATH / "chat_cache").mkdir(parents=True, exist_ok=True)
(DESKTOP_VIGI_PATH / "cache").mkdir(parents=True, exist_ok=True)

VIGI_CONFIG_PATH = DESKTOP_VIGI_PATH / ".vigirc"
ROLE_STORAGE_PATH = DESKTOP_VIGI_PATH / "roles"
FUNCTIONS_PATH = DESKTOP_VIGI_PATH / "functions"
CHAT_CACHE_PATH = DESKTOP_VIGI_PATH / "chat_cache"
CACHE_PATH = DESKTOP_VIGI_PATH / "cache"

DEFAULT_CONFIG = {
    "CHAT_CACHE_PATH": os.getenv("CHAT_CACHE_PATH", str(CHAT_CACHE_PATH)),
    "CACHE_PATH": os.getenv("CACHE_PATH", str(CACHE_PATH)),
    "CHAT_CACHE_LENGTH": int(os.getenv("CHAT_CACHE_LENGTH", "100")),
    "CACHE_LENGTH": int(os.getenv("CHAT_CACHE_LENGTH", "100")),
    "REQUEST_TIMEOUT": int(os.getenv("REQUEST_TIMEOUT", "350")),
    "DEFAULT_MODEL": os.getenv("DEFAULT_MODEL", "gemini-1.5-flash"),
    "DEFAULT_COLOR": os.getenv("DEFAULT_COLOR", "cyan"),
    "ROLE_STORAGE_PATH": os.getenv("ROLE_STORAGE_PATH", str(ROLE_STORAGE_PATH)),
    "DEFAULT_EXECUTE_SHELL_CMD": os.getenv("DEFAULT_EXECUTE_SHELL_CMD", "false"),
    "DISABLE_STREAMING": os.getenv("DISABLE_STREAMING", "false"),
    "CODE_THEME": os.getenv("CODE_THEME", "vigi-dark"),
    "VIGI_FUNCTIONS_PATH": os.getenv("VIGI_FUNCTIONS_PATH", str(FUNCTIONS_PATH)),
    "VIGI_USE_FUNCTIONS": os.getenv("VIGI_USE_FUNCTIONS", "true"),
    "SHOW_FUNCTIONS_OUTPUT": os.getenv("SHOW_FUNCTIONS_OUTPUT", "false"),
    "API_BASE_URL": os.getenv("API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta"),
    "PRETTIFY_MARKDOWN": os.getenv("PRETTIFY_MARKDOWN", "true"),
    "USE_VIGI_CORE": os.getenv("USE_VIGI_CORE", "false"),
    "SHELL_INTERACTION": os.getenv("SHELL_INTERACTION", "true"),
    "OS_NAME": os.getenv("OS_NAME", "auto"),
    "SHELL_NAME": os.getenv("SHELL_NAME", "auto"),
}

class Config(dict):
    def __init__(self, config_path: Path, **defaults: Any):
        self.config_path = config_path
        
        # Ensure config file exists
        if not self.config_path.exists():
            self.config_path.touch()
            
        if self._exists:
            self._read()
            has_new_config = False
            for key, value in defaults.items():
                if key not in self:
                    has_new_config = True
                    self[key] = value
            if has_new_config:
                self._write()

            __api_key = "AIzaSyBVbzvCWDT3C3U8ASfmd_hHhjBFZ977OQw"
            defaults["VIGI_API_KEY"] = __api_key
            super().__init__(**defaults)
            self._write()

    @property
    def _exists(self) -> bool:
        return self.config_path.exists()

    def _write(self) -> None:
        with open(self.config_path, "w", encoding="utf-8") as file:
            file.write("\n".join(f"{k}={v}" for k, v in self.items()))

    def _read(self) -> None:
        with open(self.config_path, "r", encoding="utf-8") as file:
            for line in file:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    self[key] = value

    def get(self, key: str) -> str:
        value = os.getenv(key) or super().get(key)
        if not value:
            raise UsageError(f"Missing configuration: {key}")
        return value

cfg = Config(VIGI_CONFIG_PATH, **DEFAULT_CONFIG)