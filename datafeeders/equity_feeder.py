import yfinance as yf
import datetime
import json
import requests
import argparse
import sys

# trailing slash needed with APPEND_SLASH set to True
# since our backend is in Django
## RuntimeError: You called this URL via POST, 
## but the URL doesn't end in a slash and you have APPEND_SLASH set.
## Django can't redirect to the slash URL while maintaining POST data.
## Change your form to point to localhost:8000/equities/ (note the trailing slash),
## or set APPEND_SLASH=False in your Django settings.
DJANGO_BACKEND_URL = 'http://localhost:8000'
DJANGO_BACKEND_EQUITY_ENDPOINT = DJANGO_BACKEND_URL + '/equities/'
DJANGO_BACKEND_DIVIDEND_ENDPOINT = DJANGO_BACKEND_URL + '/dividends/'

def print_separator():
    print('='*50)


def get_ticker_data(ticker):
    return yf.Ticker(ticker)


def get_ticker_hist_data(ticker_data, start_date, end_date, period):
    print_separator()
    print("period: {0}".format(period))
    print("start date: {0}".format(start_date))
    print("end date: {0}".format(end_date))
    print_separator()

    sdate_delta1d = \
        (datetime.datetime.strptime(start_date, "%Y-%m-%d")
        + datetime.timedelta(days=1)).isoformat()[:10]
    edate_delta1d = \
        (datetime.datetime.strptime(end_date, "%Y-%m-%d")
        + datetime.timedelta(days=1)).isoformat()[:10]

    # get the historical prices for this ticker
    # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    # it will return the data 1 day before the actual start and end provided
    # hence we add 1 with datetime.timedelta() to the input dates
    ticker_dataframe = ticker_data.history(
        #period=period, 
        start=sdate_delta1d,
        end=edate_delta1d
    )
    return ticker_dataframe


def get_ticker_info(ticker_data):
    info_data = ticker_data.info
    if(len(info_data) == 0 or 'symbol' not in info_data.keys()):
        return None

    industry = info_data["industry"]
    country = info_data["country"]
    current_price = info_data["currentPrice"]
    long_name = info_data["longName"]
    symbol = info_data["symbol"]
    currency = info_data["currency"]
    market_cap = info_data["marketCap"]
    market = info_data["market"]
    exchange = info_data["exchange"]
    p_high = info_data["regularMarketDayHigh"] # dayHigh also exists
    p_low = info_data["regularMarketDayLow"] # dayLow also exists
    p_close = info_data["regularMarketPreviousClose"] # previousClose also exists
    p_open = info_data["regularMarketOpen"] # open also exists
    return {
        'industry': industry,'country': country,'current_price': current_price,
        'long_name': long_name,'symbol': symbol,'currency': currency,
        'market_cap': market_cap,'market': market,'exchange': exchange,
        'p_high': p_high, 'p_low': p_low, 'p_close': p_close, 'p_open': p_open
    }


def get_ticker_dividends(ticker_data):
    return ticker_data.dividends


def post_request(url, payload_as_dict):
    print_separator()
    print("URL: {0}".format(url))
    print("payload:\n{0}".format(json.dumps(payload_as_dict, indent=4, sort_keys=True)))
    print_separator()

    # make the post request
    try:
        r = requests.post(url, json=payload_as_dict)
        http_status = r.status_code
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    except Exception as e:
        raise SystemExit(e)
    print("HTTP POST ended with {0} status code".format(http_status))
    return http_status


def get_yesterday_iso_date():
    today = datetime.date.today()
    
    if(today.weekday() == 0): # monday
        yesterday = today - datetime.timedelta(days=3)
    elif(today.weekday() == 6): # sunday
        yesterday = today - datetime.timedelta(days=2)
    else:
        yesterday = today - datetime.timedelta(days=1)

    return yesterday.isoformat()


def get_today_iso_date():
    return datetime.date.today().isoformat()


def build_payload_eqhist(ticker_dataframe, ticker_info_dict):
    key_conversion_map = {
        "Open" : "p_open",
        "High" : "p_high",
        "Low"  : "p_low",
        "Close": "p_close",
        "Date": "md_date"
    }

    # for md_date get the first 10 characters (yyyy-mm-dd)
    # from the timestamp of any of the fields
    payload = {
        "label": ticker_info_dict['symbol'],
        "description": ticker_info_dict['long_name'],
        "md_date": str(list(ticker_dataframe.to_dict()['Open'])[0])[:10],
        "date_time": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")#,
        #"p_market": None
    }

    for k,v in ticker_dataframe.to_dict().items():
        if k in key_conversion_map.keys():
            # limit to 6 decimal places as our Django model has 6 decimal places
            payload[key_conversion_map[k]] = float("{:.6f}".format(list(v.values())[0]))
    return payload


