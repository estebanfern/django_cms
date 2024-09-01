FROM python:3.11.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=cms.profile.prod

RUN apt-get update -y
RUN apt-get install -y libpq-dev gcc python3-dev musl-dev

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
