import streamlit as st
import requests

# Load from secrets
CLIENT_ID = st.secrets["auth0"]["client_id"]
CLIENT_SECRET = st.secrets["auth0"]["client_secret"]
AUTH0_DOMAIN = st.secrets["auth0"]["domain"]
REDIRECT_URI = st.secrets["auth0"]["redirect_uri"]

AUTH0_AUTHORIZE_URL = f"https://{AUTH0_DOMAIN}/authorize"
AUTH0_TOKEN_URL = f"https://{AUTH0_DOMAIN}/oauth/token"
AUTH0_USERINFO_URL = f"https://{AUTH0_DOMAIN}/userinfo"

# Set page
st.set_page_config(page_title="🔐 Rudrassa AI Login", layout="centered")
st.title("🔐 Rudrassa AI Login")
st.write("Login securely with your Gmail account via Auth0.")

# -------------------- Session Setup --------------------
if "user" not in st.session_state:
    st.session_state.user = None

# Get Auth0 code from query params
query_params = st.query_params
auth_code = query_params.get("code", [None])[0]

# 1. Show Login Button
if not st.session_state.user and not auth_code:
    login_url = (
        f"{AUTH0_AUTHORIZE_URL}"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=openid%20profile%20email"
    )
    st.markdown(f"[🟢 Login with Auth0]({login_url})", unsafe_allow_html=True)

# 2. Exchange Auth Code for Access Token
if auth_code and not st.session_state.user:
    try:
        token_response = requests.post(AUTH0_TOKEN_URL, data={
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": auth_code,
            "redirect_uri": REDIRECT_URI,
        })

        access_token = token_response.json().get("access_token")

        # 3. Get user info
        user_info_response = requests.get(
            AUTH0_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = user_info_response.json()
        st.session_state.user = user_info

        # Clear query params
        st.query_params.clear()

    except Exception as e:
        st.error(f"Authentication failed: {str(e)}")
        st.stop()

# 4. Show profile + logout
if st.session_state.user:
    user = st.session_state.user
    st.success(f"✅ Logged in as {user.get('name')} ({user.get('email')})")

    if st.button("🔴 Logout"):
        logout_url = (
            f"https://{AUTH0_DOMAIN}/v2/logout?"
            f"returnTo={REDIRECT_URI}&client_id={CLIENT_ID}"
        )
        st.session_state.user = None
        st.query_params.clear()
        st.markdown(f'<meta http-equiv="refresh" content="0;url={logout_url}">', unsafe_allow_html=True)
