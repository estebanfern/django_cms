FROM python:3.11.9-slim AS builder
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y make
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN cd docs && make html -f Makefile

FROM nginx:alpine
COPY ./docs/.nginx/nginx.conf /etc/nginx/conf.d/default.conf
WORKDIR /usr/share/nginx/html
RUN rm -rf ./*
COPY --from=builder /app/docs/_build/html .
EXPOSE 80
ENTRYPOINT ["nginx", "-g", "daemon off;"]
