import uvicorn

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
        log_level="debug",
        workers=4,
    )
    server = uvicorn.Server(config)
    server.run()
