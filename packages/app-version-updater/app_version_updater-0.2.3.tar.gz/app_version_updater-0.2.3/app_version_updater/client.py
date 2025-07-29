import aiohttp.client_exceptions
import requests
from pathlib import Path
import time
import asyncio
import os
import aiohttp

from standarted_logger.logger import Logger
from app_version_updater.models import UpdaterException, UpdaterConnectionError
from app_version_updater.utils import get_os, log, run_file_platform_independen

class UpdaterClient():

    def __init__(self, 
                 host: str,                                     # host ip in form http://<ip>
                 host_domain: str,                              # application prefix: /<app>/route1, /<app>/<route2>
                 request_period=600,                            # timeout of requests in seconds
                 use_logger=False,                              # turn on/off logging
                 module_name="client-updater",                  # module name for logger
                 log_level=10,                                  # 10/20...50 or logging.DEBUG
                 log_dir=None,                                  # path to save log files
                 console_handler=True,                          # set False if double logging (TODO: fix later)
                 save_folder: Path = Path.home() / "Downloads"): # directory to save new version's files
        """Host domain will be added to the downloaded file name
        """

        self.HOST = host
        self.host_domain = host_domain
        self.app_request_version_period = request_period
        self.CLIENT_SAVE_FOLDER = save_folder
        self.logger = Logger.get_logger(module_name, log_level, log_dir, console_handler) if use_logger else None
        self.current_os = get_os()

    def manage_app_versions(self, current_app_version: str, cred: str) -> str:
        while True:
            version = self.__main_iteration(current_app_version, cred)
            if version is not None:
                return version
            time.sleep(self.app_request_version_period)

    async def manage_app_versions_async(self, current_app_version: str, cred: str) -> str:
        while True:
            version = await self.__main_iteration_async(current_app_version, cred)
            if version is not None:
                return version
            await asyncio.sleep(self.app_request_version_period)

    def __main_iteration(self, current_app_version: str, cred: str) -> str|None:
        '''
        Main thread that requests newer app versions from server,
        fetches updates (if any) and updates app
        :raises: UpdaterException If new version is downloaded - raise UpdaterException with file name as error message
        :raises: UpdaterConnectionError If the server is unavailable
        '''
        try:
            version = self.__get_actual_app_version(cred, get_os()) # Getting only version value
            log(self.logger, "debug", f"Requested actual client version - got {version}")
            if not version:
                log(self.logger, "debug", f"No client update")
            elif current_app_version < version and version != "None":
                log(self.logger, "info", f"Newer version available: {version}")
                return version
            else:
                log(self.logger, "debug", f"Latest app version ({version}) matching, no update required")
        except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
            log(self.logger, "warning", f"Connection with server is broken...")
            raise UpdaterConnectionError(f"Connection with server is broken...")
        return None
    
    async def __main_iteration_async(self, current_app_version: str, cred: str) -> str|None:
        '''
        Main thread that requests newer app versions from server,
        fetches updates (if any) and updates app
        :raises: UpdaterException If new version is downloaded - raise UpdaterException with file name as error message
        :raises: UpdaterConnectionError If the server is unavailable
        '''
        try:
            version = await self.__get_actual_app_version_async(cred, get_os()) # Getting only version value
            log(self.logger, "debug", f"Requested actual client version - got {version}")
            if not version:
                log(self.logger, "debug", f"No client update")
            elif current_app_version < version and version != "None":
                log(self.logger, "info", f"Newer version available: {version}")
                return version
            else:
                log(self.logger, "debug", f"Latest app version ({version}) matching, no update required")
        except (aiohttp.client_exceptions.ClientConnectorError, aiohttp.client_exceptions.ConnectionTimeoutError):
            log(self.logger, "warning", f"Connection with server is broken...")
            raise UpdaterConnectionError(f"Connection with server is broken...")
        return None

    def upgrade(self, 
                version: str,                       # newer app version string
                cred: str,                          # credentials string (user defined or "")
                install: bool = False,              # run setup file or not
                filename: str = None,                   # path to save setup file
                remove_setup_file: bool = True,         # removing setup file after install or not
                overwrite_old: bool = False):           # set True to remove old file with same name if exists
        """ Run this to retrieve new app from server"""
        try:
            log(self.logger, "info", f"Downloading version {version}...")
            app = self.__download_new_app(version, cred, get_os()) # getting in memory, not on disk yet
            log(self.logger, "info", f"Upgrading to verison {version}, extracting...")
            self.__save_setup_file(content=app, 
                                   version=version,
                                   install=install,
                                   filename=filename,
                                   remove_setup_file=remove_setup_file,
                                   overwrite_old=overwrite_old) # saving to path on disk
        except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
            log(self.logger, "warning", f"Connection with server is broken...")
            raise UpdaterConnectionError(f"Connection with server is broken...")
        
    async def upgrade_async(self, 
                version: str,                       # newer app version string
                cred: str,                          # credentials string (user defined or "")
                install: bool = False,              # run setup file or not
                filename: str = None,                   # path to save setup file
                remove_setup_file: bool = True,         # removing setup file after install or not
                overwrite_old: bool = False):           # set True to remove old file with same name if exists
        """ Run this to retrieve new app from server"""
        try:
            log(self.logger, "info", f"Downloading version {version}...")
            app = await self.__download_new_app_async(version, cred, get_os()) # getting in memory, not on disk yet
            log(self.logger, "info", f"Upgrading to verison {version}, extracting...")
            self.__save_setup_file(content=app, 
                                   version=version,
                                   install=install,
                                   filename=filename,
                                   remove_setup_file=remove_setup_file,
                                   overwrite_old=overwrite_old) # saving to path on disk
        except (aiohttp.client_exceptions.ClientConnectorError, aiohttp.client_exceptions.ConnectionTimeoutError):
            log(self.logger, "warning", f"Connection with server is broken...")
            raise UpdaterConnectionError(f"Connection with server is broken...")

    def __save_setup_file(self, 
                          content: bytes,                   # server FileResponce
                          version: str,                     # newer version string
                          install: bool = False,            # run file or not
                          filename: str = None,                 # save path
                          remove_setup_file: bool = True,       # removing setup file after running or not
                          overwrite_old: bool = False):         # set True to remove old file with same name if exists
        # Loads setup file
        file_extension = ".exe" if get_os() in ["windows", "win32"] else ".sh"
        if filename is not None:
            path = Path(f"{filename}{file_extension}")
        else:
            path = Path(self.CLIENT_SAVE_FOLDER / f'setup_{self.host_domain}_{version.replace(".", "")}{file_extension}')
        if path.exists():
            if path.stat().st_size == len(content):
                if not overwrite_old:
                    log(self.logger, "info", "The setup file was already downloaded")
                    return
                else:
                    log(self.logger, "info", "Removing old setup file...")
                    os.remove(path)
        if not os.path.exists(path.parent):
            path.parent.mkdir(parents=True)
        path.write_bytes(content)
        if install:
            log(self.logger, "info", "Installing...")
            run_file_platform_independen(path)
        if remove_setup_file:
            log(self.logger, "info", "Removing new setup file...")
            os.remove(path)
        log(self.logger, "info", "Client update was downloaded successfully")

    def __get_actual_app_version(self, cred: str, os_: str) -> str:
        # Getting latest app version from server
        res = requests.get(self.HOST + f"/{self.host_domain}/appVersion", 
                            params={"cred": cred, "os_": os_})
            
        if res.status_code == 200:
            return res.content.decode().replace("\"", "")
        if res.status_code == 404:
            return ""
        else:
            raise UpdaterException(f"HTTP {res.status_code} {res.text}")

    def __download_new_app(self, new_version: str, cred: str, os_: str) -> bytes:
        # Getting FileResponse from server in bytes - needs further writing to disk
        res = requests.get(self.HOST + f"/{self.host_domain}/app", 
                            params={"cred": cred, "version": new_version, "os_": os_})
        
        if res.status_code == 200:
            return res.content
        else:
            raise UpdaterException(f"HTTP {res.status_code}")

    async def __get_actual_app_version_async(self, cred: str, os_: str) -> str:
        # Getting latest app version from server
        async with aiohttp.ClientSession() as session:
            async with session.get(self.HOST + f"/{self.host_domain}/appVersion", 
                                   params={"cred": cred, "os_": os_}) as res:
            
                if res.status == 200:
                    payload = await res.text()
                    return payload.replace("\"", "")
                if res.status == 404:
                    return ""
                else:
                    raise UpdaterException(f"HTTP {res.status} {await res.text()}")

    async def __download_new_app_async(self, new_version: str, cred: str, os_: str) -> bytes:
        # Getting FileResponse from server in bytes - needs further writing to disk
        async with aiohttp.ClientSession() as session:
            async with session.get(self.HOST + f"/{self.host_domain}/app", 
                            params={"cred": cred, "version": new_version, "os_": os_}) as res:
        
                if res.status == 200:
                    return await res.text()
                else:
                    raise UpdaterException(f"HTTP {res.status}")