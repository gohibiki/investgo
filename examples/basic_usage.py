"""
Basic Usage Examples for InvestGo

This script demonstrates the core functionality of the InvestGo library
with simple, practical examples.
"""

import pandas as pd
from datetime import datetime, timedelta
from investgo import get_pair_id, get_historical_prices, get_holdings, get_technical_data


def example_1_search_stocks():
    """Example 1: Search for stock pair IDs"""
    print("=" * 60)
    print("Example 1: Searching for Stock Pair IDs")
    print("=" * 60)
    
    # Search for single ticker
    print("🔍 Searching for Apple (AAPL)...")
    try:
        apple_ids = get_pair_id('AAPL')
        print(f"✅ Apple pair ID: {apple_ids[0]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Search for multiple tickers with names
    print("\n🔍 Searching for multiple tech stocks with names...")
    try:
        tickers = ['AAPL', 'MSFT', 'GOOGL']
        ids, names = get_pair_id(tickers, name='yes')
        
        print("Results:")
        for ticker, pair_id, name in zip(tickers, ids, names):
            print(f"  {ticker}: {name} (ID: {pair_id})")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Get all search results for a ticker
    print("\n🔍 Getting all search results for 'Apple'...")
    try:
        all_results = get_pair_id('Apple', display_mode='all')
        print(f"Found {len(all_results)} results:")
        print(all_results.head().to_string(index=False))
    except Exception as e:
        print(f"❌ Error: {e}")


def example_2_historical_data():
    """Example 2: Fetch historical stock data"""
    print("\n" + "=" * 60)
    print("Example 2: Fetching Historical Data")
    print("=" * 60)
    
    try:
        # Get QQQ ETF data for the last year
        print("📈 Fetching QQQ historical data...")
        qqq_id = get_pair_id(['QQQ'])[0]
        
        # Calculate date range (last year)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        date_from = start_date.strftime("%d%m%Y")
        date_to = end_date.strftime("%d%m%Y")
        
        print(f"Date range: {date_from} to {date_to}")
        
        # Fetch data
        df = get_historical_prices(qqq_id, date_from, date_to)
        
        if not df.empty:
            print(f"✅ Retrieved {len(df)} data points")
            print("\nFirst 5 rows:")
            print(df.head().to_string())
            
            print("\nBasic statistics:")
            print(f"  Start price: ${df['price'].iloc[0]:.2f}")
            print(f"  End price: ${df['price'].iloc[-1]:.2f}")
            print(f"  Total return: {((df['price'].iloc[-1] / df['price'].iloc[0]) - 1) * 100:.2f}%")
            print(f"  Highest price: ${df['high'].max():.2f}")
            print(f"  Lowest price: ${df['low'].min():.2f}")
        else:
            print("❌ No data retrieved")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def example_3_etf_holdings():
    """Example 3: Analyze ETF holdings"""
    print("\n" + "=" * 60)
    print("Example 3: ETF Holdings Analysis")
    print("=" * 60)
    
    try:
        # Analyze SPY ETF holdings
        print("🏢 Analyzing SPY ETF holdings...")
        spy_id = get_pair_id(['SPY'])[0]
        
        # Get top holdings
        print("\n📊 Top 10 Holdings:")
        top_holdings = get_holdings(spy_id, "top_holdings")
        if not top_holdings.empty:
            print(top_holdings.head(10).to_string(index=False))
        else:
            print("No holdings data available")
        
        # Get asset allocation
        print("\n📊 Asset Allocation:")
        allocation = get_holdings(spy_id, "assets_allocation")
        if not allocation.empty:
            print(allocation.to_string(index=False))
        
        # Get sector breakdown
        print("\n📊 Sector Breakdown:")
        sectors = get_holdings(spy_id, "stock_sector")
        if not sectors.empty and len(sectors) > 1:
            print(sectors.head(10).to_string(index=False))
        else:
            print("No detailed sector data available")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def example_4_technical_analysis():
    """Example 4: Technical analysis data"""
    print("\n" + "=" * 60)
    print("Example 4: Technical Analysis")
    print("=" * 60)
    
    try:
        # Get pivot points for S&P 500
        print("📊 S&P 500 Daily Pivot Points:")
        pivot_data = get_technical_data('pivot_points', 'daily')
        if not pivot_data.empty:
            print(pivot_data.to_string(index=False))
        else:
            print("No pivot data available")
        
        # Get moving averages
        print("\n📊 S&P 500 Moving Averages:")
        ma_data = get_technical_data('ma', 'daily')
        if not ma_data.empty:
            print(ma_data.to_string(index=False))
        else:
            print("No moving average data available")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def example_5_portfolio_comparison():
    """Example 5: Compare multiple stocks"""
    print("\n" + "=" * 60)
    print("Example 5: Portfolio Comparison")
    print("=" * 60)
    
    try:
        # Compare popular ETFs
        tickers = ['SPY', 'QQQ', 'IWM']
        print(f"📈 Comparing performance: {', '.join(tickers)}")
        
        # Get pair IDs
        ids, names = get_pair_id(tickers, name='yes')
        
        # Calculate 6-month date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        date_from = start_date.strftime("%d%m%Y")
        date_to = end_date.strftime("%d%m%Y")
        
        print(f"Period: {start_date.strftime('%B %Y')} to {end_date.strftime('%B %Y')}")
        print()
        
        # Fetch and compare data
        for ticker, pair_id, name in zip(tickers, ids, names):
            try:
                df = get_historical_prices(pair_id, date_from, date_to)
                if not df.empty:
                    start_price = df['price'].iloc[0]
                    end_price = df['price'].iloc[-1]
                    total_return = ((end_price / start_price) - 1) * 100
                    
                    print(f"{ticker} ({name[:30]}...):")
                    print(f"  Return: {total_return:+.2f}%")
                    print(f"  Start: ${start_price:.2f} → End: ${end_price:.2f}")
                    print(f"  Data points: {len(df)}")
                else:
                    print(f"{ticker}: No data available")
                print()
            except Exception as e:
                print(f"{ticker}: Error - {e}")
                print()
                
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all examples."""
    print("🚀 InvestGo Library - Basic Usage Examples")
    print("Visit: https://github.com/gohibiki/investgo")
    print()
    
    # Run all examples
    example_1_search_stocks()
    example_2_historical_data()
    example_3_etf_holdings()
    example_4_technical_analysis()
    example_5_portfolio_comparison()
    
    print("\n" + "=" * 60)
    print("✅ Examples completed!")
    print("For more advanced usage, check out the other example scripts.")
    print("=" * 60)


if __name__ == "__main__":
    main()
