import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from pathlib import Path
from matplotlib.ticker import FuncFormatter

st.set_page_config(page_title="CO₂ Emissions in Europe", layout="wide")
st.title("CO₂ Leading Sectors in Co₂ emissions")

st.markdown(""" 
On this page, we highlight the leading sectors contributing to CO₂ emissions across Europe. We identified
the most influential sectors by analyzing the top 10 emitting sectors within the top 5 CO₂ emitting countries:
**Russia, Germany, the United Kingdom, Ukraine, and France**.
""")

data_path1 = Path(__file__).resolve().parents[2] / "data" / "co2_emmisions_complicated.csv"
data_path2 = Path(__file__).resolve().parents[2] / "data" / "co2_emmisions_by_sector.csv"

df_co2 = pd.read_csv(data_path1)
df_co2_sectors   = pd.read_csv(data_path2)

# Filtering the data only for European countries
df_co2_europe = df_co2[df_co2['Region'].str.contains('Europe', case=False, na=False)]

# Add Russia
df_russia = df_co2[df_co2['Name'].str.contains('Russian Federation', case=False, na=False)].copy()
df_russia['Name'] = df_russia['Name'].replace('Russian Federation', 'Russia')

# Add Ukraine
df_ukraine = df_co2[df_co2['Name'].str.contains('Ukraine', case=False, na=False)].copy()

# Add Belarus
df_belarus = df_co2[df_co2['Name'].str.contains('Belarus', case=False, na=False)].copy()

# Add Moldova
df_moldova = df_co2[df_co2['Name'].str.contains('Moldova', case=False, na=False)].copy()
df_moldova['Name'] = df_moldova['Name'].replace('Moldova, Republic of', 'Moldova')

# Combine all
df_co2_europe = pd.concat([df_co2_europe, df_russia, df_ukraine, df_belarus, df_moldova]).drop_duplicates()
# Calculating the average CO2 emission by country from the year 1970 to the year 2023
year_columns = [col for col in df_co2_europe.columns if col.isdigit()]

df_avg = df_co2_europe.copy()
df_avg["Average_CO2"] = df_avg[year_columns].mean(axis=1)

df_avg_sorted = df_avg.sort_values(by="Average_CO2", ascending=False)

# Getting the top5 countries with most average emissions 
# Which we'll try to find the leading factors for that cause
df_top_5 = df_avg_sorted[["Name", "Average_CO2"]].reset_index(drop=True).head(5)
print('Top 5 european countries with most emissions:')
df_top_5


# Creating individual dataframes for the top 5 countries with most emissions containing emission per sector
df_russia = df_co2_sectors[(df_co2_sectors["Name"] == "Russian Federation") & (df_co2_sectors["Substance"] == "CO2")].dropna(axis=0)
df_germany = df_co2_sectors[(df_co2_sectors["Name"] == "Germany") & (df_co2_sectors["Substance"] == "CO2")].dropna(axis=0)
df_uk = df_co2_sectors[(df_co2_sectors["Name"] == "United Kingdom") & (df_co2_sectors["Substance"] == "CO2")].dropna(axis=0)
df_ukraine = df_co2_sectors[(df_co2_sectors["Name"] == "Ukraine") & (df_co2_sectors["Substance"] == "CO2")].dropna(axis=0)
df_france = df_co2_sectors[(df_co2_sectors["Name"] == "France") & (df_co2_sectors["Substance"] == "CO2")].dropna(axis=0)

# Ploting CO2 timeline emission by sector for Russia

st.markdown("### Top 10 sectors by total CO₂ emissions in Russia (1970–2023):")
year_columns = [col for col in df_russia.columns if col.isdigit()]
df_russia_sector = df_russia.groupby("Sector")[year_columns].sum()
years = list(map(int, year_columns))
data = df_russia_sector.values

plt.figure(figsize=(10, 6))
plt.stackplot(years, df_russia_sector.values, labels=df_russia_sector.index)

plt.title('Russia CO₂ Emissions by Sector (1970–2023)')
plt.xlabel('Year')
plt.ylabel('CO₂ Emissions (kt)')
plt.legend(loc='upper right', fontsize='small')
plt.grid(True, linestyle='--', alpha=0.6)
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'))

plt.tight_layout()
st.pyplot(plt.gcf())  # Streamlit plot display

total_emissions_by_sector = df_russia_sector.sum(axis=1).sort_values(ascending=False).reset_index()
total_emissions_by_sector.columns = ['Sector', 'Total CO₂ Emissions (kt)']

st.dataframe(total_emissions_by_sector.head(10))


# Ploting CO2 timeline emission by sector for Germany
st.markdown("### Top 10 sectors by total CO₂ emissions in Germany (1970–2023):")

year_columns = [col for col in df_germany.columns if col.isdigit()]
df_germany_sector = df_germany.groupby("Sector")[year_columns].sum()
years = list(map(int, year_columns))
data = df_germany_sector.values

