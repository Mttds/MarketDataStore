# MarketDataStore
Flutter Web Application with MongoDB and Django Backend for market data storage and visualization. Built to try out Flutter/Dart.

Run the Django backend from the backend dir with: `python manage.py runserver`

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

| Type                              | URI                                                        |
| --------------------------------- | ---------------------------------------------------------- |
| Equities                          | http://\<host\>:\<port\>/equities                          |
| Dividends                         | http://\<host\>:\<port\>/dividends                         |
| Single Equity                     | http://\<host\>:\<port\>/equities/\<id\>                   |
| Single Dividend                   | http://\<host\>:\<port\>/dividends/\<id\>                  |
| All Dividends for an Equity       | http://\<host\>:\<port\>/equities/\<id\>/dividends         |
| Filtering by Equity label         | http://\<host\>:\<port\>/equities/?label=MSFT              |
| Filtering by Equity md_date       | http://\<host\>:\<port\>/equities/?md_date=2021-08-20      |
| Searching by Equity label         | http://\<host\>:\<port\>:8000/equities/?search=M           |

## MONGODB
Installed locally with URI "mongodb://127.0.0.1:27017" (default).
In the settings.py file the CLIENT does not need the URI since it's the default one, but would need one under the CLIENT structure plus the authentication method if it is enabled:

```
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'mddb',
        #'CLIENT': {
        #    'host': 'mongodb://127.0.0.1:27017'
        #}
    }
}
```

Each Django model is a MongoDB collection named <app_name>_<model> inside the database (mddb in this case).

## DATAFEEDERS
The datafeeders directory is used for feeding data with POST requests to the backend which will deserialize the JSON data into the Django Model using the ORM. The data from the model is then inserted into MongoDB as a document.

For now the only data feeding is done with equity_feeder.py which uses the Yahoo! Finance python API yfinance to retrieve Market/Historical/Dividend data.

Usage: equity_feeder.py [-h] --type TYPE --ticker TICKER [--sdate SDATE] [--edate EDATE] [--period PERIOD]

--type can be: EQMKT for today's market price, EQHIST for an historical price (generating a document with multiple nested historical dates is not yet possible), or EQDVD for dividends (Django model will need to be implemented as a subclass of the Equity model)