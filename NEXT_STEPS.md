# Next Steps for OFI Replication Improvement

## Current Status (After AMD Validation)

### ✓ Completed
- Git repository set up and synced with GitHub
- Python environment configured with all dependencies
- Unit tests passing (4/4)
- Data quality filters implemented (duplicates, outliers)
- Diagnostic and validation scripts created
- AMD single-symbol validation completed

### ⚠️ Current Performance on AMD (Clean Symbol)
- **Beta Positivity**: 60% (Target: ≥80%)
- **Mean R²**: 0.0016 (Target: ≥0.01)
- **Significance Rate**: 0% (Target: ≥60%)

**Interpretation**: Even on our cleanest symbol (AMD), results are below target. This suggests methodological differences from the Cont et al. paper rather than just data quality issues.

---

## Priority Action Items

### 1. Review OFI Calculation Sign Conventions (HIGH PRIORITY)
**Why**: Sign errors are the most common cause of negative betas in OFI research.

**Actions**:
- Re-read Cont et al. Section 2.2 on OFI definition
- Verify our implementation in `compute_ofi_depth_mid()`:
  ```python
  # Current logic:
  # Bid side: +bS when price up, -bS when price down, +dbS when price unchanged
  # Ask side: -aS when price up, +aS when price down, -daS when price unchanged
  ```
- Create test case with known OFI sign (e.g., aggressive buy should → positive OFI → positive price impact)
- Compare with other OFI implementations (e.g., LOBSTER data format)

### 2. Test Different Sampling Frequencies (MEDIUM PRIORITY)
**Why**: 1-second sampling may be too coarse; the paper may use tick-by-tick or 100ms intervals.

**Actions**:
- Modify `validate_amd_week.py` to test multiple frequencies:
  - 100ms (0.1s)
  - 500ms (0.5s)
  - 1s (current)
  - 5s
- Compare R² across frequencies
- Expected: Higher frequency → better R² (if data quality permits)

### 3. Adjust Normalization Window (MEDIUM PRIORITY)
**Why**: 10-minute window may smooth too much or too little.

**Actions**:
- Test normalization windows:
  - 5 minutes (300s)
  - 10 minutes (600s) - current
  - 15 minutes (900s)
- Compare beta stability across windows
- Check if depth normalization is actually helping (compare normalized vs raw OFI)

### 4. Verify Mid-Price Definition (MEDIUM PRIORITY)
**Why**: Our definition might differ from the paper.

**Current**: `mid = 0.5 * (bid + ask)`

**Alternative approaches to test**:
- Volume-weighted mid: `mid = (bid*ask_sz + ask*bid_sz) / (bid_sz + ask_sz)`
- Last trade price (if available in data)

### 5. Check Time Alignment (LOW-MEDIUM PRIORITY)
**Why**: OFI and price changes must be aligned correctly for predictive power.

**Current**: OFI at time t predicts price change from t to t+1

**Alternative to test**:
- OFI at time t-1 predicts price change from t-1 to t (lagged regression)
- Cumulative OFI over [t-5, t] predicts price change at t (multi-period OFI)

---

## Recommended Testing Workflow

### Phase 1: Sign Convention Check (1-2 hours)
```python
# Create scripts/test_ofi_sign.py
# Manually construct scenario:
# - Bid price increases from $10.00 to $10.01
# - Bid size = 100 shares
# Expected: OFI = +100 (aggressive buy pressure)
# Expected: Mid-price increases
# Expected: Beta should be positive
```

### Phase 2: Frequency Sweep (2-3 hours)
```python
# Modify validate_amd_week.py to accept --freq parameter
# Run for freq in [0.1, 0.5, 1, 5, 10]:
#     python scripts/validate_amd_week.py --freq {freq}
# Compare results and identify optimal frequency
```

### Phase 3: Parameter Tuning (2-3 hours)
```python
# Test combinations of:
# - Normalization window: [300, 600, 900]
# - Outlier threshold: [500, 1000, 2000] bps
# - Min periods for rolling: [30, 50, 100]
# Create grid search script to find best combo
```

### Phase 4: Expand to All Symbols (1 hour)
```python
# Once AMD shows good results (beta+ 80%, R²>0.01):
# - Run on all 8 symbols for full month
# - Generate final report with figures
# - Compare to Cont et al. reported statistics
```

---

## Key Metrics to Track

For each test configuration, record:
1. **Beta positivity rate**: % of symbol-days with beta > 0
2. **Mean R²**: Average explanatory power
3. **Significance rate**: % with p-value < 0.05
4. **Beta magnitude**: Are values in reasonable range (1-10)?
5. **Stability**: Does beta stay consistent across days?

---

## Expected Outcomes from Cont et al. Paper

Based on typical OFI research findings:
- **Beta**: Positive in 80-90% of cases
- **R²**: 0.05 - 0.20 (5-20% variance explained)
- **T-statistic**: > 2.0 for most symbol-days
- **Beta magnitude**: 1 - 10 (price changes 1-10 bps per unit normalized OFI)

---

## Debug Resources

### Diagnostic Scripts Available
1. `scripts/diagnose_results.py` - Analyze regression results across all symbols
2. `scripts/debug_ofi.py` - Deep dive into single symbol-day timeseries
3. `scripts/verify_single_symbol.py` - Check data quality across days
4. `scripts/validate_amd_week.py` - Focused AMD validation

### Key Data Files
- `results/validation/amd_week1.csv` - AMD validation results
- `results/regressions/by_symbol_day.parquet` - All regression results
- `results/timeseries/{date}/{symbol}.parquet` - Processed timeseries
- `ANALYSIS_SUMMARY.md` - Comprehensive findings documentation

---

## Questions to Answer

1. **Does the paper use tick-by-tick data or sampled grid?**
   - Impact: Determines optimal sampling frequency
   
2. **What exact normalization does the paper use?**
   - Options: By rolling depth, by daily depth, by volatility
   
3. **Are crossed quotes filtered in the paper?**
   - Current: We filter where bid > ask
   
4. **What time range is used?**
   - Current: 9:30 AM - 4:00 PM ET
   - Alternative: Exclude first/last 30 minutes (high volatility)

---

## Contact & References

- **Repository**: https://github.com/xecuterisaquant/replication-cont-ofi
- **Paper**: Cont et al. - "The Price Impact of Order Book Events" (see `references/` folder)
- **Python**: 3.13.0
- **Key Libraries**: pandas 2.3.2, statsmodels 0.14.5, pyreadr 0.5.3

---

## Success Criteria

We'll consider the replication successful when:
✓ Beta positivity ≥ 80% on AMD over 1 week  
✓ Mean R² ≥ 0.01 on AMD  
✓ At least 60% of AMD days show p < 0.05  
✓ Beta magnitudes in reasonable range (0.5 - 10)  
✓ Results replicate across all 8 symbols  
✓ Findings documented with figures and tables  

---

**Last Updated**: After AMD week 1 validation (2017-01-03 to 2017-01-09)
