from pathlib import Path
from typing import Literal
from standarted_logger.logger import Logger
import re
from app_version_updater.models import UpdaterException
import os
from app_version_updater.utils import log

class UpdaterServer:
    __validate_expression_default = r'\d+.\d+.\d.[a-z]+.[a-z]+'


    def __init__(self, client_version_path = None, use_logger=False, 
                 module_name="client-updater", log_level=10, log_dir=None, console_handler=True,
                 validate_expression: None | str = None):
        
        self.validate_expression = validate_expression

        if client_version_path is None:
            self.client_version_path = Path(".") / "client_versions"
            if not self.client_version_path.exists():
                self.client_version_path.mkdir(parents=True, exist_ok=True)
        else:
            self.client_version_path = client_version_path
        
        self.logger = Logger.get_logger(module_name, log_level, log_dir, console_handler) if use_logger else None

    def app_version(self, os_: Literal["windows", "win32", "linux"]) -> str:
        try:
            return self.__find_latest_version(os_).encode()
        except FileNotFoundError:
            raise UpdaterException("404 No client update")

    def app(self, version: str, os_: Literal["windows", "win32", "linux"]) -> bytes:
        try:
            file_path = self.__get_file_by_version(version, os_)
            with open(file_path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            raise UpdaterException("403 Client required app version that does not exist")


    def __find_latest_version(self, os_: Literal["windows", "win32", "linux"]) -> str:
        """Among content of client_version_path find the file with 
        the greates version in the name"""
        filenames = self.__get_folder_content(os_)
        if not filenames:
            raise FileNotFoundError("No client updates")
        max_version = "0.0.0"
        for file_name in filenames:
            try:
                max_version = max(max_version, file_name)
            except Exception as e:
                log(self.logger, "info", f"Invalid client_update file name")
        return max_version


    def __get_file_by_version(self, version: str, os_: Literal["windows", "win32", "linux"]) -> Path:
        for file in os.listdir(self.client_version_path):
            if not self.__is_file_valid(file, os_):
                continue
            if self.__split_extension(file) == version:
                return Path(self.client_version_path) / Path(file)
        raise FileNotFoundError(f"File with the {version=} is not found or not valid")
    
    def __get_folder_content(self, os_: Literal["windows", "win32", "linux"]):
        """return valid client_update files without extensions"""
        filenames = [self.__split_extension(f) \
                    for f in os.listdir(os.path.join(Path(os.getcwd()), self.client_version_path)) \
                        if self.__is_file_valid(f, os_)]
        return filenames
    
    def __is_file_valid(self, file_name: str, os_: Literal["windows", "win32", "linux"]):
        if self.validate_expression is None:
            validate_expression = UpdaterServer.__validate_expression_default

        if re.match(validate_expression, file_name) is None:
            return os_ in file_name
        return (Path(self.client_version_path) / Path(file_name)).exists()
    
    def __split_extension(self, file_name: str):
        """Remove extension from file. Doesn't verify if the file exists"""
        file_path = Path(self.client_version_path) / Path(file_name)
        return Path(file_path.stem).stem