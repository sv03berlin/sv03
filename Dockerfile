FROM python:3.11-slim-bullseye

RUN apt-get update -y && apt-get install wget unzip git -y

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
ENV GIT_SHA $GIT_SHA
ENV GIT_BRANCH $GIT_BRANCH

ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "python3", "/code/clubapp_uvicorn.py" ]
