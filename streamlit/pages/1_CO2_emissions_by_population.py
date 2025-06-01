import pandas as pd
import seaborn as sns
import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt

from pathlib import Path


st.set_page_config(page_title="CO₂ Emissions in Europe", layout="wide")
st.title("Visualizing CO₂ Emissions in Relation to Population")

st.markdown("""
On this page, we analyze the relationship between CO₂ emissions and the population of each European country. 
Explore how emissions and population have changed over time, see the top 10 countries by CO₂ emissions per capita,
and also view a map visualization highlighting the emissions per across the continent.
""")

data_path1 = Path(__file__).resolve().parents[2] / "data" / "co2_emmisions_complicated.csv"
data_path2 = Path(__file__).resolve().parents[2] / "data" / "world_population.csv"
data_path3 = Path(__file__).resolve().parents[2] / "data" / "cultural" / "ne_110m_admin_0_countries.shp"
df_co2 = pd.read_csv(data_path1)
df_pop = pd.read_csv(data_path2)
world = gpd.read_file(data_path3)

# --- FILTERING ---
df_co2_europe = df_co2[df_co2['Region'].str.contains('Europe', case=False, na=False)]

# Add and clean specific countries
df_russia = df_co2[df_co2['Name'].str.contains('Russian Federation', case=False)].copy()
df_russia['Name'] = 'Russia'

df_ukraine = df_co2[df_co2['Name'].str.contains('Ukraine', case=False)].copy()
df_belarus = df_co2[df_co2['Name'].str.contains('Belarus', case=False)].copy()
df_moldova = df_co2[df_co2['Name'].str.contains('Moldova', case=False)].copy()
df_moldova['Name'] = 'Moldova'

df_co2_europe = pd.concat([df_co2_europe, df_russia, df_ukraine, df_belarus, df_moldova]).drop_duplicates()

# Fix Serbia and Montenegro
row = df_co2_europe[df_co2_europe['Name'] == 'Serbia and Montenegro'].copy()
serbia_row = row.copy(); serbia_row['Country_code'] = 'SRB'; serbia_row['Name'] = 'Serbia'
montenegro_row = row.copy(); montenegro_row['Country_code'] = 'MNE'; montenegro_row['Name'] = 'Montenegro'
year_columns = [col for col in df_co2_europe.columns if col.isdigit()]
serbia_row[year_columns] = row[year_columns] * 0.96
montenegro_row[year_columns] = row[year_columns] * 0.04
df_co2_europe = df_co2_europe[df_co2_europe['Name'] != 'Serbia and Montenegro']
df_co2_europe = pd.concat([df_co2_europe, serbia_row, montenegro_row], ignore_index=True)

# Filter population
df_pop_europe = df_pop[df_pop['Continent'] == 'Europe']
df_co2_filtered = df_co2_europe[['Name'] + year_columns]
pop_years = [f"{year} Population" for year in [1970, 1980, 1990, 2000, 2010, 2015, 2020, 2022]]
df_pop_filtered = df_pop_europe[['Country/Territory'] + pop_years]

# Sum totals
years = ['1970', '1980', '1990', '2000', '2010', '2015', '2020', '2022']
co2_total = df_co2_filtered[years].sum()
pop_total = df_pop_filtered[pop_years].sum()
pop_total.index = years

fig, ax1 = plt.subplots(figsize=(10, 4))

# CO2 emissions
st.subheader("Trends in CO₂ Emissions and Population Growth in Europe (1970–2023)")
ax1.plot(years, co2_total, color='crimson', marker='o', linewidth=2, label='CO2 emissions (*1 million tons)')
ax1.set_xlabel('Year', fontsize=12)
ax1.set_ylabel('CO2 emissions (*1 million tons)', color='crimson', fontsize=12)
ax1.tick_params(axis='y', labelcolor='crimson')
ax1.grid(True, which='both', axis='y', linestyle='--', alpha=0.5)

# Population on second Y-axis
ax2 = ax1.twinx()
ax2.plot(years, pop_total, color='royalblue', marker='s', linewidth=2, label='Population (*100 million)')
ax2.set_ylabel('Population (*100 million)', color='royalblue', fontsize=12)
ax2.tick_params(axis='y', labelcolor='royalblue')

# Title and legend
fig.suptitle('Total CO2 Emissions and Population in Europe (1970 - 2023)', fontsize=14, weight='bold')
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

