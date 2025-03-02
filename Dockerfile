FROM python:3.12-slim-bookworm

RUN apt-get update -y && apt-get install wget curl unzip git -y

# install
RUN mkdir /code
WORKDIR /code
COPY . .

RUN pip install poetry
RUN poetry install --no-root
ENV PATH="/code/.venv/bin:$PATH"

# get bootstrap
RUN chmod +x /code/load_deps.sh
RUN /code/load_deps.sh

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

ARG GIT_SHA
ARG GIT_BRANCH
ENV GIT_SHA=$GIT_SHA
ENV GIT_BRANCH=$GIT_BRANCH

EXPOSE 8000


HEALTHCHECK --interval=10s --timeout=5s --start-period=3s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "python3", "/code/clubapp_uvicorn.py" ]
