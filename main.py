import streamlit as st
import pandas as pd
from utils.stock_data import get_stock_data, get_multiple_stocks_data, get_key_metrics, format_large_number, calculate_technical_indicators
from utils.ai_advisor import get_stock_analysis, ask_follow_up_question, suggest_stocks
from utils.chart_helper import create_stock_chart, create_comparison_chart
from utils.portfolio_manager import generate_portfolio_recommendation, analyze_portfolio_health
from utils.goal_planner import FinancialGoal, analyze_goal_feasibility, generate_investment_plan
import time

# Page configuration
st.set_page_config(
    page_title="ViBro Finance - Stock Analysis Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "ViBro Finance - Your AI-Powered Financial Assistant"
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
st.markdown("### Your AI-Powered Financial Assistant")

# Navigation
nav_options = ["Market Analysis", "ViBro Assistant"]
st.markdown("<div class='nav-container'>", unsafe_allow_html=True)
cols = st.columns(2)
for i, option in enumerate(nav_options):
    with cols[i]:
        if st.button(
            option,
            key=f"nav_{option}",
            type="secondary" if st.query_params.get("section", "Market Analysis") != option else "primary",
            use_container_width=True,
        ):
            st.query_params["section"] = option
st.markdown("</div>", unsafe_allow_html=True)

# Get current section from URL parameters
section = st.query_params.get("section", "Market Analysis")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm ViBro, your AI financial assistant. I can help you with:\n\n" +
         "📊 Portfolio Management\n" +
         "🎯 Goal Planning\n" +
         "💰 Investment Recommendations\n" +
         "📈 Market Analysis\n\n" +
         "What would you like to know about?"}
    ]

if section == "Market Analysis":
    analysis_type = st.radio(
        "Select Analysis Type",
        ["Single Stock", "Compare Stocks"],
        horizontal=True
    )

    if analysis_type == "Single Stock":
        symbol = st.text_input("Enter Stock Symbol", value="ViBro").upper()
        symbols = [symbol]
    else:
        col1, col2, col3, col4 = st.columns(4)
        symbols = []
        with col1:
            symbol1 = st.text_input("Stock Symbol 1")
            if symbol1: symbols.append(symbol1.upper())
        with col2:
            symbol2 = st.text_input("Stock Symbol 2")
            if symbol2: symbols.append(symbol2.upper())
        with col3:
            symbol3 = st.text_input("Stock Symbol 3")
            if symbol3: symbols.append(symbol3.upper())
        with col4:
            symbol4 = st.text_input("Stock Symbol 4")
            if symbol4: symbols.append(symbol4.upper())

    time_period = st.select_slider(
        "Select Time Period",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        value="1y"
    )

    if st.button("Analyze", type="primary"):
        st.session_state.analyze = True
        st.session_state.symbols = symbols

