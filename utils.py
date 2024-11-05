import pandas as pd

def analyze_delivery_signals(df, threshold):
    """Detect first threshold crossing in 3 months"""
    df = df.sort_values('Date')
    three_months = pd.Timedelta(days=90)
    signals = []
    
    for idx, row in df.iterrows():
        if row['% Dly Qt to Traded Qty'] > threshold:
            lookback_date = row['Date'] - three_months
            previous_crosses = df[
                (df['Date'].between(lookback_date, row['Date'])) & 
                (df['% Dly Qt to Traded Qty'] > threshold)
            ]
            
            if len(previous_crosses) == 1:  # Only current crossing
                signal_data = {
                    'Date': row['Date'],
                    'Delivery %': row['% Dly Qt to Traded Qty'],
                    'Previous Avg': df[
                        (df['Date'].between(lookback_date, row['Date']))
                    ]['% Dly Qt to Traded Qty'].mean(),
                }
                
                # Add volume metrics if available
                if 'Volume_Multiple' in df.columns:
                    signal_data.update({
                        'Volume_Multiple': row['Volume_Multiple'],
                        'Delivery_to_Traded': row['Delivery_to_Traded']
                    })
                
                signals.append(signal_data)
    
    return signals

def add_volume_analysis(df):
    """Add volume analysis metrics"""
    if 'Total Traded Quantity' in df.columns and 'Deliverable Qty' in df.columns:
        # Calculate 3-month moving average of traded quantity
        df['Volume_3M_Avg'] = df['Total Traded Quantity'].rolling(window=90, min_periods=1).mean()
        df['Volume_Ratio'] = df['Total Traded Quantity'] / df['Volume_3M_Avg']
        
        # Calculate delivery to traded ratio
        df['Delivery_to_Traded'] = (df['Deliverable Qty'] / df['Total Traded Quantity']) * 100
        
        # Calculate average volume
        df['Avg_Volume'] = df['Total Traded Quantity'].mean()
        df['Volume_Multiple'] = df['Total Traded Quantity'] / df['Avg_Volume']
    
    return df

def detect_delivery_patterns(df, threshold):
    """Detect patterns in delivery percentage"""
    df['High_Delivery'] = df['% Dly Qt to Traded Qty'] > threshold
    df['Consecutive_Days'] = df['High_Delivery'].groupby(
        (df['High_Delivery'] != df['High_Delivery'].shift()).cumsum()
    ).cumcount() + 1
    
    # Detect increasing delivery pattern
    df['Delivery_Change'] = df['% Dly Qt to Traded Qty'].diff()
    df['Increasing_Delivery'] = df['Delivery_Change'] > 0
    df['Consecutive_Increases'] = df['Increasing_Delivery'].groupby(
        (df['Increasing_Delivery'] != df['Increasing_Delivery'].shift()).cumsum()
    ).cumcount() + 1
    
    return df

def analyze_price_correlation(df, threshold):
    """Analyze correlation between high delivery and price movements"""
    if 'Close' in df.columns:
        df['Price_Change_5D'] = df['Close'].pct_change(5)
        df['High_Delivery_Days'] = df['% Dly Qt to Traded Qty'] > threshold
        
        correlation = df[df['High_Delivery_Days']]['Price_Change_5D'].mean()
        success_rate = (df[df['High_Delivery_Days']]['Price_Change_5D'] > 0).mean()
        
        return {
            'correlation': correlation,
            'success_rate': success_rate
        }
    return None

def calculate_sector_performance(df, sector_info):
    """Calculate sector-wise signal performance"""
    if 'Symbol' in df.columns and sector_info is not None:
        symbol = df['Symbol'].iloc[0]
        sector = sector_info.get(symbol, 'Unknown')
        return {
            'sector': sector,
            'avg_delivery': df['% Dly Qt to Traded Qty'].mean(),
            'high_delivery_days': (df['% Dly Qt to Traded Qty'] > 90).sum()
        }
    return None
