import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import squarify as sq
from sklearn.preprocessing import MinMaxScaler
    

def handle_base_positions(base_df: pd.DataFrame):
    base_df['amount_invested'] = base_df['shares'] * base_df['avg_price']
    base_df['position'] = base_df['amount_invested'] + base_df['p_l']
    base_df['return'] = round(base_df['p_l'] / base_df['amount_invested'], 4)
    return base_df


def specific_positions_dfs(base_df: pd.DataFrame):
    sorted_positions_s = base_df.sort_values('position', ascending=False)
    sorted_positions = base_df.sort_values('p_l', ascending=False)
    sorted_positions_g = sorted_positions[sorted_positions['p_l'] >= 0]
    sorted_positions_l = sorted_positions[sorted_positions['p_l'] < 0]
    sorted_positions_ia = base_df.sort_values('amount_invested', ascending=False)
    return sorted_positions, sorted_positions_g, sorted_positions_l, sorted_positions_s, sorted_positions_ia


def explode(length, explosion: tuple, increment):
    if length == 0:
        return explosion[::-1]
    elif length < 6:
        explosion += (increment,)
        increment += 0.05
        return explode(length - 1, explosion, increment)
    else:
        explosion += (0,)
        return explode(length-1, explosion, increment)


def fig_all_pie(df: pd.DataFrame, cash, p_l):
    sorted_positions_invested_amount = specific_positions_dfs(df)[4][['ticker', 'amount_invested', 'p_l', 'p_l_fx']]
    fx = sorted_positions_invested_amount['p_l_fx'].sum()

    if fx >= 0:
        temp_df_pl = pd.DataFrame.from_dict({'ticker': ['P/L'], 'amount_invested': [p_l - fx], 'p_l': [0], 'p_l_fx': [0]})
        temp_df_plfx = pd.DataFrame.from_dict({'ticker': ['P/L_fx'], 'amount_invested': [fx], 'p_l': [0], 'p_l_fx': [0]})
    else:
        temp_df_pl = pd.DataFrame.from_dict({'ticker': ['P/L'], 'amount_invested': [p_l], 'p_l': [0], 'p_l_fx': [0]})
        temp_df_plfx = pd.DataFrame.from_dict({'ticker': ['P/L_fx'], 'amount_invested': [0], 'p_l': [0], 'p_l_fx': [0]})
    temp_df_cash = pd.DataFrame.from_dict({'ticker': ['cash'], 'amount_invested': [cash], 'p_l': [0], 'p_l_fx': [0]})
    final_df = pd.concat([sorted_positions_invested_amount, temp_df_pl, temp_df_plfx, temp_df_cash])
    final_df = final_df.sort_values('amount_invested', ascending=False)
    
    fig = plt.figure()
    _, _, autotexts = plt.pie(final_df['amount_invested'], 
            labels=final_df['ticker'],
            colors=sns.color_palette('magma', len(final_df)),
            explode=explode(len(final_df), (), 0.05), 
            autopct='%1.1f%%', 
            textprops={'size': 'smaller', 'color': 'white'},
            radius=1.5)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(6)
    fig.set_facecolor('#0E1117')
    return fig


def fig_options_pie(df: pd.DataFrame, *args: str):
    sorted_positions_size = specific_positions_dfs(df)[3]
    if 'stocks' in args and 'etfs' in args:
        type_df = sorted_positions_size[['ticker','position']]
    elif 'stocks' in args:
        type_df = sorted_positions_size[['ticker','position']][sorted_positions_size['is_ETF'] == 0]
    elif 'etfs' in args:
        type_df = sorted_positions_size[['ticker','position']][sorted_positions_size['is_ETF'] == 1]
        
    if len(type_df) > 11:
        data1 = type_df.iloc[:11]
        data2 = type_df.iloc[-(len(type_df) - len(data1)):]
        temp_dict = {'ticker': ['Other'], 'position': [data2['position'].sum()]}
        data_temp_df = pd.DataFrame.from_dict(temp_dict)
        data = pd.concat([data1, data_temp_df])
    else:
        data = type_df

    fig = plt.figure()
    _, _, autotexts = plt.pie(data['position'], 
            labels=data['ticker'],
            explode=explode(len(data), (), 0.05),
            colors=sns.color_palette('magma', len(type_df)), 
            autopct='%1.1f%%', textprops={'size': 'small', 'color': 'white'})
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(6)
    fig.set_facecolor('#0E1117')
    return fig