# Main content
try:
    if 'analyze' not in st.session_state:
        st.session_state.analyze = False

    if section == "Market Analysis":
        if st.session_state.analyze and len(st.session_state.symbols) > 0:
            if analysis_type == "Single Stock":
                with st.spinner(f'Fetching data for {symbols[0]}...'):
                    # Get stock data
                    hist_data, stock_info = get_stock_data(symbols[0], time_period)
                    metrics = get_key_metrics(stock_info)

                    # Calculate technical indicators
                    df = calculate_technical_indicators(hist_data)

                    # Two-column layout
                    col_data, col_ai = st.columns([1, 1])

                    with col_data:
                        # Company header
                        st.markdown(f"## {stock_info.get('longName', symbols[0])}")
                        st.markdown(f"*{stock_info.get('sector', '')} | {stock_info.get('industry', '')}*")

                        current_price = stock_info.get('currentPrice', 0)
                        price_change = stock_info.get('regularMarketChangePercent', 0)
                        price_color = "stock-up" if price_change >= 0 else "stock-down"
                        st.markdown(f"""
                            <div class='price-display'>
                                <h2>${current_price:.2f}</h2>
                                <p class='{price_color}'>{price_change:+.2f}%</p>
                            </div>
                        """, unsafe_allow_html=True)

                        # Key metrics
                        st.markdown("### Key Metrics")
                        metric_cols = st.columns(2)
                        for i, (metric, value) in enumerate(metrics.items()):
                            with metric_cols[i % 2]:
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

                    with col_ai:
                        st.markdown("### ViBro Insights")
                        with st.spinner('Generating ViBro analysis...'):
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

                                with st.expander("Strengths & Risks", expanded=True):
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

                                # Interactive AI Chat
                                st.markdown("### Ask ViBro Finance")

                                # Suggested questions
                                st.markdown("#### Suggested Questions")
                                for question in analysis['suggested_questions']:
                                    if st.button(question, key=f"q_{question}"):
                                        with st.spinner('Analyzing...'):
                                            answer = ask_follow_up_question(stock_info, metrics, question)
                                            st.markdown(f"""
                                                <div class='ai-insight'>
                                                    <p>{answer}</p>
                                                </div>
                                            """, unsafe_allow_html=True)

                                # Custom questions
                                custom_question = st.text_input("Ask your own question:")
                                if st.button("Ask") and custom_question:
                                    with st.spinner('Analyzing...'):
                                        answer = ask_follow_up_question(stock_info, metrics, custom_question)
                                        st.markdown(f"""
                                            <div class='ai-insight'>
                                                <p>{answer}</p>
                                            </div>
                                        """, unsafe_allow_html=True)

                    # Export data moved to data column
                    with col_data:
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

    elif section == "ViBro Assistant":
        # Chat container
        st.markdown("""
            <div class='chat-container'>
                <div class='chat-messages'>
        """, unsafe_allow_html=True)

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask me anything about your finances..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Display assistant response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""

                # Simulate stream of response with a typing indicator
                with st.spinner("ViBro is thinking..."):
                    # Process the user's message and generate a response
                    if "portfolio" in prompt.lower() or "stocks" in prompt.lower():
                        risk_tolerance = "moderate"
                        investment_amount = 10000
                        try:
                            suggestions = suggest_stocks(risk_tolerance, investment_amount)
                            response = "Based on your interest in portfolio management, here are some stock suggestions:\n\n"
                            for suggestion in suggestions:
                                response += f"📈 **{suggestion['ticker']} - {suggestion['company']}**\n{suggestion['reason']}\n\n"
                        except Exception as e:
                            response = f"Error generating portfolio recommendations: {str(e)}"
                    elif "goal" in prompt.lower() or "planning" in prompt.lower():
                        response = "Let's discuss your financial goals. To help you better, I'll need to know:\n\n" + \
                                 "1. What type of goal are you planning for? (e.g., retirement, house, education)\n" + \
                                 "2. What's your target amount?\n" + \
                                 "3. When do you want to achieve this goal?\n\n" + \
                                 "Share these details, and I'll create a personalized plan for you."
                    else:
                        response = "I can help you with portfolio management, goal planning, and investment recommendations. " + \
                                 "What specific aspect would you like to explore?"

                    # Simulate typing
                    for chunk in response.split():
                        full_response += chunk + " "
                        time.sleep(0.05)
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        # Add disclaimer at the bottom of the page
        st.markdown("---")
        st.markdown("""
        ### Disclaimer
        Quotes are not sourced from all markets and may be delayed by up to 20 minutes. All information provided on this platform is offered "as is" and is intended solely for informational purposes. It should not be considered as investment advice, financial planning guidance, or a recommendation to buy or sell any securities. Please consult a qualified financial advisor before making any trading or investment decisions.

        ### ViBro Finance
        Thank you for choosing ViBro Finance as your trading partner. We are committed to providing you with the best information. If you have any questions or concerns, please contact our support team at [hi@veerbajaj.com](mailto:hi@veerbajaj.com).

        [Veer Bajaj ↗](https://veerbajaj.com)

        """)


    # Add Technical Indicators Explanation section at the bottom
    st.markdown("---")
    with st.expander("📚 Understanding Technical Indicators", expanded=False):
        st.markdown("""
        ### Stock Chart Components - A ViBro Guide

        #### OHLC (Candlestick Chart)
        - **O**pen: The stock's price at market open
        - **H**igh: The highest price during the trading day
        - **L**ow: The lowest price during the trading day
        - **C**lose: The final price when the market closes
        - 🎯 *Green candles* indicate price increase, *red candles* indicate price decrease

        #### Moving Averages
        - **20 SMA** (Simple Moving Average): Average price over the last 20 days
        - **50 SMA**: Average price over the last 50 days
        - 🎯 These help identify trends and potential support/resistance levels

        #### RSI (Relative Strength Index)
        - A momentum indicator that measures the speed and magnitude of recent price changes
        - Scale: 0 to 100
        - Above 70: Potentially overbought
        - Below 30: Potentially oversold
        - 🎯 Helps identify potential reversal points

        ### Key Metrics Explained

        #### Market Fundamentals
        - **Market Cap**: Total value of all shares (Price × Outstanding Shares)
        - **P/E Ratio**: Price per share divided by earnings per share
        - **EPS**: Earnings Per Share - Company's profit divided by outstanding shares

        #### Price Indicators
        - **52 Week High**: Highest stock price in the past year
        - **52 Week Low**: Lowest stock price in the past year
        - **Volume**: Number of shares traded

        #### Income Metrics
        - **Dividend Yield**: Annual dividend payments relative to stock price
        - 🎯 Higher yield might indicate better income potential, but verify company's stability

        ### Using This Information

        - Compare current price to 52-week range for context
        - Use P/E ratio to assess if stock is potentially over/undervalued
        - Watch volume for confirmation of price movements
        - Monitor RSI for potential entry/exit points
        """)

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.markdown("Please try again with valid stock symbols.")