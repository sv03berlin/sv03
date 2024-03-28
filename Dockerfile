FROM python:3.11-slim-bullseye

RUN apt-get update -y && apt-get install sudo python3-dev gettext wget unzip python3-pip git -y

# install
RUN mkdir /code
WORKDIR /code
COPY . .

RUN pip install poetry
RUN poetry install --no-root

# get bootstrap
RUN chmod +x /code/load_deps.sh
RUN /code/load_deps.sh

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
ENV PATH="/code/.venv/bin:$PATH"
ENV DEBUG=true
CMD [ "python3", "/code/clubapp_uvicorn.py" ]
