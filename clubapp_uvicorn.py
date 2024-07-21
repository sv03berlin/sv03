import threading
from time import sleep

import schedule
import uvicorn
from django.core.management import call_command
from uvicorn.config import LOGGING_CONFIG

from clubapp.clubapp.asgi import application as app

if __name__ == "__main__":
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
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

    schedule.every(3).hours.do(lambda: call_command("synckc"))
    schedule.every(12).hours.do(lambda: call_command("notify"))

    while True:
        schedule.run_pending()
        sleep(1)
