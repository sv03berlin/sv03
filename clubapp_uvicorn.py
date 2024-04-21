import sys
import threading
from time import sleep

import uvicorn
from django.core.management import execute_from_command_line

from clubapp.clubapp.asgi import application as app


def runjobs() -> None:
    sys.argv = ["manage.py", "synckc"]
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        http="h11",
        lifespan="off",
        forwarded_allow_ips="*",
        proxy_headers=True,
        log_level="info",
        workers=4,
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run)
    thread.start()

    while True:
        runjobs()
        sleep(60 * 60 * 3)  # 3 hours
