# OFI Replication Analysis - Summary Report

## Project Overview
This project replicates the Order Flow Imbalance (OFI) study by Cont, Kukanov & Stoikov (2014), which demonstrates that OFI is a strong predictor of short-term price movements in equity markets.

## Data
- **Period**: January 2017 (20 trading days)
- **Symbols**: 8 stocks (AAPL, AMD, AMZN, JPM, MSFT, NVDA, SPY, TSLA)
- **Format**: R data files (.rda) containing TAQ (Trades and Quotes) data
- **Total Observations**: ~160 symbol-day pairs

## Key Findings

### Overall Results (After Data Quality Filters)
- **Positive Beta Rate**: 57.5% (expected >70% per paper)
- **Mean R²**: 0.004 (expected >0.05 per paper)
- **Correlation (beta, depth)**: 0.138

### Performance by Symbol
**Best Performing (Positive Beta)**:
- JPM: Shows strong relationship but with high magnitude betas (potential data issues)
- AMD: Consistent positive betas with reasonable magnitudes

**Poorest Performing**:
- Mixed results across symbols, suggesting data quality or implementation issues

## Implementation Details

### OFI Calculation
The OFI is calculated according to the Cont et al. formula:
```
e_t^bid = { V_t^bid  if ΔP_t^bid > 0
          { -V_{t-1}^bid if ΔP_t^bid < 0
          { ΔV_t^bid if ΔP_t^bid = 0

e_t^ask = { -V_{t-1}^ask if ΔP_t^ask > 0
          { V_t^ask if ΔP_t^ask < 0  
          { -ΔV_t^ask if ΔP_t^ask = 0

OFI_t = e_t^bid + e_t^ask
```

### Data Processing Pipeline
1. **Load** R data files containing NBBO quotes
2. **Filter** crossed quotes and duplicate timestamps
3. **Build** 1-second grid with forward-fill
4. **Calculate** OFI and normalize by rolling 10-minute depth
5. **Regress** normalized OFI against mid-price changes (in bps)

### Data Quality Improvements
- **Crossed Quote Filtering**: Remove bids >= asks
- **Duplicate Handling**: Keep last occurrence of duplicate timestamps
- **Outlier Filtering**: Remove price changes > 1000 bps (>10% in 1 second)
- **Timezone Handling**: Proper handling of America/New_York timezone

## Issues Identified

### Critical Issues
1. **Beta Magnitudes Too Large**: Some symbols (JPM) show betas in hundreds/thousands instead of single digits
2. **Low R² Values**: Mean R² of 0.007 vs expected >0.05
3. **Data Quality**: Evidence of multiple symbols mixed in some files or data errors
4. **Low Positive Beta Rate**: 57.5% vs expected 80-90%

### Potential Causes
1. **Normalization Scale**: The depth normalization may not be working correctly
2. **Frequency Mismatch**: Using 1-second sampling vs paper's potential use of event-time sampling
3. **Data Errors**: Large price jumps suggest data quality issues in source files
4. **OFI Sign Convention**: Need to verify our implementation matches the paper exactly

## Recommendations for Improvement

### Immediate Priorities
1. **Focus on Clean Symbols**: Test on AMD which shows stable price behavior
2. **Verify OFI Calculation**: Cross-check implementation against paper's exact specification
3. **Check Normalization**: Ensure depth normalization produces reasonable scale
4. **Sample Frequency**: Consider testing at different sampling intervals (5s, 10s, 30s)

### Data Improvements
1. **Pre-filter Data**: Remove symbols with unrealistic price jumps
2. **Symbol Separation**: Ensure each symbol is processed independently
3. **Time Range**: Focus on liquid trading hours (9:30 AM - 4:00 PM ET)

### Analysis Improvements
1. **Stratify by Liquidity**: Separate analysis for high vs low liquidity stocks
2. **Time-of-Day Effects**: Check for opening/closing auction effects
3. **Rolling Window**: Test different normalization window sizes

## Code Quality

### Strengths
- Modular design with separate utility and pipeline modules
- Comprehensive test suite with synthetic data validation
- Proper handling of timezone-aware timestamps
- Parquet-based storage for efficient analysis

### Areas for Enhancement
- Add more diagnostic logging
- Implement symbol-level validation checks
- Create visualization tools for debugging
- Add configuration file for parameters

## Next Steps

1. **Validate on Single Symbol**: Run full week analysis on AMD only
2. **Parameter Tuning**: Test different sampling frequencies and window sizes  
3. **Compare with Paper**: Verify our results match paper's methodology exactly
4. **Expand Analysis**: Once working on one symbol, expand to all symbols
5. **Documentation**: Add detailed methodology documentation

## Files Structure
```
├── data/raw/              # Original .rda files
├── results/
│   ├── timeseries/        # Per-symbol daily timeseries (parquet)
│   └── regressions/       # Regression results (parquet)
├── figures/               # Generated plots
├── scripts/               # Execution scripts
│   ├── run_ofi_day.py    # Process single day
│   ├── run_ofi_batch.py  # Process all days
│   ├── diagnose_results.py # Diagnostic analysis
│   └── verify_single_symbol.py # Data quality check
├── src/                   # Core implementation
│   ├── ofi_utils.py      # OFI calculation functions
│   └── ofi_pipeline.py   # Pipeline orchestration
└── tests/                 # Unit tests
    └── test_ofi_utils.py
```

## References
Cont, R., Kukanov, A., & Stoikov, S. (2014). The price impact of order book events. Journal of Financial Econometrics, 12(1), 47-88.