def fig_all_positions_bar(df: pd.DataFrame):
    sorted_positions_size = specific_positions_dfs(df)[3]
    fig = plt.figure()
    fig.set_size_inches([10, 5])
    ax = fig.add_subplot()
    ax.bar(sorted_positions_size['ticker'], sorted_positions_size['position'], zorder=3)
    
    ax.spines['top'].set_color('#0E1117')
    ax.spines['right'].set_color('#0E1117')
    ax.spines['bottom'].set_color('#0E1117')
    ax.spines['left'].set_color('#0E1117')
    ax.tick_params(axis='x', colors='white', rotation=45)
    ax.tick_params(axis='y', colors='white')
    ax.grid(True, axis='y', linestyle='-', linewidth=0.5, color='w', zorder=0, alpha=0.1)
    ax.set_facecolor('#0E1117')
    fig.set_facecolor('#0E1117')
    return fig


def fig_stock_positions_bar(df: pd.DataFrame):
    sorted_positions_size = specific_positions_dfs(df)[3]
    fig = plt.figure(figsize=[9, 4])
    ax = fig.add_subplot()
    ax.bar(sorted_positions_size['ticker'][sorted_positions_size['is_ETF'] == 0], 
            sorted_positions_size['position'][sorted_positions_size['is_ETF'] == 0], zorder=3)
    
    ax.spines['top'].set_color('#0E1117')
    ax.spines['right'].set_color('#0E1117')
    ax.spines['bottom'].set_color('#0E1117')
    ax.spines['left'].set_color('#0E1117')
    ax.tick_params(axis='x', colors='white', rotation=45)
    ax.tick_params(axis='y', colors='white')
    ax.grid(True, axis='y', linestyle='-', linewidth=0.5, color='w', zorder=0, alpha=0.1)
    ax.set_facecolor('#0E1117')
    fig.set_facecolor('#0E1117')
    
    return fig


def fig_etf_positions_bar(df: pd.DataFrame):
    sorted_positions_size = specific_positions_dfs(df)[3]
    fig = plt.figure(figsize=[9, 4])
    ax = fig.add_subplot()
    ax.bar(sorted_positions_size['ticker'][sorted_positions_size['is_ETF'] == 1], 
            sorted_positions_size['position'][sorted_positions_size['is_ETF'] == 1], zorder=3)
    
    ax.spines['top'].set_color('#0E1117')
    ax.spines['right'].set_color('#0E1117')
    ax.spines['bottom'].set_color('#0E1117')
    ax.spines['left'].set_color('#0E1117')
    ax.tick_params(axis='x', colors='white', rotation=45)
    ax.tick_params(axis='y', colors='white')
    ax.grid(True, axis='y', linestyle='-', linewidth=0.5, color='w', zorder=0, alpha=0.1)
    ax.set_facecolor('#0E1117')
    fig.set_facecolor('#0E1117')
    
    return fig


