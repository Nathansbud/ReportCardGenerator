from math import floor
import platform
import re
import darkdetect

def index_to_column(idx):
    supermajor = chr(65 + floor((idx - 26) / (26**2) - 1)) if (idx > 26**2 + 25) else ""
    major = chr(65 + (floor((idx / 26 - 1)) % 26)) if idx > 25 else ""
    minor = chr(65 + idx % 26)
    return str(supermajor + major + minor)

def is_macos(): return platform.system().startswith("Darwin")
def is_windows(): return platform.system().startswith("Windows")
def is_windows8(): return platform.platform().startswith("Windows-8")
def is_hexcode(hex_str): return re.match(r"(?i)^#[0-9A-F]{6}$", hex_str) is not None
def is_darkmode(): return darkdetect.isDark() if is_macos() else False

#https://stackoverflow.com/a/11868398/11584108
def foreground_from_background(hex_str):
    hex_str = hex_str.replace("#", "")
    r, g, b = [int(h, 16) for h in hex_str[::2]]
    return "#000000" if ((r*299)+(g*587)+(b*114))/100 >= 128 else "#ffffff"

if __name__ == "__main__":
    print(is_windows())
    pass

