
# Documentación de despliegue en ambiente productivo

Este documento guia paso a paso como realizar el despliegue de la aplicación en un ambiente productivo.

## Prerequisitos
- Servidor donde se alojará la aplicación con mínimo 2vCPUs, 4GB de RAM y 80GB de almacenamiento SSD, le pondremos como alias ```cms-app```.
- Servidor donde se alojará la base de datos con mínimo 2vCPUs, 2GB de RAM y 60GB de almacenamiento SSD, le pondremos como alias ```cms-db```.
- Configuración de red entre ```cms-app``` y ```cms-db``` para su comunicación interna
- Registros y configuración DNS de nuestro dominio y subdominio para dirigir el tráfico a nuestro servidor de aplicaciones

## Servidor de base de datos
Para ejemplo de esta documentación, el servidor de base de datos fue montado con el sistema operativo Ubuntu 22.04 LTS.
- Instalar PostgreSQL
```bash
sudo apt update && \
sudo apt install postgresql postgresql-contrib
```
- Iniciar el servicio postgresql
```bash
sudo systemctl start postgresql.service
```
- Comprobar el servicio postgresql
```bash
sudo systemctl status postgresql
```
- Comprobar el estado correcto
```bash
● postgresql.service - PostgreSQL RDBMS
     Loaded: loaded (/lib/systemd/system/postgresql.service; enabled; vendor preset: enabled)
     Active: active (exited) since Sun 2024-09-01 07:13:54 UTC; 15h ago
    Process: 2196 ExecStart=/bin/true (code=exited, status=0/SUCCESS)
   Main PID: 2196 (code=exited, status=0/SUCCESS)
        CPU: 1ms
```
- Editar el archivo de configuración ```/etc/postgresql/14/main/postgresql.conf```
```bash
vim /etc/postgresql/14/main/postgresql.conf
```
- Cambiar la configuración ```listen_addresses``` para permitir la conexión de nuestro otro servidor
```bash
listen_addresses = 'localhost,10.116.16.2'
```
- Guardar el archivo
- Editar el archivo de configuración ```/etc/postgresql/14/main/pg_hba.conf```
```bash
vim /etc/postgresql/14/main/pg_hba.conf
```
- Permitir la conección a todas o a una de las base de datos de nuestra red local entre ```cms-app``` y ```cms-db``` por el método ```md5```
```bash
host    all             all             10.116.16.0/24          md5
```
- Reiniciar el servicio PostgreSQL para activar los cambios
```bash
sudo systemctl restart postgresql
```
- Comprobar el estado correcto
```bash
● postgresql.service - PostgreSQL RDBMS
     Loaded: loaded (/lib/systemd/system/postgresql.service; enabled; vendor preset: enabled)
     Active: active (exited) since Sun 2024-09-01 07:13:54 UTC; 15h ago
    Process: 2196 ExecStart=/bin/true (code=exited, status=0/SUCCESS)
   Main PID: 2196 (code=exited, status=0/SUCCESS)
        CPU: 1ms
```
- Ahora para probar que podemos acceder desde nuestro servidor ```cms-app``` a la base de datos en ```cms-db```, podemos conectarnos a nuestro servidor ```cms-app``` y ejecutar telnet, por ejemplo:
```bash
telnet 10.116.16.2 5432
```
- Telnet debería de poder conectarse a la ip y puerto de nuestra base de datos
```bash
Trying 10.116.16.2...
Connected to 10.116.16.2.
Escape character is '^]'.
```
- Con esto podemos confirmar que nuestro servidor de base de datos esta funcionando correctamente, ahora nos queda crear la base de datos y el usuario
- Nos conectamos a nuestra base de datos
```bash
sudo -u postgres psql
```
- Creamos la base de datos
```sql
CREATE DATABASE django_cms;
```
- Creamos el usuario
```sql
CREATE USER cms_app WITH PASSWORD 'secret-password';
```
- Para ejemplo práctico, vamos a darle permisos totales en la base de datos
```sql
ALTER DATABASE django_cms OWNER TO cms_app;
```
Con estas configuraciones nuestro servidor de base de datos ya está listo para el despliegue de la aplicación.

