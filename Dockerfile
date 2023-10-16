FROM python:3.11-slim-bullseye

RUN apt-get update -y && apt-get install sudo python3-dev gettext wget unzip python3-pip git -y

# install
RUN mkdir /code
WORKDIR /code
COPY . .

RUN pip install -r /code/requirements.txt

# get bootstrap
RUN chmod +x /code/load_deps.sh
RUN /code/load_deps.sh

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]