import os
import platform
import socket
from time import sleep


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def kill_masscode_1():
    if platform.system() == "Windows":
        os.system("taskkill /f /im masscode.exe")
    elif platform.system() == "Darwin":
        os.system("killall -9 masscode")
    elif platform.system() == "Linux":
        os.system("killall -9 masscode")
    sleep(1.5)


def detach_open(path: str):
    import subprocess

    return subprocess.Popen(
        path,
        creationflags=(
            subprocess.DETACHED_PROCESS
            | subprocess.CREATE_NEW_PROCESS_GROUP
            | subprocess.CREATE_BREAKAWAY_FROM_JOB
        ),
    )


def get_exe_path():
    if platform.system() == "Windows":
        raw = (
            os.popen(
                'powershell "Get-CimInstance Win32_Process -Filter \\"name=\'masscode.exe\'\\" | Select-Object -ExpandProperty ExecutablePath"'
            )
            .read()
            .strip()
        )
        try:
            path = raw.splitlines()[2].strip()
        except IndexError:
            path = None
    else:
        path = None

    return path
