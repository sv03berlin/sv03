import threading
from time import sleep

import uvicorn
from django.core.management import call_command

from clubapp.clubapp.asgi import application as app


def runjobs() -> None:
    call_command("synckc")


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
