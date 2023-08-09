# Deployment of Server APIs on Linux environment

## Install python and nginx

---

`sudo apt install python3-pip python-dev nginx`

## Install virtualenv

---

`sudo pip3 install virtualenv`

## Create a virtual environment

---

`virtualenv env`

## activate venv on linux

---

`source env/bin/activate`

## Install required Python packages

---

`pip3 install -r requirements.txt`

## Change location inside app/config.py

For eg:

change
`PDF_PATH="/path/to/deviceapp"`

to
`PDF_PATH="/home/user/Desktop/deviceapp/"`

## Create a sysyemd service

---

First close the activated virtual environment using

`deactivate`

then create a file using below command

`sudo vim /etc/systemd/system/app.service`

Copy the below code inside this file

```
[Unit]
#  specifies metadata and dependencies
Description=Gunicorn instance to serve myproject
After=network.target
# tells the init system to only start this after the networking target has been reached
# We will give our regular user account ownership of the process since it owns all of the relevant files
[Service]
# Service specify the user and group under which our process will run.
User=deviceapp
# give group ownership to the www-data group so that Nginx can communicate easily with the Gunicorn processes.
Group=www-data
# We'll then map out the working directory and set the PATH environmental variable so that the init system knows where our the executables for the process are located (within our virtual environment).
WorkingDirectory=/home/user/Desktop/deviceapp/
Environment="PATH=/home/user/Desktop/deviceapp/env/bin"
# We'll then specify the commanded to start the service
ExecStart=/home/user/Desktop/deviceapp/env/bin/gunicorn --workers 3 --bind unix:app.sock -m 007 'app:create_app()'
# This will tell systemd what to link this service to if we enable it to start at boot. We want this service to start when the regular multi-user system is up and running:
[Install]
WantedBy=multi-user.target
```

In above code change

- User: As per your machine
- WorkingDirectory: As per your "pwd"
- Environment: Only change path before /env with "pwd"
- ExecStart: Only change path before /env with "pwd"

- pwd - Present Working Directory`

## Start the app

---

`sudo systemctl start app`

`sudo systemctl enable app`

## configure nginx

---

`sudo vim /etc/nginx/sites-available/app`

Copy the below code inside this file

```
server {
listen 80;
server_name 192.168.0.111;

location / {
  include proxy_params;
  proxy_pass http://unix:/home/user/Desktop/deviceapp/app.sock;
    }
}
```

In above code change

- server_name : with ip of host
- put your pwd in http://unix:/home/user/Desktop/deviceapp/app.sock; before "/app.sock"

## Activate configuration

---

`sudo ln -s /etc/nginx/sites-available/app /etc/nginx/sites-enabled`

## Restart nginx

---

`sudo systemctl restart nginx`

`sudo ufw allow 'Nginx Full'`
