import api_package.api_connection as connection
import pandas as pd
import numpy as np
import re


def is_etf(ticker):
    pattern = '.*_.*_EQ'
    if re.match(pattern, ticker):
        return 0
    else:
        return 1
    

def handle_base_df(base_df: pd.DataFrame):
    base_df['is_ETF'] = np.nan
    for i, row in base_df.iterrows():
        current_ticker = row['ticker']
        base_df.at[i, 'is_ETF'] = round(is_etf(current_ticker))
        #base_df['is_ETF'][i] = is_etf(current_ticker)
        if base_df['is_ETF'][i]:
            base_df.at[i, 'ticker'] = current_ticker.split('_')[0][:-1]
            #base_df['ticker'][i] = current_ticker.split('_')[0][:-1]
        else:
            base_df.at[i, 'ticker'] = current_ticker.split('_')[0]
            #base_df['ticker'][i] = current_ticker.split('_')[0]
    return base_df


def return_positions(api_key):
    positions = connection.get_positions(api_key)

    ticker = []
    shares = []
    avg_price = []
    current_price = []
    p_l = []
    p_l_fx = []

    for p in positions:
        ticker.append(p['ticker'])
        shares.append(p['quantity'])
        avg_price.append(p['averagePrice'])
        current_price.append(p['currentPrice'])
        p_l.append(p['ppl'])
        p_l_fx.append(p['fxPpl'])
    
    positions_df = pd.DataFrame({'ticker': ticker, 'shares': shares, 'avg_price': avg_price,
                                 'current_price': current_price, 'p_l': p_l, 'p_l_fx': p_l_fx})
    df = handle_base_df(positions_df)
    return df


def return_dividends(api_key):
    dividends = connection.get_dividends(api_key)
    
    tickers = []
    amounts = []
    pay_dates = []

    for div in dividends:
        tickers.append(div['ticker'])
        amounts.append(div['amountInEuro'])
        pay_dates.append(div['paidOn'])
    dividends_df = pd.DataFrame({'ticker': tickers, 'amount': amounts, 'pay_date': pay_dates})
    df = handle_base_df(dividends_df)
    return df


def return_balances(api_key):
    balances = connection.get_balances(api_key)
    cash = balances['free']
    amount_invested = balances['invested']
    portfolio_value = balances['total']
    current_p_and_l = balances['ppl']
    balances = {'cash': cash, 'amount_invested': amount_invested, 'account_value':
                portfolio_value, 'current_p_and_l': current_p_and_l}
    return balances
    