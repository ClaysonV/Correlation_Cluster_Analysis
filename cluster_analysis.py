import yfinance as yf
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings # <--- New import

# --- Step 0: Silence Warnings & Clear Plots ---
# This line tells Python to shut up about "FutureWarnings"
warnings.simplefilter(action='ignore', category=FutureWarning)
plt.close('all')

# --- Step 1: Define a Massive Asset Universe ---
assets = {
    "Technology": ["NVDA", "AAPL", "MSFT", "AMD", "CRM"],
    "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD", "COIN", "MSTR"],
    "Energy": ["XOM", "CVX", "USO", "OXY", "VLO"],
    "Precious Metals": ["GLD", "SLV", "GDX"], 
    "Bonds": ["TLT", "IEF", "SHy", "GOVT"],
    "Banks/Finance": ["JPM", "BAC", "GS", "KBE"],
    "Healthcare": ["JNJ", "PFE", "UNH", "XLV"],
    "Consumer Staples": ["PG", "KO", "WMT", "XLP"], 
    "Real Estate": ["VNQ", "O", "PLD"],
    "China/Emerging": ["BABA", "JD", "FXI", "EEM"],
    "Defense": ["LMT", "RTX", "ITA"]
}

tickers = [ticker for sector in assets.values() for ticker in sector]

print(f"Downloading data for {len(tickers)} assets...")

# --- Step 2: Download & Clean Data ---
# FIX: Added 'auto_adjust=True' to fix the yfinance warning
data = yf.download(tickers, start="2022-01-01", end="2024-01-01", progress=False, auto_adjust=True, multi_level_index=False)['Close']

# FIX: Added 'fill_method=None' to fix the pandas warning
returns = data.pct_change(fill_method=None).dropna()

# --- Step 3: Create Sector Data ---
sector_returns = pd.DataFrame()
for sector, tickers_in_sector in assets.items():
    valid_tickers = [t for t in tickers_in_sector if t in returns.columns]
    if valid_tickers:
        sector_returns[sector] = returns[valid_tickers].mean(axis=1)

# --- Step 4: Calculate Correlations ---
asset_corr = returns.corr()
sector_corr = sector_returns.corr()
print("Correlations Computed.")

# --- Step 5: User Input for Specific Analysis ---
print("-" * 50)
print(f"Available Assets: {len(returns.columns)} total tickers.")
print("-" * 50)
target_asset = input("Enter an asset symbol to analyze (e.g., NVDA, BTC-USD, LMT) or press Enter to skip: ").strip().upper()

if target_asset and target_asset in returns.columns:
    print(f"Generating specific correlation report for {target_asset}...")
    
    target_data = asset_corr[target_asset].drop(target_asset).sort_values(ascending=False)
    
    # We take the Top 10 positive and Top 10 negative correlations to keep the chart readable
    top_10 = target_data.head(10)
    bottom_10 = target_data.tail(10)
    combined = pd.concat([top_10, bottom_10])

    plt.figure(figsize=(12, 8))
    colors = ['#cc3333' if x > 0 else '#3366cc' for x in combined.values]
    
    sns.barplot(x=combined.values, y=combined.index, palette=colors, hue=combined.index, legend=False)
    
    plt.title(f"Top Correlation Drivers for {target_asset} (2022-2024)", fontsize=16)
    plt.xlabel("Correlation Coefficient")
    plt.axvline(0, color='black', linestyle='--', alpha=0.7)
    plt.tight_layout()

elif target_asset:
    print(f"Warning: {target_asset} not found in data. Skipping Chart 3.")

# --- Step 6: Visualization 1 - Asset Cluster Map ---
# This map will be huge now, so we adjust the font size
sns.set_theme(style="darkgrid")
clustermap = sns.clustermap(
    asset_corr,
    method='ward',
    cmap='vlag', 
    center=0,
    linewidths=0.2,   # Thinner lines
    figsize=(18, 18), # Bigger image
    annot=False,      # Turn OFF numbers because it's too crowded now
    dendrogram_ratio=(.1, .2),
    cbar_pos=(0.02, 0.8, 0.03, 0.18)
)
clustermap.fig.suptitle(
    f"Diversified Asset Cluster Map (2022-2024)\nHierarchical Clustering", 
    y=0.92, fontsize=20, color='black'
)

# --- Step 7: Visualization 2 - Sector Correlation Matrix ---
plt.figure(figsize=(12, 10))
sns.heatmap(
    sector_corr, 
    annot=True, 
    cmap='coolwarm', 
    center=0, 
    fmt=".2f", 
    linewidths=1, 
    linecolor='black'
)
plt.title("Sector vs. Sector Correlation Matrix", fontsize=16)
plt.tight_layout()

print("Analysis Complete. Displaying plots...")

# --- Step 8: Show Plots ---
plt.show()

# --- Step 9: Text Report ---
print("\nSECTOR HIGHLIGHTS:")
sector_corr_masked = sector_corr.mask(np.eye(len(sector_corr), dtype=bool))
max_corr = sector_corr_masked.stack().idxmax()
max_val = sector_corr_masked.max().max()

min_corr = sector_corr_masked.stack().idxmin()
min_val = sector_corr_masked.min().min()

print(f"HIGHEST Sector Correlation: {max_corr} ({max_val:.2f})")
print(f"LOWEST Sector Correlation:  {min_corr} ({min_val:.2f})")