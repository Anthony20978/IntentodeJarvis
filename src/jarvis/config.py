from pathlib import Path
# Directorio raíz del proyecto
ROOT_DIR = Path(__file__).resolve().parents[2]
# Directorio de datos locales
DATA_DIR = ROOT_DIR / "data"
DATABASE_PATH = DATA_DIR / "jarvis.db"
# Directorio de memoria persistente
MEMORY_DIR = DATA_DIR / "memory"
# Versión del proyecto
VERSION = "0.1.1"
# Configuración general
DEFAULT_LANGUAGE = "es"