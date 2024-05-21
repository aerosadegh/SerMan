import re
import sys
import os


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def parse_services(output):
    # This regular expression matches services in the format 'S{number}'
    pattern = re.compile(r"S\d+")
    services = pattern.findall(output)
    return set(services)
