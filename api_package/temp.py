import requests
import numpy as np
import pandas as pd
import yfinance as yf


def return_instruments():
    url = "https://live.trading212.com/api/v0/equity/metadata/instruments"

    headers = {"Authorization": "4340988ZFGzGjOePPGdcMAdhhYmWMiQjzfCY"}

    response = requests.get(url, headers=headers)

    instruments = response.json()

    ticker = []
    type = []
    currency_code = []

    for i in instruments:
        ticker.append(i['ticker'])
        type.append(i['type'])
        currency_code.append(i['currencyCode'])
    
    instruments_df = pd.DataFrame({'ticker': ticker, 'type': type, 'currency_code': currency_code})
    return instruments_df


def get_exchange_rate():
    df = pd.DataFrame([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    df.columns = ['EUR', 'GBP', 'USD']
    df.set_index(df.columns, inplace=True)
    np.fill_diagonal(df.values, 1)

    # to euro
    gbp = yf.Ticker('GBPEUR=X')
    usd = yf.Ticker('EUR=X')
    hist1 = gbp.history(period="5d")
    hist2 = usd.history(period="5d")
    df.loc['EUR', 'GBP'] = hist1.tail(1)['Close'].item()
    df.loc['EUR', 'USD'] = hist2.tail(1)['Close'].item()

    # to gbp
    eur = yf.Ticker('EURGBP=X')
    usd = yf.Ticker('GBP=X')
    hist1 = eur.history(period="5d")
    hist2 = usd.history(period="5d")
    df.loc['GBP', 'EUR'] = hist1.tail(1)['Close'].item()
    df.loc['GBP', 'USD'] = hist2.tail(1)['Close'].item()

    # to usd
    eur = yf.Ticker('EURUSD=X')
    gbp = yf.Ticker('GBPUSD=X')
    hist1 = eur.history(period="5d")
    hist2 = gbp.history(period="5d")
    df.loc['USD', 'EUR'] = hist1.tail(1)['Close'].item()
    df.loc['USD', 'GBP'] = hist2.tail(1)['Close'].item()

    return df


def main():
    '''instruments = return_instruments()
    print(instruments.head(20))'''
    df = get_exchange_rate()
    print(df)

if __name__ == '__main__':
    main()