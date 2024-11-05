# Stock Delivery Analysis Tool

A Streamlit-based web application for analyzing stock delivery percentages using NSE (National Stock Exchange) data.

https://bas-stock-analysis.streamlit.app/

## Features

### 1. Daily High Delivery Stocks Analysis
- Analyzes daily stock delivery data from NSE
- Filters stocks with high delivery percentages (default >90%)
- Excludes specific series (GB, GS, BE, BO, BL, W*, K*)
- Groups stocks by series for easy viewing
- Shows summary statistics in the sidebar

<img width="1428" alt="Screenshot 2024-11-05 at 6 26 35 PM" src="https://github.com/user-attachments/assets/cec5c338-98d0-4dda-a163-a401e00f2dd2">

### 2. Historical Delivery Analysis
- Analyzes historical delivery data for individual stocks
- Interactive plot showing delivery percentage trends
- Highlights periods of high delivery (customizable threshold)
- Detects and displays trading signals when:
  - Stock crosses the threshold delivery percentage
  - No such crossing in the previous 3 months
- Shows comprehensive statistics including:
  - Date range analysis
  - Pattern detection
  - Volume analysis (when available)

<img width="1428" alt="Screenshot 2024-11-05 at 6 30 52 PM" src="https://github.com/user-attachments/assets/b0a19ea3-c4e3-4952-9dbc-5237c743e7af">
<img width="1428" alt="Screenshot 2024-11-05 at 6 31 00 PM" src="https://github.com/user-attachments/assets/2ea4b467-ff4c-49a0-9636-f40dfecf3178">

## Data Sources

### For Daily Analysis
1. Visit [NSE All Reports](https://www.nseindia.com/all-reports)
2. Search for "Security Deliverable Data"
3. Download the CSV file for the current day

### For Historical Analysis
1. Visit [NSE Security-wise Archive](https://www.nseindia.com/report-detail/eq_security)
2. Download historical data for specific stocks

## Installation & Deployment

### Local Development

#### Clone the repository
```git clone [repository-url]```

#### Install required packages
```pip install streamlit pandas plotly numpy```

#### Run the application
```streamlit run stock_delivery_analysis_tool.py```


## Usage

1. Launch the application using Streamlit
2. Choose between "Daily High Delivery Stocks" or "Historical Delivery Analysis"
3. Upload the relevant CSV file
4. Adjust the delivery percentage threshold as needed
5. Analyze the results

## Theory Behind the Tool

The tool is based on the trading theory that when a stock crosses a high delivery percentage threshold (e.g., 90%) for the first time in three months, it might indicate a good short-term investment opportunity. This could suggest strong institutional buying and potential price movement.

## Technical Details

- Built with Python and Streamlit
- Uses Plotly for interactive visualizations
- Implements pandas for data processing
- Provides real-time analysis and filtering
- Handles both daily market-wide data and individual stock historical data

## Notes

- Data should be in the format provided by NSE
- Historical analysis works best with at least 3 months of data
- The tool automatically handles missing data and invalid entries
- Delivery percentage thresholds are customizable

## Limitations

- Depends on NSE data format
- Requires manual data download from NSE
- Historical analysis is limited to one stock at a time
