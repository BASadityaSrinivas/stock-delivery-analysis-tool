import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import *

def load_daily_data(file, min_delivery):
    try:
        # Read CSV file with explicit handling of whitespace in headers
        df = pd.read_csv(file, skipinitialspace=True)
        
        # Clean column names by stripping whitespace
        df.columns = df.columns.str.strip()

        # Clean the DELIV_PER column by converting "-" to NaN and then to numeric
        df['DELIV_PER'] = pd.to_numeric(df['DELIV_PER'].replace(['-', ''], pd.NA), errors='coerce')
        
        # Filter out unwanted series using regex pattern
        unwanted_series = r'^(GB|GS|BE|BO|BL|W[0-9A-Z]|K[0-9A-Z]|MF|ME|TB|SG)$'
        df = df[~df['SERIES'].str.match(unwanted_series)]
        
        # Filter stocks with delivery percentage > min_delivery (excluding NaN values)
        high_delivery_df = df[df['DELIV_PER'] > min_delivery].dropna(subset=['DELIV_PER'])
        
        # Modified groupby operation
        grouped = {}
        for series, group in high_delivery_df.groupby('SERIES'):
            grouped[series] = group[['SYMBOL', 'DELIV_PER']].values.tolist()
        
        return grouped, df['DATE1'].iloc[0]
    
    except Exception as e:
        st.error(f"Error in data processing: {str(e)}")
        st.error(f"Error type: {type(e)}")
        raise e

def load_historical_data(file):
    try:
        # Read CSV file
        df = pd.read_csv(file)
        
        # Clean column names
        df.columns = [col.strip() for col in df.columns]
        
        # Convert date column to datetime
        df['Date'] = pd.to_datetime(df['Date'].astype(str).str.strip(), format='%d-%b-%Y')
        
        # Convert delivery percentage to numeric
        df['% Dly Qt to Traded Qty'] = (df['% Dly Qt to Traded Qty']
                                       .astype(str)
                                       .str.strip()
                                       .str.replace(',', '')
                                       .astype(float))
        
        # Clean symbol column
        df['Symbol'] = df['Symbol'].astype(str).str.strip()
        
        # Sort by date
        df = df.sort_values('Date')
        
        return df
        
    except Exception as e:
        st.error(f"Data processing error details: {str(e)}")
        st.write("DataFrame info:")
        st.write(df.info())
        raise e

def create_delivery_plot(df, highlight_threshold):
    """Enhanced plot with more indicators"""
    fig = go.Figure()
    
    # Background for high delivery range
    fig.add_shape(
        type="rect",
        x0=df['Date'].min(),
        x1=df['Date'].max(),
        y0=highlight_threshold,
        y1=100,
        fillcolor="rgba(0, 255, 0, 0.2)",
        line_width=0,
        layer="below"
    )
    
    # Main delivery percentage line
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['% Dly Qt to Traded Qty'],
            name="Delivery %",
            line=dict(color='rgba(120, 75, 200, 1)', width=3),
            mode='lines'
        )
    )
    
    # Add volume bars if available
    if 'Volume_Multiple' in df.columns:
        fig.add_trace(
            go.Bar(
                x=df['Date'],
                y=df['Volume_Multiple'],
                name="Volume Multiple",
                yaxis="y2",
                opacity=0.3
            )
        )
        
        # Add second y-axis for volume
        fig.update_layout(
            yaxis2=dict(
                title="Volume (× Average)",
                overlaying="y",
                side="right"
            )
        )
    
    # Update layout
    fig.update_layout(
        title=f"Delivery Percentage Trend for {df['Symbol'].iloc[0]}",
        xaxis_title="Date",
        yaxis_title="Delivery Percentage (%)",
        hovermode='x unified',
        showlegend=True,
        height=600,
        template='plotly_white'
    )
    
    return fig

def show_summary_dashboard(df, signals, price_analysis):
    """Display summary dashboard"""
    st.subheader("Signal Analysis Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Signal Strength", 
            f"{len(signals)} signals",
            f"in {(df['Date'].max() - df['Date'].min()).days} days"
        )
    
    with col2:
        if 'Volume_Multiple' in df.columns:
            signal_dates = [s['Date'] for s in signals]
            if signal_dates:  # Only calculate if there are signals
                avg_volume = df[df['Date'].isin(signal_dates)]['Volume_Multiple'].mean()
                st.metric(
                    "Avg Volume on Signal Days", 
                    f"{avg_volume:.1f}x normal"
                )
    
    with col3:
        if price_analysis:
            st.metric(
                "Success Rate", 
                f"{price_analysis['success_rate']*100:.1f}%",
                f"Correlation: {price_analysis['correlation']:.2f}"
            )

def daily_analysis():
    st.header("Daily High Delivery Stocks")
    
    st.markdown("""
    **Note:** Get today's delivery percentage data for all stocks from 
    [NSE All Reports](https://www.nseindia.com/all-reports). 
    Search for "Security Deliverable Data" in the reports list, download the CSV file and upload below.
    """)
    
    # Add delivery percentage filter
    min_delivery = st.number_input(
        "Minimum Delivery Percentage Filter",
        min_value=0.0,
        max_value=100.0,
        value=90.0,
        step=5.0,
        help="Show stocks with delivery percentage above this value"
    )
    
    uploaded_file = st.file_uploader("Upload daily CSV file", type=['csv'], key="daily")
    
    if uploaded_file is not None:
        try:
            grouped_stocks, date = load_daily_data(uploaded_file, min_delivery)
            
            st.subheader(f"Analysis for date: {date}")
            
            # Display results in expandable sections for each series
            for series, stock_data in grouped_stocks.items():
                with st.expander(f"{series} ({len(stock_data)} stocks)"):
                    cols = st.columns(3)
                    # Sort by delivery percentage in descending order
                    sorted_stocks = sorted(stock_data, key=lambda x: x[1], reverse=True)
                    for idx, (symbol, deliv_per) in enumerate(sorted_stocks):
                        cols[idx % 3].write(f"{symbol}: {deliv_per:.2f}%")
            
            # Show summary statistics
            st.sidebar.subheader("Summary")
            total_stocks = sum(len(stocks) for stocks in grouped_stocks.values())
            st.sidebar.metric("Total Stocks", total_stocks)
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.write("Please ensure your CSV file has the correct format.")

