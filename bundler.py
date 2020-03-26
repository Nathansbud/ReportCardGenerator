"""
I don't know how to use setup.py or requirements.txt or pip. Everything is WIP.

That said, certain macOS-specific libraries break on Windows for dev stuff. Sooooo...
"""
import os

os.system("pip freeze > requirements.txt")
with open("requirements.txt", "r+") as input_mode: lines = input_mode.readlines()
with open("requirements.txt", "w+") as output_mode:
    output_mode.truncate(0)
    output_mode.writelines([l if not l.startswith("pyobjc") else l.strip() + "; sys_platform == 'darwin'\n" for l in lines])