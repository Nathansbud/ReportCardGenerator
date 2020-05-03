from math import floor
import platform
import re

def index_to_column(idx):
    major = chr(65 + floor(idx / 26 - 1)) if idx > 25 else ""
    minor = chr(65 + idx % 26)
    return str(major + minor)

def is_macos(): return platform.system().startswith("Darwin")
def is_hexcode(hex_str): return re.match(r"(?i)^#[0-9A-F]{6}$", hex_str) is not None

if __name__ == "__main__":
    pass

