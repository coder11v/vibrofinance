import streamlit as st
import pandas as pd
from utils.stock_data import get_stock_data, get_key_metrics, format_large_number, calculate_technical_indicators
from utils.ai_advisor import get_stock_analysis
from utils.chart_helper import create_stock_chart
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="ViBro Finance - Stock Analysis Platform",
    page_icon="📈",
    layout="wide"
)

# Load custom CSS
with open('styles/custom.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Header
st.title("📈 ViBro Finance")
st.markdown("### AI-Powered Stock Analysis Platform")

# Sidebar
with st.sidebar:
    st.markdown("### Stock Search")
    symbol = st.text_input("Enter Stock Symbol", value="AAPL").upper()
    time_period = st.selectbox(
        "Select Time Period",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3
    )
    
    if st.button("Analyze Stock"):
        st.session_state.analyze = True
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    ViBro Finance provides real-time stock analysis with AI-powered insights.
    Data provided by Yahoo Finance.
    """)

# Main content
try:
    if 'analyze' not in st.session_state:
        st.session_state.analyze = False

    if st.session_state.analyze:
        with st.spinner(f'Fetching data for {symbol}...'):
            # Get stock data
            hist_data, stock_info = get_stock_data(symbol, time_period)
            metrics = get_key_metrics(stock_info)
            
            # Calculate technical indicators
            df = calculate_technical_indicators(hist_data)
            
            # Company header
            col1, col2, col3 = st.columns([2,1,1])
            with col1:
                st.markdown(f"## {stock_info.get('longName', symbol)}")
                st.markdown(f"*{stock_info.get('sector', '')} | {stock_info.get('industry', '')}*")
            
            with col2:
                current_price = stock_info.get('currentPrice', 0)
                price_change = stock_info.get('regularMarketChangePercent', 0)
                price_color = "stock-up" if price_change >= 0 else "stock-down"
                st.markdown(f"""
                    <div style='text-align: right'>
                        <h2>${current_price:.2f}</h2>
                        <p class='{price_color}'>{price_change:+.2f}%</p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Key metrics
            st.markdown("### Key Metrics")
            metric_cols = st.columns(4)
            for i, (metric, value) in enumerate(metrics.items()):
                with metric_cols[i % 4]:
                    st.markdown(f"""
                        <div class='metric-card'>
                            <h4>{metric}</h4>
                            <p>{format_large_number(value) if metric == 'Market Cap' else value}</p>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Stock chart
            st.markdown("### Technical Analysis")
            fig = create_stock_chart(df)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
            
            # AI Analysis
            st.markdown("### AI Insights")
            with st.spinner('Generating AI analysis...'):
                analysis = get_stock_analysis(stock_info, metrics)
                
                st.markdown(f"""
                    <div class='ai-insight'>
                        <h4>Summary</h4>
                        <p>{analysis['summary']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### Strengths")
                    for strength in analysis['strengths']:
                        st.markdown(f"✅ {strength}")
                
                with col2:
                    st.markdown("#### Risks")
                    for risk in analysis['risks']:
                        st.markdown(f"⚠️ {risk}")
                
                st.markdown("#### Recommendation")
                st.info(analysis['recommendation'])
            
            # Export data
            st.markdown("### Export Data")
            csv = df.to_csv().encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{symbol}_stock_data.csv",
                mime="text/csv"
            )

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.markdown("Please try again with a valid stock symbol.")

