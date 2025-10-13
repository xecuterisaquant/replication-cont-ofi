#!/usr/bin/env python3
"""
Quick validation run on first 5 days to show improvement from OFI sign fix.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pathlib import Path
from src.ofi_pipeline import run_one_day
import pandas as pd

def main():
    base_dir = Path(__file__).resolve().parents[1]
    raw_dir = base_dir / 'data' / 'raw'
    out_dir = base_dir / 'results_fixed'
    
    # First 5 days
    dates = ['2017-01-03', '2017-01-04', '2017-01-05', '2017-01-06', '2017-01-09']
    
    print("\nProcessing first 5 days with corrected OFI sign...")
    print("="*70)
    
    all_rows = []
    for date_str in dates:
        rda_file = raw_dir / f'{date_str}.rda'
        if not rda_file.exists():
            print(f"Skipping {date_str}: file not found")
            continue
        
        print(f"\nProcessing {date_str}...")
        try:
            rows = run_one_day(
                str(rda_file),
                outdir=str(out_dir),
                freq="1s",
                baseline10s=False,
                make_daily_scatter=False
            )
            all_rows.extend(rows.to_dict('records'))
            print(f"  ✓ Completed {len(rows)} symbol regressions")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Analyze results
    df = pd.DataFrame(all_rows)
    
    print("\n" + "="*70)
    print("SUMMARY - FIRST 5 DAYS (ALL SYMBOLS)")
    print("="*70)
    print(f"\nTotal symbol-day observations: {len(df)}")
    print(f"Symbols: {sorted(df['symbol'].unique())}")
    print(f"Days: {sorted(df['day'].unique())}")
    
    print(f"\nBeta statistics:")
    print(f"  Mean: {df['beta'].mean():.4f}")
    print(f"  Median: {df['beta'].median():.4f}")
    print(f"  Std: {df['beta'].std():.4f}")
    print(f"  Positive: {(df['beta'] > 0).sum()}/{len(df)} ({100*(df['beta'] > 0).mean():.1f}%)")
    
    print(f"\nR² statistics:")
    print(f"  Mean: {df['r2'].mean():.6f}")
    print(f"  Median: {df['r2'].median():.6f}")
    print(f"  Range: [{df['r2'].min():.6f}, {df['r2'].max():.6f}]")
    
    print(f"\nPer-symbol summary:")
    symbol_summary = df.groupby('symbol').agg({
        'beta': ['mean', 'std', lambda x: (x > 0).mean()],
        'r2': 'mean'
    }).round(4)
    symbol_summary.columns = ['Beta Mean', 'Beta Std', 'Beta+ Rate', 'R² Mean']
    print(symbol_summary)
    
    print(f"\n✓ Results saved to: {out_dir}")


if __name__ == '__main__':
    main()
