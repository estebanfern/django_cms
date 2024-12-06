![Logo](static/poli.jpg)

# Tabla de contenidos
1. [ Variables de Entorno ](#variables-de-entorno)
1. [ Descripción ](#descripción)
2. [ Desarrollo ](#desarrollo)
3. [ Historial de Cambios ](#historial-de-cambios)
4. [ Despliegue en Producción ](#despliegue-en-producción)
5. [ Autores ](#authors)

# Descripción
![Django](https://img.shields.io/badge/django-000000?style=for-the-badge&logo=django&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-000000?style=for-the-badge&logo=bootstrap&logoColor=white)
![AWS](https://img.shields.io/badge/amazon-000000?style=for-the-badge&logo=amazon&logoColor=white)

Sistema de Gestión de Contenidos con Django para la materia Ingenieria de Software II

# Variables de Entorno

Para correr este proyecto, necesitas configurar estas variables de entorno en tu archivo .env

```bash
DB_NAME=django_cms
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
AWS_ACCESS_KEY_ID=secret-key-id
AWS_SECRET_ACCESS_KEY=secrect-access-key
AWS_STORAGE_BUCKET_NAME=djangocms
AWS_S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
AWS_S3_REGION_NAME=nyc3
DEFAULT_PROFILE_PHOTO=profile_pics/perfil.png
EMAIL_HOST_USER=cms@mail.com
EMAIL_HOST_PASSWORD=secret-password
CMS_DOCS_URL=https://docs.is2equipo10.me
STRIPE_SECRET_KEY=secret-key
DOCKER_HOST=172.17.0.1
ENDPOINT_SECRET=secret-endpoint
```

# Desarrollo

Puedes desplegar el proyecto en modo desarrollo con estos comandos

```bash
  ./manage.py makemigrations
  ./manage.py migrate
  ./manage.py runserver
```

# Historial de Cambios

Para ver el historial de cambios visita [CHANGELOG.md](https://github.com/estebanfern/django_cms/tree/main/CHANGELOG.md)

# Despliegue en producción

Para ver la guía de despliegue a producción [DEPLOYMENT.md](https://github.com/estebanfern/django_cms/tree/main/DEPLOYMENT.md)


# Authors

- [Esteban Fernández](https://www.github.com/estebanfern)
- [Fabrizio Román](https://www.github.com/fabri10roman)
- [Roberto Acosta](https://www.github.com/robertodayudis)
- [Abigail Nuñez](https://www.github.com/Abinues)
