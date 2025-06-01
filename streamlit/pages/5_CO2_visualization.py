import warnings
warnings.filterwarnings('ignore')
import geodatasets
import pandas as pd
import seaborn as sns
import streamlit as st
import geopandas as gpd
import matplotlib as mpl
import ipywidgets as widgets
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec

from pathlib import Path
from IPython.display import display
from matplotlib.colors import Normalize
from matplotlib.animation import FuncAnimation
from ipywidgets import interact, IntSlider, widgets
from cryptography.utils import CryptographyDeprecationWarning


st.set_page_config(page_title="CO₂ Emissions in Europe", layout="wide")
st.title("CO₂ Emissions clustering")

st.markdown("""
This page has a few interactive visualizations about the CO2 emissions in Europe from 1970 to 2023.
""")


data_path1 = Path(__file__).resolve().parents[2] / "data" / "co2_emmisions_complicated.csv"
data_path2 = Path(__file__).resolve().parents[2] / "data" / "co2-emissions-vs-gdp.csv"
data_path3 = Path(__file__).resolve().parents[2] / "data" / "world_population.csv"
data_path4 = Path(__file__).resolve().parents[2] / "data" / "cultural" / "ne_110m_admin_0_countries.shp"

df_co2 = pd.read_csv(data_path1)
df_gdp  = pd.read_csv(data_path2)
df_pop = pd.read_csv(data_path3)
world = gpd.read_file(data_path4)



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
df_pop_europe = df_pop[df_pop['Continent'] == 'Europe']

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

years = ['1970', '1980', '1990', '2000', '2010', '2015', '2020', '2022']

df_co2_filtered = df_co2_europe[['Name'] + years]

pop_years = [f"{year} Population" for year in [1970, 1980, 1990, 2000, 2010, 2015, 2020, 2022]]
df_pop_filtered = df_pop_europe[['Country/Territory'] + pop_years]

# total CO2 per year
co2_total = df_co2_filtered[years].sum()

# total population per year
pop_total = df_pop_filtered[pop_years].sum()
pop_total.index = years # index -> years
co2__ = df_co2_europe[['Name']]
pop__ = df_pop_europe[['Country/Territory']]

df_merged = pd.merge(df_co2_filtered,df_pop_filtered, left_on='Name', right_on='Country/Territory', how='inner')


# Calculate CO2 per capita for each year
df_per_capita = df_merged.copy()

for year in years:
    co2_col = year
    pop_col = f"{year} Population"
    df_per_capita[year] = df_per_capita[co2_col] / df_per_capita[pop_col]

# Keep only country names and per capita columns
df_per_capita = df_per_capita[['Name'] + years]


# Your CO2 data
df = df_per_capita

name_corrections = {
    "Czech Republic": "Czechia",
    "Bosnia and Herzovina": "Bosnia and Herz.",
    "Macedonia": "Macedonia",
    "United Kingdom": "United Kingdom",
    "Russia": "Russia",
    "Moldova": "Moldova",
    "Slovakia": "Slovakia",
    "Serbia": "Republic of Serbia",
    "Montenegro": "Montenegro",
    "Germany": "Germany"
}

df_melted = df.melt(id_vars=['Name'], var_name='Year', value_name='CO2_per_capita')
df_melted["Name"] = df_melted["Name"].replace(name_corrections)

# Convert 'Year' column to int
df_melted['Year'] = df_melted['Year'].astype(int)

# Your exact years list
years = [1970, 1980, 1990, 2000, 2010, 2015, 2020, 2022]

europe = world[world['CONTINENT'] == 'Europe']

