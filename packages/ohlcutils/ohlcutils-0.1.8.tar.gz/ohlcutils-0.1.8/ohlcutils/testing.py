from tradingapi.fivepaisa import FivePaisa
from tradingapi.utils import historical_to_dataframes
from ohlcutils.data import load_symbol, change_timeframe, _split_adjust_market_data
from ohlcutils.enums import Periodicity
from ohlcutils.indicators import calculate_ratio_bars, trend
import datetime as dt

fp = FivePaisa()
fp.connect(redis_db=0)

s = "COFORGE_STK___"
column_mapping = {
    "ratio_adj_open": "aopen",
    "ratio_adj_high": "ahigh",
    "ratio_adj_low": "alow",
    "ratio_adj_close": "aclose",
}
md_benchmark = fp.get_historical("NIFTY_IND___", dt.date.today() - dt.timedelta(days=1000), periodicity="1d")
md_benchmark = historical_to_dataframes(md_benchmark)[0]
# md_benchmark = md_benchmark.rename(columns=column_mapping)

md = fp.get_historical(s, dt.date.today() - dt.timedelta(days=1000), periodicity="1d")
md = historical_to_dataframes(md)[0]
md = _split_adjust_market_data(md, Periodicity.DAILY, tz="Asia/Kolkata")
# md = md.rename(columns=column_mapping)
print(md.columns)
print(md_benchmark.columns)
md_ratio = calculate_ratio_bars(
    md, md_benchmark, columns={"open": "open", "high": "high", "low": "low", "close": "close"}
)
md_ratio = md_ratio.rename(columns=column_mapping)
tr_ratio_d = trend(md_ratio)

if tr_ratio_d.trend.iloc[-1] != 0:
    tr_d = trend(md, columns={"open": "open", "high": "high", "low": "low", "close": "close"})
    if (
        abs(tr_d.trend.iloc[-1]) == 1
        and abs(tr_d.trend.iloc[-2]) == 1
        and tr_d.trend.iloc[-1] == tr_d.trend.iloc[-2]
        and tr_d.trend.iloc[-2] != tr_d.trend.iloc[-3]
    ):
        md_w = change_timeframe(md, dest_bar_size="5D")
        tr_w = trend(md_w, columns={"open": "open", "high": "high", "low": "low", "close": "close"})
        if abs(tr_w.trend.iloc[-1]) == 1 and tr_w.trend.iloc[-1] == tr_d.trend.iloc[-1]:
            md_m = change_timeframe(md, dest_bar_size="20D")
            tr_m = trend(md_m, columns={"open": "open", "high": "high", "low": "low", "close": "close"})
            if abs(tr_m.trend.iloc[-1]) == 1 and tr_m.trend.iloc[-1] == tr_d.trend.iloc[-1]:
                if tr_d.trend.iloc[-1] == tr_ratio_d.trend.iloc[-1]:
                    print(tr_d.trend.iloc[-1])
            print("0")

md = load_symbol(
    "INFY_STK___",
    days=100,
    src=Periodicity.DAILY,
    dest_bar_size="1W",
    label="left",
    adjust_for_holidays=True,
    adjustment="fbd",
)
print(md)
