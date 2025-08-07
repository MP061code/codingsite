import streamlit as st
import requests
import urllib.parse
import openai

# Load Auth0 secrets from .streamlit/secrets.toml
AUTH0_CLIENT_ID = st.secrets["auth0"]["client_id"]
AUTH0_CLIENT_SECRET = st.secrets["auth0"]["client_secret"]
AUTH0_DOMAIN = st.secrets["auth0"]["domain"]
AUTH0_REDIRECT_URI = st.secrets["auth0"]["redirect_uri"]

AUTH0_AUTHORIZE_URL = f"https://{AUTH0_DOMAIN}/authorize"
AUTH0_TOKEN_URL = f"https://{AUTH0_DOMAIN}/oauth/token"
AUTH0_USERINFO_URL = f"https://{AUTH0_DOMAIN}/userinfo"

# Configure Streamlit page
st.set_page_config(page_title="Rudrassa AI Assistant", layout="wide")

# Session state to store user
if "user" not in st.session_state:
    st.session_state.user = None
if "access_token" not in st.session_state:
    st.session_state.access_token = None

# Handle Auth0 callback
query_params = st.query_params
if "code" in query_params and st.session_state.user is None:
    code = query_params["code"]

    # Get access token
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

        # Get user info
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        userinfo_response = requests.get(AUTH0_USERINFO_URL, headers=headers)
        st.session_state.user = userinfo_response.json()
    else:
        st.error("Failed to authenticate. Please try again.")

# -----------------------
# LOGIN / LOGOUT DISPLAY
# -----------------------
if st.session_state.user:
    st.sidebar.success(f"Logged in as {st.session_state.user['email']}")
    if st.sidebar.button("🚪 Logout"):
        # Clear session state
        st.session_state.user = None
        st.session_state.access_token = None
        st.experimental_set_query_params()
        st.rerun()
else:
    st.markdown("## 🔒 Rudrassa AI Login")
    st.markdown("Login securely with your Gmail account via Auth0.")

    # Build login URL
    params = {
        "response_type": "code",
        "client_id": AUTH0_CLIENT_ID,
        "redirect_uri": AUTH0_REDIRECT_URI,
        "scope": "openid profile email",
    }
    login_url = f"{AUTH0_AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"
    st.markdown(f"[👉 Login with Google]({login_url})")
    st.stop()

# -----------------------
# AUTHENTICATED CONTENT
# -----------------------

st.title("🤖 Rudrassa AI Content Generator")

api_key = st.text_input("Enter your OpenAI API key:", type="password")
user_query = st.text_area("Describe what you want:", height=100)

# Result placeholders
if 'response_text' not in st.session_state:
    st.session_state.response_text = ""

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

if st.button("Generate Content") and user_query and api_key:
    with st.spinner("Generating..."):
        st.session_state.response_text = generate_response(user_query, api_key)

if st.session_state.response_text:
    st.subheader("✨ Generated Content")
    st.write(st.session_state.response_text)
    st.download_button(
        "📥 Download as .txt",
        st.session_state.response_text,
        file_name="ai_content.txt"
    )

# Footer
st.markdown("---")
st.caption("🔐 Secure login powered by Auth0 · Rudrassa AI 2025")
