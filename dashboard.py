import pandas as pd
import streamlit as st
from api_package import return_values as api
from api_package import api_connection as connection
from plots import position_plots as pplts
from plots import dividend_plots as dplts


@st.cache_data(show_spinner="Fetching data from trading 212")
def load_data(api_key):
    _, acc_currency = api.return_metadata(api_key)
    exchange_rates_df = connection.get_exchange_rate()
    instruments = api.return_instruments(api_key)
    positions_df_temp = api.return_positions(api_key, instruments)
    dividends_df_temp = api.return_dividends(api_key, instruments)
    balances = api.return_balances(api_key)
    
    return acc_currency, balances, dividends_df_temp, positions_df_temp, exchange_rates_df


def etf_stock_div_values(df: pd.DataFrame):
    total = df['amount'].sum()
    totals = df.groupby('is_ETF')['amount'].sum()
    stocks_total = totals[0]
    etfs_total = totals[1]
    return total, stocks_total, etfs_total


def load_pplots_pie():
    etf_pie = pplts.fig_options_pie(positions_df, 'etfs')
    stock_pie = pplts.fig_options_pie(positions_df, 'stocks')
    pie = pplts.fig_options_pie(positions_df, 'etfs', 'stocks')
    return etf_pie, stock_pie, pie


def load_pplots_bar():
    all_positions_bar = pplts.fig_all_positions_bar(positions_df)
    stock_bar = pplts.fig_stock_positions_bar(positions_df)
    etf_bar = pplts.fig_etf_positions_bar(positions_df)
    return all_positions_bar, stock_bar, etf_bar


def load_pplots_tree():
    stocks_tree_all, tree_data_all = pplts.stocks_tree(positions_df, 'all')
    stocks_tree_stocks, tree_data_stocks = pplts.stocks_tree(positions_df, 'stocks')
    stocks_tree_etfs, tree_data_etfs = pplts.stocks_tree(positions_df, 'etfs')
    return stocks_tree_all, tree_data_all, stocks_tree_stocks, tree_data_stocks, stocks_tree_etfs, tree_data_etfs


st.set_page_config(
    page_title='Trading 212 portfolio tracker',
    layout='wide'
)


