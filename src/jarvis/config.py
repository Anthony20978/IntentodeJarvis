import os
import platform
from pathlib import Path
SYSTEM = platform.system()
def get_data_directory() -> Path:
    """Obtiene el directorio de datos según el sistema operativo."""
    if SYSTEM == "Windows":
        base_directory = os.getenv("LOCALAPPDATA")
        if base_directory:
            return Path(base_directory) / "JARVIS"
        return Path.home() / "AppData" / "Local" / "JARVIS"
    if SYSTEM == "Darwin":
        return Path.home() / "Library" / "Application Support" / "JARVIS"
    xdg_directory = os.getenv("XDG_DATA_HOME")
    if xdg_directory:
        return Path(xdg_directory) / "jarvis"
    return Path.home() / ".local" / "share" / "jarvis"
# Directorio de datos personalizable
DATA_DIR = Path(
    os.getenv("JARVIS_DATA_DIR", str(get_data_directory()))
).expanduser()
# Base de datos
DATABASE_PATH = DATA_DIR / "jarvis.db"
# Versión
VERSION = "0.2.0"
# Idioma configurable
DEFAULT_LANGUAGE = os.getenv("JARVIS_LANGUAGE", "es").strip() or "es"