def create_map_app(df_melted, europe, years):
    # Calculate GLOBAL min and max values for consistent coloring
    vmin = df_melted['CO2_per_capita'].min()
    vmax = df_melted['CO2_per_capita'].max()
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.cm.Reds

    st.title("CO₂ Emissions per Capita in Europe")
    
    # Create slider - use the first year as default
    year = st.select_slider(
        "Select Year",
        options=years,
        value=years[0]
    )
    
    # Create plot
    fig = plt.figure(figsize=(20, 10))  
    gs = gridspec.GridSpec(1, 2, width_ratios=[30, 1], wspace=0.05)  
    fig.subplots_adjust(left=0.02, right=0.95, top=0.95, bottom=0.05)

    ax = fig.add_subplot(gs[0])  
    cax = fig.add_subplot(gs[1])  

    # Filter data for selected year
    df_year = df_melted[df_melted['Year'] == year]
    merged = europe.merge(df_year, how='left', left_on='ADMIN', right_on='Name')

    # Plot with FIXED color normalization
    merged.plot(column='CO2_per_capita', 
                cmap=cmap, 
                linewidth=0.8, 
                ax=ax, 
                edgecolor='0.8',
                missing_kwds={'color': 'lightgrey'}, 
                norm=norm)  # Using the GLOBAL norm

    ax.set_xlim(-10, 170)
    ax.set_ylim(20, 90)
    ax.set_title(f"CO₂ Emissions per Capita in Europe ({year})", fontsize=22)
    ax.axis('off')

    # Create colorbar with FIXED scale
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []
    cbar = fig.colorbar(sm, cax=cax, orientation="vertical")
    cbar.set_label("CO₂ per Capita (tons)", fontsize=16)

    st.pyplot(fig)

create_map_app(df_melted, europe, years)



df_emissions_anim1 = df_co2_filtered.copy()

# Correct country names
name_corrections_anim1 = {
    "Czech Republic": "Czechia",
    "Macedonia": "Macedonia",
    "United Kingdom": "United Kingdom",
    "Russia": "Russia",
    "Moldova": "Moldova",
    "Slovakia": "Slovakia",
    "Serbia": "Republic of Serbia",
    "Montenegro": "Montenegro",
    "Germany": "Germany"
}

df_emissions_anim1['Name'] = df_emissions_anim1['Name'].replace(name_corrections_anim1)

df_emissions_long1 = df_emissions_anim1.melt(id_vars=['Name'], var_name='Year', value_name='Total_CO2')
df_emissions_long1['Year'] = df_emissions_long1['Year'].astype(int)

# years
years_anim1 = [1970, 1980, 1990, 2000, 2010, 2015, 2020, 2022]

# Normalize colors
vmin_anim1 = df_emissions_long1['Total_CO2'].min()
vmax_anim1 = df_emissions_long1['Total_CO2'].max()
norm_anim1 = mcolors.Normalize(vmin=vmin_anim1, vmax=vmax_anim1)
cmap_anim1 = plt.cm.Reds


import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

def plot_emissions_anim1(year):
    fig = plt.figure(figsize=(20, 10))
    gs = gridspec.GridSpec(1, 2, width_ratios=[30, 1], wspace=0.05)
    fig.subplots_adjust(left=0.02, right=0.95, top=0.95, bottom=0.05)

    ax = fig.add_subplot(gs[0])
    cax = fig.add_subplot(gs[1])

    df_year_anim1 = df_emissions_long1[df_emissions_long1['Year'] == year]
    merged_anim1 = europe.merge(df_year_anim1, how='left', left_on='ADMIN', right_on='Name')

    ax.clear()
    merged_anim1.plot(column='Total_CO2', cmap=cmap_anim1, linewidth=0.8, ax=ax, edgecolor='0.8',
                     missing_kwds={'color': 'lightgrey'}, norm=norm_anim1)

    ax.set_xlim(-10, 170)
    ax.set_ylim(20, 90)
    ax.set_title(f"Total CO₂ Emissions in Europe ({year})", fontsize=22)
    ax.axis('off')

    sm = plt.cm.ScalarMappable(cmap=cmap_anim1, norm=norm_anim1)
    sm._A = []
    cbar = fig.colorbar(sm, cax=cax, orientation="vertical")
    cbar.set_label("Total CO₂ Emissions (tons)", fontsize=16)

    st.pyplot(fig)

# Streamlit UI components
st.title("Total CO₂ Emissions in Europe")

# Create unique key for the slider by adding a suffix
year = st.select_slider(
    "Select Year",
    options=years_anim1,
    value=years_anim1[0],
    key="total_co2_year_slider"  # Unique key added here
)

# Call the plotting function with selected year
plot_emissions_anim1(year)





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

df_gdp_europe.columns = df_gdp_europe.columns.str.strip()
df_gdp_europe = df_gdp_europe.dropna(subset=['GDP per capita'])

