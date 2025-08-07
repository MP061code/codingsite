import streamlit as st
import requests
import urllib.parse
import openai
from PIL import Image

# Load secrets
AUTH0_CLIENT_ID = st.secrets["auth0"]["client_id"]
AUTH0_CLIENT_SECRET = st.secrets["auth0"]["client_secret"]
AUTH0_DOMAIN = st.secrets["auth0"]["domain"]
AUTH0_REDIRECT_URI = st.secrets["auth0"]["redirect_uri"]

# Auth0 URLs
AUTH0_AUTHORIZE_URL = f"https://{AUTH0_DOMAIN}/authorize"
AUTH0_TOKEN_URL = f"https://{AUTH0_DOMAIN}/oauth/token"
AUTH0_USERINFO_URL = f"https://{AUTH0_DOMAIN}/userinfo"

# Page setup
st.set_page_config(page_title="Rudrassa AI", page_icon="🤖", layout="centered")

# Session state
if "user" not in st.session_state:
    st.session_state.user = None
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "response_text" not in st.session_state:
    st.session_state.response_text = ""

# Handle Auth0 callback
query_params = st.query_params
if "code" in query_params and st.session_state.user is None:
    code = query_params["code"]

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
        st.session_state.access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        userinfo_response = requests.get(AUTH0_USERINFO_URL, headers=headers)
        st.session_state.user = userinfo_response.json()
    else:
        st.error("❌ Authentication failed. Please try again.")

# -----------------------
# LOGIN / LOGOUT DISPLAY
# -----------------------
if st.session_state.user:
    st.sidebar.success(f"✅ Logged in as {st.session_state.user['email']}")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.access_token = None
        st.experimental_set_query_params()
        st.rerun()
else:
    # Logo
    st.image("rudrassaaaa.png", width=180)

    st.markdown("## 🔒 Welcome to Rudrassa AI")
    st.markdown("Login securely with your **Gmail account** via Auth0 to access the AI assistant.")

    # Build login URL
    params = {
        "response_type": "code",
        "client_id": AUTH0_CLIENT_ID,
        "redirect_uri": AUTH0_REDIRECT_URI,
        "scope": "openid profile email",
        "connection": "google-oauth2"  # force Google login
    }
    login_url = f"{AUTH0_AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"

    # Google login button with icon
    google_icon = "https://upload.wikimedia.org/wikipedia/commons/4/4a/Logo_2013_Google.png"
    st.markdown(f"""
        <a href="{login_url}" target="_self" style="text-decoration: none;">
            <button style="
                background-color: white;
                border: 1px solid #ddd;
                color: #444;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 16px;
                cursor: pointer;
                display: flex;
                align-items: center;
            ">
                <img src="{google_icon}" width="20" style="margin-right: 10px" />
                Sign in with Google
            </button>
        </a>
    """, unsafe_allow_html=True)

    st.stop()

# -----------------------
# AUTHENTICATED APP
# -----------------------
st.title("🤖 Rudrassa AI Content Generator")

api_key = st.text_input("Enter your OpenAI API key:", type="password")
user_query = st.text_area("📝 Describe what you want to generate:", height=100)

def generate_response(prompt, key):
    try:
        client = openai.OpenAI(api_key=key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert content creator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=600
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"

if st.button("⚡ Generate Content") and user_query and api_key:
    with st.spinner("Generating your content..."):
        st.session_state.response_text = generate_response(user_query, api_key)

if st.session_state.response_text:
    st.subheader("✨ Your AI-Generated Content")
    st.write(st.session_state.response_text)
    st.download_button(
        "📥 Download as .txt",
        st.session_state.response_text,
        file_name="rudrassa_ai_content.txt"
    )

# Footer
st.markdown("---")
st.caption("🔐 Secure login powered by Auth0 · Built by Rudrassa AI © 2025")
