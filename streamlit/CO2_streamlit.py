import streamlit as st

# Configure page
st.set_page_config(
    page_title="CO₂ and Harmful Gas Emissions Analysis",
    page_icon="🌍",
    layout="wide"
)

# Title
st.title("🌍 CO₂ and Harmful Gas Emissions Analysis")

# Overview section
st.header("1. Overview")
st.markdown("""
This project focuses on analyzing **CO₂ and other harmful gas emissions**. The main goal is to study how different factors impact these emissions and identify potential contributors. By conducting this analysis, we aim to gain a better understanding of the relationships between human activities and gas emissions.

### Objectives
- Analyze the impact of various factors on CO₂ and other harmful gas emissions  
- Identify potential contributors to emissions  
- Develop insights into trends and correlations  
- Provide visualizations for better interpretation of results  
- Make predictions about future CO₂ emissions based on identified trends and contributing factors  

### Expected Results
- Better understanding of the impact of various factors on CO₂ and harmful gas emissions  
- Visualization tools that will allow a better understanding of the connections  

Global climate change is one of the most pressing issues of our time. CO₂ emissions from fossil fuels and industrial processes are the leading contributors to global warming.  
We also provide **interactive tools** to visualize and understand emissions by country, sector, and economic indicators, with the goal of revealing actionable insights.
""")

# Project overview
st.header("2. Project Overview")
st.markdown("""
In this project, our main goal is to analyze how much CO₂ and other harmful gases are produced in **Europe**. We're especially interested in identifying which countries are the biggest polluters and which ones produce the least emissions, based on yearly data from **1970 to 2023**. This includes looking at both the total emissions and how they’ve changed over time.

We also wanted to connect the data to **major global events**, such as:
- Epidemics (e.g., COVID-19 lockdowns)  
- Natural disasters  
- International agreements (e.g., Paris Agreement, Kyoto Protocol)  

Events like these tend to have a noticeable impact on human activity, which can clearly show up as sudden drops or increases in emissions. These patterns help us understand the real-world consequences of **policy changes, crises, or economic slowdowns**.

Another important part of our research is analyzing how different **economic sectors** contribute to emissions. We’re looking at industries such as:
- Transportation  
- Agriculture  
- Energy production  
- Manufacturing  

Some countries have higher emissions due to a strong industrial base, while others might have large agricultural sectors or heavy transport traffic. By breaking this down, we can highlight areas for improvement.
""")

# Data and tools
st.subheader("2.1 Data and Tools")
st.markdown("""
Our datasets come from reputable sources including:
- **Eurostat**
- **EDGAR**
- **Kaggle** (filtered to include only reliable data)

We ensured quality by excluding unofficial datasets and supplementing missing countries. This allowed for a more **comprehensive and accurate** analysis across Europe.

In our analysis of climate change and international agreements, we correlated cumulative CO₂ emissions with **global temperature change**. However, we did not account for the fact that around **50% of CO₂ is absorbed by oceans and natural sinks**. Future analyses should include **carbon sink data** for improved accuracy.
""")

# Footer
st.markdown("---")
st.caption("Created by group PR2515 | University of Ljubljana - FRI PR Project 2025")
