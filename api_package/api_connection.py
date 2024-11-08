import requests
import time
import numpy as np
import pandas as pd
import yfinance as yf


def get_exchange_rate():
    df = pd.DataFrame([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
    df.columns = ['EUR', 'GBP', 'USD', 'GBX', 'CAD', 'CHF']
    df.set_index(df.columns[0:2], inplace=True)
    np.fill_diagonal(df.values, 1)

    # to euro
    gbp = yf.Ticker('GBPEUR=X')
    usd = yf.Ticker('EUR=X')
    cad = yf.Ticker('CADEUR=X')
    chf = yf.Ticker('CHFEUR=X')

    # to gbp
    eur = yf.Ticker('EURGBP=X')
    usd2 = yf.Ticker('GBP=X')
    cad2 = yf.Ticker('CADGBP=X')
    chf2 = yf.Ticker('CHFGBP=X')

    for col in df.columns:
        if col == 'EUR':
            hist = eur.history(period="5d")
            df.loc['GBP', 'EUR'] = hist.tail(1)['Close'].item()
        elif (col == 'GBP') | (col == 'GBX'):
            hist = gbp.history(period="5d")
            df.loc['EUR', 'GBP'] = hist.tail(1)['Close'].item()
            df.loc['EUR', 'GBX'] = round((hist.tail(1)['Close'].item() / 100), 5)
            df.loc['GBP', 'GBX'] = 0.01
        else:
            if col == 'USD':
                hist1 = usd.history(period="5d")
                hist2 = usd2.history(period="5d")
            if col == 'CAD':
                hist1 = cad.history(period="5d")
                hist2 = cad2.history(period="5d")
            if col == 'CHF':
                hist1 = chf.history(period="5d")
                hist2 = chf2.history(period="5d")
            df.loc['EUR', col] = hist1.tail(1)['Close'].item()
            df.loc['GBP', col] = hist2.tail(1)['Close'].item()

    return df


def get_metadata(api_key):
    url = "https://live.trading212.com/api/v0/equity/account/info"
    headers = {"Authorization": f"{api_key}"}

    try:
        response = requests.get(url, headers=headers)
        metadata = response.json()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    return metadata


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
