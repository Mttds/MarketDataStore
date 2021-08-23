import yfinance as yf
import datetime
import json
import requests

DJANGO_BACKEND_URL = 'http://localhost:8000'
# trailing slash needed with APPEND_SLASH set to True
# since our backend is in Django
## RuntimeError: You called this URL via POST, 
## but the URL doesn't end in a slash and you have APPEND_SLASH set.
## Django can't redirect to the slash URL while maintaining POST data.
## Change your form to point to localhost:8000/equities/ (note the trailing slash),
## or set APPEND_SLASH=False in your Django settings.
DJANGO_BACKEND_EQUITY_ENDPOINT = DJANGO_BACKEND_URL + '/equities/'

def print_separator():
    print('='*50)

# define lookup params
ticker_symbol = 'MSFT'
today = datetime.date.today()
yesterday = today - datetime.timedelta(1)
if(today.weekday() == 0): # monday
    yesterday = today - datetime.timedelta(3)
elif(today.weekday() == 6): # sunday
    yesterday = today - datetime.timedelta(2)

today_iso = today.isoformat()
yesterday_iso = yesterday.isoformat()
period = '1d'

# get data on this ticker
ticker_data = yf.Ticker(ticker_symbol)
info_data = ticker_data.info
industry = info_data["industry"]
current_price = info_data["currentPrice"]
long_name = info_data["longName"]
symbol = info_data["symbol"]
currency = info_data["currency"]
market_cap = info_data["marketCap"]
market = info_data["market"]
exchange = info_data["exchange"]
print_separator()
print("ticker: {0}".format(ticker_symbol))
print("period: {0}".format(period))
print("start: {0}".format(yesterday_iso))
print("end: {0}".format(yesterday_iso))
print_separator()

# get the historical prices for this ticker
ticker_dataframe = ticker_data.history(
    period=period, start=yesterday_iso, end=yesterday_iso
)

# see your data
print(ticker_dataframe.head())
print(ticker_dataframe.to_dict())

# build the JSON for the post request
key_conversion_map = {
    "Open" : "p_open",
    "High" : "p_high",
    "Low"  : "p_low",
    "Close": "p_close"
}

payload = {
    "label": symbol,
    "description": long_name,
    "md_date": yesterday_iso,
    "date_time": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
}

for k,v in ticker_dataframe.to_dict().items():
    if k in key_conversion_map.keys():
        # limit to 6 decimal places as our Django model has 6 decimal places
        payload[key_conversion_map[k]] = float("{:.6f}".format(list(v.values())[0]))

print_separator()
print("URL: {0}".format(DJANGO_BACKEND_EQUITY_ENDPOINT))
print("payload:\n{0}".format(json.dumps(payload, indent=4, sort_keys=True)))
print_separator()

# make the post request
try:
    r = requests.post(DJANGO_BACKEND_EQUITY_ENDPOINT, json=payload)
    http_status = r.status_code
    r.raise_for_status()
except requests.exceptions.HTTPError as err:
    raise SystemExit(err)

print("HTTP POST ended with {0} status code".format(http_status))
