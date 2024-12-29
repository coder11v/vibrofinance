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
    page_title="ViBro Finance - AI Financial Assistant",
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
st.markdown("### Your AI Financial Assistant")

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
    # Chat container
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me about stocks, investments, or financial planning..."):
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
                        portfolio = generate_portfolio_recommendation("moderate", 10000)
                        suggestions = suggest_stocks("moderate", 10000)

                        response = f"""Here's a personalized investment strategy:

**Asset Allocation:**
"""
                        for asset, percentage in portfolio["allocation"].items():
                            response += f"- {asset.title()}: {percentage*100:.0f}%\n"

                        response += "\n**Recommended Stocks:**\n"
                        for suggestion in suggestions:
                            response += f"📈 **{suggestion['ticker']} - {suggestion['company']}**\n{suggestion['reason']}\n\n"

                    except Exception as e:
                        response = "I encountered an issue generating portfolio recommendations. Please try again."

                elif "goal" in prompt.lower() or "planning" in prompt.lower():
                    response = """Let me help create a personalized financial plan. I'll need a few details:

1. What are you saving for? (retirement, house, education, etc.)
2. How much do you need to reach your goal?
3. When would you like to achieve this goal?
4. How much have you saved so far?

Once you share these details, I can analyze feasibility and suggest an optimal strategy."""

                elif "technical" in prompt.lower() or "indicators" in prompt.lower():
                    st.markdown("""
                    ### Understanding Technical Analysis

                    #### Candlestick Charts
                    Each candlestick represents four key prices:
                    - **Open**: Price at market open
                    - **High**: Highest price during the period
                    - **Low**: Lowest price during the period
                    - **Close**: Final price at period end

                    Green candles show price increases, red candles show decreases.

                    #### Moving Averages
                    - **20-day SMA**: Short-term trend indicator
                      - Above price = Bearish pressure
                      - Below price = Bullish support
                    - **50-day SMA**: Medium-term trend indicator
                      - Key support/resistance level
                      - Crossovers signal trend changes

                    #### RSI (Relative Strength Index)
                    - Measures momentum (0-100 scale)
                    - Above 70: Potentially overbought
                    - Below 30: Potentially oversold
                    - Divergences can signal reversals

                    #### Volume
                    - Confirms price movements
                    - Higher volume = Stronger trend
                    - Lower volume = Weaker trend

                    #### Key Market Metrics
                    - **Market Cap**: Total company value
                    - **P/E Ratio**: Price relative to earnings
                    - **EPS**: Earnings per share
                    - **52-Week Range**: Price context
                    - **Dividend Yield**: Income potential
                    """)
                    response = "I've displayed a comprehensive guide to technical analysis above. Which aspect would you like me to explain in more detail?"

                else:
                    response = ask_follow_up_question({}, {}, prompt)

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

    # Footer
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
    st.markdown("Please try again.")