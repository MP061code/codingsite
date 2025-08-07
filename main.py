import streamlit as st
import openai
import requests
import urllib
import jwt
from urllib.parse import urlencode

# -------------------- AUTH0 SETTINGS --------------------
AUTH0_DOMAIN = st.secrets["auth0"]["domain"]
CLIENT_ID = st.secrets["auth0"]["client_id"]
CLIENT_SECRET = st.secrets["auth0"]["client_secret"]
REDIRECT_URI = st.secrets["auth0"]["redirect_uri"]
AUTH0_BASE_URL = f"https://{AUTH0_DOMAIN}"
AUTHORIZE_URL = f"{AUTH0_BASE_URL}/authorize"
TOKEN_URL = f"{AUTH0_BASE_URL}/oauth/token"
USERINFO_URL = f"{AUTH0_BASE_URL}/userinfo"

# -------------------- LOGIN LOGIC -----------------------
def login_button():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "openid profile email",
    }
    login_url = f"{AUTHORIZE_URL}?{urlencode(params)}"
    st.markdown(f"[Login with Auth0]({login_url})")

def get_token(code):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    return requests.post(TOKEN_URL, headers=headers, data=data).json()

def get_user_info(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    return requests.get(USERINFO_URL, headers=headers).json()

# -------------------- AUTHENTICATION --------------------
query_params = st.experimental_get_query_params()
code = query_params.get("code", [None])[0]

if code:
    token_data = get_token(code)
    user_info = get_user_info(token_data["access_token"])
    st.session_state["user"] = user_info

if "user" not in st.session_state:
    st.title("🔒 Rudrassa AI Login")
    login_button()
    st.stop()
else:
    st.sidebar.write(f"👤 Logged in as {st.session_state['user']['name']}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.experimental_set_query_params()  # Clear ?code from URL
        st.rerun()

# -------------------- APP START ------------------------
st.set_page_config(page_title="Rudrassa AI Assistant", layout="wide")
st.title("🧠 Rudrassa AI Content Assistant")

# Input for OpenAI API key
api_key = st.text_input("Enter your OpenAI API key:", type="password")

# Input for user query
user_query = st.text_area("Enter your problem/topic:", height=100)

if 'blog_article' not in st.session_state:
    st.session_state.blog_article = ""
if 'social_media_posts' not in st.session_state:
    st.session_state.social_media_posts = ""
if 'story' not in st.session_state:
    st.session_state.story = ""
if 'processing' not in st.session_state:
    st.session_state.processing = False

def generate_blog_article(topic, api_key):
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a blog writer..."},
                {"role": "user", "content": f"Write a short blog article about: {topic}"}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating blog article: {str(e)}"

def generate_social_media_posts(topic, api_key):
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a social media expert..."},
                {"role": "user", "content": f"Create 3 social media posts about: {topic}"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating posts: {str(e)}"

def generate_story(topic, api_key):
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a fiction storyteller..."},
                {"role": "user", "content": f"Write a story related to: {topic}"}
            ],
            temperature=0.8,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating story: {str(e)}"

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
    st.info("Processing... please wait")
    run_agents()

# Display results
if st.session_state.blog_article or st.session_state.social_media_posts or st.session_state.story:
    tab1, tab2, tab3 = st.tabs(["Blog Article", "Social Media Posts", "Short Story"])
    with tab1:
        st.markdown("### Blog Article")
        st.markdown(st.session_state.blog_article)
    with tab2:
        st.markdown("### Social Media Posts")
        st.markdown(st.session_state.social_media_posts)
    with tab3:
        st.markdown("### Short Story")
        st.markdown(st.session_state.story)

st.markdown("---")
st.markdown("🔐 Secure login via Auth0 (Gmail or email/password). Powered by OpenAI & Streamlit.")
