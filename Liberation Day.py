import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =================================================================
# 1. DATA SOURCES & PARAMETERS
# Sources: Executive Order 14257, Yale Budget Lab (2025-2026), 
# Pricing Lab Pass-through Studies.
# =================================================================

# Sector Mapping
sectors = {
    "ONLN": "E-Commerce (De Minimis Trap)",
    "MCHI": "China Market (Reciprocal Target)",
    "XLI": "US Industrials (Onshoring Bet)",
    "SMH": "Semiconductors (High Tech Tech)"
}

# Yale Budget Lab & Pricing Lab Coefficients
# Pass-through: 61-80% for core goods.
# Base Growth: Reflects 2.5-3.2% manufacturing expansion vs macro drag.
forecasting_factors = {
    "E-Commerce (De Minimis Trap)": {
        "pass_through": 0.80, "elasticity": 0.15, "retaliation_hit": 0.05, "base_growth": -0.015
    },
    "China Market (Reciprocal Target)": {
        "pass_through": 0.70, "elasticity": 0.40, "retaliation_hit": 0.15, "base_growth": -0.01
    },
    "US Industrials (Onshoring Bet)": {
        "pass_through": 0.20, "elasticity": 0.90, "retaliation_hit": 0.02, "base_growth": 0.032
    },
    "Semiconductors (High Tech Tech)": {
        "pass_through": 0.61, "elasticity": 0.60, "retaliation_hit": 0.20, "base_growth": 0.01
    }
}

# =================================================================
# 2. HISTORICAL REPLICATION (APRIL 2025)
# =================================================================

def get_historical_data():
    """Simulates the April 2025 'Liberation Day' Abnormal Returns."""
    dates = pd.to_datetime([
        '2025-04-02', '2025-04-03', '2025-04-04', '2025-04-07', 
        '2025-04-08', '2025-04-09', '2025-04-10', '2025-04-11', '2025-04-14'
    ])
    
    # Cumulative Abnormal Returns (CAR) relative to SPY
    data = {
        'China Market (Reciprocal Target)': [-0.012, 0.028, 0.017, -0.061, -0.062, -0.105, -0.062, -0.045, -0.037],
        'E-Commerce (De Minimis Trap)':     [0.008, -0.025, -0.020, -0.026, -0.042, -0.046, -0.042, -0.041, -0.041],
        'Semiconductors (High Tech Tech)':  [-0.005, -0.036, -0.053, -0.028, -0.040, 0.028, 0.001, 0.010, 0.002],
        'US Industrials (Onshoring Bet)':   [0.001, -0.001, -0.006, -0.009, -0.001, -0.018, 0.000, 0.000, 0.000],
        'S&P 500 (Benchmark)':              [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    }
    return pd.DataFrame(data, index=dates)

# =================================================================
# 3. PREDICTIVE FORECASTING ENGINE (2026-2027)
# =================================================================

def generate_forecast(historical_df):
    """Projects 2026-2027 values using structural realignment factors."""
    years = [2025, 2026, 2027]
    
    # Set 2025 start values based on historical CAR (Base 100)
    start_vals = {col: 100 + (historical_df[col].iloc[-1] * 100) 
                  for col in historical_df.columns if col != 'S&P 500 (Benchmark)'}
    
    forecast_results = {k: [v] for k, v in start_vals.items()}
    
    # TBL Macro Drags
    CPI_DRAG = 0.013  # 1.3% PCE price level rise
    GDP_DRAG = 0.004  # 0.4 pp slow in real GDP growth
    
    for year in [2026, 2027]:
        for sector, stats in forecasting_factors.items():
            # Efficiency gain increases in 2027 as supply chains move
            efficiency_gain = stats['elasticity'] * (0.05 if year == 2027 else 0.02)
            
            # Aggregate drag calculation
            drag = (stats['pass_through'] * CPI_DRAG) + (stats['retaliation_hit'] * 0.03) + GDP_DRAG
            
            prev_val = forecast_results[sector][-1]
            # Growth Formula
            new_val = prev_val * (1 + stats['base_growth'] + efficiency_gain - drag)
            forecast_results[sector].append(new_val)
            
    return pd.DataFrame(forecast_results, index=years)

# =================================================================
# 4. EXECUTION & PLOTTING
# =================================================================

# 1. Run Analysis
hist_df = get_historical_data()
fore_df = generate_forecast(hist_df)

# 2. Visualisation
plt.style.use('fivethirtyeight')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))

# Plot 1: Past Shock
hist_df.plot(ax=ax1, linewidth=3, marker='o')
ax1.set_title("Past: Liberation Day Shock (April 2025)", fontsize=16, fontweight='bold')
ax1.set_ylabel("Abnormal Return vs SPY")
ax1.axvline(x=pd.to_datetime('2025-04-02'), color='red', linestyle='--', alpha=0.5, label='Announcement')
ax1.legend(loc='lower left', fontsize=10)

# Plot 2: Future Forecast
for col in fore_df.columns:
    ax2.plot(fore_df.index, fore_df[col], marker='o', label=col, linewidth=4)
ax2.set_title("Future: Structural Realignment (2026-2027)", fontsize=16, fontweight='bold')
ax2.set_ylabel("Projected Value Index (Base 100)")
ax2.set_xticks([2025, 2026, 2027])
ax2.legend(loc='upper left', fontsize=10)

plt.tight_layout()
plt.show()

# 3. Print Conclusions
print("\n--- 2-YEAR FORECAST SUMMARY (TBL ADJUSTED) ---")
print(fore_df.round(2))
print(f"\nAggregate Household Impact: -$3,800/year purchasing power loss")
print(f"Long-Run GDP Drag: -0.6% persistent contraction")
