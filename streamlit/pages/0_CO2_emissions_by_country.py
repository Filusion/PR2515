import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from pathlib import Path

st.set_page_config(page_title="CO₂ Emissions in Europe", layout="wide")
st.title("CO₂ emissions in European Countries")


st.markdown("""
Explore detailed visualizations showcasing CO₂ emissions across European countries.  
This page presents:  
- The average total CO₂ emissions for each country  
- Emission patterns of the top 10 highest polluting countries  
- Trends over time comparing both the top 10 highest and lowest polluting nations  

Gain insights into historical and current emission levels, helping to understand regional impacts on climate change.
""")


# Load data
BASE_DIR = Path(__file__)  
data_path = BASE_DIR.parents[2] / "data" / "co2_emmisions_complicated.csv"

df_co2 = pd.read_csv(data_path)
# Filter European countries
df_co2_europe = df_co2[df_co2['Region'].str.contains('Europe', case=False, na=False)]

# Add specific countries
df_russia = df_co2[df_co2['Name'].str.contains('Russian Federation', case=False, na=False)].copy()
df_russia['Name'] = 'Russia'
df_ukraine = df_co2[df_co2['Name'].str.contains('Ukraine', case=False, na=False)].copy()
df_belarus = df_co2[df_co2['Name'].str.contains('Belarus', case=False, na=False)].copy()
df_moldova = df_co2[df_co2['Name'].str.contains('Moldova', case=False, na=False)].copy()
df_moldova['Name'] = 'Moldova'

# Combine data
df_co2_europe = pd.concat([df_co2_europe, df_russia, df_ukraine, df_belarus, df_moldova]).drop_duplicates()

# Handle Serbia and Montenegro split
row = df_co2_europe[df_co2_europe['Name'] == 'Serbia and Montenegro'].copy()
serbia_row = row.copy()
montenegro_row = row.copy()
year_columns = [col for col in df_co2_europe.columns if col.isdigit()]
serbia_row['Country_code'] = 'SRB'
serbia_row['Name'] = 'Serbia'
montenegro_row['Country_code'] = 'MNE'
montenegro_row['Name'] = 'Montenegro'
serbia_row[year_columns] = row[year_columns] * 0.96
montenegro_row[year_columns] = row[year_columns] * 0.04
df_co2_europe = df_co2_europe[df_co2_europe['Name'] != 'Serbia and Montenegro']
df_co2_europe = pd.concat([df_co2_europe, serbia_row, montenegro_row], ignore_index=True)

# Calculate average emissions
df_avg = df_co2_europe.copy()
df_avg["Average_CO2"] = df_avg[year_columns].mean(axis=1)
df_avg_sorted = df_avg.sort_values(by="Average_CO2", ascending=False)[["Name", "Average_CO2"]].reset_index(drop=True)

# Plot all countries
st.subheader("Average CO₂ Emissions in European countries (1970–2023)")
fig1, ax1 = plt.subplots(figsize=(14, 4))
ax1.bar(df_avg_sorted["Name"], df_avg_sorted["Average_CO2"], color='mediumseagreen')
ax1.set_ylabel("Average CO₂ Emissions (kt)")
ax1.set_xlabel("Country")
ax1.set_title("Average CO₂ Emissions by European Country (1970–2023)")
plt.xticks(rotation=45, ha='right')
st.pyplot(fig1)

st.markdown("""
The chart above provides a clear overview of the average CO₂ emissions for every European country over the period from 1970 to 2023. The countries are ranked from highest to lowest average emissions, highlighting the major contributors and offering insight into the overall distribution of emissions across Europe.  
""")

