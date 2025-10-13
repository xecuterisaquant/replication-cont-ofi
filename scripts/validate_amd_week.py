#!/usr/bin/env python3
"""
Focused validation on AMD for the first week of January 2017.
This script tests the OFI methodology on a single clean symbol before expanding.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import numpy as np
import pyreadr
from pathlib import Path
from src.ofi_utils import (
    resolve_columns,
    build_tob_series_1s,
    compute_ofi_depth_mid,
    normalize_ofi,
    run_ols_symbol_day
)

def process_amd_day(raw_path: Path, date_str: str) -> dict:
    """Process AMD data for a single day and return detailed statistics."""
    print(f"\n{'='*70}")
    print(f"Processing AMD for {date_str}")
    print(f"{'='*70}")
    
    # Read the RDA file
    rda_dict = pyreadr.read_r(str(raw_path))
    df_raw = rda_dict[list(rda_dict.keys())[0]]
    
    # Resolve columns first to get standard names
    cmap = resolve_columns(df_raw)
    
    # Filter for AMD only
    df_raw = df_raw[df_raw[cmap.symbol] == 'AMD'].copy()
    print(f"Raw records: {len(df_raw):,}")
    
    # Build TOB series
    trading_day = pd.Timestamp(date_str, tz="America/New_York")
    tob = build_tob_series_1s(df_raw, cmap, trading_day, freq="1s")
    
    # Calculate basic statistics
    stats = {
        'date': date_str,
        'symbol': 'AMD',
        'raw_records': len(df_raw),
        'tob_seconds': len(tob),
        'bid_min': tob['bid'].min(),
        'bid_max': tob['bid'].max(),
        'ask_min': tob['ask'].min(),
        'ask_max': tob['ask'].max(),
        'spread_mean': (tob['ask'] - tob['bid']).mean(),
        'spread_median': (tob['ask'] - tob['bid']).median(),
        'spread_max': (tob['ask'] - tob['bid']).max(),
    }
    
    print(f"TOB grid points: {stats['tob_seconds']:,}")
    print(f"Bid range: ${stats['bid_min']:.2f} - ${stats['bid_max']:.2f}")
    print(f"Ask range: ${stats['ask_min']:.2f} - ${stats['ask_max']:.2f}")
    print(f"Spread: mean=${stats['spread_mean']:.4f}, median=${stats['spread_median']:.4f}, max=${stats['spread_max']:.4f}")
    
    # Compute OFI and mid-price changes
    ofi_tob = compute_ofi_depth_mid(tob)
    
    # Check for extreme values before normalization
    ofi_vals = ofi_tob['ofi'].dropna()
    d_mid_bps_vals = ofi_tob['d_mid_bps'].dropna()
    
    stats.update({
        'ofi_count': len(ofi_vals),
        'ofi_mean': ofi_vals.mean(),
        'ofi_std': ofi_vals.std(),
        'ofi_min': ofi_vals.min(),
        'ofi_max': ofi_vals.max(),
        'd_mid_bps_count': len(d_mid_bps_vals),
        'd_mid_bps_mean': d_mid_bps_vals.mean(),
        'd_mid_bps_std': d_mid_bps_vals.std(),
        'd_mid_bps_min': d_mid_bps_vals.min(),
        'd_mid_bps_max': d_mid_bps_vals.max(),
    })
    
    print(f"\nOFI statistics ({stats['ofi_count']:,} values):")
    print(f"  Mean: {stats['ofi_mean']:.2f}, Std: {stats['ofi_std']:.2f}")
    print(f"  Range: [{stats['ofi_min']:.2f}, {stats['ofi_max']:.2f}]")
    
    print(f"\nMid-price change (bps) statistics ({stats['d_mid_bps_count']:,} values):")
    print(f"  Mean: {stats['d_mid_bps_mean']:.2f}, Std: {stats['d_mid_bps_std']:.2f}")
    print(f"  Range: [{stats['d_mid_bps_min']:.2f}, {stats['d_mid_bps_max']:.2f}]")
    
    # Check for extreme d_mid_bps values
    extreme_count = (ofi_tob['d_mid_bps'].abs() > 1000).sum()
    if extreme_count > 0:
        print(f"  ⚠ WARNING: {extreme_count} extreme values (>1000 bps) detected and filtered")
    
    # Normalize OFI
    ofi_tob = normalize_ofi(ofi_tob, window_secs=600, min_periods=50)
    
    # Check normalized values
    norm_ofi_vals = ofi_tob['normalized_OFI'].dropna()
    stats.update({
        'ofi_norm_count': len(norm_ofi_vals),
        'ofi_norm_mean': norm_ofi_vals.mean(),
        'ofi_norm_std': norm_ofi_vals.std(),
        'ofi_norm_min': norm_ofi_vals.min(),
        'ofi_norm_max': norm_ofi_vals.max(),
    })
    
    print(f"\nNormalized OFI statistics ({stats['ofi_norm_count']:,} values):")
    print(f"  Mean: {stats['ofi_norm_mean']:.4f}, Std: {stats['ofi_norm_std']:.4f}")
    print(f"  Range: [{stats['ofi_norm_min']:.4f}, {stats['ofi_norm_max']:.4f}]")
    
    # Run regression
    reg_res = run_ols_symbol_day(ofi_tob)
    
    if reg_res is not None and 'beta' in reg_res:
        # Calculate t-statistic and approximate p-value
        t_stat = reg_res['beta'] / reg_res['se_beta'] if reg_res['se_beta'] > 0 else 0
        # Simple two-tailed p-value approximation
        import scipy.stats
        pval = 2 * (1 - scipy.stats.norm.cdf(abs(t_stat))) if reg_res['n'] > 10 else 1.0
        
        stats.update({
            'beta': reg_res['beta'],
            'beta_se': reg_res['se_beta'],
            'pval': pval,
            'rsquared': reg_res['r2'],
            'nobs': reg_res['n'],
        })
        
        print(f"\nRegression results:")
        print(f"  Beta: {stats['beta']:.4f} (SE: {stats['beta_se']:.4f})")
        print(f"  P-value: {stats['pval']:.6f} {'***' if stats['pval'] < 0.001 else '**' if stats['pval'] < 0.01 else '*' if stats['pval'] < 0.05 else ''}")
        print(f"  R²: {stats['rsquared']:.6f}")
        print(f"  N: {stats['nobs']:,}")
        
        # Interpretation
        if stats['beta'] > 0 and stats['pval'] < 0.05:
            print(f"  ✓ PASS: Positive and significant beta")
        elif stats['beta'] > 0:
            print(f"  ~ WEAK: Positive but not significant (p={stats['pval']:.3f})")
        else:
            print(f"  ✗ FAIL: Negative beta ({stats['beta']:.4f})")
    else:
        print(f"\n✗ Regression failed (insufficient data)")
        stats.update({
            'beta': np.nan,
            'beta_se': np.nan,
            'pval': np.nan,
            'rsquared': np.nan,
            'nobs': 0,
        })
    
    return stats


def main():
    # Define the first week of data
    dates = [
        '2017-01-03',
        '2017-01-04',
        '2017-01-05',
        '2017-01-06',
        # Weekend skip
        '2017-01-09',
    ]
    
    # Paths
    base_dir = Path(__file__).resolve().parents[1]
    raw_dir = base_dir / 'data' / 'raw'
    
    print("\n" + "="*70)
    print("AMD VALIDATION - FIRST WEEK OF JANUARY 2017")
    print("="*70)
    print(f"\nTesting OFI methodology on AMD stock over {len(dates)} trading days")
    print("Goal: Validate that beta > 0 and R² > 0.01 consistently")
    
    # Process each day
    results = []
    for date_str in dates:
        raw_file = raw_dir / f'{date_str}.rda'
        if not raw_file.exists():
            print(f"\n⚠ Skipping {date_str}: file not found")
            continue
        
        try:
            stats = process_amd_day(raw_file, date_str)
            results.append(stats)
        except Exception as e:
            print(f"\n✗ Error processing {date_str}: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary statistics
    if results:
        df_results = pd.DataFrame(results)
        
        print("\n" + "="*70)
        print("WEEKLY SUMMARY FOR AMD")
        print("="*70)
        
        print(f"\nDays processed: {len(df_results)}")
        print(f"\nBeta statistics:")
        print(f"  Mean: {df_results['beta'].mean():.4f}")
        print(f"  Median: {df_results['beta'].median():.4f}")
        print(f"  Std: {df_results['beta'].std():.4f}")
        print(f"  Range: [{df_results['beta'].min():.4f}, {df_results['beta'].max():.4f}]")
        print(f"  Positive: {(df_results['beta'] > 0).sum()}/{len(df_results)} ({100*(df_results['beta'] > 0).mean():.1f}%)")
        
        print(f"\nR² statistics:")
        print(f"  Mean: {df_results['rsquared'].mean():.6f}")
        print(f"  Median: {df_results['rsquared'].median():.6f}")
        print(f"  Range: [{df_results['rsquared'].min():.6f}, {df_results['rsquared'].max():.6f}]")
        
        print(f"\nSignificance (p < 0.05):")
        sig_count = (df_results['pval'] < 0.05).sum()
        print(f"  {sig_count}/{len(df_results)} days ({100*sig_count/len(df_results):.1f}%)")
        
        print(f"\nMid-price change magnitudes:")
        print(f"  Mean |Δmid|: {df_results['d_mid_bps_std'].mean():.2f} bps")
        print(f"  Max |Δmid|: {df_results['d_mid_bps_max'].mean():.2f} bps (avg across days)")
        
        # Save results
        out_dir = base_dir / 'results' / 'validation'
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / 'amd_week1.csv'
        df_results.to_csv(out_file, index=False)
        print(f"\nResults saved to: {out_file}")
        
        # Assessment
        print("\n" + "="*70)
        print("ASSESSMENT")
        print("="*70)
        
        positive_rate = (df_results['beta'] > 0).mean()
        mean_rsq = df_results['rsquared'].mean()
        sig_rate = (df_results['pval'] < 0.05).mean()
        
        passed = []
        failed = []
        
        if positive_rate >= 0.8:
            passed.append(f"✓ Beta positivity: {100*positive_rate:.0f}% (target: ≥80%)")
        else:
            failed.append(f"✗ Beta positivity: {100*positive_rate:.0f}% (target: ≥80%)")
        
        if mean_rsq >= 0.01:
            passed.append(f"✓ R² magnitude: {mean_rsq:.4f} (target: ≥0.01)")
        else:
            failed.append(f"✗ R² magnitude: {mean_rsq:.4f} (target: ≥0.01)")
        
        if sig_rate >= 0.6:
            passed.append(f"✓ Significance rate: {100*sig_rate:.0f}% (target: ≥60%)")
        else:
            failed.append(f"✗ Significance rate: {100*sig_rate:.0f}% (target: ≥60%)")
        
        if passed:
            print("\nPassing criteria:")
            for p in passed:
                print(f"  {p}")
        
        if failed:
            print("\nFailing criteria:")
            for f in failed:
                print(f"  {f}")
        
        if not failed:
            print("\n🎉 ALL CRITERIA PASSED - Methodology validated on AMD!")
            print("Ready to expand to all symbols.")
        else:
            print("\n⚠ Some criteria not met - Further tuning needed:")
            print("  - Adjust outlier filter threshold")
            print("  - Test different sampling frequencies")
            print("  - Review normalization window size")
            print("  - Check sign conventions in OFI calculation")


if __name__ == '__main__':
    main()
