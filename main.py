import streamlit as st
import openai
import time
import requests
import json
import urllib.parse

# Load Auth0 credentials from secrets.toml
AUTH0_CLIENT_ID = st.secrets["auth0"]["client_id"]
AUTH0_CLIENT_SECRET = st.secrets["auth0"]["client_secret"]
AUTH0_DOMAIN = st.secrets["auth0"]["domain"]
REDIRECT_URI = st.secrets["auth0"]["redirect_uri"]

# Set Streamlit page config
st.set_page_config(page_title="Rudrassa AI Assistant", layout="wide")

# Build Auth0 URLs
AUTH0_AUTHORIZE_URL = f"https://{AUTH0_DOMAIN}/authorize"
AUTH0_TOKEN_URL = f"https://{AUTH0_DOMAIN}/oauth/token"
AUTH0_USERINFO_URL = f"https://{AUTH0_DOMAIN}/userinfo"

# Get query params (new way)
query_params = st.query_params
auth_code = query_params.get("code", [None])[0]

# Session state variables
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# Login
def login_button():
    st.markdown("## 🔒 Rudrassa AI Login")
    st.markdown("Login securely with your Gmail account via Auth0.")
    login_url = (
        f"{AUTH0_AUTHORIZE_URL}?"
        f"response_type=code&"
        f"client_id={AUTH0_CLIENT_ID}&"
        f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
        f"scope=openid profile email"
    )
    st.markdown(f"[Login with Auth0]({login_url})", unsafe_allow_html=True)

# Exchange code for token
def exchange_code_for_token(code):
    payload = {
        "grant_type": "authorization_code",
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(AUTH0_TOKEN_URL, data=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        st.error("⚠️ Failed to exchange code for token")
        return None

# Get user info
def get_user_info(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(AUTH0_USERINFO_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("⚠️ Failed to fetch user info")
        return None

# Auth flow
if auth_code and not st.session_state.access_token:
    token = exchange_code_for_token(auth_code)
    if token:
        st.session_state.access_token = token
        st.session_state.user_info = get_user_info(token)
        st.experimental_set_query_params()  # Clear code from URL

# Show login or app
if not st.session_state.access_token:
    login_button()
    st.stop()
else:
    st.sidebar.success(f"👋 Welcome, {st.session_state.user_info.get('name', 'User')}")
    if st.sidebar.button("Logout"):
        st.session_state.access_token = None
        st.session_state.user_info = None
        st.rerun()

# -------------------- AI Assistant Below --------------------

st.title("🧠 Rudrassa AI Assistant")

# Input for OpenAI API key
api_key = st.text_input("Enter your OpenAI API key:", type="password")

# Input for user query
user_query = st.text_area("Enter your problem:", height=100)

# Session state init
if "blog_article" not in st.session_state:
    st.session_state.blog_article = ""
if "social_media_posts" not in st.session_state:
    st.session_state.social_media_posts = ""
if "story" not in st.session_state:
    st.session_state.story = ""
if "processing" not in st.session_state:
    st.session_state.processing = False

# Content generation functions
def generate_blog_article(topic, api_key):
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional blog writer. Write a blog article on the topic."},
                {"role": "user", "content": f"Write a blog about: {topic}"}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"

def generate_social_media_posts(topic, api_key):
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Create 3 social media posts (Twitter, LinkedIn, Instagram) with hashtags and CTA."},
                {"role": "user", "content": f"Topic: {topic}"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"

def generate_story(topic, api_key):
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Write a short fictional story based on the topic."},
                {"role": "user", "content": f"Topic: {topic}"}
            ],
            temperature=0.8,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"

def run_agents():
    st.session_state.blog_article = generate_blog_article(user_query, api_key)
    st.session_state.social_media_posts = generate_social_media_posts(user_query, api_key)
    st.session_state.story = generate_story(user_query, api_key)
    st.session_state.processing = False

# Generate button
if st.button("Generate Content") and user_query and api_key:
    st.session_state.processing = True
    st.session_state.blog_article = ""
    st.session_state.social_media_posts = ""
    st.session_state.story = ""

# Processing state
if st.session_state.processing:
    st.info("⏳ Generating content... please wait.")
    run_agents()

# Display tabs
if st.session_state.blog_article or st.session_state.social_media_posts or st.session_state.story:
    tab1, tab2, tab3 = st.tabs(["📖 Blog", "📱 Social Media", "📚 Story"])

    with tab1:
        st.markdown("### ✍️ Blog Article")
        st.markdown(st.session_state.blog_article)
        st.download_button("Download", st.session_state.blog_article, file_name="blog.md")

    with tab2:
        st.markdown("### 📢 Social Media Posts")
        st.markdown(st.session_state.social_media_posts)
        st.download_button("Download", st.session_state.social_media_posts, file_name="social_posts.md")

    with tab3:
        st.markdown("### 🧙‍♂️ Short Story")
        st.markdown(st.session_state.story)
        st.download_button("Download", st.session_state.story, file_name="story.md")

st.markdown("---")
st.markdown("Powered by OpenAI • Secure Login via Auth0")