# Plot the top 10 countries
st.subheader("Average CO₂ Emissions in European countries (1970–2023)")
fig1, ax1 = plt.subplots(figsize=(14, 4))
ax1.bar(df_avg_sorted["Name"].head(10), df_avg_sorted["Average_CO2"].head(10), color='mediumseagreen')
ax1.set_ylabel("Average CO₂ Emissions (kt)")
ax1.set_xlabel("Country")
ax1.set_title("CO₂ Emissions by the Top 10 European Countries (1970–2023)")
plt.xticks(rotation=45, ha='right')
st.pyplot(fig1)

st.markdown("""
This next plot focuses exclusively on the top 10 European countries with the highest average CO₂ emissions, allowing us to clearly identify the leading contributors to pollution on the continent.

The top 10 countries are:
1. Russia  
2. Germany  
3. United Kingdom  
4. Ukraine  
5. France  
6. Italy  
7. Poland  
8. Spain  
9. Netherlands  
10. Czech Republic  

Russia stands out with significantly higher CO₂ emissions compared to the others. This is largely due to its vast landmass, which results in a higher overall industrial output and energy consumption. Additionally, Russia's economy heavily depends on oil and natural gas extraction and processing, which are major sources of CO₂ emissions. Its large industrial sector, combined with extensive fossil fuel use, drives these elevated emission levels.
""")

# Plot emission trends for top 10 emitters
df_top10 = df_avg.sort_values(by="Average_CO2", ascending=False).head(10)
df_plot = df_top10.set_index("Name")[year_columns].T
df_plot.index = df_plot.index.astype(int)
st.subheader("Emission Trends: Top 10 Polluting Countries (1970–2023)")
fig2, ax2 = plt.subplots(figsize=(14, 6))
for country in df_plot.columns:
    ax2.plot(df_plot.index, df_plot[country], label=country)
ax2.set_xlabel("Year")
ax2.set_ylabel("CO₂ Emissions (kt)")
ax2.set_title("CO₂ Emission Timeline - Top 10 Polluting Countries")
ax2.legend()
ax2.grid(True)
st.pyplot(fig2)

st.markdown("""
The plot above presents a time series visualization of CO₂ emissions from 1970 to 2023 for the top 10 most
polluting European countries. This dynamic view helps us observe how emissions have changed over time 
and whether countries are making progress in reducing their impact.

Most countries in the list show a clear downward trend, indicating positive steps toward decarbonization and environmental awareness.
Russia, however, is an exception — its emissions have remained consistently high, with some fluctuations, reflecting its ongoing reliance on fossil fuels and heavy industry.

This visualization also allows for deeper analysis by helping identify unusual spikes or drops in emissions, 
which may correspond to economic, political, or environmental events worth investigating.
""")

# Plot emission trends for bottom 10 emitters
df_plot_bottom10 = df_avg.sort_values(by="Average_CO2", ascending=True).head(10)
df_plot_bottom10 = df_plot_bottom10.set_index("Name")[year_columns].T
df_plot_bottom10.index = df_plot_bottom10.index.astype(int)
st.subheader("Emission Trends: 10 Least Polluting Countries (1970–2023)")
fig3, ax3 = plt.subplots(figsize=(14, 6))
for country in df_plot_bottom10.columns:
    ax3.plot(df_plot_bottom10.index, df_plot_bottom10[country], label=country)
ax3.set_xlabel("Year")
ax3.set_ylabel("CO₂ Emissions (kt)")
ax3.set_title("CO₂ Emission Timeline - Least Polluting Countries")
ax3.legend()
ax3.grid(True)
st.pyplot(fig3)

st.markdown("""
This plot shows the CO₂ emission trends from 1970 to 2023 for the 10 least polluting 
countries in Europe. These countries are generally smaller in both geographic size and 
population, which naturally contributes to their lower overall emissions.

Unlike the larger countries, their emission patterns tend to vary more noticeably over the years.
This variability may be influenced by a range of factors such as economic shifts, energy policy changes, industrial development, or even improvements in data collection and reporting methods.

Tracking these trends is important for understanding how smaller nations contribute to and are 
affected by global emissions patterns — and how their environmental strategies evolve over time. """)

