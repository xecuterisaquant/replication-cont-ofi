# scripts/debug_ofi.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np

# Load a timeseries to debug
ts_file = "results/timeseries/2017-01-04/JPM.parquet"
if os.path.exists(ts_file):
    ts = pd.read_parquet(ts_file)
    print("="*60)
    print(f"Analyzing: {ts_file}")
    print("="*60)
    print(f"\nData shape: {ts.shape}")
    print(f"Time range: {ts.index[0]} to {ts.index[-1]}")
    
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    print(ts[['bid', 'ask', 'bid_sz', 'ask_sz', 'depth', 'ofi', 'normalized_OFI', 'd_mid_bps']].describe())
    
    print("\n" + "="*60)
    print("SAMPLE DATA (first 10 rows)")
    print("="*60)
    print(ts[['bid', 'ask', 'bid_sz', 'ask_sz', 'depth', 'ofi', 'normalized_OFI', 'd_mid_bps']].head(10))
    
    print("\n" + "="*60)
    print("OFI STATISTICS")
    print("="*60)
    print(f"OFI mean: {ts['ofi'].mean():.2f}")
    print(f"OFI std: {ts['ofi'].std():.2f}")
    print(f"OFI min: {ts['ofi'].min():.2f}")
    print(f"OFI max: {ts['ofi'].max():.2f}")
    print(f"OFI non-zero: {(ts['ofi'] != 0).sum()} ({(ts['ofi'] != 0).mean()*100:.1f}%)")
    
    print("\n" + "="*60)
    print("NORMALIZED OFI STATISTICS")
    print("="*60)
    valid_nofi = ts['normalized_OFI'].dropna()
    print(f"Normalized OFI mean: {valid_nofi.mean():.4f}")
    print(f"Normalized OFI std: {valid_nofi.std():.4f}")
    print(f"Normalized OFI min: {valid_nofi.min():.4f}")
    print(f"Normalized OFI max: {valid_nofi.max():.4f}")
    print(f"Normalized OFI valid: {len(valid_nofi)} ({len(valid_nofi)/len(ts)*100:.1f}%)")
    
    print("\n" + "="*60)
    print("MID-PRICE CHANGE STATISTICS (basis points)")
    print("="*60)
    valid_dmid = ts['d_mid_bps'].dropna()
    print(f"d_mid_bps mean: {valid_dmid.mean():.4f}")
    print(f"d_mid_bps std: {valid_dmid.std():.4f}")
    print(f"d_mid_bps min: {valid_dmid.min():.4f}")
    print(f"d_mid_bps max: {valid_dmid.max():.4f}")
    
    print("\n" + "="*60)
    print("DEPTH STATISTICS")
    print("="*60)
    print(f"Depth mean: {ts['depth'].mean():.2f}")
    print(f"Depth std: {ts['depth'].std():.2f}")
    print(f"Depth min: {ts['depth'].min():.2f}")
    print(f"Depth max: {ts['depth'].max():.2f}")
    print(f"Depth roll (10m) mean: {ts['depth_roll_10m'].mean():.2f}")
    
    print("\n" + "="*60)
    print("QUICK REGRESSION CHECK")
    print("="*60)
    from statsmodels.api import OLS, add_constant
    data = ts[['normalized_OFI', 'd_mid_bps']].dropna()
    if len(data) > 10:
        X = add_constant(data['normalized_OFI'].values)
        y = data['d_mid_bps'].values
        res = OLS(y, X).fit(cov_type='HC1')
        print(f"Beta: {res.params[1]:.4f}")
        print(f"SE: {res.bse[1]:.4f}")
        print(f"t-stat: {res.tvalues[1]:.4f}")
        print(f"p-value: {res.pvalues[1]:.4f}")
        print(f"R²: {res.rsquared:.4f}")
        print(f"N: {len(data)}")
    
    print("\n" + "="*60)
    print("CHECKING FOR DATA QUALITY ISSUES")
    print("="*60)
    print(f"Infinite values in normalized_OFI: {np.isinf(ts['normalized_OFI']).sum()}")
    print(f"NaN values in normalized_OFI: {ts['normalized_OFI'].isna().sum()}")
    print(f"Infinite values in d_mid_bps: {np.isinf(ts['d_mid_bps']).sum()}")
    print(f"NaN values in d_mid_bps: {ts['d_mid_bps'].isna().sum()}")
    
    # Check depth roll
    print(f"Depth roll (10m) NaN: {ts['depth_roll_10m'].isna().sum()}")
    print(f"Depth roll (10m) zero: {(ts['depth_roll_10m'] == 0).sum()}")
    print(f"Depth roll (10m) < 1: {(ts['depth_roll_10m'] < 1).sum()}")
    
else:
    print(f"File not found: {ts_file}")
    print("\nAvailable directories:")
    if os.path.exists("results/timeseries"):
        for day in os.listdir("results/timeseries"):
            day_dir = os.path.join("results/timeseries", day)
            if os.path.isdir(day_dir):
                files = os.listdir(day_dir)
                print(f"  {day}: {files}")
