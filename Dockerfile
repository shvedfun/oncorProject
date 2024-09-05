FROM python:3.11-bookworm

#ARG RELEASE_VERSION
#
#ENV RELEASE_VERSION=$RELEASE_VERSION

RUN mkdir -p /app/media /app/static

#COPY requrements.txt ./requrements.txt
COPY . ./

RUN pip install -r ./requrements.txt

#RUN echo ${RELEASE_VERSION} > RELEASE_VERSION

CMD [ "gunicorn", "-c", "./gunicorn_conf.py" ]