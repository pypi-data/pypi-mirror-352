import os

def find_bash():
    for path in [
        '/bin/bash',
        r"C:\Git\bin\bash.exe",
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
        os.getenv("LOCALAPPDATA","") + r"\Programs\Git\bin\bash.exe"
    ]:
        if os.path.exists(path):
            return path
