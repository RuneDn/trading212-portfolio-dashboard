import api_package.api_connection as connection
import pandas as pd
import numpy as np


def return_metadata(api_key):
    metadata = connection.get_metadata(api_key)
    id = metadata['id']
    currency = metadata['currencyCode']
    return id, currency


def return_instruments(api_key):
    instruments = connection.get_instruments(api_key)
    ticker, type, currency_code, short_name = ([] for i in range(4))

    for i in instruments:
        ticker.append(i['ticker'])
        type.append(i['type'])
        currency_code.append(i['currencyCode'])
        short_name.append(i['shortName'])
    
    instruments_df = pd.DataFrame({'ticker': ticker, 'type': type, 'currency_code': currency_code,
                                   'short_name': short_name})
    return instruments_df


def return_positions(api_key, instruments_df):
    positions = connection.get_positions(api_key)
    ticker, shares, avg_price, current_price, p_l, p_l_fx = ([] for i in range(6))

    for p in positions:
        ticker.append(p['ticker'])
        shares.append(p['quantity'])
        avg_price.append(p['averagePrice'])
        current_price.append(p['currentPrice'])
        p_l.append(p['ppl'])
        p_l_fx.append(p['fxPpl'])
    
    positions_df = pd.DataFrame({'ticker': ticker, 'shares': shares, 'avg_price': avg_price,
                                 'current_price': current_price, 'p_l': p_l, 'p_l_fx': p_l_fx})
    
    positions_df['is_ETF'] = ''
    positions_df['currency'] = ''
    for i, row in positions_df.iterrows():
        positions_df.loc[i, 'ticker'] = instruments_df.loc[instruments_df['ticker'] == row['ticker'], 'short_name'].values[0]
        positions_df.loc[i, 'is_ETF'] = instruments_df.loc[instruments_df['ticker'] == row['ticker'], 'type'].values[0]
        positions_df.loc[i, 'currency'] = instruments_df.loc[instruments_df['ticker'] == row['ticker'], 'currency_code'].values[0]
    positions_df['is_ETF'] = np.where(positions_df['is_ETF'] == 'ETF', 1, 0)

    return positions_df


def return_dividends(api_key, instruments_df):
    dividends = connection.get_dividends(api_key)
    tickers, amounts, pay_dates = ([] for i in range(3))

    for div in dividends:
        tickers.append(div['ticker'])
        amounts.append(div['amountInEuro'])
        pay_dates.append(div['paidOn'])
    dividends_df = pd.DataFrame({'ticker': tickers, 'amount': amounts, 'pay_date': pay_dates})
    dividends_df['is_ETF'] = ''
    for i, row in dividends_df.iterrows():
        dividends_df.at[i, 'ticker'] = instruments_df.loc[instruments_df['ticker'] == row['ticker'], 'short_name'].values[0]
        dividends_df.at[i, 'is_ETF'] = instruments_df.loc[instruments_df['ticker'] == row['ticker'], 'type'].values[0]
    dividends_df['is_ETF'] = np.where(dividends_df['is_ETF'] == 'ETF', 1, 0)
    return dividends_df


def return_balances(api_key):
    balances = connection.get_balances(api_key)
    cash = balances['free']
    amount_invested = balances['invested']
    portfolio_value = balances['total']
    current_p_and_l = balances['ppl']
    balances = {'cash': cash, 'amount_invested': amount_invested, 'account_value':
                portfolio_value, 'current_p_and_l': current_p_and_l}
    return balances
    