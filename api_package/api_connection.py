import requests
import time


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
