FROM python:3.11.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=cms.profile.prod

RUN apt-get update -y
RUN apt-get install -y libpq-dev gcc python3-dev musl-dev tzdata locales

ENV TZ=America/Asuncion
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN echo "es_PY.UTF-8 UTF-8" >> /etc/locale.gen && locale-gen es_PY.UTF-8
ENV LANG es_PY.UTF-8
ENV LANGUAGE es_PY:es
ENV LC_ALL es_PY.UTF-8

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x ./entrypoint.sh

RUN addgroup --system cms && adduser --system cms --ingroup cms

USER cms:cms

USER root
RUN mkdir /app/logs
RUN chown -R cms:cms /app/logs
RUN chmod -R 775 /app/logs
RUN chown cms:cms /app/entrypoint.sh
USER cms

ENTRYPOINT [ "./entrypoint.sh" ]
