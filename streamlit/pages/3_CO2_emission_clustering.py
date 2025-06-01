import os
import warnings
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt

from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


st.set_page_config(page_title="CO₂ Emissions in Europe", layout="wide")
st.title("CO₂ Emissions clustering")

st.markdown("""
This page presents cluster analyses of CO₂ emissions in European countries, comparing them across various factors.
""")



# function returns WSS score for k values from 1 to kmax
def get_elbow(df, max_clusters=10, plot=True):
    """Compute and plot the elbow graph using KMeans WSS (inertia) values."""
    
    wss = []

    # Loop through possible k values
    for k in range(1, max_clusters + 1):
        kmeans = KMeans(n_clusters=k, random_state=0, n_init='auto')
        kmeans.fit(df)
        wss.append(kmeans.inertia_)

    
    # # Plotting in Streamlit
    # fig, ax = plt.subplots(figsize=(5, 3))  # Shrink the plot size here
    # ax.plot(range(1, max_clusters + 1), wss, marker='o')
    # ax.set_title('Elbow Method')
    # ax.set_xlabel('Number of Clusters (k)')
    # ax.set_ylabel('WSS (Within-cluster Sum of Squares)')
    # ax.grid(True)

    # st.pyplot(fig)

    return wss
    

os.environ["LOKY_MAX_CPU_COUNT"] = "4"
warnings.filterwarnings("ignore")

data_path1 = Path(__file__).resolve().parents[2] / "data" / "co2_emmisions_complicated.csv"
data_path2 = Path(__file__).resolve().parents[2] / "data" / "co2-emissions-vs-gdp.csv"
data_path3 = Path(__file__).resolve().parents[2] / "data" / "world_population.csv"
df_emissions = pd.read_csv(data_path1)
df_gdp  = pd.read_csv(data_path2)
df_pop = pd.read_csv(data_path3)




# Filter df_emissions to Europe
df_emissions_europe = df_emissions[df_emissions['Region'].str.contains("Europe", case=False, na=False)]

# Filter df_pop to Europe
df_pop_europe = df_pop[df_pop['Continent'] == 'Europe']

#Euro codes
europe_codes = df_pop_europe["CCA3"].unique()

# Filter df_gdp to Europe by codes
df_gdp_europe = df_gdp[df_gdp['Code'].isin(europe_codes)]

#Add Russia
df_russia = df_emissions_europe[df_emissions_europe['Name'].str.contains('Russian Federation', case=False, na=False)].copy()
df_russia['Name'] = df_russia['Name'].replace('Russian Federation', 'Russia')

# Add Ukraine
df_ukraine = df_emissions_europe[df_emissions_europe['Name'].str.contains('Ukraine', case=False, na=False)].copy()

# Add Belarus
df_belarus = df_emissions_europe[df_emissions_europe['Name'].str.contains('Belarus', case=False, na=False)].copy()

# Add Moldova
df_moldova = df_emissions_europe[df_emissions_europe['Name'].str.contains('Moldova', case=False, na=False)].copy()
df_moldova['Name'] = df_moldova['Name'].replace('Moldova, Republic of', 'Moldova')

# Combine all
df_co2_europe = pd.concat([df_emissions_europe, df_russia, df_ukraine, df_belarus, df_moldova]).drop_duplicates()
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


year = 2020

# Reshape df_co2_europe from wide to long
df_emissions_long = df_co2_europe.melt(
    id_vars=['Region', 'Country_code', 'Name', 'Substance'],
    var_name='Year',
    value_name='Emissions'
)

df_emissions_long['Year'] = pd.to_numeric(df_emissions_long['Year'], errors='coerce')
df_emissions_long = df_emissions_long.dropna(subset=['Year'])
df_emissions_long['Year'] = df_emissions_long['Year'].astype(int)

# Filter for CO2 and selected year
df_emissions_year = df_emissions_long[
    (df_emissions_long['Year'] == year) &
    (df_emissions_long['Substance'].str.lower() == 'co2')
]

