# Fintop

## Introducción

## Introducción

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
Luego, se instala supervisor en el entorno global. Este programa ejecuta automáticamente los comandos que se hayan especificado al iniciar la instancia. Por eso hay que instalarlo en el entorno global de la instancia EC2.

En la ruta /etc/supervisor/conf.d/ hay que crear el archivo gunicorn.conf:
```
[program:gunicorn]
command=/home/ec2-user/fintop/.venv/bin/gunicorn -c /home/ec2-user/fintop/gunicorn_config.py wisr.wsgi:application
directory=/home/ec2-user/fintop
user=ec2-user
autostart=true
autorestart=true
stdout_logfile=/var/log/gunicorn/gunicorn_stdout.log
stderr_logfile=/var/log/gunicorn/gunicorn_stderr.log

[group:guni]
programs:gunicorn
```
e incluirlo en la configuración global de supervisor, en etc/supervisor/supervisord.conf:

```
...
[include]
files = /etc/supervisor/conf.d/*.conf
```
Cada vez que se modifique ese archivo, hay que ejecutar:
```
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart all
```
Para comprobar el estado se ejecuta `supervisorctl status`

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
    server_name ec2-13-38-95-163.eu-west-3.compute.amazonaws.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /ruta/a/tu/directorio/de/estaticos;
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

Por último, hay que asegurarse de que tenemos una regla de seguridad para conexiones HTTP al puerto 80 en AWS.