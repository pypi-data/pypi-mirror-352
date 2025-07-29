# app-version-updater
### Setting up client
Setting up client to start <em>delay</em> seconds after server. 

```
ip = your_ip_str
port = your_port_int
updater_client = UpdaterClient(f"http://{ip}:{port}", "testapp", request_period=3, use_logger=True)
app_version = "0.0.1"
```
It is better that you provide mechanism to evaluate <em>app_version</em> since otherwise the following scenario possible:
1. You update your code, compress it to .exe file, rename to next version
2. In code occasionaly <em>app_version</em> was not changed
3. Program will pull THE SAME version of itself due to version mismatch
4. Process repeats in case you made autorestart

In case you have single-thread program you can run
```
updater_client.manage_app_versions(current_app_version, cred)
```
This will block the program and is useful if you have single-thread program. Otherwise it is better to make a thread-based approach with whatever starting condition (delay, for example):

```

ip = get_ip()
port = 49784
print(f"Testing client-server architecture for auto updater on {ip}:{port}")
updater_client = UpdaterClient(f"http://{ip}:{port}", "testapp", request_period=1, use_logger=True)
app_version = "0.0.1"


if __name__ == "__main__":
    print("Starting client...")
    try:
        # this will decide if need to download a new version and download it
        updater_client.manage_app_versions(app_version, "some_string_e.g._password_login_hash")
    except UpdaterException as e: # a way to get the downloaded file path
        downloaded_file_path: str = e.args[0]
        os.startfile(downloaded_file_path)
    sleep(5)
```

### Setting up server
Yo need to create two routes with prefix <em>testapp</em> (or any else you specified before):
```

# setting up server
updater = UpdaterServer(client_version_path=Path("./client_versions"), # folder where to search for files
                               use_logger=True, log_level=logging.DEBUG,
                               module_name="testapp-server-updater")

# Setting up router
router = APIRouter(prefix="/testapp")

@router.get("/appVersion")
def app_version(cred: str):
    try:
        app_version = updater.app_version()
    except UpdaterException:
        raise HTTPException(status_code=404, detail="No client versions available")
    return app_version

@router.get("/app")
def app(version: str, cred: str):
    try:
        content = updater.app(version)
        file_like = BytesIO(content)
        file_like.seek(0)
        return Response(content=content, media_type='application/octet-stream')
    except UpdaterException:
        raise HTTPException(404, f"Version \"{version}\" not found")


main_app = FastAPI()
main_app.include_router(router)
```

### Running both client and server in one program
Replace <em>basic_client_server</em> with the name of your script (without extension)
```
if __name__ == "__main__":
    try:
        print("Starting client and server...")
        updater_client_thread.start()
        uvicorn.run(f"basic_client_server:main_app", host=ip, port=port, workers=1)
    except KeyboardInterrupt:
        updater_client_thread.join()
```

### Expected behaviour
If the file of a newer version has just been downloaded (and located at home_dir/Downloads) the execution would be raised:
```
app_version_updater.models.UpdaterException: (<str(Path(downloaded_file))>)
```
If the file was downloaded previously, you'll see logs like the following:
```
2025-01-21 11:17:55,520 - client-updater - INFO - manage_app_versions - Requested actual client version - got 0.0.2

2025-01-21 11:17:55,520 - client-updater - INFO - manage_app_versions - Downloading version 0.0.2...
```
If no newer version is available:
```
2025-01-21 11:22:11,762 - client-updater - INFO - manage_app_versions - Requested actual client version - got 0.0.1

2025-01-21 11:22:11,763 - client-updater - INFO - manage_app_versions - Latest app version (0.0.1) matching, no update required
```
If folder you specified contains no existing .exe files:
```
2025-01-21 11:23:40,312 - client-updater - INFO - manage_app_versions - Requested actual client version - got 

2025-01-21 11:23:40,312 - client-updater - DEBUG - manage_app_versions - No client update
```
as well as 404 response from server.

### Override versioning
In case you want something except for d.d.d.exe file versioning, you can set your own regex pattern for matching valid file versions:
```
updater_client = UpdaterClient(f"http://{ip}:{port}", "testapp", request_period=3, use_logger=True, validate_expression=<your expression>)

```