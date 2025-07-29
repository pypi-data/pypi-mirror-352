from pathlib import Path
import os
from sys import platform
from typing import Literal
import socket

from app_version_updater.models import UpdaterException

def run_file_platform_independen(path: Path|str):
    assert (isinstance(path, str) and path != "") or (isinstance(path, Path) and str(path) != "."), "Invalid path"
    assert Path(path).exists(), "File not exists"
    
    current_os = get_os()
    if current_os in ["windows", "win32"]:
        os.startfile(Path(path))
    elif current_os == "linux":
        dir = str(Path(path).parent)
        filename = os.path.basename(Path(path))
        os.system(f"cd {dir} && chmod +x {filename} && ./{filename}")

def get_os():
    current_os = platform.lower()
    if current_os not in ["windows", "win32", "linux"]:
        raise UpdaterException(f"Incompatible operating system, should be linux/windows, current: {current_os}")
    return current_os

def log(logger, level: Literal["info", "debug", "error", "exception", "warning"], msg: str):
    """ Checks if logger is set and if so logs to terminal """
    if logger is not None:
        match level:
            case "info":
                logger.info(msg)
            case "debug":
                logger.debug(msg)
            case "error":
                logger.error(msg)
            case "exception":
                logger.exception(msg)
            case "warning":
                logger.warning(msg)

def get_ip(DNS: str = "8.8.8.8", port: int = 80):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((DNS, port))
    ip = s.getsockname()[0]
    s.close()
    return ip