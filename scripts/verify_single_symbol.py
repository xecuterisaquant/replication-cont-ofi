# scripts/verify_single_symbol.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
import glob
from src.ofi_utils import read_rda, resolve_columns

# First, let's see what symbols are in the data files
print("="*60)
print("EXAMINING DATA FILES - SYMBOLS PER DAY")
print("="*60)

rda_files = sorted(glob.glob("data/raw/*.rda"))[:7]  # First week
all_symbols = set()

for rda_file in rda_files:
    day = os.path.splitext(os.path.basename(rda_file))[0]
    df = read_rda(rda_file)
    cmap = resolve_columns(df)
    symbols = df[cmap.symbol].unique()
    all_symbols.update(symbols)
    print(f"{day}: {len(symbols)} symbols - {sorted(symbols)}")

print("\n" + "="*60)
print(f"UNIQUE SYMBOLS ACROSS FIRST WEEK: {sorted(all_symbols)}")
print("="*60)

# Pick one symbol that appears frequently (likely AMD or JPM)
target_symbol = "AMD" if "AMD" in all_symbols else list(all_symbols)[0]
print(f"\nSelected symbol for detailed analysis: {target_symbol}")

# Examine this symbol's data across multiple days
print("\n" + "="*60)
print(f"DATA QUALITY CHECK FOR {target_symbol}")
print("="*60)

for rda_file in rda_files[:5]:  # First 5 days
    day = os.path.splitext(os.path.basename(rda_file))[0]
    df = read_rda(rda_file)
    cmap = resolve_columns(df)
    
    symbol_data = df[df[cmap.symbol] == target_symbol]
    if len(symbol_data) == 0:
        print(f"{day}: {target_symbol} not found")
        continue
    
    print(f"\n{day}: {len(symbol_data)} records")
    print(f"  Bid range: ${symbol_data[cmap.bid].min():.2f} - ${symbol_data[cmap.bid].max():.2f}")
    print(f"  Ask range: ${symbol_data[cmap.ask].min():.2f} - ${symbol_data[cmap.ask].max():.2f}")
    print(f"  Bid size range: {symbol_data[cmap.bidsz].min():.0f} - {symbol_data[cmap.bidsz].max():.0f}")
    print(f"  Ask size range: {symbol_data[cmap.asksz].min():.0f} - {symbol_data[cmap.asksz].max():.0f}")
    
    # Check for crossed quotes
    crossed = symbol_data[symbol_data[cmap.bid] >= symbol_data[cmap.ask]]
    if len(crossed) > 0:
        print(f"  WARNING: {len(crossed)} crossed quotes ({len(crossed)/len(symbol_data)*100:.1f}%)")
    
    # Check for unrealistic spreads
    spread_pct = (symbol_data[cmap.ask] - symbol_data[cmap.bid]) / symbol_data[cmap.bid] * 100
    large_spread = spread_pct > 1.0  # More than 1%
    if large_spread.sum() > 0:
        print(f"  WARNING: {large_spread.sum()} quotes with spread > 1% ({large_spread.sum()/len(symbol_data)*100:.1f}%)")
    
    # Check price consistency (no sudden jumps > 10%)
    mid_price = (symbol_data[cmap.bid] + symbol_data[cmap.ask]) / 2
    pct_change = mid_price.pct_change().abs() * 100
    big_jumps = pct_change > 10
    if big_jumps.sum() > 0:
        print(f"  WARNING: {big_jumps.sum()} price jumps > 10% ({big_jumps.sum()/len(symbol_data)*100:.1f}%)")
        # Show some examples
        jump_indices = symbol_data.index[big_jumps.values][:3]
        for idx in jump_indices:
            loc = symbol_data.index.get_loc(idx)
            if loc > 0:
                prev_mid = (symbol_data.iloc[loc-1][cmap.bid] + symbol_data.iloc[loc-1][cmap.ask]) / 2
                curr_mid = (symbol_data.iloc[loc][cmap.bid] + symbol_data.iloc[loc][cmap.ask]) / 2
                print(f"    Jump: ${prev_mid:.2f} -> ${curr_mid:.2f} ({((curr_mid/prev_mid)-1)*100:.1f}%)")
