### Set Up for Windows

> Install modules via venv (Windows) 

```
$ virtualenv venv
$ .\venv\Scripts\activate
$ pip3 install -r requirements.txt
```

> Set Up Database

```
$ python manage.py makemigrations
$ python manage.py migrate
```

> Start the App

```
$ python manage.py runserver
```

At this point, the app runs at `http://127.0.0.1:8000/`