def build_payload_eqmkt(ticker_info_dict):
    key_conversion_map = {
        "p_open" : "p_open",
        "p_high" : "p_high",
        "p_low"  : "p_low",
        "p_close": "p_close",
        "p_market": "current_price"
    }

    payload = {
        "label": ticker_info_dict['symbol'],
        "description": ticker_info_dict['long_name'],
        "date_time": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "md_date": get_today_iso_date(),
        "p_low": ticker_info_dict[key_conversion_map['p_low']],
        "p_high": ticker_info_dict[key_conversion_map['p_high']],
        "p_open": ticker_info_dict[key_conversion_map['p_open']],
        "p_close": ticker_info_dict[key_conversion_map['p_close']],
        "p_market": ticker_info_dict[key_conversion_map['p_market']]
    }
    return payload


def get_equity_by_label(symbol):
    url = DJANGO_BACKEND_EQUITY_ENDPOINT + "?label={0}".format(symbol)
    try:
        r = requests.get(url)
        http_status = r.status_code
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    except Exception as e:
        raise SystemExit(e)
    
    print("HTTP POST ended with {0} status code".format(http_status))
    return r.json()


def build_payload_eqdvd(dividends_dict, equity_id, ex_div_year):
    dividends_list = []

    for k,v in dividends_dict.items():
        ex_div_date = str(k)[:10]
        dividend = v
        # only dividends for the input year will be added to the payload
        if(ex_div_date[:4] == ex_div_year): 
            dividends_list.append(
                {"ex_div_date": ex_div_date, "dividend": dividend}
            )

    payload = {
        "year": ex_div_year,
        "equity": equity_id,
        "dividends": dividends_list
    }
    return payload

def main(argv):
    parser = argparse.ArgumentParser(description='Equity Feeder for Django MongoDB backend.')
    parser.add_argument('--type',      type=str, required=True)
    parser.add_argument('--ticker',    type=str, required=True)
    parser.add_argument('--sdate',     type=str)
    parser.add_argument('--edate',     type=str)
    parser.add_argument('--period',    type=str)
    parser.add_argument('--exdivyear', type=str)
    args = parser.parse_args()

    # get params
    ticker_symbol = args.ticker
    period = args.period if args.period is not None else '1d'
    start_date = args.sdate if args.sdate is not None else get_yesterday_iso_date()
    end_date = args.edate if args.edate is not None else get_yesterday_iso_date()
    feed_type = args.type
    ex_div_year = args.exdivyear if args.exdivyear is not None else '1900'

    ticker_data = get_ticker_data(ticker_symbol)  
    ticker_info_dict = get_ticker_info(ticker_data)
    
    if(feed_type == "EQHIST"):
        ticker_dataframe = get_ticker_hist_data(ticker_data, start_date, end_date, period)
        #print(ticker_dataframe.to_dict())
        if ticker_dataframe.empty:
            print("No historical data found for the provided --sdate {0} and --edate {1}".format(start_date, end_date))
            sys.exit(1)
        payload = build_payload_eqhist(ticker_dataframe, ticker_info_dict)
    elif(feed_type == "EQMKT"):
        if ticker_info_dict == None:
            print("No data found for the provided symbol {0}".format(ticker_symbol))
            sys.exit(1)
        payload = build_payload_eqmkt(ticker_info_dict)
    elif(feed_type == "EQDVD"):
        ticker_dividends = get_ticker_dividends(ticker_data)
        #print(ticker_dividends.head(100))
        #print(ticker_dividends.to_dict())

        if ticker_dividends.empty:
            print("No dividends data found for the provided symbol  {0} and year {1}".format(ticker_symbol, ex_div_year))
            sys.exit(1)

        # get the id field from the JSON GET request response
        # filtering by equity label
        # we will need it for the equity field in the dividend document
        # since it's the foreign key to the equity document
        equity_id = get_equity_by_label(ticker_symbol)[0]['id']
        payload = build_payload_eqdvd(ticker_dividends.to_dict(), equity_id, ex_div_year)
    else:
        print("--type should be EQHIST, EQMKT, EQDVD instead of {0}".format(feed_type))
        sys.exit(1)

    if(feed_type == "EQHIST" or feed_type == "EQMKT"):
        post_request(DJANGO_BACKEND_EQUITY_ENDPOINT, payload)
    elif(feed_type == "EQDVD"):
        post_request(DJANGO_BACKEND_DIVIDEND_ENDPOINT, payload)

if __name__ == "__main__":
    main(sys.argv[1:])