# Filter GDP for the same year
df_gdp_year = df_gdp_europe[df_gdp_europe['Year'] == year]

df_merged = df_emissions_year.merge(
    df_gdp_year,
    left_on='Country_code',
    right_on='Code',
    how='inner'
)

# Drop missing values in key columns
df_merged = df_merged.dropna(subset=['Emissions', 'GDP per capita'])

# Dynamically find the per capita emissions column (case insensitive)
per_capita_cols = [col for col in df_merged.columns if 'emissions' in col.lower() and 'per capita' in col.lower()]
if not per_capita_cols:
    raise ValueError("Per capita emissions column not found!")
per_capita_col = per_capita_cols[0]

# Compute helper columns
df_merged['gdp_per_emission'] = df_merged['GDP per capita'] / df_merged['Emissions']
df_merged['emissions_per_capita'] = df_merged[per_capita_col]

# Prepare features for clustering
X = df_merged[['Emissions', 'GDP per capita']]

wss = get_elbow(X, 10, True)

kmeans = KMeans(n_clusters=3, random_state=42)
df_merged['Cluster'] = kmeans.fit_predict(X)

st.subheader("Clustering of European Countries by CO₂ Emissions and GDP – 2020")

# Scatter plot
fig, ax = plt.subplots(figsize=(10, 6))
scatter = ax.scatter(
    df_merged['GDP per capita'],
    df_merged['Emissions'],
    c=df_merged['Cluster'],
    cmap='viridis',
    alpha=0.8
)
cbar = fig.colorbar(scatter, ax=ax)
cbar.set_label('Cluster')

ax.set_xlabel('GDP per Capita (USD) per person')
ax.set_ylabel(f'CO₂ Emissions ({year}) in metric tons')
ax.set_title(f'Clustering of European Countries by CO₂ Emissions and GDP ({year})')

# Add labels
for _, row in df_merged.iterrows():
    ax.text(row['GDP per capita'], row['Emissions'], row['Name'], fontsize=8, alpha=0.7)

st.pyplot(fig, clear_figure=True)

# Cluster-wise listing
st.subheader("Countries by Cluster:")
for cluster_id in sorted(df_merged['Cluster'].unique()):
    st.markdown(f"**Cluster {cluster_id}:**")
    cluster_df = df_merged[df_merged['Cluster'] == cluster_id][['Name', 'gdp_per_emission', 'emissions_per_capita']]
    cluster_df_sorted = cluster_df.sort_values('gdp_per_emission', ascending=False)
    st.dataframe(cluster_df_sorted.reset_index(drop=True))


st.markdown(""" The scatter plot above shows European countries clustered by their CO₂ emissions and GDP. Using K-Means clustering, we identified groups of countries with similar economic and environmental profiles. This approach helps reveal patterns and relationships between a country's economic output and its environmental impact, particularly whether higher GDP correlates with higher or lower emissions.

### Cluster Summary

**Cluster 0:**  
Includes smaller or high-income countries like **Malta, Iceland, Luxembourg, Cyprus, and Norway**. These nations typically show **higher GDP per unit of CO₂ emissions**, suggesting **greater economic efficiency**. However, their per capita emissions vary, indicating differing energy structures or population sizes. These countries tend to be more efficient or have smaller total emissions.

**Cluster 1:**  
Comprises larger economies such as **Spain, France, Italy, the United Kingdom, and Poland**. They exhibit **moderate GDP per emission ratios** and **balanced per capita emissions**, reflecting economies that are **well-developed yet still reliant on moderate emission outputs**.

**Cluster 2:**  
Consists solely of **Germany**, which appears as a unique case. It has the **lowest GDP per emission ratio** among all clusters, coupled with relatively high per capita emissions. This suggests a **large industrial base with significant energy consumption**, making it an outlier in both economic scale and environmental impact.
""")

st.subheader("Clustering of European Countries by GDP Efficiency vs CO2 emissions")
st.markdown("Next, we did clustering of countries based on efficiency — how much GDP they produce per unit of CO₂ emitted. This gives insight into “green” economies that generate more economic output with less pollution.")

