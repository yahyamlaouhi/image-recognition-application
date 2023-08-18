FROM python:3.8
LABEL maintainer="image-recognition-app"

ENV PYTHONUNBUFFERED 1


RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt


RUN  mkdir /app
WORKDIR /app
COPY ./app /app

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN /bin/sh
RUN chmod -R 755 /vol/web
VOLUME /vol/web
CMD [ "python", "manage.py","runserver" ]