plt.figure(figsize=(16, 8))
plt.stackplot(years, data, labels=df_germany_sector.index)

plt.title('Germany CO₂ Emissions by Sector (1970–2023)')
plt.xlabel('Year')
plt.ylabel('CO₂ Emissions (kt)')
plt.legend(loc='upper right', fontsize='small')
plt.grid(True, linestyle='--', alpha=0.6)
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'))

plt.tight_layout()
st.pyplot(plt.gcf())  

total_emissions_by_sector = df_germany_sector.sum(axis=1).sort_values(ascending=False).reset_index()
total_emissions_by_sector.columns = ['Sector', 'Total CO₂ Emissions (kt)']

st.dataframe(total_emissions_by_sector.head(10))

# Ploting CO2 timeline emission by sector for the United Kingdom
st.markdown("### Top 10 sectors by total CO₂ emissions in the United Kingdom (1970–2023):")

year_columns = [col for col in df_uk.columns if col.isdigit()]
df_uk_sector = df_uk.groupby("Sector")[year_columns].sum()
years = list(map(int, year_columns))
data = df_uk_sector.values

plt.figure(figsize=(16, 8))
plt.stackplot(years, data, labels=df_uk_sector.index)

plt.title('United Kingdom CO₂ Emissions by Sector (1970–2023)')
plt.xlabel('Year')
plt.ylabel('CO₂ Emissions (kt)')
plt.legend(loc='upper right', fontsize='small')
plt.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
st.pyplot(plt.gcf())  

total_emissions_by_sector = df_uk_sector.sum(axis=1).sort_values(ascending=False).reset_index()
total_emissions_by_sector.columns = ['Sector', 'Total CO₂ Emissions (kt)']

st.dataframe(total_emissions_by_sector.head(10))


# Ploting CO2 timeline emission by sector for Ukraine
st.markdown("### Top 10 sectors by total CO₂ emissions in Ukraine (1970–2023):")

year_columns = [col for col in df_ukraine.columns if col.isdigit()]
df_ukraine_sector = df_ukraine.groupby("Sector")[year_columns].sum()
years = list(map(int, year_columns))
data = df_ukraine_sector.values

plt.figure(figsize=(16, 8))
plt.stackplot(years, data, labels=df_ukraine_sector.index)

plt.title('Ukraine CO₂ Emissions by Sector (1970–2023)')
plt.xlabel('Year')
plt.ylabel('CO₂ Emissions (kt)')
plt.legend(loc='upper right', fontsize='small')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
st.pyplot(plt.gcf())  

total_emissions_by_sector = df_ukraine_sector.sum(axis=1).sort_values(ascending=False).reset_index()
total_emissions_by_sector.columns = ['Sector', 'Total CO₂ Emissions (kt)']

st.dataframe(total_emissions_by_sector.head(10))


# Ploting CO2 timeline emission by sector for France
st.markdown("### Top 10 sectors by total CO₂ emissions in France (1970–2023):")

year_columns = [col for col in df_france.columns if col.isdigit()]
df_france_sector = df_france.groupby("Sector")[year_columns].sum()
years = list(map(int, year_columns))
data = df_france_sector.values

plt.figure(figsize=(16, 8))
plt.stackplot(years, data, labels=df_france_sector.index)

plt.title('France CO₂ Emissions by Sector (1970–2023)')
plt.xlabel('Year')
plt.ylabel('CO₂ Emissions (kt)')
plt.legend(loc='upper right', fontsize='small')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
st.pyplot(plt.gcf())  

total_emissions_by_sector = df_france_sector.sum(axis=1).sort_values(ascending=False).reset_index()
total_emissions_by_sector.columns = ['Sector', 'Total CO₂ Emissions (kt)']

st.dataframe(total_emissions_by_sector.head(10))


st.markdown(""" 
### List of Leading Factors in CO₂ Emissions

From the stacked area plots of CO₂ emissions per sector for the top 5 European countries with the highest emissions, we can
see that the most impactful sectors for CO₂ emissions are:

- Public electricity and heat production  
- Residential and other sectors  
- Manufacturing Industries and Construction  
- Road transportation (no resuspension)  
- Other Energy Industries  
- Cement production  
- Production of chemicals  
- Fugitive emissions from solid fuels  
- Production of metals  
- Lime production  
- Fugitive emissions from oil and gas  
- Fugitive emissions from gaseous fuels  
- Other direct soil emissions  
- Inland navigation  
- Rail transportation  
- And others...

The analysis reveals that sectors like electricity and heat production, residential use, road transport, manufacturing industries
and construction, cement production, production of metals, and others are the main contributors to CO₂ emissions in Europe’s top-emitting
countries. Their strong alignment with total emissions suggests a high impact.
""")