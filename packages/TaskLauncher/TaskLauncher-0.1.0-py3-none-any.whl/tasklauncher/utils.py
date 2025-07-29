import platform
import sys

def get_system_info():
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "python_version": sys.version
    }
