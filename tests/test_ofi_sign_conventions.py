#!/usr/bin/env python3
"""
Test OFI sign conventions to ensure correctness.

Based on Cont et al. definition:
- OFI measures the net order flow imbalance
- Positive OFI = net buying pressure → price should increase
- Negative OFI = net selling pressure → price should decrease

Key scenarios to test:
1. Bid price increases (aggressive buy) → positive OFI
2. Ask price decreases (aggressive sell) → negative OFI
3. Bid size increases at same price → positive OFI
4. Ask size increases at same price → negative OFI
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import numpy as np
from src.ofi_utils import compute_ofi_depth_mid

def test_bid_price_increase():
    """Bid price increases (aggressive buy) → positive OFI"""
    print("\n" + "="*70)
    print("TEST 1: Bid price increases (aggressive buy)")
    print("="*70)
    
    # Time t=0: bid=10.00, ask=10.01, bidsz=100, asksz=100
    # Time t=1: bid=10.01, ask=10.01, bidsz=100, asksz=100
    # Expected: OFI = +100 (bid size consumed at higher price)
    
    df = pd.DataFrame({
        'bid': [10.00, 10.01],
        'ask': [10.01, 10.01],
        'bid_sz': [100.0, 100.0],
        'ask_sz': [100.0, 100.0],
    })
    
    result = compute_ofi_depth_mid(df)
    ofi = result['ofi'].iloc[1]
    
    print(f"Setup: Bid increases from $10.00 to $10.01")
    print(f"Bid size constant at 100")
    print(f"OFI at t=1: {ofi}")
    print(f"Expected: OFI > 0 (aggressive buying)")
    
    assert ofi > 0, f"FAIL: OFI should be positive but got {ofi}"
    print("✓ PASS: Positive OFI as expected")
    return True


def test_ask_price_decrease():
    """Ask price decreases (aggressive sell) → negative OFI"""
    print("\n" + "="*70)
    print("TEST 2: Ask price decreases (aggressive sell)")
    print("="*70)
    
    # Time t=0: bid=10.00, ask=10.01, bidsz=100, asksz=100
    # Time t=1: bid=10.00, ask=10.00, bidsz=100, asksz=100
    # Expected: OFI = -100 (ask size consumed at lower price)
    
    df = pd.DataFrame({
        'bid': [10.00, 10.00],
        'ask': [10.01, 10.00],
        'bid_sz': [100.0, 100.0],
        'ask_sz': [100.0, 100.0],
    })
    
    result = compute_ofi_depth_mid(df)
    ofi = result['ofi'].iloc[1]
    
    print(f"Setup: Ask decreases from $10.01 to $10.00")
    print(f"Ask size constant at 100")
    print(f"OFI at t=1: {ofi}")
    print(f"Expected: OFI < 0 (aggressive selling)")
    
    assert ofi < 0, f"FAIL: OFI should be negative but got {ofi}"
    print("✓ PASS: Negative OFI as expected")
    return True


def test_bid_size_increase():
    """Bid size increases at same price → positive OFI"""
    print("\n" + "="*70)
    print("TEST 3: Bid size increases at same price")
    print("="*70)
    
    # Time t=0: bid=10.00, ask=10.01, bidsz=100, asksz=100
    # Time t=1: bid=10.00, ask=10.01, bidsz=150, asksz=100
    # Expected: OFI = +50 (more buying interest)
    
    df = pd.DataFrame({
        'bid': [10.00, 10.00],
        'ask': [10.01, 10.01],
        'bid_sz': [100.0, 150.0],
        'ask_sz': [100.0, 100.0],
    })
    
    result = compute_ofi_depth_mid(df)
    ofi = result['ofi'].iloc[1]
    
    print(f"Setup: Bid size increases from 100 to 150")
    print(f"Prices unchanged")
    print(f"OFI at t=1: {ofi}")
    print(f"Expected: OFI = +50 (more buying interest)")
    
    assert ofi > 0, f"FAIL: OFI should be positive but got {ofi}"
    assert abs(ofi - 50) < 1e-6, f"FAIL: OFI should be ~50 but got {ofi}"
    print("✓ PASS: OFI = +50 as expected")
    return True


def test_ask_size_increase():
    """Ask size increases at same price → negative OFI"""
    print("\n" + "="*70)
    print("TEST 4: Ask size increases at same price")
    print("="*70)
    
    # Time t=0: bid=10.00, ask=10.01, bidsz=100, asksz=100
    # Time t=1: bid=10.00, ask=10.01, bidsz=100, asksz=150
    # Expected: OFI = -50 (more selling interest)
    
    df = pd.DataFrame({
        'bid': [10.00, 10.00],
        'ask': [10.01, 10.01],
        'bid_sz': [100.0, 100.0],
        'ask_sz': [100.0, 150.0],
    })
    
    result = compute_ofi_depth_mid(df)
    ofi = result['ofi'].iloc[1]
    
    print(f"Setup: Ask size increases from 100 to 150")
    print(f"Prices unchanged")
    print(f"OFI at t=1: {ofi}")
    print(f"Expected: OFI = -50 (more selling interest)")
    
    assert ofi < 0, f"FAIL: OFI should be negative but got {ofi}"
    assert abs(ofi + 50) < 1e-6, f"FAIL: OFI should be ~-50 but got {ofi}"
    print("✓ PASS: OFI = -50 as expected")
    return True


def test_bid_price_decrease():
    """Bid price decreases (bid withdrawn) → negative OFI"""
    print("\n" + "="*70)
    print("TEST 5: Bid price decreases (bid withdrawn)")
    print("="*70)
    
    # Time t=0: bid=10.01, ask=10.02, bidsz=100, asksz=100
    # Time t=1: bid=10.00, ask=10.02, bidsz=100, asksz=100
    # Expected: OFI < 0 (bid liquidity removed)
    
    df = pd.DataFrame({
        'bid': [10.01, 10.00],
        'ask': [10.02, 10.02],
        'bid_sz': [100.0, 100.0],
        'ask_sz': [100.0, 100.0],
    })
    
    result = compute_ofi_depth_mid(df)
    ofi = result['ofi'].iloc[1]
    
    print(f"Setup: Bid decreases from $10.01 to $10.00")
    print(f"Bid size constant at 100")
    print(f"OFI at t=1: {ofi}")
    print(f"Expected: OFI < 0 (bid liquidity removed)")
    
    assert ofi < 0, f"FAIL: OFI should be negative but got {ofi}"
    print("✓ PASS: Negative OFI as expected")
    return True


def test_correlation_with_price_change():
    """Test that OFI correlates positively with subsequent price changes"""
    print("\n" + "="*70)
    print("TEST 6: OFI vs Price Change Correlation")
    print("="*70)
    
    # Create synthetic series with positive OFI → price increases
    np.random.seed(42)
    n = 1000
    
    # Generate autocorrelated OFI
    ofi_signal = np.cumsum(np.random.randn(n)) * 10
    
    # Price follows OFI with noise
    price_changes = 0.1 * ofi_signal + np.random.randn(n) * 0.5
    
    # Build DataFrame
    prices = 100 + np.cumsum(price_changes * 0.01)  # Convert to price levels
    df = pd.DataFrame({
        'bid': prices - 0.005,
        'ask': prices + 0.005,
        'bid_sz': 100.0 + ofi_signal,  # Bid size correlates with OFI
        'ask_sz': 100.0 - ofi_signal,  # Ask size anti-correlates
    })
    
    # Ensure sizes are positive
    df['bid_sz'] = df['bid_sz'].clip(lower=10)
    df['ask_sz'] = df['ask_sz'].clip(lower=10)
    
    result = compute_ofi_depth_mid(df)
    
    # Check correlation
    valid = result[['ofi', 'd_mid_bps']].dropna()
    correlation = valid['ofi'].corr(valid['d_mid_bps'])
    
    print(f"Synthetic data: {len(valid)} observations")
    print(f"OFI vs d_mid_bps correlation: {correlation:.4f}")
    print(f"Expected: correlation > 0 (positive relationship)")
    
    assert correlation > 0, f"FAIL: Correlation should be positive but got {correlation}"
    print("✓ PASS: Positive correlation as expected")
    return True


def test_realistic_scenario():
    """Test a realistic multi-step scenario"""
    print("\n" + "="*70)
    print("TEST 7: Realistic trading scenario")
    print("="*70)
    
    # Simulate a sequence where:
    # 0-1. Stable state
    # 2. Bid size increases (passive buy interest)
    # 3. Bid jumps up to meet ask (aggressive buy - lifts offer)
    # 4. Ask gets hit (aggressive sell)
    # 5. Return to equilibrium
    
    df = pd.DataFrame({
        'bid':    [10.00, 10.00, 10.00, 10.01, 10.00, 10.00],
        'ask':    [10.01, 10.01, 10.01, 10.02, 10.01, 10.01],
        'bid_sz': [100.0, 100.0, 150.0, 150.0, 100.0, 100.0],
        'ask_sz': [100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
    })
    
    result = compute_ofi_depth_mid(df)
    
    print("\nScenario:")
    print("t=0-1: Stable state (bid=10.00, ask=10.01)")
    print("t=2: Bid size increases from 100 to 150")
    print(f"     OFI = {result['ofi'].iloc[2]:.2f} (expect +50)")
    print("t=3: Aggressive buy - bid jumps to 10.01 (lifting offer)")
    print(f"     OFI = {result['ofi'].iloc[3]:.2f} (expect positive)")
    print("t=4: Ask gets hit - aggressive sell")
    print(f"     OFI = {result['ofi'].iloc[4]:.2f} (expect negative)")
    print("t=5: Return to equilibrium")
    print(f"     OFI = {result['ofi'].iloc[5]:.2f}")
    
    # Check expectations
    assert result['ofi'].iloc[2] > 0, f"t=2: Bid size increase should yield positive OFI but got {result['ofi'].iloc[2]}"
    assert result['ofi'].iloc[3] > 0, f"t=3: Aggressive buy should yield positive OFI but got {result['ofi'].iloc[3]}"
    assert result['ofi'].iloc[4] < 0, f"t=4: Aggressive sell should yield negative OFI but got {result['ofi'].iloc[4]}"
    
    print("\n✓ PASS: Realistic scenario behaves as expected")
    return True


def main():
    print("\n" + "="*70)
    print("OFI SIGN CONVENTION VERIFICATION TESTS")
    print("="*70)
    print("\nTesting implementation against Cont et al. OFI definition...")
    
    tests = [
        ("Bid price increase (buy)", test_bid_price_increase),
        ("Ask price decrease (sell)", test_ask_price_decrease),
        ("Bid size increase", test_bid_size_increase),
        ("Ask size increase", test_ask_size_increase),
        ("Bid price decrease", test_bid_price_decrease),
        ("OFI-price correlation", test_correlation_with_price_change),
        ("Realistic scenario", test_realistic_scenario),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Tests passed: {passed}/{len(tests)}")
    print(f"Tests failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✓ ALL TESTS PASSED - OFI sign conventions are correct!")
        print("The implementation matches Cont et al. definition.")
    else:
        print(f"\n✗ {failed} TEST(S) FAILED - OFI implementation needs review!")
        print("Check the sign conventions in compute_ofi_depth_mid()")
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
