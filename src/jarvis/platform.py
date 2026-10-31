import os
import platform
def get_system_info():
    """Obtiene información básica del sistema."""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "cpu_cores": os.cpu_count() or 1,
    }