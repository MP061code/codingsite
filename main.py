import streamlit as st
import requests
import urllib.parse
import openai

# ------------------
# Auth0 Configuration
# ------------------
AUTH0_CLIENT_ID = st.secrets["auth0"]["client_id"]
AUTH0_CLIENT_SECRET = st.secrets["auth0"]["client_secret"]
AUTH0_DOMAIN = st.secrets["auth0"]["domain"]
AUTH0_REDIRECT_URI = st.secrets["auth0"]["redirect_uri"]

AUTH0_AUTHORIZE_URL = f"https://{AUTH0_DOMAIN}/authorize"
AUTH0_TOKEN_URL = f"https://{AUTH0_DOMAIN}/oauth/token"
AUTH0_USERINFO_URL = f"https://{AUTH0_DOMAIN}/userinfo"

# --------------
# Streamlit Setup
# --------------
st.set_page_config(
    page_title="Rudrassa AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# --------------
# Session Storage
# --------------
if "user" not in st.session_state:
    st.session_state.user = None
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "response_text" not in st.session_state:
    st.session_state.response_text = ""

# -----------------
# Auth0 Callback Logic
# -----------------
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
        st.error("❌ Failed to authenticate. Please try again.")

# -----------------------
# LOGIN / LOGOUT DISPLAY
# -----------------------
if st.session_state.user:
    st.sidebar.success(f"Logged in as {st.session_state.user['email']}")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.access_token = None
        st.experimental_set_query_params()
        st.rerun()
else:
    # -----------------
    # Styled Login Page
    # -----------------
    st.markdown("""
        <style>
        .centered {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding-top: 50px;
        }
        .login-btn {
            background-color: white;
            border: 1px solid #ccc;
            padding: 10px 16px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-top: 20px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        .login-btn:hover {
            background-color: #f0f0f0;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="centered">', unsafe_allow_html=True)
    st.image("rudrassaaaa.png", width=120)
    st.markdown("## 🔐 Welcome to Rudrassa AI")
    st.markdown("Login securely using your Gmail account via Auth0.")

    params = {
        "response_type": "code",
        "client_id": AUTH0_CLIENT_ID,
        "redirect_uri": AUTH0_REDIRECT_URI,
        "scope": "openid profile email",
    }
    login_url = f"{AUTH0_AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"

    st.markdown(f"""
        <a class="login-btn" href="{login_url}">
            <img src="https://img.icons8.com/color/24/google-logo.png" alt="Google Icon"/>
            Login with Google
        </a>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# -----------------------
# AUTHENTICATED CONTENT
# -----------------------
st.title("🤖 Rudrassa AI Content Generator")

api_key = st.text_input("Enter your OpenAI API key:", type="password")
user_query = st.text_area("Describe what you want:", height=100)

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

if st.button("🚀 Generate Content") and user_query and api_key:
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
