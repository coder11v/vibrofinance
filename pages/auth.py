import streamlit as st
from utils.database import get_db, User
from utils.auth import get_password_hash, authenticate_user, create_access_token
import time

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
                    db = next(get_db())
                    user = authenticate_user(db, email, password)
                    if user:
                        token = create_access_token({"sub": user.id})
                        st.session_state.user = user
                        st.session_state.token = token
                        st.success("Login successful!")
                        time.sleep(1)
                        st.experimental_rerun()
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
                        db = next(get_db())
                        # Check if user exists
                        existing_user = db.query(User).filter(
                            (User.email == email) | (User.username == username)
                        ).first()
                        
                        if existing_user:
                            st.error("Username or email already exists")
                        else:
                            # Create new user
                            new_user = User(
                                username=username,
                                email=email,
                                hashed_password=get_password_hash(password)
                            )
                            db.add(new_user)
                            db.commit()
                            db.refresh(new_user)
                            
                            # Log user in
                            token = create_access_token({"sub": new_user.id})
                            st.session_state.user = new_user
                            st.session_state.token = token
                            st.success("Account created successfully!")
                            time.sleep(1)
                            st.experimental_rerun()

def check_auth():
    if "user" not in st.session_state or st.session_state.user is None:
        auth_page()
        return False
    return True
