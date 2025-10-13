# scripts/run_ofi_day.py
import argparse
from src.ofi_pipeline import run_one_day, build_all_figures

def main():
    ap = argparse.ArgumentParser(description="Process one .rda day and run OFI regressions.")
    ap.add_argument("--raw", required=True, help="Path to .rda file for a single day")
    ap.add_argument("--out", default="results", help="Output dir (parquet)")
    ap.add_argument("--freq", default="1s", help="Resample frequency for TOB grid (default 1s)")
    ap.add_argument("--no-scatter", action="store_true", help="Disable per symbol×day scatter plots")
    ap.add_argument("--no-baseline10s", action="store_true", help="Disable CK&S 10s half-hour regressions")
    args = ap.parse_args()

    res = run_one_day(args.raw, outdir=args.out, freq=args.freq, baseline10s=(not args.no_baseline10s), make_daily_scatter=(not args.no_scatter))
    build_all_figures(args.out, figdir="figures")

    if len(res):
        pos_share = (res["beta"] > 0).mean(skipna=True)
        avg_r2 = res["r2"].mean(skipna=True)
        print(f"[run_ofi_day] processed={len(res)} rows | share(β>0)={pos_share:.2%} | mean R²={avg_r2:.3f}")
    else:
        print("[run_ofi_day] no symbols processed / empty results")

if __name__ == "__main__":
    main()
