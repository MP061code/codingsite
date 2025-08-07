import streamlit as st
import requests
import os

# App info
st.set_page_config(page_title="Rudrassa AI Login", layout="centered")

st.title("🔒 Rudrassa AI Login")
st.write("Login securely with your Gmail account via Auth0.")

# ------------------ 🔧 Auth0 Configuration ------------------

AUTH0_DOMAIN = "dev-5na6o7a8kl28dh6c.us.auth0.com"
CLIENT_ID = "Ec5Z4DuNAAlrrFNqldOmIQ8dJ5xYmAy8"
CLIENT_SECRET = st.secrets["auth0"]["client_secret"]  # stored in secrets.toml
REDIRECT_URI = "https://codingsite-3udnejsbf4xtvuv8yxgrbu.streamlit.app"

AUTH0_AUTHORIZE_URL = f"https://{AUTH0_DOMAIN}/authorize"
AUTH0_TOKEN_URL = f"https://{AUTH0_DOMAIN}/oauth/token"
AUTH0_USERINFO_URL = f"https://{AUTH0_DOMAIN}/userinfo"

# ------------------ 🧠 Session State Setup ------------------

if "user" not in st.session_state:
    st.session_state.user = None

# ------------------ 🔐 Login Flow ------------------

query_params = st.query_params  # ✅ New API replacing experimental_get_query_params
auth_code = query_params.get("code", [None])[0]

# 1. Show Login Button (before login)
if not st.session_state.user and not auth_code:
    login_url = (
        f"{AUTH0_AUTHORIZE_URL}"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=openid%20profile%20email"
    )
    st.markdown(f"[🟢 Login with Auth0]({login_url})", unsafe_allow_html=True)

# 2. Exchange code for access token
if auth_code and not st.session_state.user:
    try:
        token_response = requests.post(AUTH0_TOKEN_URL, data={
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": auth_code,
            "redirect_uri": REDIRECT_URI,
        })

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        # 3. Fetch user info
        user_info_response = requests.get(
            AUTH0_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = user_info_response.json()
        st.session_state.user = user_info

        # Remove code from URL
        st.query_params.clear()

    except Exception as e:
        st.error("Authentication failed.")
        st.stop()

# 4. If logged in, show profile and logout
if st.session_state.user:
    user = st.session_state.user
    st.success(f"✅ Logged in as {user.get('name')} ({user.get('email')})")

    if st.button("🔴 Logout"):
        logout_url = f"https://{AUTH0_DOMAIN}/v2/logout?returnTo={REDIRECT_URI}&client_id={CLIENT_ID}"
        st.session_state.user = None
        st.query_params.clear()
        st.markdown(f'<meta http-equiv="refresh" content="0;url={logout_url}">', unsafe_allow_html=True)
