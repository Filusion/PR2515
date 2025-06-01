import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from pathlib import Path

st.set_page_config(page_title="CO₂ Emissions in Europe", layout="wide")
st.title("Forecasts for CO₂ emissions in Europe")

data_path1 = Path(__file__).resolve().parents[2] / "data" / "co2_emissions_transformed.csv"
data_path2 = Path(__file__).resolve().parents[2] / "data" / "forecasts_sarima.csv"

df_co2 = pd.read_csv(data_path1, sep=';')
df_co2_sarima = pd.read_csv(data_path2, sep=';')

df_past_grouped = df_co2.groupby('Year')['CO2_emissions'].sum().reset_index()
df_pred_grouped = df_co2_sarima.groupby('year')['CO2_emissions'].sum().reset_index()

fig, ax = plt.subplots(figsize=(16, 6))

ax.grid(axis="y", linestyle="--", alpha=0.5, zorder=0)
ax.bar(df_past_grouped['Year'], df_past_grouped['CO2_emissions'], label='Actual', color='dodgerblue')
ax.bar(df_pred_grouped['year'], df_pred_grouped['CO2_emissions'], label='Prediction', color='orange')

ax.set_title('Forecasts for Total CO₂ Emissions in Europe')
ax.set_xlabel("Year")
ax.set_ylabel("CO₂ Emissions")
ax.legend()
fig.tight_layout()

st.pyplot(fig)

st.markdown("""
We have generated forecasted CO₂ emissions for every country in our dataset. The plot above
shows the combined total emissions for all European countries. As observed, the predicted 
trend closely follows historical data and indicates a gradual decline in CO₂ emissions in the near future.

This downward trend suggests that current efforts toward emission reduction and sustainability
may be having a positive impact. However, continued monitoring and proactive policies will be 
essential to maintain and accelerate this progress.
""")