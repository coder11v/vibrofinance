import streamlit as st
from utils.auth import AuthManager

def init_auth():
    """Initialize authentication state"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None

def login_page():
    """Display login/signup page"""
    st.title("🔐 Welcome to ViBro Finance")
    
    # Initialize auth manager
    auth_manager = AuthManager()
    
    # Create tabs for login and signup
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", type="primary", key="login_button"):
            if auth_manager.verify_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Successfully logged in!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    with tab2:
        st.subheader("Sign Up")
        new_username = st.text_input("Username", key="signup_username")
        new_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("Sign Up", type="primary", key="signup_button"):
            if not new_username or not new_password:
                st.error("Please fill in all fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                if auth_manager.register_user(new_username, new_password):
                    st.success("Account created successfully! Please log in.")
                    # Switch to login tab
                    st.query_params["tab"] = "login"
                    st.rerun()
                else:
                    st.error("Username already exists")

def logout():
    """Log out the user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()
