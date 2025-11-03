#!/usr/bin/env python
# %%
# uv run ~/bin/py_tools/PlotBTEodPnl.py ~/backtest/BT_LowVolBreak_short/BT_LowVolBreak_short.bt.eod_pos.csv

import sys
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path


def post_trade(acc_pnl: pd.Series, name):
    name = name.split('/')[-1]
    start = acc_pnl.index[0]
    end = acc_pnl.index[-1]
    day_pnl = acc_pnl.diff().fillna(0)
    last_pnl = acc_pnl.iloc[-1]
    win = day_pnl[day_pnl > 0].mean()
    lost = abs(day_pnl[day_pnl < 0].mean())
    max_lost = acc_pnl.min()
    max_day_lost = day_pnl.min()
    win_rate = f"win rate={(day_pnl > 0).mean():.3f}"
    win_lost_rate = f"win/lost rate={(win / lost):.3f}"
    SR = f"SR={day_pnl.mean() / day_pnl.std() * 16:.3f}"
    # print(f"SR={pnl_diff.div(AUM).mean() / pnl_diff.div(AUM).std() * 16:.3f}")
    # pnl_diff.div(AUM).mean(), pnl_diff.div(AUM).std(), pnl_diff.mean(), pnl_diff.std()
    rst = f"[{start},{end}] {win_rate}; {win_lost_rate}; {SR}; {last_pnl=:.3f}; {max_lost=:.3f}; {max_day_lost=:.3f}; name={name}"
    print(rst)
    return rst


def set_sub_plot(fig, px_plot, row, col, yaxis_name, title=None):
    for i in px_plot.data:
        fig.add_trace(i, row=row, col=col)
    fig['layout'][f'xaxis{row}']['title'] = title
    fig['layout'][f'yaxis{row}']['title'] = yaxis_name
    fig['layout'][f'yaxis{row}']['side'] = "right"
    # fig.update_layout(yaxis=dict(side="right"))


drop_ins = {}
if __name__ == "__main__":
    HOME = Path.home()
    BT_Root = HOME / "backtest"
    # pos_file = '~/backtest/SRT_bt/SRT_bt.bt.eod_pos.csv'
    # AUM = 100000
    pos_file = sys.argv[1]
    html_file = pos_file + ".html"
    pos = pd.read_csv(pos_file).set_index('time').query("ins_id not in @drop_ins")
    eod_acc_pnl = pos.groupby('time').pnl.sum().to_frame()

    pos_t = post_trade(eod_acc_pnl.pnl, pos_file)

    ins_ids = list(set(pos['ins_id'].tolist()))
    ins_ids.sort()
    # %%
    # data = pos.query('today_pnl != 0.0').reset_index()
    data = pos.reset_index()
    ltp = px.line(data, x='time', y='ltp', color='ins_id', category_orders={'ins_id': ins_ids}, log_y=True)
    ins_qty = px.line(data, x='time', y='qty', color='ins_id', log_y=True)

    data = data.query('today_pnl != 0.0')
    ins_pnl = px.line(data, x='time', y='pnl', color='ins_id', log_y=True)
    ins_day_pnl = px.scatter(data, x='time', y='today_pnl', color='ins_id', log_y=True)

    all_pnl = px.line(eod_acc_pnl.reset_index(), x='time', y='pnl', log_y=True)
    all_day_pnl = px.bar(eod_acc_pnl.pnl.diff().fillna(0).to_frame().reset_index(), x='time', y='pnl', log_y=True)

    # %%

    fig = make_subplots(rows=6, cols=1, shared_xaxes=True, vertical_spacing=0.02)
    set_sub_plot(fig, ltp, 1, 1, 'ltp')
    set_sub_plot(fig, ins_qty, 2, 1, 'ins_qty')
    set_sub_plot(fig, ins_pnl, 3, 1, 'ins_pnl')
    set_sub_plot(fig, ins_day_pnl, 4, 1, 'ins_day_pnl')
    set_sub_plot(fig, all_pnl, 5, 1, 'all_pnl')
    set_sub_plot(fig, all_day_pnl, 6, 1, 'all_day_pnl')

    # fig.update_layout(width=1500, height=1000)
    fig.update_layout(legend=dict(yanchor="top", y=0.9, xanchor="left", x=-0.1), title=pos_t)
    fig.write_html(html_file)
    print(f"save post trade to {html_file}")