st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 200px !important;
        }

        button {
            height: 10px;
            width: 50px;
            padding-top: 1px !important;
            padding-bottom: 1px !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


if "my_input" not in st.session_state: st.session_state["my_input"] = ""


api_key = st.text_input('Paste your trading :blue[212] API key here \
                        (Trading :blue[212] > Settings > API > Generate API Key)', st.session_state["my_input"])
st.write("Note: Loading the data may take some time, mainly depending on the amount of dividend payouts, \
         since the Trading :blue[212] servers only allow a set amount of requests per minute.")


acc_currency, balances, dividends_df_temp, positions_df_temp, exchange_rates_df = load_data(api_key)
if acc_currency in ('EUR', 'GBP'): CURRENCY = acc_currency 
else: CURRENCY = 'EUR'
dividends_df = dplts.handle_base_dividends(dividends_df_temp)
positions_df = pplts.handle_base_positions(positions_df_temp, CURRENCY, exchange_rates_df)

st.divider()

st.header('Your Trading :blue[212] Portfolio Dashboard', anchor=False)
tab1, tab2 = st.tabs(["Overview", "Breakdown"])
with tab1:
    col1, col2 = st.columns([2, 2])
    with col1:
        st.subheader(f'Account value: {"€" if CURRENCY=="EUR" else "£"}{balances["account_value"]}', anchor=False)
        col_left, col_right = st.columns([1.3, 2])
        with col_left:
            st.write(f'Portfolio value: {"€" if CURRENCY=="EUR" else "£"}{round(balances["amount_invested"] + balances["current_p_and_l"], 2)}')
            st.write(f'Amount invested: {"€" if CURRENCY=="EUR" else "£"}{round(balances["amount_invested"], 2)}')        
        with col_right:
            st.write(f'Cash: {"€" if CURRENCY=="EUR" else "£"}{round(balances["cash"], 2)}')
            if balances["current_p_and_l"] >= 0:
                st.write(f'P/L: :green[{"€" if CURRENCY=="EUR" else "£"}{round(balances["current_p_and_l"], 2)}]')
            else:
                st.write(f'P/L: :red[{"€" if CURRENCY=="EUR" else "£"}{round(balances["current_p_and_l"], 2)}]')
    with col2:
        total, stocks_total, etfs_total = etf_stock_div_values(dividends_df)
        st.subheader(f'Total dividends: :green[{"€" if CURRENCY=="EUR" else "£"}{round(total, 2)}]', anchor=False)
        col111, col222 = st.columns([1.2, 2])
        with col111:
            st.write(f'From stocks: :green[{"€" if CURRENCY=="EUR" else "£"}{round(stocks_total, 2)}]')
        with col222:
            st.write(f"From etf's: :green[{'€' if CURRENCY=='EUR' else '£'}{round(etfs_total, 2)}]")
with tab2:
    col_left1, col_left3 = st.columns([1.5, 2])
    with col_left1:
        all_pie = pplts.fig_all_pie(positions_df, balances['cash'], balances['current_p_and_l'])
        st.pyplot(all_pie)

st.divider()

col3, col4 = st.columns([2, 2])
with col3:
    st.subheader('Positions', anchor=False)
    all_positions_bar = pplts.fig_all_positions_bar(positions_df)
    st.pyplot(all_positions_bar)
with col4:
    st.subheader('Dividends', anchor=False)
    div_per_month_bar, _ = dplts.div_per_month_bar(dividends_df)
    st.pyplot(div_per_month_bar)

st.divider()

st.subheader('Positions')
etf_pie, stock_pie, pie = load_pplots_pie()
all_positions_bar, stock_bar, etf_bar = load_pplots_bar()
stocks_tree_all, tree_data_all, stocks_tree_stocks, tree_data_stocks, stocks_tree_etfs, tree_data_etfs = load_pplots_tree()

tab_all, tab_stocks, tab_etfs = st.tabs(["All", "Stocks", "ETF's"])
with tab_all:
    tab_first, tab_second = st.tabs(["Plot", "Data"])
    with tab_first:
        st.pyplot(stocks_tree_all)
    with tab_second:
        st.write(tree_data_all)
with tab_stocks:
    stocks_tree, tree_data = pplts.stocks_tree(positions_df, 'stocks')
    tab_first, tab_second = st.tabs(["Plot", "Data"])
    with tab_first:
        st.pyplot(stocks_tree_stocks)
    with tab_second:
        st.write(tree_data_stocks)
with tab_etfs:
    stocks_tree, tree_data = pplts.stocks_tree(positions_df, 'etfs')
    tab_first, tab_second = st.tabs(["Plot", "Data"])
    with tab_first:
        st.pyplot(stocks_tree_etfs)
    with tab_second:
        st.write(tree_data_etfs)

col11, col22 = st.columns([2, 2])
with col11:
    tab1, tab2, tab3 = st.tabs(["All", "Stocks only", "ETF's only"])
    with tab1:
        st.pyplot(pie)
    with tab2:
        st.pyplot(stock_pie)
    with tab3:
        st.pyplot(etf_pie)
with col22:
    tab11, tab22, tab33 = st.tabs(['All', 'Stocks only', "ETF's only"])
    with tab11:
        st.pyplot(all_positions_bar)
    with tab22:
        st.pyplot(stock_bar)
    with tab33:
        st.pyplot(etf_bar)

st.divider()

st.subheader('Dividends')

col111, col222 = st.columns([2, 2])
with col111:
    yearly_div_bar, div_etfs, div_stocks = dplts.fig_yearly_bar(dividends_df, CURRENCY)
    tab11, tab22 = st.tabs(['Chart', 'Data'])
    
    with tab11:
        st.pyplot(yearly_div_bar)
    with tab22:
        col_left, col_right = st.columns([2, 2])
        with col_left:
            st.write("ETF's:")
            st.write(div_etfs)
        with col_right:
            st.write("Stocks:")
            st.write(div_stocks)
with col222:
    tab1, tab2, tab3 = st.tabs(["Chart", "Data", "Summary"])
    with tab1:
        s = st.text_input("Position(s) - to add multiple tickers: msft, aapl, ... (not case sensitive)", value='MSFT')
        stocks_list = s.upper().replace(' ', '').split(',')
        test = dplts.stocks_etfs_div_line(dividends_df, stocks_list, CURRENCY)
        st.pyplot(test[0])

    with tab2:
        st.write(test[1].reset_index()[['ticker', 'amount', 'pay_date']])
    with tab3:
        st.write(test[2])