# Streamlit output
st.pyplot(fig)

st.markdown("""
The plot above shows how CO₂ emissions and population have changed over the past 53 years. 
We can see that the population has steadily increased with only minor fluctuations.  

CO₂ emissions, on the other hand, grew from 1970 until around 1990, when they dropped sharply. 
This decline corresponds to the fall of the Soviet Union, which caused significant reductions in emissions from countries like Russia and Ukraine.  

Since then, emissions have generally decreased until 2020, when they started rising slightly again following the COVID-19 pandemic.

Overall, this suggests that population growth and CO₂ emissions in Europe are not strongly correlated and are influenced by other economic and political factors.
""")

# Prepare 2022 data
co2_2022 = df_co2_europe[['Name', '2022']]
pop_2022 = df_pop_europe[['Country/Territory', '2022 Population']]

# Merge countries by name
df_merged = pd.merge(co2_2022, pop_2022, left_on='Name', right_on='Country/Territory', how='inner')

# CO2 emissions per capita
df_merged['CO2_per_capita'] = df_merged['2022'] / df_merged['2022 Population']

# Top 10 countries by CO2 per capita
top10_per_capita = df_merged.sort_values(by='CO2_per_capita', ascending=False).head(10)

# Plotting
fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(top10_per_capita['Name'], top10_per_capita['CO2_per_capita'], color='purple')
ax.set_ylabel('CO₂ Emissions per Capita (tons per person)', fontsize=12)
ax.set_title('Top 10 European Countries by CO₂ Emissions per Capita (2022)', fontsize=14, weight='bold')
ax.set_xticklabels(top10_per_capita['Name'], rotation=45, ha='right')
ax.grid(axis='y', linestyle='--', alpha=0.5)
fig.tight_layout()

st.pyplot(fig)

st.markdown("""
The plot above shows the top 10 European countries by CO₂ emissions per capita in 2022. The list includes Russia, 
Luxembourg, Estonia, Czech Republic, Iceland, Norway, Poland, Germany, Belgium, and Serbia.  

While some countries’ positions on this list make sense given their industrial profiles, others—like
Luxembourg—seem less intuitive. This suggests that using CO₂ emissions per capita alone may not fully
capture the complexities of emissions relative to population size. Further analysis may be needed to better understand these differences.
""")

# Fix country names for matching
df_co2_europe['Name'] = df_co2_europe['Name'].replace('Czech Republic', 'Czechia')
pop_2022 = df_pop_europe[['Country/Territory', '2022 Population']].copy()
pop_2022['Country/Territory'] = pop_2022['Country/Territory'].replace('Czech Republic', 'Czechia')

co2_2022 = df_co2_europe[['Name', '2022']].copy()

# Merge CO2 and population
df_merged = pd.merge(co2_2022, pop_2022, left_on='Name', right_on='Country/Territory', how='inner')
df_merged['CO2_per_capita'] = df_merged['2022'] / df_merged['2022 Population']

# Clean up some country names for display
df_merged['Name'] = df_merged['Name'].replace({'Bosnia and Herzegovina': 'Bosnia and Herz.'})

# Merge with world geopandas dataframe
map_df = world.merge(df_merged, left_on='NAME', right_on='Name')

# Filter for Europe only
map_df = map_df[map_df['CONTINENT'] == 'Europe']

# Europe bounds to zoom in
minx, miny, maxx, maxy = -25, 34, 45, 72

# Plotting
fig, ax = plt.subplots(1, 1, figsize=(10, 5))
map_df.plot(
    column='CO2_per_capita',
    cmap='OrRd',
    linewidth=0.8,
    edgecolor='0.8',
    legend=True,
    ax=ax,
    legend_kwds={'label': "CO₂ Emissions per Capita (tons/person)"}
)

ax.set_xlim(minx, maxx)
ax.set_ylim(miny, maxy)
ax.set_title('European CO₂ Emissions per Capita (2022)', fontsize=15, weight='bold')
ax.axis('off')
plt.tight_layout()

st.pyplot(fig)

st.markdown("""
The CO₂ emissions per capita are clearly illustrated on the map above. As expected, Russia ranks highest.
However, some countries that might not be commonly perceived as major emitters — such as Estonia, Luxembourg, 
Norway, Iceland, Austria, and Ireland — also show relatively high emissions per capita. This highlights the 
complexity behind CO₂ emissions and the need to consider multiple factors when interpreting the data.
""")
