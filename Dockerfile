FROM python:3.11-bookworm

#ARG RELEASE_VERSION
#
#ENV RELEASE_VERSION=$RELEASE_VERSION

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir -p /app/media /app/static

WORKDIR /app

COPY . /app/


RUN pip install -r ./requirements.txt

#RUN echo ${RELEASE_VERSION} > RELEASE_VERSION

#CMD [ "gunicorn", "-c", "./gunicorn_conf.py" ]