# Convert GDP per capita to numeric if needed
df_gdp_europe['GDP per capita'] = pd.to_numeric(df_gdp_europe['GDP per capita'], errors='coerce')
df_filtered = df_gdp_europe[(df_gdp_europe['Year'] >= 1970) & (df_gdp_europe['Year'] <= 2023)].copy()

# columns to numbers, avoid errors
df_filtered['Annual CO₂ emissions (per capita)'] = pd.to_numeric(df_filtered['Annual CO₂ emissions (per capita)'], errors='coerce')
df_filtered['GDP per capita'] = pd.to_numeric(df_filtered['GDP per capita'], errors='coerce')

# Drop rows with missing values
df_filtered = df_filtered.dropna(subset=['Annual CO₂ emissions (per capita)', 'GDP per capita'])

# Group by year and sum values
annual_co2_sum = df_filtered.groupby('Year')['Annual CO₂ emissions (per capita)'].sum()
annual_gdp_sum = df_filtered.groupby('Year')['GDP per capita'].sum()

years = [1970, 1980, 1990, 2000, 2010, 2015, 2020, 2022]



df_years = df_filtered[df_filtered['Year'].isin(years)]

df_pivot = df_years.pivot(index='Entity', columns='Year', values='GDP per capita')

df_pivot = df_pivot.sort_index()
df_pivot = df_pivot[sorted(df_pivot.columns)]
df_gdp_anim2 = df_filtered.copy()

name_corrections_gdp2 = {
    "Czech Republic": "Czechia",
    "Macedonia": "Macedonia",
    "United Kingdom": "United Kingdom",
    "Russia": "Russia",
    "Moldova": "Moldova",
    "Slovakia": "Slovakia",
    "Serbia": "Republic of Serbia",
    "Montenegro": "Montenegro",
    "Germany": "Germany"
}

df_gdp_anim2['Entity'] = df_gdp_anim2['Entity'].replace(name_corrections_gdp2)

# Filter only required years
years_gdp2 = [1970, 1980, 1990, 2000, 2010, 2015, 2020, 2022]
df_years_gdp2 = df_gdp_anim2[df_gdp_anim2['Year'].isin(years_gdp2)]

# Normalize colors for GDP per capita
vmin_gdp2 = df_years_gdp2['GDP per capita'].min()
vmax_gdp2 = df_years_gdp2['GDP per capita'].max()
norm_gdp2 = mcolors.Normalize(vmin=vmin_gdp2, vmax=vmax_gdp2)
cmap_gdp2 = plt.cm.viridis

def plot_gdp_per_capita_anim2(year):
    fig = plt.figure(figsize=(20, 10))
    gs = gridspec.GridSpec(1, 2, width_ratios=[30, 1], wspace=0.05)
    fig.subplots_adjust(left=0.02, right=0.95, top=0.95, bottom=0.05)

    ax = fig.add_subplot(gs[0])
    cax = fig.add_subplot(gs[1])

    df_year_gdp2 = df_years_gdp2[df_years_gdp2['Year'] == year]
    merged_gdp2 = europe.merge(df_year_gdp2, how='left', left_on='ADMIN', right_on='Entity')

    ax.clear()
    merged_gdp2.plot(column='GDP per capita', cmap=cmap_gdp2, linewidth=0.8, ax=ax, edgecolor='0.8',
                    missing_kwds={'color': 'lightgrey'}, norm=norm_gdp2)

    ax.set_xlim(-10, 170)
    ax.set_ylim(20, 90)
    ax.set_title(f"GDP per Capita in Europe ({year})", fontsize=22)
    ax.axis('off')

    sm = plt.cm.ScalarMappable(cmap=cmap_gdp2, norm=norm_gdp2)
    sm._A = []
    cbar = fig.colorbar(sm, cax=cax, orientation="vertical")
    cbar.set_label("GDP per Capita (USD)", fontsize=16)

    st.pyplot(fig)

# Streamlit UI components
st.title("GDP per Capita in Europe")

# Create slider with unique key
year = st.select_slider(
    "Select Year",
    options=years_gdp2,
    value=years_gdp2[0],
    key="gdp_per_capita_year_slider"  # Unique key for this slider
)

# Call the plotting function
plot_gdp_per_capita_anim2(year)
