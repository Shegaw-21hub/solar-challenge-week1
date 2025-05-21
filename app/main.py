import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set page config
st.set_page_config(page_title="Solar Potential Dashboard", layout="wide")

# Title
st.title("🌞 Solar Potential Comparison Dashboard")
st.markdown("Compare solar radiation metrics across different countries")

# Load data function
@st.cache_data
def load_data(country):
    file_path = f"data/{country.lower()}_clean.csv"
    if os.path.exists(file_path):
        return pd.read_csv(file_path, parse_dates=['Timestamp'])
    return None

# Sidebar for country selection
st.sidebar.header("Filters")
selected_countries = st.sidebar.multiselect(
    "Select countries to compare",
    ["Benin", "Sierra Leone", "Togo"],
    default=["Benin", "Sierra Leone", "Togo"]
)

# Load selected data
data = {}
for country in selected_countries:
    df = load_data(country)
    if df is not None:
        df['Country'] = country
        data[country] = df

if not data:
    st.warning("No data available for selected countries. Please check if clean data files exist.")
    st.stop()

# Combine data for comparison
combined_df = pd.concat(data.values())

# Metrics selection
metric = st.selectbox(
    "Select solar metric to compare",
    ["GHI", "DNI", "DHI", "Tamb", "RH"]
)

# Visualization section
st.header(f"{metric} Comparison Across Countries")

# Boxplot
st.subheader("Distribution Comparison")
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=combined_df, x="Country", y=metric, ax=ax)
ax.set_title(f"{metric} Distribution by Country")
ax.set_ylabel(f"{metric} Value")
st.pyplot(fig)

# Summary table
st.subheader("Statistical Summary")
summary_stats = combined_df.groupby("Country")[metric].agg(["mean", "median", "std", "min", "max"])
st.dataframe(summary_stats.style.background_gradient(cmap="YlOrBr"))

# Time series analysis
st.header("Time Series Analysis")
country_ts = st.selectbox("Select country for time series", selected_countries)

if country_ts in data:
    ts_df = data[country_ts].set_index("Timestamp")
    
    # Resample to daily for cleaner visualization
    daily_df = ts_df.resample("D").mean()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    daily_df[metric].plot(ax=ax)
    ax.set_title(f"Daily Average {metric} for {country_ts}")
    ax.set_ylabel(f"{metric} Value")
    st.pyplot(fig)

# Wind analysis (if available)
if "WD" in combined_df.columns and "WS" in combined_df.columns:
    st.header("Wind Analysis")
    
    # Wind rose would be complex, so we'll do a simple polar plot
    country_wind = st.selectbox("Select country for wind analysis", selected_countries)
    
    if country_wind in data:
        wind_df = data[country_wind].dropna(subset=["WD", "WS"])
        
        fig, ax = plt.subplots(subplot_kw={"polar": True}, figsize=(8, 8))
        
        # Bin wind directions and speeds
        wind_df["WD_bin"] = pd.cut(wind_df["WD"], bins=16, labels=range(16))
        wind_stats = wind_df.groupby("WD_bin")["WS"].mean()
        
        theta = [i * (360/16) for i in wind_stats.index]
        radii = wind_stats.values
        
        ax.bar([t * (3.1416/180) for t in theta], radii, width=0.3)
        ax.set_title(f"Wind Direction/Speed for {country_wind}")
        st.pyplot(fig)

# Add some explanatory text
st.markdown("""
### Insights:
- Compare solar radiation metrics (GHI, DNI, DHI) across countries
- Examine distributions using boxplots
- View time series trends for each country
- Analyze wind patterns where available
""")