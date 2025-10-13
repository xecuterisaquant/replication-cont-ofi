# tests/test_ofi_utils.py
import pandas as pd, numpy as np
from src.ofi_utils import compute_ofi_depth_mid, normalize_ofi, run_ols_symbol_day, detect_time_unit

def make_df(bid,ask,bidsz,asksz,freq="1s"):
    idx=pd.date_range("2024-06-03 09:30:00-04:00",periods=len(bid),freq=freq)
    return pd.DataFrame({"bid":bid,"ask":ask,"bid_sz":bidsz,"ask_sz":asksz},index=idx)

def test_detect_time_unit():
    assert detect_time_unit(80000)=="s"
    assert detect_time_unit(8_000_000)=="ms"
    assert detect_time_unit(8_000_000_000)=="us"

def test_ofi_bid_price_up():
    df=make_df([100,100.01,100.01],[100.02,100.02,100.02],[10,12,12],[15,15,15])
    out=compute_ofi_depth_mid(df)
    assert out["ofi"].iloc[1] > 0

def test_ofi_ask_down_positive():
    df=make_df([100,100,100],[100.02,100.01,100.01],[10,10,10],[15,14,14])
    out=compute_ofi_depth_mid(df)
    assert out["ofi"].iloc[1] > 0

def test_positive_beta_on_synthetic():
    rng=np.random.default_rng(7); n=1500; k=4.0
    bid=100+np.cumsum(rng.normal(0,0.001,size=n)); ask=bid+0.01
    bsz=100+rng.integers(0,10,size=n); asz=110+rng.integers(0,10,size=n)
    df=make_df(bid,ask,bsz,asz)
    out=compute_ofi_depth_mid(df); out=normalize_ofi(out,600,50)
    y=k*out["normalized_OFI"].fillna(0).values + rng.normal(0,0.5,size=n)
    out["d_mid_bps"]=y
    st=run_ols_symbol_day(out)
    assert st["beta"]>0 and st["r2"]>0
