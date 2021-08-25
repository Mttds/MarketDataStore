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

| Type                              | URI                                                            |
| --------------------------------- | -------------------------------------------------------------- |
| Equities                          | http://\<host\>:\<port\>/equities                              |
| Dividends                         | http://\<host\>:\<port\>/dividends                             |
| Single Equity                     | http://\<host\>:\<port\>/equities/\<id\>                       |
| Single Dividend                   | http://\<host\>:\<port\>/dividends/\<id\>                      |
| All Dividends for an Equity       | http://\<host\>:\<port\>/equities/\<id\>/dividends             |
| Filtering by Equity label         | http://\<host\>:\<port\>/equities/?label=MSFT                  |
| Filtering by Equity md_date       | http://\<host\>:\<port\>/equities/?md_date=2021-08-20          |
| Filtering by Dividend year        | http://\<host\>:\<port\>/dividends/?year=2021                  |
| Filtering by Dividend equity id   | http://\<host\>:\<port\>/dividends/?equity=10                  |
| Combined filtering by Equity      | http://\<host\>:\<port\>/equities/?md_date=2021-08-20&label=AA |
| Combined filtering by Dividends   | http://\<host\>:\<port\>/dividends/?year=2021&equity=10        |
| Searching by Equity label         | http://\<host\>:\<port\>/equities/?search=M                    | 

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

## MODELS

- Equity
The Equity models contains a tickdata array which can be updated with each PUT request for the same label/md_date.
If an historical price does not already exist,  or it does exist but with an empty tickdata, it will be inserted/updated with an empty tickdata structure.
This is because we cannot have tickdata for historical prices, unless we collected and inserted that data during that trading day (in that case updating the document would most likely yield the same document with a PUT request given the same market data source).

```
{
    "country": "United States",
    "currency": "USD",
    "date_time": "2021-08-25T19:06:42.776746Z",
    "description": "Tesla, Inc.",
    "exchange": "NMS",
    "industry": "Auto Manufacturers",
    "label": "TSLA",
    "market": "us_market",
    "market_cap": 706534047744,
    "md_date": "2021-08-25",
    "p_close": 708.49,
    "p_high": 716.97,
    "p_low": 704.07,
    "p_open": 707.03,
    "tickdata": [
        {
            "p_mkt": "715.57",
            "timestamp": "2021-08-25T18:59:16.512000"
        },
        {
            "p_mkt": 713.66,
            "timestamp": "2021-08-25T19:06:42.776799Z"
        }
    ]
}
```

In this way we will have multiple documents for a single Equity, each containing information for that trading date (hence unique document by label/md_date).

- Dividend
The Dividend model actually describes a dividends list for a given year. Dividend data does not need the same frequency of Equity prices, so we can have one document per year that can be updated accordingly and will be linked by the equity relation which points to the last Equity id inserted for the Security related to the dividends. In this example, equity = 31 points to the last inserted document by md_date/label for MSFT (Microsoft). The "foreign key" (even if it's a documents database and foreign key is not the appropriate terminology) for the Equity lookup is needed just to get the correct Equity label and its market information (market, exchange, country, ...) which do not change. This is why it's not a problem if the dividends list for year 2021 points to a Security's document for a md_date which is not the latest, since we can lookup the same Equity label and its underlying information (but not the prices since they describe an old trading date).

```
{
    "date_time": "2021-08-25T18:14:44.249663Z",
    "dividends": [
        {
            "dividend": 0.56,
            "ex_div_date": "2021-02-17"
        },
        {
            "dividend": 0.56,
            "ex_div_date": "2021-05-19"
        },
        {
            "dividend": 0.56,
            "ex_div_date": "2021-08-18"
        }
    ],
    "equity": 31,
    "year": "2021"
}
```

## DATAFEEDERS
The datafeeders directory is used for feeding data with POST requests to the backend which will deserialize the JSON data into the Django Model using the ORM. The data from the model is then inserted into MongoDB as a document.

For now the only data feeding is done with equity_feeder.py which uses the Yahoo! Finance python API yfinance to retrieve Market/Historical/Dividend data.

```
usage: equity_feeder.py [-h] --type TYPE --ticker TICKER [--sdate SDATE] [--edate EDATE] [--period PERIOD] [--exdivyear EXDIVYEAR]
examples:
    python equity_feeder.py --type EQHIST --ticker GOOG --sdate 2021-08-24 --edate 2021-08-24
    python equity_feeder.py --type EQHIST --ticker GOOG # assumes --sdate and --edate as yesterday not considering saturday/sunday
    python equity_feeder.py --type EQDVD --ticker GOOG
    python equity_feeder.py --type EQMKT --ticker MSFT
```

--type: 
- EQMKT for today's market price
- EQHIST for an historical price
- EQDVD for dividends (Django model implemented with an equity field which stores the ID to one of the documents of the related Equity in order to easily retrieve the Security info).

--exdivyear:
- select the year for the ex_dividend_date and their values that will be inserted as nested documents in MongoDB. In this way we will have multiple Dividend documents, each one containing the array of dividends for the specified exdivyear.

If there is already a document with the same md_date/label for Equities and equity/year for Dividends, the HTTP request will be a PUT request updating the existing document. The lookup is performed with GET requests using the filtering described in the REST API section.