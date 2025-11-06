import streamlit as st
import yfinance as yf
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf
import matplotlib.pyplot as plt
from datetime import date, timedelta, datetime
import pytz

# Set the title of the Streamlit app
st.title('Nifty 50 Autocorrelation Visualization')

# Auto-refresh the app every 60 seconds to fetch the latest data
st.html("<meta http-equiv='refresh' content='60'>")

# Get current time in IST
ist = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(ist)
st.write(f"Last Updated: {now_ist.strftime('%Y-%m-%d %H:%M:%S %Z')}")

# --- Real-time Price Display ---
st.header('Latest Market Price')
try:
    nifty_ticker = yf.Ticker('^NSEI')
    ticker_info = nifty_ticker.info
    latest_price = ticker_info.get('regularMarketPrice')
    market_time_unix = ticker_info.get('regularMarketTime')

    if latest_price and market_time_unix:
        # Convert Unix timestamp to IST datetime
        market_time_utc = datetime.fromtimestamp(market_time_unix, tz=pytz.utc)
        market_time_ist = market_time_utc.astimezone(ist)

        st.metric(
            label=f"Nifty 50 as of {market_time_ist.strftime('%H:%M:%S %Z')}",
            value=f"{latest_price:,.2f}"
        )
    else:
        st.info("Real-time price data is not currently available.")
except Exception as e:
    st.warning(f"Could not fetch the latest price data: {e}")


# --- Historical Data for Autocorrelation ---
# Define the ticker symbol for Nifty 50
ticker = '^NSEI'

# Fetch the last 2 months of data to ensure we have the latest trading day
try:
    # Download the Nifty 50 data using a period is more reliable for recent data
    nifty_data = yf.download(ticker, period="2mo")

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

        # Make the plot more colorful by changing the confidence interval and markers
        if ax.collections:
            # The confidence interval is a PolyCollection
            poly_collection = next((coll for coll in ax.collections if isinstance(coll, plt.matplotlib.collections.PolyCollection)), None)
            if poly_collection:
                poly_collection.set_facecolor('lightgreen')
                poly_collection.set_edgecolor('green')

            # The markers are a PathCollection
            path_collection = next((coll for coll in ax.collections if isinstance(coll, plt.matplotlib.collections.PathCollection)), None)
            if path_collection:
                path_collection.set_color('red')

        ax.set_title('Autocorrelation Function (ACF) for Nifty 50', color='red')
        ax.set_xlabel('Lag (in days)', color='red')
        ax.set_ylabel('Autocorrelation', color='red')
        plt.grid(True, alpha=0.3)

        # Change tick colors
        ax.tick_params(axis='x', colors='red')
        ax.tick_params(axis='y', colors='red')

        # Change spine colors
        for spine in ax.spines.values():
            spine.set_edgecolor('red')

        # Make the plot background transparent
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)

        # Display the plot in the Streamlit app
        st.pyplot(fig)

        # --- Display Raw Data ---
        st.header('Nifty 50 Data (Last 20 Trading Days)')
        st.dataframe(nifty_data_20_days)

    else:
        st.error(f"No data fetched for the ticker {ticker}. It might be a holiday period or an issue with the data source.")

except Exception as e:
    st.error(f"An error occurred while fetching or processing data: {e}")
