FROM astral/uv:python3.13-bookworm-slim AS builder

RUN apt-get update -y && apt-get install wget curl unzip git -y

# install dependencies and build venv in /code
WORKDIR /code
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

# get bootstrap deps
COPY clubapp/static ./clubapp/static 
COPY load_deps.sh ./
RUN chmod +x load_deps.sh && ./load_deps.sh

COPY clubapp/ ./clubapp/
COPY clubapp_uvicorn.py ./
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

FROM python:3.14-slim-bookworm
WORKDIR /code

COPY --from=builder /code/.venv /code/.venv
COPY --from=builder /code/clubapp /code/clubapp
COPY --from=builder /code/clubapp_uvicorn.py /code/clubapp_uvicorn.py
COPY --from=builder /code/entrypoint.sh /entrypoint.sh
COPY --from=builder /code/load_deps.sh /code/load_deps.sh
COPY manage.py logging.yaml /code

ENV PATH="/code/.venv/bin:$PATH"

ARG GIT_SHA
ARG GIT_BRANCH
ENV GIT_SHA=$GIT_SHA
ENV GIT_BRANCH=$GIT_BRANCH

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=3s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "python3", "/code/clubapp_uvicorn.py" ]
