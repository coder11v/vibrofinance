import streamlit as st
import pandas as pd
from utils.stock_data import get_stock_data, get_multiple_stocks_data, get_key_metrics, format_large_number, calculate_technical_indicators
from utils.ai_advisor import get_stock_analysis, ask_follow_up_question, suggest_stocks
from utils.chart_helper import create_stock_chart, create_comparison_chart
from utils.portfolio_manager import generate_portfolio_recommendation, analyze_portfolio_health
from utils.database import get_db
from pages.auth import check_auth
from datetime import datetime
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

# Check authentication
if not check_auth():
    st.stop()

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

# Initialize chat history from JSON database
if "messages" not in st.session_state:
    db = get_db()
    user_email = st.session_state.user['email']
    user_chats = [chat for chat in db.chats.values() 
                  if chat['user_email'] == user_email]
    user_chats.sort(key=lambda x: x['timestamp'], reverse=True)

    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm ViBro, your AI financial assistant. How can I help you today?"}
    ]

    for chat in user_chats[:10]:  # Load last 10 chats
        st.session_state.messages.extend([
            {"role": "user", "content": chat['message']},
            {"role": "assistant", "content": chat['response']}
        ])

# Main content
try:
    if section == "Market Analysis":
        analysis_type = st.radio(
            "Select Analysis Type",
            ["Single Stock", "Compare Stocks"],
            horizontal=True
        )

        if analysis_type == "Single Stock":
            symbol = st.text_input("Enter Stock Symbol", value="AAPL").upper()
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
            if len(symbols) > 0:
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

                            # Stock chart
                            st.markdown("### Technical Analysis")
                            fig = create_stock_chart(df)
                            st.plotly_chart(fig, use_container_width=True)

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

                else:
                    # Comparison View
                    with st.spinner('Fetching data for comparison...'):
                        stock_data = get_multiple_stocks_data(symbols, time_period)

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

                # Process the user's message and generate a response
                with st.spinner("ViBro is thinking..."):
                    if "portfolio" in prompt.lower():
                        try:
                            # Generate portfolio recommendation
                            portfolio = generate_portfolio_recommendation("moderate", 10000)
                            suggestions = suggest_stocks("moderate", 10000)

                            response = "Based on my analysis, here's a personalized investment strategy:\n\n"
                            response += "**Recommended Asset Allocation:**\n"
                            for asset, percentage in portfolio["allocation"].items():
                                response += f"- {asset.title()}: {percentage*100:.0f}%\n"

                            response += "\n**Top Stock Picks:**\n"
                            for suggestion in suggestions:
                                response += f"📈 **{suggestion['ticker']} - {suggestion['company']}**\n{suggestion['reason']}\n\n"

                            response += "\nWould you like to explore any specific stock in detail or discuss investment strategies further?"

                        except Exception as e:
                            response = f"I encountered an issue generating portfolio recommendations. Let me help you with something else."

                    elif "goal" in prompt.lower() or "planning" in prompt.lower():
                        response = "I'll help you create a personalized financial plan. Please share:\n\n" + \
                                "1. What's your target goal? (retirement, house, education)\n" + \
                                "2. How much do you need? (target amount)\n" + \
                                "3. When do you want to achieve this? (target date)\n" + \
                                "4. Current savings towards this goal?\n\n" + \
                                "Once you provide these details, I'll analyze the feasibility and create a custom strategy."

                    elif "technical" in prompt.lower() or "indicators" in prompt.lower():
                        with st.expander("📊 Understanding Technical Indicators", expanded=True):
                            st.markdown("""
                            ### Key Technical Indicators

                            #### 1. Moving Averages (MA)
                            - **20-day MA**: Short-term trend indicator
                            - **50-day MA**: Medium-term trend indicator
                            - When shorter MA crosses above longer MA = Bullish signal
                            - When shorter MA crosses below longer MA = Bearish signal

                            #### 2. Relative Strength Index (RSI)
                            - Measures momentum on a scale of 0 to 100
                            - Above 70 = Potentially overbought
                            - Below 30 = Potentially oversold
                            - Can indicate potential trend reversals

                            #### 3. Volume
                            - Higher volume = Stronger price movement
                            - Lower volume = Weaker price movement
                            - Volume should confirm price trends

                            Would you like me to explain any of these indicators in more detail?
                            """)
                        response = "I've opened up a detailed guide about technical indicators above. Which aspect would you like me to explain further?"

                    else:
                        response = "I can assist you with portfolio management, goal planning, or technical analysis. What would you like to explore?"

                    # Save chat to database
                    db = get_db()
                    chat_id = str(len(db.chats) + 1)
                    db.chats[chat_id] = {
                        'user_email': st.session_state.user['email'],
                        'message': prompt,
                        'response': response,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    db.save()

                    # Simulate typing
                    for chunk in response.split():
                        full_response += chunk + " "
                        time.sleep(0.05)
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)

                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})

        # Footer content for ViBro Assistant
        st.markdown("---")
        with st.expander("ℹ️ About ViBro Finance"):
            st.markdown("""
            ### ViBro Finance

            Your AI-powered financial assistant, bringing intelligent investment guidance through an advanced conversational interface.

            **Created by:** [Veer Bajaj](https://veerbajaj.com)  
            **Contact:** [hi@veerbajaj.com](mailto:hi@veerbajaj.com)

            ### Disclaimer
            All information provided is for educational purposes only. Market data may be delayed. 
            Always conduct your own research and consult with a qualified financial advisor before making investment decisions.
            """)

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.markdown("Please try again with valid inputs.")