def historical_analysis():
    st.header("Historical Delivery Analysis")
    
    st.markdown("""
    **Note:** Get the stock's historical delivery percentage data from 
    [NSE Security-wise Archive](https://www.nseindia.com/report-detail/eq_security).
    Download the CSV file for any stock and upload below.
    """)
    
    highlight_threshold = st.number_input(
        "Highlight Delivery Percentage Above",
        min_value=0.0,
        max_value=100.0,
        value=90.0,
        step=5.0,
        help="Highlight regions where delivery percentage is above this value"
    )
    
    uploaded_file = st.file_uploader("Upload historical CSV file", type=['csv'], key="historical")
    
    if uploaded_file is not None:
        try:
            df = load_historical_data(uploaded_file)
            
            # Add analysis only if required columns are present
            if 'Traded Qty' in df.columns:
                df = add_volume_analysis(df)
            df = detect_delivery_patterns(df, highlight_threshold)
            signals = analyze_delivery_signals(df, highlight_threshold)
            price_analysis = analyze_price_correlation(df, highlight_threshold) if 'Close' in df.columns else None
            
            # Check if stock crossed threshold exactly once
            high_delivery_days = len(df[df['% Dly Qt to Traded Qty'] > highlight_threshold])
            if high_delivery_days == 1:
                st.balloons()  # Show celebration
                st.success(f"🎉 {df['Symbol'].iloc[0]} crossed {highlight_threshold}% delivery for the first time!")
                
                # Get the date when it happened
                cross_date = df[df['% Dly Qt to Traded Qty'] > highlight_threshold]['Date'].iloc[0]
                st.info(f"Date: {cross_date.strftime('%d-%b-%Y')} | " 
                       f"Delivery: {df[df['Date'] == cross_date]['% Dly Qt to Traded Qty'].iloc[0]:.2f}%")
            
            # Show summary dashboard
            show_summary_dashboard(df, signals, price_analysis)
            
            # Create and display plot
            fig = create_delivery_plot(df, highlight_threshold)
            st.plotly_chart(fig, use_container_width=True)
            
            st.sidebar.markdown("---")
            
            # Signal notifications
            if signals:
                st.sidebar.subheader("🎯 Trading Signals")
                stock_symbol = df['Symbol'].iloc[0]  # Get the stock symbol
                st.sidebar.markdown(f"**Stock: {stock_symbol}**")  # Display stock symbol at the top
                
                for signal in signals:
                    signal_text = f"""
                    Signal Detected:
                    - Symbol: {stock_symbol}
                    - Date: {signal['Date'].strftime('%d-%b-%Y')}
                    - Delivery: {signal['Delivery %']:.2f}%
                    - 3M Avg Before: {signal['Previous Avg']:.2f}%
                    """
                    if 'Volume_Multiple' in signal and not pd.isna(signal['Volume_Multiple']):
                        signal_text += f"- Volume: {signal['Volume_Multiple']:.1f}x"
                    if 'Delivery_to_Traded' in signal and not pd.isna(signal['Delivery_to_Traded']):
                        signal_text += f"\n- Delivery/Traded: {signal['Delivery_to_Traded']:.1f}%"
                    st.sidebar.success(signal_text)
            
            # Pattern Analysis
            st.sidebar.subheader("📊 Pattern Analysis")
            max_consecutive = df['Consecutive_Days'].max()
            if max_consecutive > 1:
                st.sidebar.info(f"Max consecutive days above {highlight_threshold}%: {max_consecutive}")
            
            max_increases = df['Consecutive_Increases'].max()
            if max_increases > 2:
                st.sidebar.info(f"Max consecutive days of increasing delivery: {max_increases}")
            
            # Statistics
            st.sidebar.subheader("📈 Statistics")
            start_date = df['Date'].min()
            end_date = df['Date'].max()
            date_range = (end_date - start_date).days
            months = date_range // 30
            remaining_days = date_range % 30
            
            st.sidebar.metric("Date Range", 
                            f"{start_date.strftime('%d-%b-%Y')} to {end_date.strftime('%d-%b-%Y')}")
            st.sidebar.metric("Period", 
                            f"{months} months, {remaining_days} days" if months > 0 else f"{date_range} days")
            
            # Display data table
            st.subheader("Data Table")
            display_cols = ['Date', '% Dly Qt to Traded Qty']
            if 'Volume_Multiple' in df.columns:
                display_cols.append('Volume_Multiple')
                
            st.dataframe(
                df[display_cols]
                .sort_values('Date', ascending=False)
                .style.format({
                    '% Dly Qt to Traded Qty': '{:.2f}%',
                    'Volume_Multiple': '{:.1f}x'
                })
            )
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.write("Please ensure your CSV file has the correct format.")

def main():
    st.set_page_config(page_title="Stock Delivery Analysis Tool", layout="wide")
    
    st.title("Stock Delivery Analysis Tool")
    
    tab1, tab2 = st.tabs(["Daily High Delivery Stocks", "Historical Delivery Analysis"])
    
    with tab1:
        daily_analysis()
        
    with tab2:
        historical_analysis()

if __name__ == "__main__":
    main() 