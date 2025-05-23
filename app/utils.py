import pandas as pd

def load_clean_data(countries):
    """Load clean data for multiple countries"""
    data = {}
    for country in countries:
        try:
            df = pd.read_csv(f"data/{country.lower()}_clean.csv", parse_dates=['Timestamp'])
            df['Country'] = country
            data[country] = df
        except FileNotFoundError:
            continue
    return data

def calculate_summary_stats(df, metric):
    """Calculate summary statistics for a given metric"""
    return df.groupby("Country")[metric].agg(["mean", "median", "std", "min", "max"])