import streamlit as st
import pandas as pd
from utils.stock_data import get_stock_data, get_multiple_stocks_data, get_key_metrics, format_large_number, calculate_technical_indicators
from utils.ai_advisor import get_stock_analysis, ask_follow_up_question, suggest_stocks
from utils.chart_helper import create_stock_chart, create_comparison_chart
from utils.portfolio_manager import generate_portfolio_recommendation, analyze_portfolio_health
from utils.goal_planner import FinancialGoal, analyze_goal_feasibility, generate_investment_plan
from utils.auth import AuthManager
from utils.ml_predictor import StockPredictor # Added import
from datetime import datetime # Added import
from pages.auth import init_auth, login_page, logout  # Re-added import
import logging
from utils.education_manager import EducationManager  # Add this import

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

# Load custom CSS
with open('styles/custom.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize authentication state
init_auth()

# Initialize session states
if "analyze" not in st.session_state:
    st.session_state.analyze = False
if "symbols" not in st.session_state:
    st.session_state.symbols = []
if "portfolio_update" not in st.session_state:
    st.session_state.portfolio_update = None
if "goal_update" not in st.session_state:
    st.session_state.goal_update = None
if "show_notifications" not in st.session_state:
    st.session_state.show_notifications = False

# Check authentication
if not st.session_state.authenticated:
    login_page()
else:
    # Initialize AuthManager for user activity tracking
    auth_manager = AuthManager()
    logger.info(f"User {st.session_state.username} logged in.")
    # Header with user greeting and logout
    col1, col2, col3 = st.columns([3, 0.5, 0.5])
    with col1:
        st.title("📈 ViBro Finance")
        st.markdown(f"### Welcome back, {st.session_state.username}! 👋")

    # Add notification bell in the middle column
    with col2:
        notifications = auth_manager.get_notifications(st.session_state.username)
        unread_count = len([n for n in notifications if not n['read']])

        if notifications:
            notification_button = f"🔔 {unread_count}" if unread_count > 0 else "🔔"
            if st.button(notification_button, key="notification_bell"):
                st.session_state.show_notifications = not st.session_state.get('show_notifications', False)
        else:
            st.button("🔔", key="notification_bell", disabled=True)

        # Show notifications popup when clicked
        if st.session_state.get('show_notifications', False) and notifications:
            with st.container():
                st.markdown("""
                    <style>
                    .notification-popup {
                        position: fixed;
                        top: 60px;
                        right: 20px;
                        max-width: 300px;
                        z-index: 1000;
                        background: var(--secondary-background-color);
                        border-radius: 8px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                        padding: 1rem;
                    }
                    </style>
                    <div class="notification-popup">
                """, unsafe_allow_html=True)

                for notification in notifications:
                    if not notification['read']:
                        st.markdown(f"""
                            <div style='background-color: rgba(0, 171, 65, 0.1); padding: 10px; border-radius: 5px; margin: 5px 0;'>
                                <small style='color: #00AB41'>From ViBro finance:</small><br>
                                {notification['message']}
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("Mark as Read", key=f"notify_{notification['id']}"):
                            if auth_manager.mark_notification_as_read(st.session_state.username, notification["id"]):
                                st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

    # Logout button in the last column
    with col3:
        if st.button("Logout", key="logout"):
            logout()

    # Navigation
    nav_options = ["Market Analysis", "Portfolio Management", "Goal Planning", "Education", "Investor Chat"]
    st.markdown("<div class='nav-container'>", unsafe_allow_html=True)
    cols = st.columns(5)  # Updated to 5 columns
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

    # Main content
    try:
        if section == "Market Analysis":
            analysis_type = st.radio(
                "Select Analysis Type",
                ["Single Stock", "Compare Stocks"],
                horizontal=True
            )

            if analysis_type == "Single Stock":
                symbol = st.text_input("Enter Stock Symbol", value="AAPL").upper() # Changed default value
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
                # Add activity tracking for searches
                if 'analyze' in st.session_state and st.session_state.analyze:
                    for symbol in st.session_state.symbols:
                        auth_manager.save_user_activity(
                            st.session_state.username,
                            "search",
                            {"symbol": symbol, "period": time_period}
                        )

        # Show recent searches
        with st.expander("Recent Searches"):
            history = auth_manager.get_search_history(st.session_state.username)
            if history:
                for search in reversed(history[-5:]):  # Show last 5 searches
                    st.write(f"🔍 {search['symbol']} ({search['period']}) - {search['timestamp']}")
            else:
                st.write("No recent searches")

        if section == "Market Analysis":
            if st.session_state.analyze and len(st.session_state.symbols) > 0:
                if analysis_type == "Single Stock":
                    with st.spinner(f'Fetching data for {symbols[0]}...'):
                        # Get stock data
                        hist_data, stock_info = get_stock_data(symbols[0], time_period)
                        metrics = get_key_metrics(stock_info)

                        # Calculate technical indicators
                        df = calculate_technical_indicators(hist_data)

                        # Generate price predictions
                        predictor = StockPredictor()
                        with st.spinner('Generating price predictions...'):
                            try:
                                predictions, confidence = predictor.analyze_stock(hist_data)

                                # Show prediction confidence
                                st.info(f"""
                                    **ML Prediction Confidence:**
                                    - Model Accuracy: {confidence['test_score']:.2%}
                                    - Prediction Quality: {confidence['prediction_quality']}
                                    - Predicting next {len(predictions)} trading days
                                """)
                            except Exception as e:
                                st.warning(f"Could not generate predictions: {str(e)}")
                                predictions = None

                        # Two-column layout
                        col_data, col_ai = st.columns([1, 1])

                        with col_data:
                            # Company header
                            st.markdown(f"## {stock_info.get('longName', symbols[0])}")
                            st.markdown(f"*{stock_info.get('sector', '')} | {stock_info.get('industry', '')}*")

                            current_price = stock_info.get('currentPrice', 0)
                            price_change = stock_info.get('regularMarketChangePercent', 0)
                            price_color = "stock-up" if price_change >= 0 else "stock-down"

                            # Show current price and predicted price if available
                            if predictions is not None:
                                predicted_price = predictions['Predicted_Close'].iloc[-1]
                                predicted_change = ((predicted_price - current_price) / current_price) * 100
                                predicted_color = "stock-up" if predicted_change >= 0 else "stock-down"

                                st.markdown(f"""
                                    <div class='price-display'>
                                        <h2>${current_price:.2f}</h2>
                                        <p class='{price_color}'>{price_change:+.2f}%</p>
                                        <p>Predicted (30d): <span class='{predicted_color}'>${predicted_price:.2f} ({predicted_change:+.2f}%)</span></p>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
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

        elif section == "Portfolio Management":
            st.title("📊 Portfolio Management")

            tab1, tab2 = st.tabs(["Create Portfolio", "Analyze Portfolio"])

            with tab1:
                risk_tolerance = st.select_slider(
                    "Risk Tolerance",
                    options=["Conservative", "Moderate", "Aggressive"],
                    value="Moderate"
                )

                investment_amount = st.number_input(
                    "Investment Amount ($)",
                    min_value=1000,
                    max_value=10000000,
                    value=10000,
                    step=1000
                )

                # Add sector preferences
                sectors = st.multiselect(
                    "Preferred Sectors (Optional)",
                    ["Technology", "Healthcare", "Financial Services", "Consumer Cyclical",
                     "Industrial", "Energy", "Materials", "Real Estate", "Utilities"]
                )

                if st.button("Generate Portfolio Recommendation", type="primary"):
                    with st.spinner("Analyzing and generating recommendations..."):
                        try:
                            # Get portfolio allocation
                            portfolio = generate_portfolio_recommendation(
                                risk_tolerance.lower(),
                                investment_amount
                            )

                            # Display allocation
                            st.subheader("Recommended Asset Allocation")
                            cols = st.columns(len(portfolio["allocation"]))
                            for i, (asset, percentage) in enumerate(portfolio["allocation"].items()):
                                cols[i].metric(
                                    f"{asset.title()}",
                                    f"{percentage*100:.0f}%",
                                    f"${investment_amount * percentage:,.2f}"
                                )

                            # Get and display stock suggestions
                            st.subheader("Recommended Stocks")
                            suggestions = suggest_stocks(
                                risk_tolerance.lower(),
                                investment_amount,
                                sectors if sectors else None
                            )

                            for suggestion in suggestions:
                                st.info(f"**{suggestion['ticker']} - {suggestion['company']}**\n\n{suggestion['reason']}")

                            # Add activity tracking for portfolio updates
                            st.session_state.portfolio_update = {
                                "risk_tolerance": risk_tolerance.lower(),
                                "investment_amount": investment_amount,
                                "sectors": sectors,
                                "recommendations": suggestions
                            }

                        except Exception as e:
                            st.error(f"Error generating portfolio recommendation: {str(e)}")

            with tab2:
                available_stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "META", "TSLA", "NVDA", "JPM", "BAC", "WMT"]
                portfolio_stocks = st.multiselect(
                    "Select stocks in your portfolio",
                    options=available_stocks,
                    default=["AAPL"]  # Changed default from 'ViBro' to 'AAPL'
                )

                if st.button("Analyze Portfolio", type="primary"):
                    with st.spinner("Analyzing portfolio..."):
                        try:
                            analysis = analyze_portfolio_health(portfolio_stocks)

                            # Display portfolio metrics
                            st.subheader("Portfolio Overview")

                            # Sector allocation
                            st.markdown("#### Sector Allocation")
                            sector_cols = st.columns(len(analysis["sector_allocation"]))
                            for i, (sector, count) in enumerate(analysis["sector_allocation"].items()):
                                sector_cols[i].metric(sector, f"{count} stocks")

                            # Stock recommendations
                            st.markdown("#### Stock Analysis")
                            for rec in analysis["recommendations"]:
                                st.markdown(f"### {rec['symbol']}")
                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown("**Analysis Summary**")
                                    st.write(rec["analysis"]["summary"])

                                with col2:
                                    st.markdown("**Key Points**")
                                    st.markdown("✅ **Strengths:**")
                                    for strength in rec["analysis"]["strengths"]:
                                        st.markdown(f"- {strength}")
                                    st.markdown("⚠️ **Risks:**")
                                    for risk in rec["analysis"]["risks"]:
                                        st.markdown(f"- {risk}")

                            # Add activity tracking for portfolio updates
                            st.session_state.portfolio_update = {
                                "portfolio_stocks": portfolio_stocks,
                                "analysis": analysis
                            }

                        except Exception as e:
                            st.error(f"Error analyzing portfolio: {str(e)}")

        elif section == "Goal Planning":
            st.title("🎯 Financial Goal Planning")

            with st.expander("Create New Goal", expanded=True):
                goal_type = st.selectbox(
                    "Goal Type",
                    ["Retirement", "House Down Payment", "Education", "Emergency Fund", "Travel"]
                )

                target_amount = st.number_input(
                    "Target Amount ($)",
                    min_value=1000,
                    max_value=10000000,
                    value=50000,
                    step=1000
                )

                target_date = st.date_input(
                    "Target Date",
                    value=pd.to_datetime("2025-12-31")
                )

                current_amount = st.number_input(
                    "Current Amount Saved ($)",
                    min_value=0,
                    max_value=10000000,
                    value=0,
                    step=1000
                )

                if st.button("Create Goal"):
                    try:
                        goal = FinancialGoal(
                            goal_type,
                            target_amount,
                            target_date.strftime("%Y-%m-%d"),
                            current_amount
                        )

                        # Analyze goal feasibility
                        monthly_income = st.number_input("Monthly Income ($)", min_value=0, value=5000)
                        monthly_expenses = st.number_input("Monthly Expenses ($)", min_value=0, value=3000)

                        feasibility = analyze_goal_feasibility(goal, monthly_income, monthly_expenses)

                        # Display feasibility analysis
                        st.subheader("Goal Analysis")
                        st.metric("Progress", f"{goal.progress:.1f}%")
                        st.metric("Monthly Savings Required",
                                  f"${feasibility['monthly_required']:,.2f}")

                        st.info(feasibility["recommendation"])

                        # Generate investment plan
                        risk_preference = st.select_slider(
                            "Risk Tolerance",
                            options=["Conservative", "Moderate", "Aggressive"],
                            value="Moderate"
                        )

                        investment_plan = generate_investment_plan(goal, risk_preference.lower())

                        # Display investment plan
                        st.subheader("Investment Plan")
                        st.write(f"Time Horizon: {investment_plan['time_horizon']:.1f} years")
                        st.write(f"Recommended Strategy: {investment_plan['strategy'].title()}")

                        # Show allocation
                        cols = st.columns(len(investment_plan["allocation"]))
                        for i, (asset, percentage) in enumerate(investment_plan["allocation"].items()):
                            cols[i].metric(
                                f"{asset.title()}",
                                f"{percentage}%",
                                f"${target_amount * (percentage/100):,.2f}"
                            )

                        # Add activity tracking for goal updates
                        st.session_state.goal_update = {
                            "goal_type": goal_type,
                            "target_amount": target_amount,
                            "target_date": target_date.strftime("%Y-%m-%d"),
                            "current_amount": current_amount,
                            "monthly_income": monthly_income,
                            "monthly_expenses": monthly_expenses,
                            "risk_preference": risk_preference.lower(),
                            "investment_plan": investment_plan
                        }

                    except Exception as e:
                        st.error(f"Error creating goal plan: {str(e)}")

        elif section == "Education":
            st.title("📚 Financial Education")

            # Initialize education manager
            education_manager = EducationManager()

            # Get all courses
            courses = education_manager.get_all_courses()

            # Get user's progress
            user_progress = education_manager.get_user_progress(st.session_state.username)

            # Display available courses
            st.markdown("### Available Courses")

            for course in courses:
                # Create an expandable section for each course
                with st.expander(f"📘 {course['title']}", expanded=True):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"**Duration:** {course['duration']}")
                        st.markdown(course['description'])

                        # Calculate progress
                        modules_completed = sum(
                            1 for module in course['modules']
                            if education_manager.get_module_completion(
                                st.session_state.username,
                                course['id'],
                                module['id']
                            )
                        )
                        progress = (modules_completed / len(course['modules'])) if len(course['modules']) > 0 else 0

                        # Display progress bar
                        st.write(f"Progress: {progress*100}%")
                        st.progress(float(progress))

                    with col2:
                        if st.button("Start Course", key=f"start_{course['id']}"):
                            st.session_state.current_course = course['id']
                            st.rerun()

            # Display course content if a course is selected
            if hasattr(st.session_state, 'current_course'):
                current_course = education_manager.get_course(st.session_state.current_course)

                if current_course:
                    st.markdown(f"## {current_course['title']}")

                    for i, module in enumerate(current_course['modules'], 1):
                        module_completed = education_manager.get_module_completion(
                            st.session_state.username,
                            current_course['id'],
                            module['id']
                        )

                        with st.expander(
                            f"Module {i}: {module['title']} {'✅' if module_completed else ''}",
                            expanded=not module_completed
                        ):
                            st.markdown(module['content'])

                            # Display quiz
                            if 'quiz' in module:
                                st.markdown("### Quick Quiz")
                                for j, question in enumerate(module['quiz'], 1):
                                    st.markdown(f"**Q{j}: {question['question']}**")
                                    answer = st.radio(
                                        "Select your answer:",
                                        question['options'],
                                        key=f"quiz_{module['id']}_{j}"
                                    )

                                    if st.button("Check Answer", key=f"check_{module['id']}_{j}"):
                                        if question['options'].index(answer) == question['correct']:
                                            st.success("Correct!")
                                            education_manager.update_user_progress(
                                                st.session_state.username,
                                                current_course['id'],
                                                module['id']
                                            )
                                            st.rerun()
                                        else:
                                            st.error("Try again!")

        elif section == "Investor Chat":
            st.title("💬 Investor Chat")

            # Initialize chat container
            if "chat_messages" not in st.session_state:
                st.session_state.chat_messages = []

            # Show superuser controls if applicable
            is_superuser = auth_manager.is_superuser(st.session_state.username)
            if is_superuser:
                with st.expander("🛡️ Superuser Controls"):
                    st.markdown("### User Management")
                    users = auth_manager.get_all_users(st.session_state.username)
                    if users:
                        user_df = pd.DataFrame(users)
                        st.dataframe(user_df)
                    else:
                        st.warning("Unable to fetch users list")

                    # Add notification controls
                    st.markdown("### Send Notification")

                    # Option to select between single user or all users
                    notification_type = st.radio(
                        "Notification Type",
                        ["Single User", "All Users"],
                        horizontal=True
                    )

                    if notification_type == "Single User":
                        notify_user = st.selectbox(
                            "Select User",
                            [user["username"] for user in users if user["username"] != st.session_state.username]
                        )

                    notification_message = st.text_area("Notification Message")

                    if st.button("Send Notification", type="primary"):
                        if notification_type == "Single User":
                            if auth_manager.send_notification(st.session_state.username, notify_user, notification_message):
                                st.success(f"Notification sent to {notify_user}")
                            else:
                                st.error("Failed to send notification")
                        else:  # All Users
                            if auth_manager.send_notification_to_all(st.session_state.username, notification_message):
                                st.success("Notification sent to all users")
                            else:
                                st.error("Failed to send notification to all users")

            # Add notification display for all users
            notifications = auth_manager.get_notifications(st.session_state.username)
            if notifications:
                with st.expander(f"📬 Notifications ({len([n for n in notifications if not n['read']])} unread)", expanded=True):
                    for notification in notifications:
                        if not notification["read"]:
                            st.markdown(f"""
                                <div style='background-color: rgba(0, 171, 65, 0.1); padding: 10px; border-radius: 5px; margin: 5px 0;'>
                                    <small style='color: #00AB41'>From ViBro Finance</small><br>
                                    {notification['message']}
                                </div>
                            """, unsafe_allow_html=True)
                            if st.button("Mark as Read", key=f"notify_{notification['id']}"):
                                if auth_manager.mark_notification_as_read(st.session_state.username, notification["id"]):
                                    st.rerun()

            # Message input
            chat_input = st.text_input("Type your message (Markdown supported):", key="chat_input")
            if st.button("Send", type="primary"):
                if chat_input.strip():
                    # Save message to database
                    if auth_manager.save_chat_message(st.session_state.username, chat_input):
                        st.success("Message sent!")
                        st.session_state.chat_messages = auth_manager.get_chat_messages()
                        st.rerun()

            # Display chat messages
            with st.container():
                st.markdown("### Recent Messages")
                messages = auth_manager.get_chat_messages()

                def format_chat_message(msg, is_current_user):
                    timestamp = datetime.fromisoformat(msg['timestamp'])
                    formatted_time = timestamp.strftime("%I:%M %p")

                    if is_current_user:
                        st.markdown(f"""
                            <div style='text-align: right; margin: 10px 0;'>
                                <div style='display: inline-block; background-color: #00AB41; color: white; 
                                      padding: 10px; border-radius: 15px; max-width: 70%;'>
                                    {msg['message']}
                                </div>
                                <small style='opacity: 0.7;'>{formatted_time}</small>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div style='text-align: left; margin: 10px 0;'>
                                <div style='display: inline-block; background-color: #262730; 
                                      padding: 10px; border-radius: 15px; max-width: 70%;'>
                                    <small style='color: #00AB41;'>{msg['username']}</small><br>
                                    {msg['message']}
                                </div>
                                <small style='opacity: 0.7;'>{formatted_time}</small>
                            </div>
                        """, unsafe_allow_html=True)

                    # Show delete button for superuser
                    if is_superuser:
                        if st.button("🗑️ Delete", key=f"delete_{msg['id']}"):
                            if auth_manager.delete_message(msg['id'], st.session_state.username):
                                st.success("Message deleted!")
                                st.rerun()

                for msg in reversed(messages):
                    is_current_user = msg['username'] == st.session_state.username
                    format_chat_message(msg, is_current_user)

                # Auto-scroll to bottom (placeholder for future enhancement)
                st.markdown("""
                    <div id='chat-bottom'></div>
                    <script>
                        document.getElementById('chat-bottom').scrollIntoView();
                    </script>
                """, unsafe_allow_html=True)


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
            - A momentum indicator that measures the speedand magnitude of recent price changes
            - Scale: 0 to 100
            - Above 70: Potentially overbought
            -Below 30: Potentially oversold
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

        # Add disclaimer at the bottom of the page
        st.markdown("---")
        st.markdown("""
        ### Disclaimer
        Quotes are not sourced from all markets and may be delayed by up to 20 minutes. All information provided on this platform is offered "as is" and is intended solely for informational purposes. It should not be considered as investment advice, financial planning guidance, or a recommendation to buy or sell any securities. Please consult a qualified financial advisor before making any trading or investment decisions.

        ### ViBro Finance
        Thank you for choosing ViBro Finance as your trading partner. We are committed to providing you with the best information. If you have any questions or concerns, please contact our support team at [hi@veerbajaj.com](mailto:hi@veerbajaj.com).

        [Veer Bajaj ↗](https://veerbajaj.com)
        """)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.markdown("Please try again with valid stock symbols.")