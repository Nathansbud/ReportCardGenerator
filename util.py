from math import floor
import platform

def index_to_column(idx):
    major = chr(65 + floor(idx / 26 - 1)) if idx > 25 else ""
    minor = chr(65 + idx % 26)
    return str(major + minor)

def is_macos():
    return platform.system().startswith("Darwin")