latest_year = 2022

gdp_latest = df_gdp_europe[df_gdp_europe['Year'] == latest_year][['Entity', 'GDP per capita']].rename(columns={'Entity': 'Name'})
pop_latest = df_pop_europe[['Country/Territory', '2022 Population']].rename(columns={'Country/Territory': 'Name', '2022 Population': 'Population'})

year_cols = [str(year) for year in range(1970, 2023)]  # 1970–2022 inclusive

# Sum total emissions for Europe using df_co2_europe
df_co2_europe['total_emissions'] = df_co2_europe[year_cols].sum(axis=1)

# Merge emissions with GDP and population data
df = df_co2_europe.merge(gdp_latest, on='Name', how='inner')
df = df.merge(pop_latest, on='Name', how='inner')

# Calculate total GDP
df['total_gdp'] = df['GDP per capita'] * df['Population']

# GDP per unit CO2 emissions
df['gdp_per_emission'] = df['total_gdp'] / df['total_emissions']

# Emissions per capita
df['emissions_per_capita'] = df['total_emissions'] / df['Population']

features = df[['gdp_per_emission', 'emissions_per_capita']].dropna()
df_clean = df.loc[features.index].copy()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(features)

wss = get_elbow(X, 10, True)

kmeans = KMeans(n_clusters=3, random_state=42)
df_clean['cluster'] = kmeans.fit_predict(X_scaled)

# Plot the scatter
fig, ax = plt.subplots(figsize=(10, 6))
scatter = ax.scatter(
    df_clean['gdp_per_emission'], 
    df_clean['emissions_per_capita'], 
    c=df_clean['cluster'], 
    cmap='Set2', 
    s=100, 
    edgecolor='k'
)

ax.set_title('Clustering of European Countries by GDP Efficiency vs CO2 Emissions')
ax.set_xlabel('GDP per unit CO2 emission (USD per ton CO2)')
ax.set_ylabel('CO2 emissions per capita (tons per person)')
plt.colorbar(scatter, label='Cluster', ax=ax)

for i, row in df_clean.iterrows():
    ax.text(row['gdp_per_emission'], row['emissions_per_capita'], row['Name'], fontsize=8, alpha=0.75)

ax.grid(True)
st.pyplot(fig, clear_figure=True)

# Print cluster info
for c in sorted(df_clean['cluster'].unique()):
    st.write(f"### Cluster {c}:")
    cluster_df = df_clean[df_clean['cluster'] == c][['Name', 'gdp_per_emission', 'emissions_per_capita']]
    st.dataframe(cluster_df)

st.markdown("""
### Cluster Interpretation: GDP Efficiency vs CO₂ Emissions per Capita

**Cluster 0: High GDP Efficiency & Low Emissions per Capita**  
Countries such as **Switzerland, Norway, and Sweden** are found in this group. They produce **high GDP per unit of CO₂ emissions** while keeping **per capita emissions low**. These nations tend to be **wealthy, energy-efficient, and environmentally progressive**, often investing heavily in clean energy and sustainable infrastructure.

**Cluster 1: Low GDP Efficiency & High Emissions per Capita**  
Includes countries like **Estonia and Luxembourg**, where **CO₂ emissions per person are high**, but **economic output per ton of CO₂ is relatively low**. These countries may rely on **carbon-intensive sectors** or lack cleaner energy alternatives, highlighting potential areas for efficiency gains.

**Cluster 2: Moderate GDP Efficiency & Moderate Emissions per Capita**  
This diverse cluster features **Germany, the United Kingdom, Italy, Poland**, and others. These countries exhibit **balanced, mid-range values** for both metrics, reflecting **mixed economies with a combination of industrial output and environmental measures**. They represent the typical European profile with ongoing transitions toward sustainability.

This clustering framework helped visualize how efficiently countries convert emissions into economic value and where they stand in terms of environmental impact, offering insights into where sustainable improvements can be made.
""")

