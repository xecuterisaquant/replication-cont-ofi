# src/ofi_pipeline.py
from __future__ import annotations
import os, glob, pandas as pd
from .ofi_utils import process_day_rda, make_scatter, beta_histogram, intraday_beta_vs_depth

def run_one_day(rda_path: str, outdir: str, freq: str = "1s", baseline10s: bool = True, make_daily_scatter: bool = True) -> pd.DataFrame:
    res = process_day_rda(rda_path, outdir=outdir, freq=freq, do_halfhour_10s=baseline10s)
    if make_daily_scatter and len(res):
        day = res["day"].iloc[0]
        day_dir = os.path.join(outdir, "timeseries", day)
        if os.path.exists(day_dir):
            for pq in glob.glob(os.path.join(day_dir, "*.parquet")):
                symbol = os.path.splitext(os.path.basename(pq))[0]
                ts = pd.read_parquet(pq)
                make_scatter(ts, symbol=symbol, day=day, figdir="figures")
    return res

def build_all_figures(outdir: str, figdir: str = "figures"):
    panel = os.path.join(outdir, "regressions", "by_symbol_day.parquet")
    beta_histogram(panel, figdir=figdir)
    hh_panel = os.path.join(outdir, "regressions", "by_symbol_day_halfhour.parquet")
    timeseries_root = os.path.join(outdir, "timeseries")
    intraday_beta_vs_depth(hh_panel, timeseries_root, figdir=figdir)
