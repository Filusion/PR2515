import pandas as pd
import seaborn as sns
import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt

from pathlib import Path

st.set_page_config(page_title="CO₂ Emissions in Europe", layout="wide")
st.title("Visualizing CO₂ Emissions in Relation to country's GDP")

st.markdown("""
This page explores the relationship between a country's Gross Domestic Product (GDP) and its CO₂ emissions.

To better understand this relationship, we analyze how much CO₂ a country emits for every **1,000,000$** 
of GDP it generates. This gives us a more balanced view by accounting for the size of a country's economy 
rather than just total emissions.

We visualize this data to:

- Identify the countries that emit **the most CO₂ per economic output** (worst performers)  
- Highlight those that emit **the least CO₂ per economic output** (best performers)  
- Assess whether economic growth necessarily leads to higher emissions  

By comparing these metrics, we aim to spot trends and evaluate which countries are managing to keep 
their emissions low despite economic activity.
""")

data_path1 = Path(__file__).resolve().parents[2] / "data" / "co2_emmisions_complicated.csv"
data_path2 = Path(__file__).resolve().parents[2] / "data" / "co2-emissions-vs-gdp.csv"
data_path3 = Path(__file__).resolve().parents[2] / "data" / "cultural" / "ne_110m_admin_0_countries.shp"
df_co2 = pd.read_csv(data_path1)
df_gdp  = pd.read_csv(data_path2)
world = gpd.read_file(data_path3)


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

# List of European countries (adjust if needed to match your data exactly)
european_countries = [
    "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", "Belarus", "Belgium",
    "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus", "Czechia", "Denmark",
    "Estonia", "Finland", "France", "Georgia", "Germany", "Greece", "Hungary",
    "Iceland", "Ireland", "Italy", "Kazakhstan", "Kosovo", "Latvia", "Liechtenstein",
    "Lithuania", "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro",
    "Netherlands", "North Macedonia", "Norway", "Poland", "Portugal", "Romania",
    "Russia", "San Marino", "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden",
    "Switzerland", "Turkey", "Ukraine", "United Kingdom", "Vatican"
]

# Filter for European countries
df_gdp_europe = df_gdp[df_gdp['Entity'].isin(european_countries)].copy()

row = df_co2_europe[df_co2_europe['Name'] == 'Serbia and Montenegro'].copy()

serbia_row = row.copy()
montenegro_row = row.copy()

serbia_row['Country_code'] = 'SRB'
serbia_row['Name'] = 'Serbia'

montenegro_row['Country_code'] = 'MNE'
montenegro_row['Name'] = 'Montenegro'

year_columns = [col for col in df_co2_europe.columns if col.isdigit()]

# Split the CO2 data by 85% and 15% because Serbia is much bigger than Montenegro by area and by population
serbia_row[year_columns] = row[year_columns] * 0.96
montenegro_row[year_columns] = row[year_columns] * 0.04

# Drop the original Serbia and Montenegro row
df_co2_europe = df_co2_europe[df_co2_europe['Name'] != 'Serbia and Montenegro']

# Append the two new rows
df_co2_europe = pd.concat([df_co2_europe, serbia_row, montenegro_row], ignore_index=True)


df_gdp_europe = df_gdp_europe[df_gdp_europe['Year'] >= 1970]

gdp_avg = df_gdp_europe.groupby(['Code', 'Entity']).agg({
    'GDP per capita': 'mean',
    'Population (historical)': 'mean'
}).dropna()

gdp_avg['avg_total_gdp'] = gdp_avg['GDP per capita'] * gdp_avg['Population (historical)']
gdp_avg = gdp_avg.reset_index() 


co2_cols = df_co2_europe.columns[df_co2_europe.columns.str.fullmatch(r'\d{4}')]  # only year columns
df_co2_europe['avg_total_co2'] = df_co2_europe[co2_cols].mean(axis=1)
co2_avg = df_co2_europe[['Country_code', 'Name', 'avg_total_co2']]

# merge both dataframes in one
combined_df = pd.merge(
    gdp_avg,
    co2_avg,
    left_on='Code',
    right_on='Country_code',
    how='inner'
)

# Calculate CO₂ per dollar and per million dollars
combined_df['co2_per_dollar'] = combined_df['avg_total_co2'] / combined_df['avg_total_gdp']
combined_df['co2_per_million_dollars'] = combined_df['co2_per_dollar'] * 1_000_000

# clean up the dataframe
result_df = combined_df[['Entity', 'Code', 'avg_total_co2', 'avg_total_gdp', 'co2_per_dollar', 'co2_per_million_dollars']]

# sort by CO2 per million dollars
result_df_worst = result_df.sort_values(by='co2_per_million_dollars', ascending=False)
result_df_best = result_df.sort_values(by='co2_per_million_dollars', ascending=True)


fig, ax = plt.subplots(figsize=(10, 4))
bars = ax.bar(result_df_worst['Entity'].head(10), result_df_worst['co2_per_million_dollars'].head(10), color='red')

ax.set_title('Top 10 Worst Countries (Highest CO₂ per Million USD GDP)')
ax.set_ylabel('Tons CO₂ per Million USD GDP')
ax.set_xticklabels(result_df_worst['Entity'].head(10), rotation=45, ha='right')
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Add value labels on top of the bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, height + 0.01, f"{height:.2f}", ha='center', fontsize=8)

