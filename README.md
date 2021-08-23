# MarketDataStore
Flutter Web Application with MongoDB and Django Backend for market data storage and visualization. Built to try out Flutter/Dart.

Run the Django backend with: `python manage.py runserver`
The MongoDB server should be running locally with URI mongodb://127.0.0.1:27017 (default MongoDB URI).

## GENERAL
Usually Django will create a subdirectory with the same name as the project directory (i.e backend/backend where the first directory is the project root dir) where it stores the settings.py and all the other configuration files. The directory was renamed config just to make it clearer and all the references to the backend subdirectory were changed. Moreover, Django usually creates the apps (Django apps) directories as children of the project root directory, but in this project an additional subdirectory (apps) has been created to store all the apps that will be created using Django's built-in commands.

The MongoDB connector in order to use Django's built-in ORM is djongo. (https://github.com/nesdis/djongo). Otherwise pymongo (djongo relies on pymongo anyway) or mongoengine libraries should be used to construct the documents and interface with MongoDB. With djongo it's possible to use Django's built-in ORM as with a relational database.
In order to use it the requirements are:
- Python 3.6 or higher.
- MongoDB 3.4 or higher.
- Django version lower than 3.1 (3.0.5 used).

Also, the sqlparse (used by Django to convert ORM -> SQL -> mongoDB document insertion) library needs to be version 0.2.4 (lower than 0.3) otherwise Django's migrations won't work.

## REST API
Library djangorestframework is used for the REST API and needs to be added to the INSTALLED_APPS list in the settings.py as rest_framework and included as `path('<app_name>/', include('apps.<app_name>.urls'))` in the config/urls.py file (apps.<app_name>.urls is the urls python file under apps/<app_name> where all the REST endpoints will be specified for that app and need to be included in the main urls.py file. The endpoint is included with '<app_name>' as the base URI, so all the endpoints specified in apps.<app_name>.urls are relative to <app_name>.

- List equities:
>http://<host>:<port>/equities

- Single equity:
>http://<host>:<port>/equities/<id>
For example:

>{
>    "id": 1,
>    "date_time": "2021-08-22T12:17:28.848320Z",
>    "label": "MSFT",
>    "description": "Microsoft",
>    "p_high": "100.213000",
>    "p_close": "100.213000",
>    "p_low": "100.214000",
>    "p_open": "100.102000"
>}

- Filtering by label
>http://<host>:<port>/equities/?label=MSFT

- Filtering by md_date (market data date)
>http://localhost:8000/equities/?md_date=2021-01-01

- Searching by label/md_date (the example would retur labels containing M such as MSFT)
>http://localhost:8000/equities/?search=M

## MONGODB
Installed locally with URI "mongodb://127.0.0.1:27017" (default).
In the settings.py file the CLIENT does not need the URI since it's the default one, but would need one under the CLIENT structure plus the authentication method if it is enabled:

>DATABASES = {
>    'default': {
>        'ENGINE': 'djongo',
>        'NAME': 'mddb',
>        #'CLIENT': {
>        #    'host': 'mongodb://127.0.0.1:27017'
>        #}
>    }
>}
