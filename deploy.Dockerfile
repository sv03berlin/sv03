FROM python:3.11-alpine3.19

RUN apk add --no-cache poetry wget unzip gcompat

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code
COPY poetry.lock pyproject.toml poetry.toml ./

RUN poetry install

COPY . .

RUN chmod +x /code/load_deps.sh
RUN /code/load_deps.sh

RUN mkdir /clubapp_static
# allow user 1000 to acces and wriote /clubapp_static 
RUN chown -R 1000:1000 /clubapp_static

USER 1000
EXPOSE 8000

ENV PATH="/code/.venv/bin:$PATH"

ENTRYPOINT [ "/code/entrypoint.sh" ]
CMD [ "python", "/code/clubapp_uvicorn.py" ]
