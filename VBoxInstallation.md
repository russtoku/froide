# Installation

## Vagrant setup

 - `vagrant up`
 - `vagrant ssh`
 - `sudo aptitude update && sudo aptitude upgrade`
 - `sudo aptitude install python-pip --assume-yes`

## Application setup

 - `cd /vagrant`
 - `pip install -r requirements.txt` (might have to run multiple times)
 - `python manage.py syncdb --noinput`
 - `python manage.py runserver 0.0.0.0:8000`
 - `echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('root', 'froide@codeforhawaii.org', 'root')" | python manage.py shell`

## Testing the application

 - Open `http://127.0.0.1:50051` in a browser