plt.tight_layout()
st.pyplot(fig)

# Optionally display the dataframe table below the chart
st.dataframe(result_df_worst.head(10))

st.markdown("""
As seen in the plot above, the top 10 worst-performing countries in terms of **CO₂ emissions
per 1,000,000 USD of GDP** are:

- Ukraine  
- Estonia  
- Russia  
- Czechia  
- Bulgaria  
- Serbia  
- Moldova  
- Poland  
- Luxembourg and
- Bosnia and Herzegovina  

These countries emit significantly more CO₂ relative to the size of their economies. A few key observations:

- Many of these countries were part of the former Eastern Bloc or Soviet Union, where economies 
are often more industrial-based and reliant on fossil fuels.
- Countries like **Ukraine, Russia, and Moldova** still heavily depend on coal and natural gas,
contributing to higher emissions per dollar of GDP.
- **Luxembourg**, despite being a wealthy country, appears on this list possibly due to its small 
size and high emissions relative to its GDP — highlighting how per capita or per output metrics can reveal unexpected inefficiencies.
- This data suggests that high CO₂ intensity isn’t always tied to economic strength, but rather to **energy sources, industrial structure, and efficiency**.

This view helps us better understand which economies may benefit the most from cleaner energy transitions or modernization of industrial processes.
""")

st.markdown("### Top 10 Best Countries (Lowest CO₂ per Million USD GDP)")

fig, ax = plt.subplots(figsize=(10, 4))
bars = ax.bar(result_df_best['Entity'].head(10), result_df_best['co2_per_million_dollars'].head(10), color='green')

ax.set_title('Top 10 Best Countries (Lowest CO₂ per Million USD GDP)')
ax.set_ylabel('Tons CO₂ per Million USD GDP')
ax.set_xticklabels(result_df_best['Entity'].head(10), rotation=45, ha='right')
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Add value labels on top of the bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, height + 0.01, f"{height:.2f}", ha='center', fontsize=8)

plt.tight_layout()
st.pyplot(fig)

# Optionally display the dataframe table below the chart
st.dataframe(result_df_best.head(10))

st.markdown(""" 
On the above plot are the top 10 best-performing countries in terms of **CO₂ emissions per 1,000,000 
USD of GDP**. These countries are:

- Switzerland  
- Norway  
- Sweden  
- Portugal  
- France  
- Italy  
- Austria  
- Spain  
- Malta and
- Ireland  

These countries emit the least CO₂ relative to the size of their economies, indicating high economic
efficiency with lower environmental impact. Key insights:

- Most of these are **Western European nations** with highly developed service-based economies and 
strong environmental policies.
- Countries like **Switzerland, Sweden, and Norway** have invested heavily in renewable energy, 
energy efficiency, and sustainable infrastructure.
- **France** benefits from a nuclear-heavy energy mix, reducing carbon intensity without compromising
economic output.
- **Portugal and Spain** have made substantial gains in renewable energy (especially solar and wind)
over the past decade.
- The presence of **Malta**, a small and service-driven economy, shows how size and sector composition
can greatly affect emissions efficiency.

This ranking shows a clear trend: **strong climate policy, clean energy investment, and diversified 
economies** play a significant role in decoupling GDP growth from CO₂ emissions.
""")

st.markdown("### Map visualization of CO2 emissions per 1,000,000$ in Europe")

# Rename and replace country names
result_df = result_df.rename(columns={'Entity': 'Country'})
result_df['Country'] = result_df['Country'].replace({'Czech Republic': 'Czechia'})
result_df['Country'] = result_df['Country'].replace({'Bosnia and Herzegovina': 'Bosnia and Herz.'})

# Merge world map with data
map_df = world.merge(result_df, left_on='NAME', right_on='Country', how='inner')

# Filter for Europe
map_df = map_df[map_df['CONTINENT'] == 'Europe']

# Set map bounds
minx, miny, maxx, maxy = -25, 34, 45, 72

fig, ax = plt.subplots(1, 1, figsize=(10, 5))

map_df.plot(
    column='co2_per_million_dollars',
    cmap='YlGnBu',
    linewidth=0.8,
    edgecolor='0.8',
    legend=True,
    ax=ax,
    legend_kwds={'label': "CO₂ Emissions per Million USD GDP", 'shrink': 0.9}
)

ax.set_xlim(minx, maxx)
ax.set_ylim(miny, maxy)
ax.set_title('CO₂ Emissions per Million USD GDP by European Country', fontsize=16, weight='bold')
ax.axis('off')

plt.tight_layout()
st.pyplot(fig)

st.markdown(""" 
On the map above, you can see a visual representation of **CO₂ emissions per 1,000,000$ 
of GDP** across European countries. The darker the shade, the higher the emissions relative to economic output.

This map offers a clear geographical insight into which countries are the most and least 
efficient in converting economic activity into carbon emissions. Eastern European countries
like **Ukraine**, **Russia**, and **Estonia** stand out with higher emissions per unit of GDP, 
while Western and Northern European countries like **Switzerland**, **Sweden**, and **France**
appear much more efficient.

This approach—calculating **CO₂ per economic output**—is a useful way to account for both emissions
and the size of a country’s economy. It allows us to identify nations that generate more pollution
relative to their productivity.
""")