# Fintop

## Introducción

## Introducción

## Configuración de AWS

### Crear instancia de EC2. Automáticamente se le asocia un volumen EBS que permite instalar una base de datos.

### Instalar Python 3.11.

La instancia de EC2 con AL 2023 viene por defecto con Python 3.9. Para instalar Python 3.11 o una versión superior, instalar `pyenv`.

Instalar las dependencias necesarias para construir diferentes versiones de Python:

```
sudo yum install -y gcc zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel
```
Instalar Git
```
sudo yum install git
```

Instalar pyenv mediante curl o wget:

```
curl https://pyenv.run | bash
```
Configurar el entorno añadiendo pyenv al PATH:

```
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
```

Luego aplicar los cambios:

```
source ~/.bashrc
```

Ahora se puede usar `pyenv` para instalar Python 3.11 y establecer como la predeterminada para el usuario. Se puede comprobar con python3 --version:

```
pyenv install 3.11.x
pyenv global 3.11.x
python3 --version
```


### Instalar PostgreSQL

https://hbayraktar.medium.com/how-to-install-postgresql-15-on-amazon-linux-2023-a-step-by-step-guide-57eebb7ad9fc

Instalar tanto el cliente como el servidor de PostgreSQL:

```
sudo dnf update
sudo dnf install postgresql15.x86_64 postgresql15-server -y
```
Iniciarlizar la BD:

```
sudo postgresql-setup --initdb
```

Habilitar el servicio de PostgreSQL en `systemctl` para que se ejecute al arrancar automáticamente.
```
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo systemctl status postgresql
```
Por seguridad, usar una buena contraseña para el admin (B*****um$.):
```
# Change the ssh user password:
sudo passwd postgres

# Log in using the Postgres system account:
su - postgres

# Now, change the admin database password:
psql -c "ALTER USER postgres WITH PASSWORD 'your-password';"
exit
```
Accede al archivo de configuración `/var/lib/pgsql/data/postgresql.conf` y hazle una copia:

```
sudo cp /var/lib/pgsql/data/postgresql.conf /var/lib/pgsql/data/postgresql.conf.bck
```
Y luego modifica `listen_adresses = 'localhost'` a `'*'` si se quiere permitir que cualquiera pueda acceder a la base de datos.

Luego se modifica el archivo de configuración `/var/lib/pgsql/data/pg_hba.conf` despues de hacerle una copia:
```
sudo cp /var/lib/pgsql/data/pg_hba.conf /var/lib/pgsql/data/pg_hba.conf.bck
```
Se cambia la identidad a *md5* para permitir conexiones. Si se ha creado un usuario específico para la DB de Django, *otorgarle los permisos necesarios*.
Finalmente se reinicia el servicio para aplicar los cambios:
```
sudo systemctl restart postgresql
```
7. Si se instala psycopg2, instalar mejor psycopg2-binary porque la otra versión dice que necesita pg_config y no lo encuentra.
8. Crear claves ssh y asociarlas a github.
9. Clonar repositorio.

## Configuración de Gunicorn

En primer lugar, hay que instalar `gunicorn` en el entorno virtual de la aplicación.

Luego, se añade este archivo a la carpeta del proyecto de Django:

gunicon_config.py
```
command = '/home/ec2-user/fintop/.venv/bin/gunicorn'
pythonpath = '/home/ec2-user/fintop'
bind = '0.0.0.0:8000'
workers = 3
```
Se crea el servicio en `systemctl` para gunicorn con `sudo nano /etc/systemd/system/gunicorn.service` y se le añade la configuración, que puede ser algo así:

```
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/fintop
ExecStart=/home/ec2-user/fintop/.venv/bin/gunicorn -c /home/ec2-user/fintop/gunicorn_config.py wisr.wsgi:application
Restart=always
StandardOutput=file:/var/log/gunicorn/gunicorn_stdout.log
StandardError=file:/var/log/gunicorn/gunicorn_stderr.log

[Install]
WantedBy=multi-user.target
```

No olvidar crear las carpetas y archivos de los logs.

Para releer el archivo de configuración:
```
sudo systemctl daemon-reload
```
Para habilitar el servicio para que se inicie automáticamente en el arranque:
```
sudo systemctl enable gunicorn.service
```
Para arrancar el servicio en el momento actual:
```
sudo systemctl start gunicorn.service
```
Y cuando se hagan cambios en el proyecto de django, utilizar `sudo systemctl restart gunicorn.service`.
Para comprobar el estado se ejecuta `sudo systemctl status gunicorn.service`

## Configuración de Nginx

Hay que entender los dos puertos de la instancia que nos afectan:

- Puerto 8000: Es el puerto en el que actualmente está configurado Gunicorn para escuchar. Por lo tanto, las peticiones a tu servidor que llegan a este puerto serán atendidas por tu aplicación Django a través de Gunicorn. Gunicorn está configurado para escuchar en el puerto 8000.

- Puerto 80: Es el puerto estándar para tráfico HTTP. Cuando un usuario ingresa una dirección web en su navegador, por defecto el navegador intentará comunicarse a través del puerto 80.

Cuando tienes un servicio como Gunicorn escuchando en un puerto que no es el 80 (o 443 para HTTPS), normalmente se utiliza un servidor web como Nginx o Apache como proxy inverso para reenviar las peticiones del puerto 80 al puerto donde Gunicorn está escuchando (8000 en este caso).

En primer lugar, instalar Nginx en EC2:

```
sudo yum install nginx
```

Se crea un archivo de configuración de nginx en /etc/nginx/conf.d/fintop.conf. Este archivo se incluye automáticamente en la conifiguración global de nginx:

```
server {
    listen 80;
    server_name ec2-51-44-13-202.eu-west-3.compute.amazonaws.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        alias /home/ec2-user/fintop/staticfiles/;
    }
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Se ejecuta el comando `sudo nginx -t` y `sudo systemctl restart nginx` y ya automáticamente redirige del puerto 80 al 8000.

Por último, hay que 

### Resolución de problemas

#### 1. No se obtiene respuesta del servidor en el navegador.

Asegurarse de que tenemos una regla de seguridad para conexiones HTTP al puerto 80 en AWS.

#### 2. No se ven los archivos estáticos.

- Revisar que está configurado correctamente la configuración de `nginx`.
- Haber hecho `python manage.py collectstatic` y que estén los archivos estáticos en STATIC_ROOT.
- Revisar logs en `/var/log/nginx/error.log`.
- Si es problema de permisos, revisar que el usuario de `nginx` tenga acceso a la carpeta de los estáticos y a sus directorios padres. Lo normal es que la carpeta del usuario ec2-user esté restringida y haya que darle acceso a nginx con `chmod 755 ec2-user/`.