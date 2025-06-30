import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime

# Für historische Daten: SPY ETF als Proxy für SPX
import yfinance as yf

# Lade SPY Daten für die letzten 5 Jahre
start_date = "2020-06-30"
end_date = "2025-06-30"
spy = yf.download("SPY", start=start_date, end=end_date, progress=False)

# Monatsschlusskurse
monthly_prices = spy['Close'].resample('M').last().dropna()

# -----------------------------------------
# Strategie 1: Klassischer DCA
# -----------------------------------------
monthly_dca_investment = 1000
dca_units = (monthly_dca_investment / monthly_prices).fillna(0)
dca_cumulative_units = dca_units.cumsum()
dca_portfolio_value = dca_cumulative_units * monthly_prices

# -----------------------------------------
# Strategie 2: Saisonal mit Dynamik
# -----------------------------------------
# Definition der 10 stärksten Monate laut Historie (US-Markt): Jan, Feb, Mar, Apr, May, Jul, Oct, Nov, Dec
# Schwächste Monate: Jun, Sep
strong_months = [1, 2, 3, 4, 5, 7, 10, 11, 12]
weak_months = [6, 9]

seasonal_units = []
seasonal_value = []
units_held = 0
cash_buffer = 0
portfolio_value = 0
sell_trigger = False
next_month_extra_investment = 0

for date in monthly_prices.index:
    price = monthly_prices.loc[date]
    month = date.month
    # Verkauf 20% in schwachem Monat
    if month in weak_months:
        sell_trigger = True
        units_to_sell = 0.2 * units_held
        cash_buffer += units_to_sell * price
        units_held -= units_to_sell
    else:
        sell_trigger = False

    # In starken Monaten: 1200€ investieren, ggf. mit zusätzlichem Cash aus Verkauf
    if month in strong_months:
        invest_amount = 1200 + next_month_extra_investment
        units_held += invest_amount / price
        next_month_extra_investment = 0
    else:
        # falls im Vormonat verkauft wurde, erhöhe Sparrate in den nächsten zwei Monaten
        if sell_trigger:
            next_month_extra_investment = cash_buffer / 2
            cash_buffer = 0

    portfolio_value = units_held * price
    seasonal_units.append(units_held)
    seasonal_value.append(portfolio_value + cash_buffer)

seasonal_value_series = pd.Series(seasonal_value, index=monthly_prices.index)

# -----------------------------------------
# Plot: Vergleich der Strategien
# -----------------------------------------
plt.figure(figsize=(12, 6))
plt.plot(dca_portfolio_value, label='DCA: 1.000€/Monat', linewidth=2)
plt.plot(seasonal_value_series, label='Saisonal: 1.200€ in starken Monaten + Rebalancing', linewidth=2)
plt.title('Strategievergleich: DCA vs. Saisonal über 5 Jahre (SPY)')
plt.ylabel('Portfolio-Wert (€)')
plt.xlabel('Datum')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Endwerte für Vergleich
dca_final = dca_portfolio_value.iloc[-1]
seasonal_final = seasonal_value_series.iloc[-1]
dca_final, seasonal_final
