# scripts/diagnose_results.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the results
panel_path = "results/regressions/by_symbol_day.parquet"
if not os.path.exists(panel_path):
    print(f"Results file not found: {panel_path}")
    sys.exit(1)

panel = pd.read_parquet(panel_path)

print("="*60)
print("DIAGNOSTIC REPORT: OFI Replication Results")
print("="*60)
print(f"\nTotal observations: {len(panel)}")
print(f"Valid beta observations: {panel['beta'].notna().sum()}")
print(f"Symbols: {panel['symbol'].nunique()}")
print(f"Days: {panel['day'].nunique()}")

print("\n" + "="*60)
print("BETA STATISTICS")
print("="*60)
valid_beta = panel[panel['beta'].notna()]
print(f"Beta > 0: {(valid_beta['beta'] > 0).sum()} ({(valid_beta['beta'] > 0).mean()*100:.1f}%)")
print(f"Beta mean: {valid_beta['beta'].mean():.4f}")
print(f"Beta median: {valid_beta['beta'].median():.4f}")
print(f"Beta std: {valid_beta['beta'].std():.4f}")
print(f"Beta min: {valid_beta['beta'].min():.4f}")
print(f"Beta max: {valid_beta['beta'].max():.4f}")

print("\n" + "="*60)
print("R² STATISTICS")
print("="*60)
valid_r2 = panel[panel['r2'].notna()]
print(f"R² mean: {valid_r2['r2'].mean():.4f}")
print(f"R² median: {valid_r2['r2'].median():.4f}")
print(f"R² > 0.05: {(valid_r2['r2'] > 0.05).sum()} ({(valid_r2['r2'] > 0.05).mean()*100:.1f}%)")
print(f"R² > 0.10: {(valid_r2['r2'] > 0.10).sum()} ({(valid_r2['r2'] > 0.10).mean()*100:.1f}%)")

print("\n" + "="*60)
print("DEPTH STATISTICS")
print("="*60)
print(f"Mean depth: {panel['mean_depth'].mean():.2f}")
print(f"Median depth: {panel['mean_depth'].median():.2f}")

print("\n" + "="*60)
print("TOP 10 SYMBOLS BY BETA")
print("="*60)
top_beta = valid_beta.nlargest(10, 'beta')[['symbol', 'day', 'beta', 'r2', 'mean_depth']]
print(top_beta.to_string(index=False))

print("\n" + "="*60)
print("BOTTOM 10 SYMBOLS BY BETA")
print("="*60)
bottom_beta = valid_beta.nsmallest(10, 'beta')[['symbol', 'day', 'beta', 'r2', 'mean_depth']]
print(bottom_beta.to_string(index=False))

print("\n" + "="*60)
print("SYMBOLS WITH HIGHEST R²")
print("="*60)
top_r2 = valid_r2.nlargest(10, 'r2')[['symbol', 'day', 'beta', 'r2', 'mean_depth']]
print(top_r2.to_string(index=False))

print("\n" + "="*60)
print("CORRELATION ANALYSIS")
print("="*60)
corr_data = panel[['beta', 'r2', 'mean_depth', 'ofi_scale']].dropna()
if len(corr_data) > 0:
    print("\nCorrelation matrix:")
    print(corr_data.corr().to_string())

print("\n" + "="*60)
print("POTENTIAL ISSUES")
print("="*60)
issues = []
if (valid_beta['beta'] > 0).mean() < 0.7:
    issues.append(f"✗ Low positive beta rate: {(valid_beta['beta'] > 0).mean()*100:.1f}% (expected >70%)")
if valid_r2['r2'].mean() < 0.05:
    issues.append(f"✗ Low mean R²: {valid_r2['r2'].mean():.4f} (expected >0.05)")
if panel['n'].mean() < 1000:
    issues.append(f"✗ Low sample size: {panel['n'].mean():.0f} observations per regression")

if issues:
    for issue in issues:
        print(issue)
else:
    print("✓ No major issues detected")

print("\n" + "="*60)
print("RECOMMENDATIONS")
print("="*60)
print("1. Check if the OFI calculation is correct (sign conventions)")
print("2. Verify the normalization by depth is working properly")
print("3. Ensure the mid-price changes are in basis points")
print("4. Consider different sampling frequencies or window sizes")
print("5. Check for outliers in the data that might affect results")