st.subheader("Clusters of European Countries by % Change in CO₂ Emissions (2012 to 2022)")
st.markdown("Next, we created a graph illustrating the percentage change in CO₂ emissions per capita for each country between 2012 and 2022.")

df_co2_europe = df_co2_europe.rename(columns={'Country_code': 'Code'})

# Country, Code, and emissions for 2012 and 2022
cols_needed = ['Name', 'Code', '2012', '2022']
df_years = df_co2_europe[cols_needed].dropna(subset=['2012', '2022'])

# Calculate percentage CO2 emissions change between 2012 and 2022
df_years['CO2_pct_change'] = ((df_years['2022'] - df_years['2012']) / df_years['2012']) * 100

X = df_years[['CO2_pct_change']]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

wss = get_elbow(X, 10, True)

kmeans = KMeans(n_clusters=3, random_state=42)
df_years['Cluster'] = kmeans.fit_predict(X_scaled)

# Plot clusters:
# x-axis: CO2 emissions in 2012
# y-axis: normalized CO2 emissions in 2022 (relative to 2012)
df_years['Normalized_2022'] = df_years['2022'] / df_years['2012']
fig, ax = plt.subplots(figsize=(10, 7))

sns.scatterplot(
    x='2012',
    y='Normalized_2022',
    hue='Cluster',
    palette='Set2',
    data=df_years,
    s=100,
    ax=ax
)

for _, row in df_years.iterrows():
    ax.text(row['2012'], row['Normalized_2022'], row['Code'], fontsize=9)

ax.set_title('Clusters of European Countries by % Change in CO₂ Emissions (2012 to 2022)')
ax.set_xlabel('CO₂ Emissions per capita in 2012')
ax.set_ylabel('Normalized CO₂ Emissions in 2022 (Relative to 2012)')
ax.legend(title='Cluster')
ax.grid(True)

st.pyplot(fig, clear_figure=True)

# Print cluster info
for cluster_num in sorted(df_years['Cluster'].unique()):
    countries = df_years[df_years['Cluster'] == cluster_num]['Code'].tolist()
    st.write(f"**Cluster {cluster_num}:**")
    st.write(", ".join(countries))
    st.write("")

st.markdown("""
### Clustering of European Countries by CO₂ Emission Change (2012–2022)

The graph above illustrates how **CO₂ emissions per capita have changed** from 2012 to 2022 across European countries. Using clustering, we identified patterns in the **magnitude and direction of change**, grouping countries with similar emission trends.

**Cluster 0: Moderate Emission Changes**  
Countries in this cluster experienced **relatively stable CO₂ emissions**, with only **slight increases or decreases** over the 10-year period. These nations show more consistent emission behaviors, possibly due to stable policies or gradual economic shifts.

**Cluster 1: Larger Emission Changes**  
This group includes countries that underwent **significant changes in emissions**, whether **sharp decreases or notable increases**. These shifts could be tied to **major energy reforms, economic transitions, or changes in industrial output**.

**Cluster 2: Smaller Emission Decreases**  
Countries here generally saw **minor decreases in emissions per capita**, reflecting **gradual progress in reducing emissions**, possibly due to **incremental adoption of cleaner technologies** or **moderate policy interventions**.

This clustering provides a clearer picture of emission trends in Europe, helping highlight where rapid shifts are occurring and where progress is more gradual or static.
""")

st.subheader("European Countries: % Change in CO2 Emissions vs % Change in GDP per Capita (2010-2022)")
st.markdown("In the next section, the plot ilustrates how countries CO2 emissions relative to GDP per capita have evolved from 2010 to 2022, highlighting their environmental and economic progress over time.")

years = [str(y) for y in range(2010, 2023)]

# Filter for years 2010 and 2022 specifically
df_co2_2010_2022 = df_co2_europe[['Code', 'Name', '2010', '2022']].dropna(subset=['2010', '2022'])
df_gdp_2010_2022 = df_gdp_europe[df_gdp_europe['Year'].isin([2010, 2022])][['Code', 'Year', 'GDP per capita']]

