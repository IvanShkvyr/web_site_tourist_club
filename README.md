### Set Up for Windows

> Install modules via venv (Windows) 

```
virtualenv venv
venv\Scripts\activate
pip3 install -r requirements.txt
```

> Set Up Database

```
python manage.py makemigrations
python manage.py migrate
```
> Download Redis:

Відкрийте веб-сайт Redis для Windows, який знаходиться за адресою https://github.com/microsoftarchive/redis/releases.
У секції "Assets" знайдіть останній стабільний реліз Redis для Windows.
Завантажте ZIP-архів, що відповідає вашій версії Windows (32-біт або 64-біт).
Після завантаження ZIP-архіву розпакуйте його до бажаного місця на вашому комп'ютері, наприклад, C:\Redis.

> Run Redis:

Відкрийте командний рядок Windows (Command Prompt) або PowerShell.
Перейдіть до розпакованої папки Redis, наприклад, C:\Redis.
Виконайте команду

```
 redis-server.exe
```

для запуску Redis сервера.
Ви повинні побачити повідомлення, що сервер Redis успішно запущено.
Після запуску Redis сервера ви можете використовувати його у вашому Django проекті для налаштування з'єднання з Celery.

> Start the App

```
python manage.py runserver
```

At this point, the app runs at `http://127.0.0.1:8000/`


> Launching the Celery system / Запуск системи Celery

* Відкрийте новий термінал або командний рядок.
* Укажіть шлях до вашого проекту Django, де знаходиться файл celery_config.py.
* У командному рядку введіть наступну команду:

```
celery -A adventure_net worker --loglevel=info
```
Важливо, щоб ви виконали цю команду після запуску сервера Django, оскільки Celery використовує вашу Django-додаток для виконання завдань.

Зауважте, що ви повинні переконатися, що ви перебуваєте в потрібному середовищі (virtual environment), де ви встановили всі необхідні залежності для Celery та Redis.і