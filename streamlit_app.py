import streamlit as st

# Initialize session state variables at the top level

if 'key' not in st.session_state:
    st.session_state.key = 'value'

if "clicked" not in st.session_state:
    st.session_state.clicked = False

if "reviews" not in st.session_state:
    st.session_state.reviews = None

from streamlit_lottie import st_lottie
import datetime
import pandas as pd
from transformers import pipeline
from src.utils import app_store_reviews, generate_wordcloud, create_rating_distribution_plot, app_data_from_url
import requests

st.title("Apple Store Review Summariser :iphone:")

# animated stars
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_stars = load_lottieurl(
    "https://lottie.host/05701045-44c3-4741-a484-dbcc7f923cf7/C8quegn0oG.json"
)

st_lottie(lottie_stars, height=300, key="stars_animation")

# include text to explain the app
st.markdown(
    """
This Streamlit app provides insightful analysis of App Store reviews for any given app. 
By inputting the App Store URL, users can summaries of positive and negative reviews within a specified date range.
    """
)

st.markdown(
    """
    1. **Enter the URL of your app** in the input field above. To find the URL, open the app in the App Store and copy the URL from the address bar. For example, to analyze the reviews for the app 'Slack', you would copy the URL [https://apps.apple.com/de/app/slack/id618783545](https://apps.apple.com/de/app/slack/id618783545).
    2. **Select the date range** for the reviews you want to analyze.
    3. Click the **'Analyze reviews'** button to start the analysis.
    """,
    unsafe_allow_html=True
)

app_store_url = st.text_input("**Your App Store URL** 📱", placeholder="https://apps.apple.com/...")

today = datetime.datetime.now()
default_start_date = datetime.date(today.year - 1, 1, 1)

date_range = st.date_input(
    "Date range",
    value=(default_start_date, today),
    max_value=today,
    format="DD.MM.YYYY",
)

start_date = date_range[0].strftime("%Y-%m-%d")
end_date = today.strftime("%Y-%m-%d")  # Default to today if only one date is picked
if len(date_range) > 1:
    end_date = date_range[1].strftime("%Y-%m-%d")

def get_reviews():
    reviews = app_store_reviews(url=app_store_url, start_date=start_date, end_date=end_date)
    return reviews

def click_button():
    st.session_state.clicked = True

st.button("Analyze reviews", on_click=click_button)

@st.cache_resource
def summarize_reviews(reviews_text, model_name="sshleifer/distilbart-cnn-12-6"):
    summarizer = pipeline("summarization", model=model_name)
    reviews_text = reviews_text[:1024]  # Ensure the text does not exceed 1024 characters
    try:
        summary = summarizer(reviews_text, max_length=130, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"Error summarizing reviews: {str(e)}"

if st.session_state.clicked:
    with st.spinner("Loading reviews..."):
        if start_date and end_date and start_date < end_date:
            st.session_state.reviews = get_reviews()  # Store reviews in session state

    if st.session_state.reviews is not None:
        # Show success message and analysis only if reviews are loaded
        n_reviews_found = len(st.session_state.reviews)
        st.toast(f"🎉 Reviews successfully loaded! Found {n_reviews_found} reviews.")

                # Continue analysis only if reviews are loaded
        country, app_name, app_id = app_data_from_url(app_store_url)
        p_positive_reviews = len(
            st.session_state.reviews[st.session_state.reviews["rating"] > 3]
        ) / len(st.session_state.reviews) if len(st.session_state.reviews) > 0 else 0
        
        # Generate an introductory text for the analysis
        intro_text = f'The App **"{app_name.capitalize()}"** received **{n_reviews_found} App Store reviews** in the \
selected time frame. About **{round(p_positive_reviews * 100)}% of these \
reviews were positive**, with a rating of 4 or 5 stars.'

        st.write(intro_text)

        # Summarize positive reviews
        st.subheader("🤩 Highlights")
        if n_reviews_found > 0:
            positive_reviews = " ".join(
                st.session_state.reviews[st.session_state.reviews["rating"] > 3]["review"].tolist()
            )
            positive_summary = summarize_reviews(positive_reviews)
            st.write("The following points were highlighted by satisfied users:")
            st.write(positive_summary)
        else:
            st.write("No positive reviews to summarize.")

        # Summarize negative reviews
        st.subheader("🤔 Room for improvement")
        if n_reviews_found > 0:
            negative_reviews = " ".join(
                st.session_state.reviews[st.session_state.reviews["rating"] < 4]["review"].tolist()
            )
            negative_summary = summarize_reviews(negative_reviews)
            st.write("The following issues were raised by dissatisfied users:")
            st.write(negative_summary)
        else:
            st.write("No negative reviews to summarize.")
