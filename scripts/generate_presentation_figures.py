#!/usr/bin/env python3
"""
Generate publication-quality figures for OFI replication project presentation.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set publication-quality style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 13

def load_results():
    """Load the fixed results"""
    base_dir = Path(__file__).resolve().parents[1]
    results_file = base_dir / 'results_fixed' / 'regressions' / 'by_symbol_day.parquet'
    
    if not results_file.exists():
        print(f"Results file not found: {results_file}")
        return None
    
    df = pd.read_parquet(results_file)
    print(f"Loaded {len(df)} observations")
    return df


def figure1_beta_distribution(df, out_dir):
    """Figure 1: Distribution of beta coefficients"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Histogram
    ax1.hist(df['beta'], bins=30, edgecolor='black', alpha=0.7)
    ax1.axvline(df['beta'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean = {df["beta"].mean():.2f}')
    ax1.axvline(df['beta'].median(), color='orange', linestyle='--', linewidth=2, label=f'Median = {df["beta"].median():.2f}')
    ax1.set_xlabel('Beta Coefficient')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Distribution of OFI Beta Coefficients\n(Normalized OFI → Mid-Price Change)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Box plot by symbol
    symbols = sorted(df['symbol'].unique())
    data_by_symbol = [df[df['symbol'] == sym]['beta'].values for sym in symbols]
    bp = ax2.boxplot(data_by_symbol, labels=symbols, patch_artist=True)
    
    # Color the boxes
    colors = sns.color_palette("husl", len(symbols))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax2.axhline(0, color='gray', linestyle='-', linewidth=0.8, alpha=0.5)
    ax2.set_xlabel('Symbol')
    ax2.set_ylabel('Beta Coefficient')
    ax2.set_title('Beta Distribution by Symbol')
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(out_dir / 'fig1_beta_distribution.png', bbox_inches='tight')
    plt.close()
    print("✓ Created Figure 1: Beta Distribution")


def figure2_rsquared_analysis(df, out_dir):
    """Figure 2: R-squared analysis"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Histogram of R²
    ax1.hist(df['r2'], bins=30, edgecolor='black', alpha=0.7, color='steelblue')
    ax1.axvline(df['r2'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean = {df["r2"].mean():.4f}')
    ax1.set_xlabel('R-squared')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Distribution of R² Values\n(Explanatory Power of OFI)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # R² by symbol
    r2_by_symbol = df.groupby('symbol')['r2'].mean().sort_values(ascending=False)
    colors_r2 = sns.color_palette("viridis", len(r2_by_symbol))
    bars = ax2.bar(range(len(r2_by_symbol)), r2_by_symbol.values, color=colors_r2, alpha=0.8, edgecolor='black')
    ax2.set_xticks(range(len(r2_by_symbol)))
    ax2.set_xticklabels(r2_by_symbol.index, rotation=45)
    ax2.set_xlabel('Symbol')
    ax2.set_ylabel('Mean R²')
    ax2.set_title('Average R² by Symbol\n(Higher = Better Predictive Power)')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars, r2_by_symbol.values)):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f'{val:.3f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(out_dir / 'fig2_rsquared_analysis.png', bbox_inches='tight')
    plt.close()
    print("✓ Created Figure 2: R-squared Analysis")


def figure3_scatter_examples(df, out_dir):
    """Figure 3: Example scatter plots for selected symbols"""
    # Load timeseries for a few symbols on 2017-01-03
    base_dir = Path(__file__).resolve().parents[1]
    ts_dir = base_dir / 'results_fixed' / 'timeseries' / '2017-01-03'
    
    # Select 4 diverse symbols
    symbols_to_plot = ['AMD', 'AAPL', 'SPY', 'NVDA']
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    for idx, symbol in enumerate(symbols_to_plot):
        ts_file = ts_dir / f'{symbol}.parquet'
        if not ts_file.exists():
            continue
        
        ts = pd.read_parquet(ts_file)
        valid = ts[['normalized_OFI', 'd_mid_bps']].dropna()
        
        # Subsample for plotting
        if len(valid) > 3000:
            valid = valid.sample(n=3000, random_state=42)
        
        ax = axes[idx]
        
        # Scatter plot
        ax.scatter(valid['normalized_OFI'], valid['d_mid_bps'], 
                  s=2, alpha=0.3, color='steelblue')
        
        # Regression line
        x = valid['normalized_OFI'].values
        y = valid['d_mid_bps'].values
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        x_line = np.linspace(valid['normalized_OFI'].min(), valid['normalized_OFI'].max(), 100)
        ax.plot(x_line, p(x_line), "r-", linewidth=2, label=f'y = {z[0]:.2f}x + {z[1]:.2f}')
        
        # Get beta and R² for this symbol-day
        row = df[(df['symbol'] == symbol) & (df['day'] == '2017-01-03')]
        if len(row) > 0:
            beta = row['beta'].iloc[0]
            r2 = row['r2'].iloc[0]
            ax.set_title(f'{symbol} (2017-01-03)\nβ = {beta:.3f}, R² = {r2:.4f}', fontweight='bold')
        else:
            ax.set_title(f'{symbol} (2017-01-03)', fontweight='bold')
        
        ax.set_xlabel('Normalized OFI')
        ax.set_ylabel('Mid-Price Change (bps)')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        ax.axhline(0, color='gray', linestyle='-', linewidth=0.8, alpha=0.5)
        ax.axvline(0, color='gray', linestyle='-', linewidth=0.8, alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(out_dir / 'fig3_scatter_examples.png', bbox_inches='tight')
    plt.close()
    print("✓ Created Figure 3: Scatter Plot Examples")


def figure4_summary_table(df, out_dir):
    """Figure 4: Summary statistics table"""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Calculate statistics by symbol
    stats = []
    for symbol in sorted(df['symbol'].unique()):
        sym_data = df[df['symbol'] == symbol]
        stats.append({
            'Symbol': symbol,
            'N Days': len(sym_data),
            'Beta Mean': f"{sym_data['beta'].mean():.3f}",
            'Beta Std': f"{sym_data['beta'].std():.3f}",
            'Beta+ %': f"{100*(sym_data['beta'] > 0).mean():.0f}%",
            'R² Mean': f"{sym_data['r2'].mean():.4f}",
            'R² Median': f"{sym_data['r2'].median():.4f}",
            'Mean Depth': f"{sym_data['mean_depth'].mean():.0f}",
        })
    
    # Add overall row
    stats.append({
        'Symbol': 'OVERALL',
        'N Days': len(df),
        'Beta Mean': f"{df['beta'].mean():.3f}",
        'Beta Std': f"{df['beta'].std():.3f}",
        'Beta+ %': f"{100*(df['beta'] > 0).mean():.0f}%",
        'R² Mean': f"{df['r2'].mean():.4f}",
        'R² Median': f"{df['r2'].median():.4f}",
        'Mean Depth': f"{df['mean_depth'].mean():.0f}",
    })
    
    stats_df = pd.DataFrame(stats)
    
    # Create table
    table = ax.table(cellText=stats_df.values,
                    colLabels=stats_df.columns,
                    cellLoc='center',
                    loc='center',
                    colWidths=[0.10, 0.10, 0.12, 0.12, 0.12, 0.12, 0.14, 0.14])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    # Style header
    for i in range(len(stats_df.columns)):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Style overall row
    for i in range(len(stats_df.columns)):
        table[(len(stats_df), i)].set_facecolor('#E7E6E6')
        table[(len(stats_df), i)].set_text_props(weight='bold')
    
    # Alternate row colors
    for i in range(1, len(stats_df)):
        color = '#F2F2F2' if i % 2 == 0 else 'white'
        for j in range(len(stats_df.columns)):
            table[(i, j)].set_facecolor(color)
    
    plt.title('OFI Replication Results Summary\nContetal. (2014) Methodology', 
             fontsize=14, fontweight='bold', pad=20)
    
    plt.savefig(out_dir / 'fig4_summary_table.png', bbox_inches='tight', dpi=300)
    plt.close()
    print("✓ Created Figure 4: Summary Table")


def figure5_time_series_example(df, out_dir):
    """Figure 5: Time series example showing OFI and price movements"""
    base_dir = Path(__file__).resolve().parents[1]
    ts_dir = base_dir / 'results_fixed' / 'timeseries' / '2017-01-03'
    
    # Use AMD as example
    ts_file = ts_dir / 'AMD.parquet'
    if not ts_file.exists():
        print("! Skipping Figure 5: Timeseries file not found")
        return
    
    ts = pd.read_parquet(ts_file)
    
    # Plot first hour only for clarity (9:30-10:30)
    ts = ts.iloc[:3600]  # First 3600 seconds = 1 hour
    
    fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
    
    time_labels = pd.to_datetime(ts.index).strftime('%H:%M')
    x = range(len(ts))
    
    # Plot 1: Mid price
    axes[0].plot(x, ts['mid'], linewidth=0.8, color='black')
    axes[0].set_ylabel('Mid Price ($)')
    axes[0].set_title('AMD - January 3, 2017 (First Hour)\nMid-Price Evolution', fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: OFI (raw)
    axes[1].plot(x, ts['ofi'], linewidth=0.5, color='steelblue', alpha=0.7)
    axes[1].axhline(0, color='red', linestyle='--', linewidth=0.8)
    axes[1].set_ylabel('OFI (shares)')
    axes[1].set_title('Order Flow Imbalance (OFI)', fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    # Plot 3: Normalized OFI
    axes[2].plot(x, ts['normalized_OFI'], linewidth=0.5, color='green', alpha=0.7)
    axes[2].axhline(0, color='red', linestyle='--', linewidth=0.8)
    axes[2].set_ylabel('Normalized OFI')
    axes[2].set_title('Normalized OFI (by Rolling Depth)', fontweight='bold')
    axes[2].grid(True, alpha=0.3)
    
    # Plot 4: Mid-price change
    axes[3].bar(x, ts['d_mid_bps'], width=1.0, color='orange', alpha=0.6, edgecolor='none')
    axes[3].axhline(0, color='red', linestyle='--', linewidth=0.8)
    axes[3].set_ylabel('Δ Mid (bps)')
    axes[3].set_xlabel('Time')
    axes[3].set_title('Mid-Price Changes (basis points)', fontweight='bold')
    axes[3].grid(True, alpha=0.3)
    
    # Set x-axis labels (show every 10 minutes)
    tick_positions = range(0, len(ts), 600)  # Every 600 seconds = 10 minutes
    axes[3].set_xticks(tick_positions)
    axes[3].set_xticklabels([time_labels[i] if i < len(time_labels) else '' for i in tick_positions], rotation=0)
    
    plt.tight_layout()
    plt.savefig(out_dir / 'fig5_timeseries_example.png', bbox_inches='tight')
    plt.close()
    print("✓ Created Figure 5: Time Series Example")


def figure6_comparison_before_after(out_dir):
    """Figure 6: Before/After comparison of sign fix"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Before (from AMD validation results)
    before_data = {
        'Beta+%': 60,
        'Mean R²': 0.0016,
        'Sig.%': 0
    }
    
    # After
    after_data = {
        'Beta+%': 100,
        'Mean R²': 0.1423,
        'Sig.%': 80
    }
    
    # Targets
    targets = {
        'Beta+%': 80,
        'Mean R²': 0.01,
        'Sig.%': 60
    }
    
    metrics = list(before_data.keys())
    before_values = list(before_data.values())
    after_values = list(after_data.values())
    target_values = list(targets.values())
    
    x = np.arange(len(metrics))
    width = 0.25
    
    # Bar chart
    bars1 = ax1.bar(x - width, before_values, width, label='Before Fix', color='red', alpha=0.7)
    bars2 = ax1.bar(x, after_values, width, label='After Fix', color='green', alpha=0.7)
    bars3 = ax1.bar(x + width, target_values, width, label='Target', color='blue', alpha=0.5)
    
    ax1.set_xlabel('Metric')
    ax1.set_ylabel('Value')
    ax1.set_title('Impact of OFI Sign Convention Fix\n(AMD Week 1 Validation)', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}' if height < 10 else f'{height:.0f}',
                    ha='center', va='bottom', fontsize=8)
    
    # Radar/Spider chart
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False)
    
    # Normalize values for radar chart
    before_norm = [before_data['Beta+%']/100, before_data['Mean R²']/0.2, before_data['Sig.%']/100]
    after_norm = [after_data['Beta+%']/100, after_data['Mean R²']/0.2, after_data['Sig.%']/100]
    target_norm = [targets['Beta+%']/100, targets['Mean R²']/0.2, targets['Sig.%']/100]
    
    # Close the plot
    before_norm += before_norm[:1]
    after_norm += after_norm[:1]
    target_norm += target_norm[:1]
    angles = np.concatenate((angles, [angles[0]]))
    
    ax2 = plt.subplot(122, projection='polar')
    ax2.plot(angles, before_norm, 'o-', linewidth=2, label='Before Fix', color='red')
    ax2.fill(angles, before_norm, alpha=0.15, color='red')
    ax2.plot(angles, after_norm, 'o-', linewidth=2, label='After Fix', color='green')
    ax2.fill(angles, after_norm, alpha=0.15, color='green')
    ax2.plot(angles, target_norm, 's--', linewidth=1.5, label='Target', color='blue', alpha=0.7)
    
    ax2.set_xticks(angles[:-1])
    ax2.set_xticklabels(metrics)
    ax2.set_ylim(0, 1)
    ax2.set_title('Performance Radar\n(Normalized Scale)', fontweight='bold', pad=20)
    ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(out_dir / 'fig6_before_after_comparison.png', bbox_inches='tight')
    plt.close()
    print("✓ Created Figure 6: Before/After Comparison")


