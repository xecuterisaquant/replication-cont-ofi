# scripts/run_ofi_batch.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse, glob, pandas as pd, json
from src.ofi_pipeline import run_one_day, build_all_figures

def main():
    ap = argparse.ArgumentParser(description="Batch process all .rda files in a directory.")
    ap.add_argument("--raw", required=True, help="Directory containing .rda files")
    ap.add_argument("--out", default="results", help="Output dir (parquet)")
    ap.add_argument("--freq", default="1s", help="Resample frequency (default 1s)")
    ap.add_argument("--no-baseline10s", action="store_true", help="Disable CK&S 10s half-hour regressions")
    args = ap.parse_args()

    rdas = sorted(glob.glob(os.path.join(args.raw, "*.rda")))
    all_rows = []
    for rp in rdas:
        day_rows = run_one_day(rp, outdir=args.out, freq=args.freq, baseline10s=(not args.no_baseline10s), make_daily_scatter=True)
        if len(day_rows):
            all_rows.append(day_rows)

    build_all_figures(args.out, figdir="figures")

    if all_rows:
        panel = pd.concat(all_rows, ignore_index=True)
        valid = panel["beta"].notna()
        pos_share = ((panel.loc[valid, "beta"]) > 0).mean() if valid.any() else float("nan")
        avg_r2 = panel.loc[panel["r2"].notna(), "r2"].mean() if panel["r2"].notna().any() else float("nan")
        sub = panel[["beta", "mean_depth"]].dropna()
        inv_depth_corr = sub.corr().loc["beta", "mean_depth"] if len(sub) else float("nan")

        summary = {
            "days": len(rdas),
            "rows": int(len(panel)),
            "share_beta_positive": None if pd.isna(pos_share) else float(pos_share),
            "mean_r2": None if pd.isna(avg_r2) else float(avg_r2),
            "corr_beta_mean_depth": None if pd.isna(inv_depth_corr) else float(inv_depth_corr),
        }
        os.makedirs(os.path.join(args.out, "regressions"), exist_ok=True)
        with open(os.path.join(args.out, "regressions", "acceptance_summary.json"), "w") as f:
            json.dump(summary, f, indent=2)

        print("[run_ofi_batch] days=%d, rows=%d" % (len(rdas), len(panel)))
        print(f"  share(β>0)={0.0 if pd.isna(pos_share) else pos_share:.2%} | mean R²={0.0 if pd.isna(avg_r2) else avg_r2:.3f} | corr(beta, mean_depth)={0.0 if pd.isna(inv_depth_corr) else inv_depth_corr:.3f}")
        print("  Figures in ./figures/: beta_hist.png, intraday_beta_vs_depth.png, and scatters")
    else:
        print("[run_ofi_batch] no .rda files found or no rows processed.")

if __name__ == "__main__":
    main()
