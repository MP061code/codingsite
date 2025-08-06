import streamlit as st
import openai
import time

st.set_page_config(page_title="My AI Assistant", layout="wide")

st.title("My AI Assistant")

# Input for OpenAI API key
api_key = st.text_input("Enter your OpenAI API key:", type="password")

# Input for user query
user_query = st.text_area("Enter your problem:", height=100)

# Initialize session state for results if not already done
if 'blog_article' not in st.session_state:
    st.session_state.blog_article = ""
if 'social_media_posts' not in st.session_state:
    st.session_state.social_media_posts = ""
if 'story' not in st.session_state:
    st.session_state.story = ""
if 'processing' not in st.session_state:
    st.session_state.processing = False

def generate_blog_article(topic, api_key):
    """Agent 1: Generate a short blog article on the given topic"""
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional blog writer. Create a concise, engaging blog article on the given topic. Keep it under 500 words with a catchy title, introduction, main points with subheadings, and conclusion."},
                {"role": "user", "content": f"Write a short blog article about: {topic}"}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating blog article: {str(e)}"

def generate_social_media_posts(topic, api_key):
    """Agent 2: Generate social media posts on the given topic"""
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a social media marketing expert. Create 3 engaging, shareable posts for different platforms (Twitter, Instagram, LinkedIn) on the given topic. Include relevant hashtags and a call to action in each post."},
                {"role": "user", "content": f"Create 3 engaging social media posts about: {topic}"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating social media posts: {str(e)}"

def generate_story(topic, api_key):
    """Agent 3: Generate a short story related to the given topic"""
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative fiction writer. Create a short, engaging story related to the given topic. Keep it under 500 words with interesting characters and a clear beginning, middle, and end."},
                {"role": "user", "content": f"Write a short story related to: {topic}"}
            ],
            temperature=0.8,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating story: {str(e)}"

def run_agents():
    """Run all three agents in parallel"""
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

# Display "Processing..." message if agents are running
if st.session_state.processing:
    st.info("Processing your request... This may take a moment.")
    run_agents()

# Display results in tabs
if st.session_state.blog_article or st.session_state.social_media_posts or st.session_state.story:
    tab1, tab2, tab3 = st.tabs(["Blog Article", "Social Media Posts", "Short Story"])
    
    with tab1:
        st.markdown("### Blog Article")
        st.markdown(st.session_state.blog_article)
        if st.session_state.blog_article:
            st.download_button(
                label="Download Blog Article",
                data=st.session_state.blog_article,
                file_name="blog_article.md",
                mime="text/markdown"
            )
    
    with tab2:
        st.markdown("### Social Media Posts")
        st.markdown(st.session_state.social_media_posts)
        if st.session_state.social_media_posts:
            st.download_button(
                label="Download Social Media Posts",
                data=st.session_state.social_media_posts,
                file_name="social_media_posts.md",
                mime="text/markdown"
            )
    
    with tab3:
        st.markdown("### Short Story")
        st.markdown(st.session_state.story)
        if st.session_state.story:
            st.download_button(
                label="Download Short Story",
                data=st.session_state.story,
                file_name="short_story.md",
                mime="text/markdown"
            )

# Add footer with instructions
st.markdown("---")
st.markdown("""
### How to use this app
1. Enter your OpenAI API key in the field above
2. Type your topic or query in the text area
3. Click "Generate Content" to activate all three AI agents
4. View and download the results in the tabs above
""")
