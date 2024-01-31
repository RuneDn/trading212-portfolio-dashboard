import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
    

def handle_base_dividends(base_df: pd.DataFrame):
    base_df['pay_date'] = pd.to_datetime(pd.to_datetime(base_df['pay_date'], utc=True).dt.date)
    base_df['month'] = base_df['pay_date'].dt.month
    base_df['year'] = base_df['pay_date'].dt.year
    return base_df


def fig_yearly_bar(df: pd.DataFrame):
    fig = plt.figure()
    ax = fig.add_subplot()

    x_vals = np.flip(df['year'].unique())
    x = []
    for d in x_vals:
        x.append(str(d))

    bar = plt.bar(x, df['amount'].groupby(df['year']).sum(), figure = fig, zorder = 3)
    for rect in bar:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width() / 2.0, height, f'€{height:.0f}', ha='center', va='bottom', color=('white'))
    
    div_etfs = df['amount'][df['is_ETF'] == 1].groupby(df['year']).sum()
    div_stocks = df['amount'][df['is_ETF'] == 0].groupby(df['year']).sum()

    df1 = div_etfs.to_frame()
    df1['year'] = df1.index
    df1['year'] = df1['year'].astype(str)

    df2 = div_stocks.to_frame()
    df2['year'] = df2.index
    df2['year'] = df2['year'].astype(str)

    ax.spines['top'].set_color('#0E1117')
    ax.spines['right'].set_color('#0E1117')
    ax.spines['bottom'].set_color('#0E1117')
    ax.spines['left'].set_color('#0E1117')
    ax.tick_params(axis='x', colors='white', rotation=45)
    ax.tick_params(axis='y', colors='white')
    ax.grid(True, axis='y', linestyle='-', linewidth=0.5, color='w', zorder=0, alpha=0.1)
    ax.set_facecolor('#0E1117')
    fig.set_facecolor('#0E1117')
    return fig, df1, df2


def stocks_etfs_div_line(df: pd.DataFrame, stocks = None):
    df['pay_date'] = pd.to_datetime(df['pay_date'])
    if 'ALL' in stocks:
        stocks = list(df['ticker'].unique())
    df['pay_date'] = df['pay_date'].dt.date
    new_df = df[['amount', 'ticker', 'pay_date']][df['ticker'].isin(stocks)]
    
    fig = plt.figure()
    ax = fig.add_subplot()
    for s in stocks:
        x = new_df['pay_date'][new_df['ticker'] == s]
        y = new_df['amount'][new_df['ticker'] == s]
        ax.plot(x, y, zorder=3)

    ax.spines['top'].set_color('#0E1117')
    ax.spines['right'].set_color('#0E1117')
    ax.spines['bottom'].set_color('#0E1117')
    ax.spines['left'].set_color('#0E1117')
    ax.tick_params(axis='x', colors='white', rotation=45)
    ax.tick_params(axis='y', colors='white')
    ax.legend(stocks, labelcolor=('white'), frameon=False, loc='center left', bbox_to_anchor=(1, 0.5))
    ax.set_facecolor('#0E1117')
    ax.grid(True, axis='y', linestyle='-', linewidth=0.5, color='w', zorder=0, alpha=0.1)
    fig.set_facecolor('#0E1117')
    return fig, new_df


def div_per_month_bar(df: pd.DataFrame):
    df['month_year'] = df['pay_date'].dt.to_period('M')
    monthly_dividends = df.groupby('month_year')['amount'].sum()
    monthly_dividends.index = monthly_dividends.index.astype(str)

    fig, ax = plt.subplots()
    fig.set_size_inches([10, 5])
    ax.bar(monthly_dividends.index, monthly_dividends, zorder=3)

    ax.spines['top'].set_color('#0E1117')
    ax.spines['right'].set_color('#0E1117')
    ax.spines['bottom'].set_color('#0E1117')
    ax.spines['left'].set_color('#0E1117')
    ax.tick_params(axis='x', colors='white', rotation=45)
    ax.tick_params(axis='y', colors='white')
    ax.set_facecolor('#0E1117')
    ax.grid(True, axis='y', linestyle='-', linewidth=0.5, color='w', zorder=0, alpha=0.1)
    fig.set_facecolor('#0E1117')

    '''
    cursor = mplcursors.cursor(hover=mplcursors.HoverMode.Transient)
    @cursor.connect("add")
    def on_add(sel):
        x, y, width, height = sel.artist[sel.index].get_bbox().bounds
        sel.annotation.set(text=f"{x+width/2}: {height}",
                        position=(0, 20), anncoords="offset points")
        sel.annotation.xy = (x + width / 2, y + height)
    '''
    x = np.array([])
    for i in range(len(monthly_dividends)):
        x = np.append(x, i)
    
    z = np.polyfit(x, monthly_dividends, 1)
    p = np.poly1d(z)
    avg_div_month = p(x[len(x) - 1])
    plt.plot(x, p(x), alpha=0.5, color='g')
    
    '''
    Display point coordinates on plot
    for xy in zip(x, p(x)):
        xy = xy
    plt.annotate('(%.0f, %.2f)' % xy, xy=xy, color='w', alpha=0.5)
    '''
    return fig, avg_div_month


# def multi_year_div_bar(df = pd.DataFrame):
    df = df[['amount', 'month', 'year']]
    dfs = [x for _, x in df.groupby('year')]
    for i, d in enumerate(dfs):
        print(f'old: {d}')
        if len(d['month'].unique()) < 12:
            nr_of_rows = 12 - len(d['month'].unique())
            amounts, months, years = ([], ) * 3
            for i in reversed(range(nr_of_rows)):
                amounts.append(0)
                months.append(i)
                years.append(d['year'].unique())
            rows = {'amount': amounts,
                    'month': months,
                    'year': years}
            print(rows)
            rows_df = pd.DataFrame.from_dict(rows)
            print(f'rows df: {rows_df}')
            d = pd.concat([d, rows_df])
            print(d.tail())
        print(f'new: {d.tail(10)}')
        dfs[i] = d.groupby('month')['amount'].sum()
    # print(dfs)
    
    gap = .8 / 12
    for i, d in enumerate(dfs):
        X = np.arange(12)
        plt.bar(X + i * gap, d,
            width = gap,
            # color = color_list[i % len(color_list)]
            )
    plt.show() 
