import requests
import time
import numpy as np
import pandas as pd
import yfinance as yf


def get_exchange_rate():
    df = pd.DataFrame([[0, 0, 0], [0, 0, 0]])
    df.columns = ['EUR', 'GBP', 'USD']
    df.set_index(df.columns[0:2], inplace=True)
    np.fill_diagonal(df.values, 1)

    # to euro
    gbp = yf.Ticker('GBPEUR=X')
    usd = yf.Ticker('EUR=X') # TODO: change to gbx
    hist1 = gbp.history(period="5d")
    hist2 = usd.history(period="5d")
    df.loc['EUR', 'GBP'] = hist1.tail(1)['Close'].item()
    df.loc['EUR', 'USD'] = hist2.tail(1)['Close'].item()

    # to gbp
    eur = yf.Ticker('EURGBP=X')
    usd = yf.Ticker('GBP=X') # TODO: change to gbx
    hist1 = eur.history(period="5d")
    hist2 = usd.history(period="5d")
    df.loc['GBP', 'EUR'] = hist1.tail(1)['Close'].item()
    df.loc['GBP', 'USD'] = hist2.tail(1)['Close'].item()

    print(df)
    return df


def get_instruments(api_key):
    url = "https://live.trading212.com/api/v0/equity/metadata/instruments"
    headers = {"Authorization": f"{api_key}"}

    try:
        response = requests.get(url, headers=headers)
        instruments = response.json()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    return instruments


def get_balances(api_key):
    url = "https://live.trading212.com/api/v0/equity/account/cash"
    headers = {"Authorization": f"{api_key}"}
    try:
        response = requests.get(url, headers=headers)
        balances = response.json()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    return balances


def get_positions(api_key):
    url = "https://live.trading212.com/api/v0/equity/portfolio"
    headers = {"Authorization": f"{api_key}"}
    try:
        response = requests.get(url, headers=headers)
        positions = response.json()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    return positions


def get_dividends(api_key):
    url = "https://live.trading212.com/api/v0/history/dividends"
    headers = {"Authorization": f"{api_key}"}
    dividends = {'items': [], 'nextPagePath': ""}
    while True:
        if len(dividends["items"]) == 0:
            query = {"cursor": "", "ticker": "", "limit": "50"}
        else: 
            query = {"cursor": f"{dividends['nextPagePath']}", "ticker": "", "limit": "50"}
        try:
            response = requests.get(url, headers=headers, params=query)
            response = response.json()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        
        if 'errorMessage' in response:
            errorMessage = response['errorMessage']
            print(errorMessage)
            time.sleep(61)
            response = requests.get(url, headers=headers, params=query)
            response = response.json()

        dividends['items'].extend(response['items'])
        if response['nextPagePath'] is not None:
            dividends.update({'nextPagePath': response['nextPagePath'].split('=')[2]})
        else:
            break
    return dividends["items"]
