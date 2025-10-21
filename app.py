import streamlit as st
import yfinance as yf
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf
import matplotlib.pyplot as plt
from datetime import date, timedelta

# Set the title of the Streamlit app
st.title('Nifty 50 Autocorrelation Visualization')

# --- Data Fetching ---
# Define the ticker symbol for Nifty 50
ticker = '^NSEI'

# Calculate the start date (fetch more than 20 days to account for non-trading days)
end_date = date.today()
start_date = end_date - timedelta(days=40) # Fetching 40 days of data to ensure we get at least 20 trading days

try:
    # Download the Nifty 50 data
    nifty_data = yf.download(ticker, start=start_date, end=end_date)

    # Get the last 20 days of data
    nifty_data_20_days = nifty_data.tail(20)

    if nifty_data_20_days.shape[0] < 20:
        st.warning(f"Only able to fetch {nifty_data_20_days.shape[0]} days of data. The plot might not be based on the full 20 days.")

    if not nifty_data_20_days.empty:
        st.header('Autocorrelation Plot of Nifty 50 Closing Prices')
        st.write("This plot shows the autocorrelation of the Nifty 50 index's daily closing prices for the last 20 trading days.")

        # --- Autocorrelation Calculation and Plotting ---
        # Extract the 'Close' prices
        close_prices = nifty_data_20_days['Close']

        # Generate the autocorrelation plot
        fig, ax = plt.subplots(figsize=(10, 5))
        plot_acf(close_prices, ax=ax, lags=9) # Lags up to 9 for 20 data points
        ax.set_title('Autocorrelation Function (ACF) for Nifty 50')
        ax.set_xlabel('Lag (in days)')
        ax.set_ylabel('Autocorrelation')
        plt.grid(True)

        # Display the plot in the Streamlit app
        st.pyplot(fig)

        # --- Display Raw Data ---
        st.header('Nifty 50 Data (Last 20 Trading Days)')
        st.dataframe(nifty_data_20_days)

    else:
        st.error(f"No data fetched for the ticker {ticker}. It might be a holiday period or an issue with the data source.")

except Exception as e:
    st.error(f"An error occurred while fetching or processing data: {e}")
