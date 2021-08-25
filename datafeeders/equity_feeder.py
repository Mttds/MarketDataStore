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
        'industry': industry,'country': country,'p_mkt': current_price,
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


def put_request(url, payload_as_dict):
    print_separator()
    print("URL: {0}".format(url))
    print("payload:\n{0}".format(json.dumps(payload_as_dict, indent=4, sort_keys=True)))

    # make the post request
    try:
        r = requests.put(url, json=payload_as_dict)
        http_status = r.status_code
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    except Exception as e:
        raise SystemExit(e)
    print("HTTP PUT ended with {0} status code".format(http_status))
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
        "date_time": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "md_date": str(list(ticker_dataframe.to_dict()['Open'])[0])[:10],
        "industry": ticker_info_dict['industry'],
        "country": ticker_info_dict['country'],
        "currency": ticker_info_dict['currency'],
        "market": ticker_info_dict['market'],
        "exchange": ticker_info_dict['exchange'],
        "market_cap": ticker_info_dict['market_cap'],
        "tickdata": [] # cannot have tickdata for past prices
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
        "p_mkt"  : "p_mkt"
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
        "industry": ticker_info_dict['industry'],
        "country": ticker_info_dict['country'],
        "currency": ticker_info_dict['currency'],
        "market": ticker_info_dict['market'],
        "exchange": ticker_info_dict['exchange'],
        "market_cap": ticker_info_dict['market_cap'],
        "tickdata": [
            {
                "p_mkt": ticker_info_dict[key_conversion_map['p_mkt']],
                "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
        ]
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
    
    print("HTTP GET for equity label {0} ended with {1} status code".format(symbol, http_status))
    return r.json()


def get_equity_by_label_and_date(symbol, md_date):
    url = DJANGO_BACKEND_EQUITY_ENDPOINT + "?label={0}&md_date={1}".format(symbol, md_date)
    try:
        r = requests.get(url)
        http_status = r.status_code
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    except Exception as e:
        raise SystemExit(e)
    
    print("HTTP GET for equity label {0} at md_date {1} ended with {2} status code".format(symbol, md_date, http_status))
    return r.json()


def get_dividends_by_equity_and_year(equity_id, ex_div_year):
    url = DJANGO_BACKEND_DIVIDEND_ENDPOINT + "?equity={0}&year={1}".format(equity_id, ex_div_year)
    try:
        r = requests.get(url)
        http_status = r.status_code
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    except Exception as e:
        raise SystemExit(e)
    
    print("HTTP GET for dividends for equity id {0} and exdivyear {1} ended with {2} status code".format(equity_id, ex_div_year, http_status))
    return r.json()


def get_dividends_by_equity(equity_id):
    url = DJANGO_BACKEND_DIVIDEND_ENDPOINT + "?equity={0}".format(equity_id)
    try:
        r = requests.get(url)
        http_status = r.status_code
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    except Exception as e:
        raise SystemExit(e)
    
    print("HTTP GET for dividends for equity id {0} ended with {1} status code".format(equity_id, http_status))
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
        "dividends": dividends_list,
        "date_time": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
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
    
    #=================================================================================
    # Build the payload for EQHIST, EQMKT, or EQDVD
    #=================================================================================
    if(feed_type == "EQHIST"):
        ticker_dataframe = get_ticker_hist_data(ticker_data, start_date, end_date, period)
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
        if ticker_dividends.empty:
            print("No dividends data found for the provided symbol {0} and year {1}".format(ticker_symbol, ex_div_year))
            sys.exit(1)

        # get the id field from the JSON GET request response
        # filtering by equity label
        # we will need it for the equity field in the dividend document
        # since it's the foreign key to the equity document
        # we take the ID of the last inserted Equity for a given symbol
        # since the lookup Dividends -> Equity is just for general information
        # and not to lookup prices/tickdata
        equity = get_equity_by_label(ticker_symbol)
        equity_id = equity[len(equity)-1]['id']
        payload = build_payload_eqdvd(ticker_dividends.to_dict(), equity_id, ex_div_year)
    else:
        print("--type should be EQHIST, EQMKT, EQDVD instead of {0}".format(feed_type))
        sys.exit(1)

    #=================================================================================
    # Make the POST/PUT request
    #=================================================================================
    if(feed_type == "EQHIST" or feed_type == "EQMKT"):
        # check if the label & md_date already exists in the database
        # if it does make a PUT request instead of a POST request
        equity = get_equity_by_label_and_date(ticker_symbol, payload['md_date'])
        if(len(equity) != 0 and len(payload['tickdata']) != 0):
            new_tickdata = payload['tickdata'][0]
            existing_tickdata = json.loads(equity[0]['tickdata']) # need to convert the json nested array object into a python list
            existing_tickdata.append(new_tickdata)
            payload['tickdata'] = existing_tickdata
        elif(len(equity) != 0):
            existing_tickdata = json.loads(equity[0]['tickdata'])
            payload['tickdata'] = existing_tickdata
        if(len(equity) == 0):
            post_request(DJANGO_BACKEND_EQUITY_ENDPOINT, payload)
        else:
            put_request(DJANGO_BACKEND_EQUITY_ENDPOINT + str(equity[0]['id']) + '/', payload)
    elif(feed_type == "EQDVD"):
        dividends = get_dividends_by_equity_and_year(payload['equity'], ex_div_year)
        print(dividends)
        if(len(dividends) == 0):
            post_request(DJANGO_BACKEND_DIVIDEND_ENDPOINT, payload)
        else:
            put_request(DJANGO_BACKEND_DIVIDEND_ENDPOINT + str(dividends[0]['id']) + '/', payload)

#=================================================================================
#=================================================================================
if __name__ == "__main__":
    main(sys.argv[1:])
