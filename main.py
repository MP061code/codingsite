import streamlit as st
import requests
import urllib.parse

# Load secrets
AUTH0_CLIENT_ID = st.secrets["auth0"]["client_id"]
AUTH0_CLIENT_SECRET = st.secrets["auth0"]["client_secret"]
AUTH0_DOMAIN = st.secrets["auth0"]["domain"]
AUTH0_REDIRECT_URI = st.secrets["auth0"]["redirect_uri"]

AUTH0_AUTHORIZE_URL = f"https://{AUTH0_DOMAIN}/authorize"
AUTH0_TOKEN_URL = f"https://{AUTH0_DOMAIN}/oauth/token"
AUTH0_USERINFO_URL = f"https://{AUTH0_DOMAIN}/userinfo"

# Set page config
st.set_page_config(page_title="🔒 Rudrassa AI Login", layout="centered")

# Handle Auth0 callback
query_params = st.query_params

if "code" in query_params:
    code = query_params["code"]

    # Exchange code for tokens
    token_payload = {
        "grant_type": "authorization_code",
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "code": code,
        "redirect_uri": AUTH0_REDIRECT_URI
    }

    token_response = requests.post(AUTH0_TOKEN_URL, json=token_payload)
    token_data = token_response.json()

    if "access_token" in token_data:
        access_token = token_data["access_token"]

        # Get user info
        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_response = requests.get(AUTH0_USERINFO_URL, headers=headers)
        userinfo = userinfo_response.json()

        st.success(f"✅ Logged in as {userinfo['email']}")
        st.write("Welcome,", userinfo.get("name", "user"))
        st.write("---")
        st.write("🔐 Authenticated session data:")
        st.json(userinfo)

    else:
        st.error("Failed to authenticate. Try again.")
else:
    st.markdown("## 🔒 Rudrassa AI Login")
    st.markdown("Login securely with your Gmail account via Auth0.")

    # Build the authorization URL
    params = {
        "response_type": "code",
        "client_id": AUTH0_CLIENT_ID,
        "redirect_uri": AUTH0_REDIRECT_URI,
        "scope": "openid profile email",
    }

    login_url = f"{AUTH0_AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"

    st.markdown(f"[👉 Login with Auth0]({login_url})")
