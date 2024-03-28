FROM python:3.12-alpine3.19

RUN apk add --no-cache poetry wget unzip

RUN mkdir /code
WORKDIR /code
COPY . .

RUN poetry install --no-root

RUN chmod +x /code/load_deps.sh
RUN /code/load_deps.sh

RUN chmod +x /entrypoint.sh

USER 1000
EXPOSE 8000
ENV PATH="/code/.venv/bin:$PATH"

ENTRYPOINT [ "entrypoint.sh" ]
CMD [ "python3", "/code/clubapp_uvicorn.py" ]