## Servidor de aplicación
Para ejemplo de esta documentación, el servidor de aplicación fue montado con el sistema operativo Ubuntu 22.04 LTS.
- Instalar NGINX
```bash
sudo apt update && \
sudo apt install nginx
```
- Copiar la configuración default de ```sites-available``` a por ej ```is2equipo10.me```, también el para ```docs.is2equipo10.me```
```bash
cd /etc/nginx/sites-available/ && \
cp default is2equipo10.me && \
cp default docs.is2equipo10.me
```
- Crear un link simbólico de nuestras aplicaciones a ```sites-enabled```
```bash
ln -s /etc/nginx/sites-available/is2equipo10.me /etc/nginx/sites-enabled/is2equipo10.me && \
ln -s /etc/nginx/sites-available/docs.is2equipo10.me /etc/nginx/sites-enabled/docs.is2equipo10.me
```
- Instalar CertBot/LetsEncrypt
```bash
sudo snap install --classic certbot
```
- Configurar certificado SSL con CertBot
```bash
sudo certbot --nginx
```
- Seguir las instrucciones dadas por el cli
- Recargar NGINX
```bash
nginx -s reload
```
- Verificar el correcto funcionamiento de NGINX con HTTPS
- Desinstalar paquetes conflictivos con docker
```bash
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
```
- Agregar la llave GPG de Docker
```bash
sudo apt-get update && \
sudo apt-get install ca-certificates curl && \
sudo install -m 0755 -d /etc/apt/keyrings && \
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc  && \
sudo chmod a+r /etc/apt/keyrings/docker.asc
```
- Agregar el repositorio de docker a APT
```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null && \
sudo apt-get update
```
- Instalar paquetes de Docker
```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
- Probar nuestra instalación
```bash
sudo docker run hello-world
```
- Resultado esperado:
```bash
Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```
- Crear nuestro directorio de aplicación
```bash
mkdir /usr/cms
```
- Dentro de nuestro direcorio de aplicación, crear nuestro archivo ```docker-compose.yaml``` y ```cms-app.env```
```bash
cd /usr/cms && \
touch docker-compose.yaml cms-app.env
```
- Editar el archivo ```docker-compose.yaml```
```bash
vim docker-compose.yaml
```
- Configurar de acuerdo a nuestras necesidades, ejemplo:
```yaml
services:
  cms-app:
    image: estebanfern/cms-app:latest
    container_name: cms-app
    ports:
      - "8000:8000"
    env_file:
      - cms-app.env
    volumes:
      - logs_data:/app/logs
    logging:
      driver: "json-file"
      options:
        max-size: "500m"
        max-file: "2"
  cms-docs:
    image: estebanfern/cms-docs:latest
    container_name: cms-docs
    ports:
      - "8080:80"

volumes:
  logs_data:
```
- Creamos los servicios y le asignamos el puerto 8000 al servicio ```cms-app``` y el puerto 8080 al servicio ```cms-docs```. Asignamos el volumen ```logs_data``` para el directorio ```/app/logs``` dentro de ```cms-app``` para persistir en el servidor los logs de la aplicación, y configuramos el logging de docker. Tambien le asignamos su ```env_file``` a nuestro otro archivo recien creado
- Editar el archivo ```cms-app.env```
```bash
vim cms-app.env
```
- Configurar las variables de entorno de acuerdo a nuestras necesidades, ejemplo:
```env
DB_NAME=django_cms
DB_USER=cms_app
DB_PASSWORD=secret-password
DB_HOST=10.116.16.2
DB_PORT=5432

AWS_ACCESS_KEY_ID=secret-key-id
AWS_SECRET_ACCESS_KEY=secret-access-key
AWS_STORAGE_BUCKET_NAME=djangocms
AWS_S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
AWS_S3_REGION_NAME=nyc3

DEFAULT_PROFILE_PHOTO=profile_pics/perfil.png

EMAIL_HOST_USER=cms@mail.com
EMAIL_HOST_PASSWORD=secret-password

DJANGO_SETTINGS_MODULE=cms.profile.prod
DJANGO_ALLOWED_HOSTS=is2equipo10.me,www.is2equipo10.me,https://is2equipo10.me,https://www.is2equipo10.me
```
- Descargar las imágenes
```bash
docker compose pull
```
- Levantar los servicios
```bash
docker compose up -d
```
- Verificar el estado de los servicios
```bash
docker ps
```
- Resultado esperado
```bash
CONTAINER ID   IMAGE                         COMMAND                  CREATED          STATUS          PORTS                                       NAMES
a06c33dd7a98   estebanfern/cms-app:latest    "./entrypoint.sh"        38 minutes ago   Up 37 minutes   0.0.0.0:8000->8000/tcp, :::8000->8000/tcp   cms-app
8beff510d9c6   estebanfern/cms-docs:latest   "nginx -g 'daemon of…"   38 minutes ago   Up 37 minutes   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp     cms-docs
```
- Ahora volvemos a revisar nuestras configuraciones de NGINX en ```/etc/nginx/sites-available/```. Veremos que CertBot ya nos configuró toda la lógica de HTTPS, entonces lo que nos queda es redireccionar el tráfico a los puertos de nuestras aplicaciones y configurar los ```server_name```
- Para ```is2equipo10.me```
```bash
server_name is2equipo10.me www.is2equipo10.me;
```
```bash
location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
}
```
- Si queremos que NGINX maneje nuestros archivos estáticos agregamos otro ```location```
```bash
location /static/ {
        alias /path/to/staticfiles/;
}
```
- Para ```docs.is2equipo10.me```
```bash
server_name docs.is2equipo10.me www.docs.is2equipo10.me;
```
```bash
location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
}
```
- Recargamos NGINX
```bash
nginx -s reload
```
Con estas configuraciones nuestro servidor de aplicaciones ya está correctamente configurado y funcionando con un dominio y HTTPS.










