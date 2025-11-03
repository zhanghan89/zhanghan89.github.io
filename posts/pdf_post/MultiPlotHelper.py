#!/usr/bin/env python
# %%
import datetime
import sys
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots
import PlotBTEodPnl
from pathlib import Path

# uv run ~/bin/py_tools/PlotMultiStrategy.py BT_LowVolBreak_short,BT_LowVolBreak_long

HOME = Path.home()
BT_Root = HOME / "backtest"


def get_now_str():
    return datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')  # 2025-08-23T23:09:13+08:00


all_strat = sys.argv[1]
strategies = all_strat.split(',')
strat_pnls = []
for s in strategies:
    pos_file = BT_Root / s / f"{s}.bt.eod_pos.csv"
    pos = pd.read_csv(pos_file).set_index('time')
    eod_acc_pnl = pos.groupby('time').pnl.sum().to_frame()
    strat_pnls.append(eod_acc_pnl.assign(strat=s))

portfolio_pnls = pd.concat(strat_pnls).groupby('time').pnl.sum().to_frame()
strat_pnls.insert(0, portfolio_pnls.assign(strat='all'))

# plot
fig = make_subplots(rows=len(strat_pnls) * 2, cols=1, shared_xaxes=True, vertical_spacing=0.03)

for i, s in enumerate(strat_pnls):
    s_name = s.strat.iloc[0]
    acc_pnl = px.line(s.reset_index(), x='time', y='pnl', log_y=True)
    day_pnl = px.bar(s.pnl.diff().fillna(0).to_frame().reset_index(), x='time', y='pnl', log_y=True)

    post_trade = PlotBTEodPnl.post_trade(s.pnl, s_name)
    PlotBTEodPnl.set_sub_plot(fig, acc_pnl, 2 * i + 1, 1, f'acc_pnl', post_trade)
    PlotBTEodPnl.set_sub_plot(fig, day_pnl, 2 * i + 2, 1, f'day_pnl')

html_file = BT_Root / f"portfolio_pnl_{get_now_str()}.html"
print(f"save post trade to {html_file}")
fig.write_html(html_file)
