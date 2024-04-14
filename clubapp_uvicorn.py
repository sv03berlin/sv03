import uvicorn
import subprocess
from clubapp.clubapp.asgi import application as app
import pathlib
from time import sleep
import threading

def runjobs():
    subprocess.run(["python", pathlib.Path(__file__).parent.absolute() / "manage.py", "runjobs"])

if __name__ == "__main__":
    

    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        http="h11",
        lifespan="off",
        forwarded_allow_ips="*",
        proxy_headers=True,
        log_level="debug",
        workers=4,
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run)
    thread.start()

    while True:
        runjobs()
        sleep(60)
