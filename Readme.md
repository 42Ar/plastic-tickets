# Plastic Tickets

This is a Django project for providing and managing a 3d-printing service.

For that the [django-plastic-tickets](https://github.com/hd1ex/django-plastic-tickets)
app is used.

This project additionally provides a login view, the django admin interface
 and a html base which renders the breadcrumbs.
Additionally a [bootstrap](https://getbootstrap.com/) css theme is provided.

## Features

Here are some features this project provides:
 - (STL) file upload and hosting
 - basic access control
   - a user can only access its associated data
   - staff can access all data
 - guided form for ticket creation
   - every option can contain a detailed markdown description
     - descriptions can be translated to all configured languages
     - they are stored in the database and can be updated as needed
   - the user can add as many models (files) to a ticket
     and has to specify for each file
     - a print count
     - a desired production method (FFF, SLA, ...)
     - the desired material type (PLA, PETG, ...) based on current stock
     - the desired material color
   - the user can add a custom message containing more details about the models
 - sending plain text ticket emails, while respecting mail standards such as
   [RFC 3676](https://tools.ietf.org/html/rfc3676) 
 - basic material management (filament, resin, ...)
 - german translation

## Getting it up and running
### Basic development setup

First make sure the following dev dependencies are installed on your system:
 - python3
 - git
 - make _(optional)_
 
Then proceed by cloning the projects repository and fetching its submodule:
 ```shell script
git clone https://github.com/hd1ex/plastic-tickets.git
cd plastic-tickets
git submodule update --init
```

Now install a [python venv](https://docs.python.org/3/library/venv.html) 
with the projects dependencies by running
```shell script
make install
```

You can also do this by running the commands listed in the 
[Makefile](Makefile) manually.

Now you can activate the venv by running
```shell script
source venv/bin/activate
```

To create the database and an admin user just run
```shell script
python manage.py migrate
python manage.py createsuperuser
```

Now you probably should enable the debug mode in
 [the Django settings](plastic_tickets/settings.py) (line 31).

After that, you can simply run the django dev server with
```shell script
python manage.py runserver
```

and visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/)   
You should see the index view of the website.  
Now a Django admin (super user) can add data and other users at
[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

For some initial data, there is also a fixture provided at
[django-plastic-tickets/django_plastic_tickets/fixtures/initial_data.json](django-plastic-tickets/django_plastic_tickets/fixtures/initial_data.json).
To load that data just run
```shell script
python manage.py loaddata django-plastic-tickets/django_plastic_tickets/fixtures/initial_data.json
```

### Deployment

For deployment you need the following tools:
 - git
 - docker
 - docker-compose
 
After you made sure they are installed, 
 proceed by cloning the repo and its submodule:
 ```shell script
git clone https://github.com/hd1ex/plastic-tickets.git
cd plastic-tickets
git submodule update --init
```
 
Now you want to **configure your deployment** by adjusting
 [the Django settings](plastic_tickets/settings.py) and the
 [`server_name` in the nginx config](nginx/plastic-tickets-nginx.conf).   
Additionally you maybe want to save your config changes as a patch:
```shell script
mkdir patches
echo '*' > patches/.gitignore
git diff > patches/deployment_config.patch
```

After that you can start the website as container:
```shell script
docker-compose up -d
```

To setup a first admin user and (optionally) add the provided initial data,
 start a shell in the container by running
```shell script
docker exec -it shared_cash_shared-cash_1 /bin/sh
```
and run
```shell script
python manage.py createsuperuser
python manage.py loaddata django-plastic-tickets/django_plastic_tickets/fixtures/initial_data.json # optional
exit
```

Now you can visit your website and login with the admin user
(visit [`http://localhost`](http://localhost) if you left the default value).

In the long run you probably want to set up some kind of a backup system.   
All interesting files live in docker volumes. To list these run
```shell script
docker volume ls
```

#### Enabling https

You probably want to add a ssl certificate to enable https.    
To do this with [Let's Encrypt's](https://letsencrypt.org) you can open a shell
 in the container running nginx and generate one using
 [certbot](https://certbot.eff.org/) 
```shell script
docker exec -ti plastic-tickets_web_1 ash
# In the container run:
apk add certbot-nginx
certbot --nginx
```

## Contributing

Please read [Contributing.md](Contributing.md) for this.
