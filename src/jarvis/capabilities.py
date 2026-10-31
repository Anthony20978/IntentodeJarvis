from .platform import get_system_info
def get_capabilities():
    """Devuelve las capacidades disponibles de JARVIS."""
    return {
        "system_detection": True,
        "persistent_memory": True,
        "command_processing": True,
        "voice_recognition": False,
        "speech_synthesis": False,
        "artificial_intelligence": False,
        "system_info": get_system_info(),
    }