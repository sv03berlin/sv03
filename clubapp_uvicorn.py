import threading
from time import sleep

import schedule
import uvicorn
from django.core.management import call_command

from clubapp.clubapp.asgi import application as app

if __name__ == "__main__":
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        http="h11",
        lifespan="off",
        forwarded_allow_ips="*",
        proxy_headers=True,
        log_config="logging.yaml",
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run)
    thread.start()

    schedule.every(3).hours.do(lambda: call_command("synckc"))
    schedule.every(12).hours.do(lambda: call_command("notify"))

    while True:
        schedule.run_pending()
        sleep(1)
