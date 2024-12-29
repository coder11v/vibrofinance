import streamlit as st
import pandas as pd
from utils.stock_data import get_stock_data, get_multiple_stocks_data, get_key_metrics, format_large_number, calculate_technical_indicators
from utils.ai_advisor import get_stock_analysis
from utils.chart_helper import create_stock_chart, create_comparison_chart

# Page configuration
st.set_page_config(
    page_title="ViBro Finance - Stock Analysis Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/vibro-finance',
        'Report a bug': "https://github.com/your-repo/vibro-finance/issues",
        'About': "ViBro Finance - AI-Powered Stock Analysis Platform"
    }
)

# Set dark theme
st.markdown("""
    <style>
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
    </style>
""", unsafe_allow_html=True)

# Load custom CSS
with open('styles/custom.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Header
st.title("📈 ViBro Finance")
st.markdown("### AI-Powered Stock Analysis Platform")

# Sidebar
with st.sidebar:
    st.markdown("### Stock Analysis")
    analysis_type = st.radio(
        "Select Analysis Type",
        ["Single Stock", "Compare Stocks"]
    )

    if analysis_type == "Single Stock":
        symbol = st.text_input("Enter Stock Symbol", value="AAPL").upper()
        symbols = [symbol]
    else:
        st.markdown("Enter up to 4 stock symbols to compare:")
        symbols = []
        for i in range(4):
            symbol_input = st.text_input(f"Stock Symbol {i+1}", key=f"symbol_{i}")
            if symbol_input:
                symbols.append(symbol_input.upper())

    time_period = st.selectbox(
        "Select Time Period",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3
    )

    if st.button("Analyze", type="primary"):
        st.session_state.analyze = True
        st.session_state.symbols = symbols

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

    if st.session_state.analyze and len(st.session_state.symbols) > 0:
        if analysis_type == "Single Stock":
            with st.spinner(f'Fetching data for {symbols[0]}...'):
                # Get stock data
                hist_data, stock_info = get_stock_data(symbols[0], time_period)
                metrics = get_key_metrics(stock_info)

                # Calculate technical indicators
                df = calculate_technical_indicators(hist_data)

                # Company header
                col1, col2 = st.columns([2,1])
                with col1:
                    st.markdown(f"## {stock_info.get('longName', symbols[0])}")
                    st.markdown(f"*{stock_info.get('sector', '')} | {stock_info.get('industry', '')}*")

                with col2:
                    current_price = stock_info.get('currentPrice', 0)
                    price_change = stock_info.get('regularMarketChangePercent', 0)
                    price_color = "stock-up" if price_change >= 0 else "stock-down"
                    st.markdown(f"""
                        <div class='price-display'>
                            <h2>${current_price:.2f}</h2>
                            <p class='{price_color}'>{price_change:+.2f}%</p>
                        </div>
                    """, unsafe_allow_html=True)

                # Key metrics in expandable section
                with st.expander("Key Metrics", expanded=True):
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

                # AI Analysis in expandable section
                with st.expander("AI Insights", expanded=True):
                    with st.spinner('Generating AI analysis...'):
                        analysis = get_stock_analysis(stock_info, metrics)

                        if 'error' in analysis:
                            st.error(analysis['error'])
                        else:
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
                with st.expander("Export Data"):
                    csv = df.to_csv().encode('utf-8')
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"{symbols[0]}_stock_data.csv",
                        mime="text/csv"
                    )
        else:
            # Comparison View
            with st.spinner('Fetching data for comparison...'):
                stock_data = get_multiple_stocks_data(st.session_state.symbols, time_period)

                # Create comparison chart
                st.markdown("### Stock Price Comparison")
                comparison_fig = create_comparison_chart(stock_data, time_period)
                st.plotly_chart(comparison_fig, use_container_width=True)

                # Display key metrics comparison
                with st.expander("Key Metrics Comparison", expanded=True):
                    metrics_data = []
                    for symbol, data in stock_data.items():
                        metrics = get_key_metrics(data['info'])
                        metrics['Symbol'] = symbol
                        metrics['Company'] = data['info'].get('longName', symbol)
                        metrics_data.append(metrics)

                    metrics_df = pd.DataFrame(metrics_data)
                    metrics_df.set_index('Symbol', inplace=True)
                    st.dataframe(metrics_df, use_container_width=True)

                # Export data
                with st.expander("Export Data"):
                    for symbol, data in stock_data.items():
                        csv = data['history'].to_csv().encode('utf-8')
                        st.download_button(
                            label=f"Download {symbol} CSV",
                            data=csv,
                            file_name=f"{symbol}_stock_data.csv",
                            mime="text/csv",
                            key=f"download_{symbol}"
                        )

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.markdown("Please try again with valid stock symbols.")