def stocks_tree(df: pd.DataFrame, *args):
    sorted_positions, sorted_positions_gainers, sorted_positions_losers, _, _ = specific_positions_dfs(df)
    scaler = MinMaxScaler(feature_range=(0.15, 1))
    alphas_gainers = None
    alphas_losers = None

    if args[0] == 'stocks':
        if len(sorted_positions_gainers[sorted_positions_gainers['is_ETF'] == 0]) > 0:
            alphas_gainers = scaler.fit_transform(
                pd.array(sorted_positions_gainers['return'][df['is_ETF'] == 0]).reshape(-1, 1))
        if len(sorted_positions_losers[sorted_positions_losers['is_ETF'] == 0]) > 0:
            alphas_losers = scaler.fit_transform(
                pd.array(sorted_positions_losers['return'][df['is_ETF'] == 0]).reshape(-1, 1))
            for i, v in enumerate(alphas_losers):
                alphas_losers[i] = 1 - v + 0.15
        data = sorted_positions[sorted_positions['is_ETF'] == 0].reset_index()[['ticker', 'position', 'p_l', 'return']]
        labels = [] 
        for t, r in zip(sorted_positions['ticker'][sorted_positions['is_ETF'] == 0],
                        sorted_positions['return'][sorted_positions['is_ETF'] == 0]):
            labels.append(f'{t}\n{round(r, 2)}')
        sizes = sorted_positions['position'][sorted_positions['is_ETF'] == 0]
    
    if args[0] == 'etfs':
        if len(sorted_positions_gainers[sorted_positions_gainers['is_ETF'] == 1]) > 0:
            alphas_gainers = scaler.fit_transform(
                pd.array(sorted_positions_gainers['return'][df['is_ETF'] == 1]).reshape(-1, 1))
        if len(sorted_positions_losers[sorted_positions_losers['is_ETF'] == 1]) > 0:
            alphas_losers = scaler.fit_transform(
                pd.array(sorted_positions_losers['return'][df['is_ETF'] == 1]).reshape(-1, 1))
            for i, v in enumerate(alphas_losers):
                alphas_losers[i] = 1 - v + 0.15
        data = sorted_positions[sorted_positions['is_ETF'] == 1].reset_index()[['ticker', 'position', 'p_l', 'return']]
        labels = []
        for t, r in zip(sorted_positions['ticker'][sorted_positions['is_ETF'] == 1],
                        sorted_positions['return'][sorted_positions['is_ETF'] == 1]):
            labels.append(f'{t}\n{round(r, 2)}')
        sizes = sorted_positions['position'][sorted_positions['is_ETF'] == 1]
    
    if args[0] == 'all':
        if len(sorted_positions_gainers) > 0:
            alphas_gainers = scaler.fit_transform(pd.array(sorted_positions_gainers['return']).reshape(-1, 1))
        if len(sorted_positions_losers) > 0:
            alphas_losers = scaler.fit_transform(pd.array(sorted_positions_losers['return']).reshape(-1, 1))
            for i, v in enumerate(alphas_losers):
                alphas_losers[i] = 1 - v + 0.15
        data = sorted_positions.reset_index()[['ticker', 'position', 'p_l', 'return']]
        labels = []
        for t, r in zip(sorted_positions['ticker'], sorted_positions['return']):
            labels.append(f'{t}\n{round(r, 2)}')
        sizes = sorted_positions['position']
    
    if alphas_gainers is not None:
        alphas_gainers[alphas_gainers > 1] = 1
        rgba_colors = np.zeros((len(alphas_gainers),4))
        rgba_colors[:,0] = 0.1
        rgba_colors[:, 1] = 0.75
        rgba_colors[:,2] = 0.1
        rgba_colors[:,-1] = alphas_gainers.reshape(1,len(alphas_gainers)).flatten()
    if alphas_losers is not None:
        alphas_losers[alphas_losers > 1] = 1
        rgba_colors2 = np.zeros((len(alphas_losers),4))
        rgba_colors2[:,0] = 0.6
        rgba_colors2[:,2] = 0.1
        rgba_colors2[:,-1] = alphas_losers.reshape(1,len(alphas_losers)).flatten()
    
    if alphas_gainers is not None and alphas_losers is not None:
        rgba_colors_final = np.vstack((rgba_colors, rgba_colors2))
    elif alphas_gainers is not None:
        rgba_colors_final = rgba_colors
    else:
        rgba_colors_final = rgba_colors2
        
    '''
    labels = []
    for t, p_l, p in zip(sorted_positions['ticker'][sorted_positions['is_ETF'] == 0], 
                    sorted_positions['p_l'][sorted_positions['is_ETF'] == 0],
                    sorted_positions['position'][sorted_positions['is_ETF'] == 0]):
        labels.append(f'{t}\n€{round(p, 2)}\n(€{p_l})')
    '''

    fig = plt.figure(figsize=[10, 4])
    ax = sq.plot(sizes=sizes,
                 label=labels, color=rgba_colors_final, text_kwargs={'fontsize':10, 'color': 'beige'})
    fig.set_facecolor('#0E1117')
    plt.axis('off')
    return fig, data
