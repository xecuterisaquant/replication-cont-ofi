# scripts/make_figures.py
import argparse, os, glob, pandas as pd
from src.ofi_utils import make_scatter, beta_histogram, intraday_beta_vs_depth

def main():
    ap = argparse.ArgumentParser(description="Regenerate figures from existing results.")
    ap.add_argument("--results", default="results", help="Results directory")
    ap.add_argument("--figdir", default="figures", help="Figures directory")
    args = ap.parse_args()

    panel_path = os.path.join(args.results, "regressions", "by_symbol_day.parquet")
    beta_histogram(panel_path, figdir=args.figdir)

    panel_halfhour = os.path.join(args.results, "regressions", "by_symbol_day_halfhour.parquet")
    timeseries_root = os.path.join(args.results, "timeseries")
    intraday_beta_vs_depth(panel_halfhour, timeseries_root, figdir=args.figdir)

    timeseries_root = os.path.join(args.results, "timeseries")
    if os.path.exists(timeseries_root):
        for day in os.listdir(timeseries_root):
            day_dir = os.path.join(timeseries_root, day)
            if not os.path.isdir(day_dir): continue
            for pq in glob.glob(os.path.join(day_dir, "*.parquet")):
                symbol = os.path.splitext(os.path.basename(pq))[0]
                ts = pd.read_parquet(pq)
                make_scatter(ts, symbol=symbol, day=day, figdir=args.figdir)

    print(f"[make_figures] Figures written to: {args.figdir}")

if __name__ == "__main__":
    main()
