import streamlit as st
from utils.database import get_db
from utils.auth import get_password_hash, authenticate_user, create_access_token
import time
from datetime import datetime

def auth_page():
    if "user" not in st.session_state:
        st.session_state.user = None

    st.title("Welcome to ViBro Finance")

    # Create tabs for login and signup
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.header("Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                with st.spinner("Logging in..."):
                    db = get_db()
                    user = authenticate_user(db, email, password)
                    if user:
                        token = create_access_token({"sub": email})
                        st.session_state.user = user
                        st.session_state.token = token
                        st.success("Login successful!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid email or password")

    with tab2:
        st.header("Sign Up")
        with st.form("signup_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Sign Up")

            if submitted:
                if password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    with st.spinner("Creating account..."):
                        db = get_db()
                        # Check if user exists
                        if email in db.users:
                            st.error("Email already exists")
                        else:
                            # Create new user
                            db.users[email] = {
                                'username': username,
                                'email': email,
                                'hashed_password': get_password_hash(password),
                                'created_at': datetime.utcnow().isoformat()
                            }
                            db.save()

                            # Log user in
                            token = create_access_token({"sub": email})
                            st.session_state.user = db.users[email]
                            st.session_state.token = token
                            st.success("Account created successfully!")
                            time.sleep(1)
                            st.rerun()

def check_auth():
    if "user" not in st.session_state or st.session_state.user is None:
        auth_page()
        return False
    return True