# Pivot GDP data to have years as columns
gdp_pivot = df_gdp_2010_2022.pivot(index='Code', columns='Year', values='GDP per capita').dropna()

# Calculate % change for GDP per capita
gdp_pivot['GDP_pct_change'] = ((gdp_pivot[2022] - gdp_pivot[2010]) / gdp_pivot[2010]) * 100

# Calculate % change for CO2 emissions per capita
df_co2_2010_2022['CO2_pct_change'] = ((df_co2_2010_2022['2022'] - df_co2_2010_2022['2010']) / df_co2_2010_2022['2010']) * 100

# Merge GDP and CO2 % changes on country code
df_merged = pd.merge(
    gdp_pivot[['GDP_pct_change']], 
    df_co2_2010_2022[['Code', 'CO2_pct_change']], 
    left_index=True, 
    right_on='Code',
    how='inner'
)

df_merged = df_merged.dropna(subset=['GDP_pct_change', 'CO2_pct_change'])

wss = get_elbow(X, 10, True)

k = 3
kmeans = KMeans(n_clusters=k, random_state=42)
df_merged['Cluster'] = kmeans.fit_predict(df_merged[['GDP_pct_change', 'CO2_pct_change']])

fig, ax = plt.subplots(figsize=(12, 7))

sns.scatterplot(
    data=df_merged,
    x='GDP_pct_change',
    y='CO2_pct_change',
    hue='Cluster',
    palette='Set1',
    s=100,
    ax=ax
)

ax.set_title('European Countries: % Change in CO2 Emissions vs % Change in GDP per Capita (2010-2022)')
ax.set_xlabel('GDP per Capita % Change')
ax.set_ylabel('CO2 Emissions per Capita % Change')
ax.grid(True)
ax.legend(title='Cluster')

# Annotate country codes with staggered vertical offsets
offset_y = df_merged['CO2_pct_change'].max() * 0.04
for i, row in df_merged.iterrows():
    stagger = (i % 2) * offset_y
    ax.text(
        row['GDP_pct_change'],
        row['CO2_pct_change'] - offset_y - stagger,
        row['Code'],
        horizontalalignment='center',
        fontsize=8,
        color='black'
    )

plt.tight_layout()
st.pyplot(fig, clear_figure=True)

# Display cluster members
for cluster_num in sorted(df_merged['Cluster'].unique()):
    countries = df_merged[df_merged['Cluster'] == cluster_num]['Code'].tolist()
    st.write(f"**Cluster {cluster_num}:**")
    st.write(", ".join(countries))
    st.write("")

st.markdown("""
### Clustering of European Countries by GDP Growth and CO₂ Emissions Change (2010–2022)

This visualization explores the relationship between **economic growth (GDP per capita)** and **changes in CO₂ emissions per capita** from 2010 to 2022. The clustering reveals distinct groups of countries based on how they balance development with environmental impact.

**Cluster 0: Stable Growth, Strong Emissions Reduction**  
Countries in this cluster experienced **moderate GDP growth (-10% to +20%)** while achieving **significant CO₂ reductions (-25% to -45%)**. These nations demonstrate a **successful decoupling of economic growth from emissions**, improving sustainability without sacrificing prosperity.

**Cluster 1: Moderate Growth, Gradual Emissions Reduction**  
This group includes countries with **moderate economic growth (0% to +30%)** and **smaller emissions reductions (0% to -25%)**. Their trajectory suggests **steady progress** in both areas, with room for stronger climate action.

**Cluster 2: Rapid Growth, Mixed Emissions Trends**  
Countries here show **strong GDP growth (+30%)** but **varied CO₂ emission changes**—ranging from **moderate increases to significant decreases (-45% to +5%)**. While economic expansion is notable, the **environmental outcomes are more inconsistent**, reflecting diverse energy policies and industrial changes.

This analysis highlights how different European countries are managing the complex challenge of growing their economies while reducing emissions.
""")