def main():
    print("\n" + "="*70)
    print("GENERATING PRESENTATION FIGURES")
    print("="*70)
    
    # Create output directory
    base_dir = Path(__file__).resolve().parents[1]
    out_dir = base_dir / 'figures_presentation'
    out_dir.mkdir(exist_ok=True)
    
    # Load results
    df = load_results()
    if df is None:
        print("ERROR: Could not load results")
        return
    
    print(f"\nGenerating figures from {len(df)} observations...")
    print()
    
    # Generate all figures
    figure1_beta_distribution(df, out_dir)
    figure2_rsquared_analysis(df, out_dir)
    figure3_scatter_examples(df, out_dir)
    figure4_summary_table(df, out_dir)
    figure5_time_series_example(df, out_dir)
    figure6_comparison_before_after(out_dir)
    
    print()
    print("="*70)
    print(f"✓ ALL FIGURES CREATED")
    print(f"✓ Saved to: {out_dir}")
    print("="*70)
    print("\nFigures generated:")
    print("  1. fig1_beta_distribution.png - Beta coefficient distribution")
    print("  2. fig2_rsquared_analysis.png - R² analysis and predictive power")
    print("  3. fig3_scatter_examples.png - Example OFI vs price scatter plots")
    print("  4. fig4_summary_table.png - Summary statistics table")
    print("  5. fig5_timeseries_example.png - Intraday time series visualization")
    print("  6. fig6_before_after_comparison.png - Impact of OFI sign fix")
    print("\nReady for presentation and report!")


if __name__ == '__main__':
    main()
