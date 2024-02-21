# Initialize session state for the "analyze" button at the top level
if "clicked" not in st.session_state:
    st.session_state.clicked = False
    
import streamlit as st
from src.utils import (
    app_store_reviews,
    generate_wordcloud,
    create_rating_distribution_plot,
    app_data_from_url,
)
import datetime
import pandas as pd
import time
from transformers import pipeline

st.title("App Store Review Analysis")

app_store_url = st.text_input(
    "**Your App Store URL** 📱",
    placeholder="https://apps.apple.com/...",
)

today = datetime.datetime.now()
default_start_date = datetime.date(today.year - 1, 1, 1)

date_range = st.date_input(
    "Date range",
    value=(default_start_date, today),
    max_value=today,
    format="DD.MM.YYYY",
)

start_date = date_range[0].strftime("%Y-%m-%d")
if len(date_range) > 1:
    end_date = date_range[1].strftime("%Y-%m-%d")

def get_reviews():
    reviews = app_store_reviews(
        url=app_store_url, start_date=start_date, end_date=end_date
    )
    return reviews

# Initialize session state for reviews if it doesn't exist
if "reviews" not in st.session_state:
    st.session_state.reviews = None

def click_button():
    if st.session_state.clicked:
        pass
    st.session_state.clicked = True

st.button("Analyze reviews", type="primary", on_click=click_button)

@st.cache_resource
def summarize_reviews(reviews_text, model_name="sshleifer/distilbart-cnn-12-6"):
    summarizer = pipeline("summarization", model=model_name)
    # Ensure the reviews text does not exceed 1024 characters
    reviews_text = reviews_text[:1024]
    try:
        summary = summarizer(reviews_text, max_length=130, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        # Handle any other errors
        return f"Error summarizing reviews: {str(e)}"

if st.session_state.clicked:
    with st.spinner("Loading reviews..."):
        if start_date and end_date:
            if start_date < end_date:
                # Store reviews in session state
                st.session_state.reviews = get_reviews()

    # Show a success message
    n_reviews_found = len(st.session_state.reviews)
    st.toast(f"🎉 Reviews successfully loaded!")

    # Generate an introductory text for the analysis
    country, app_name, app_id = app_data_from_url(app_store_url)
    p_positive_reviews = len(
        st.session_state.reviews[st.session_state.reviews["rating"] > 3]
    ) / len(st.session_state.reviews)
    intro_text = f'The App **"{app_name.capitalize()}"** received **{n_reviews_found} App Store reviews** in the \
        selected time frame. About **{round(p_positive_reviews*100)}% of these \
            reviews were positive**, with a rating 4 or 5 stars.'

    st.write(intro_text)

    # Summarize positive reviews
    st.subheader("🤩 Highlights")
    positive_reviews = " ".join(st.session_state.reviews[st.session_state.reviews["rating"] > 3]["review"].tolist())
    positive_summary = summarize_reviews(positive_reviews)
    st.write("The following points were highlighted by satisfied users:")
    st.write(positive_summary)

    # Summarize negative reviews
    st.subheader("🤔 Room for improvement")
    negative_reviews = " ".join(st.session_state.reviews[st.session_state.reviews["rating"] < 4]["review"].tolist())
    negative_summary = summarize_reviews(negative_reviews)
    st.write("The following issues were raised by dissatisfied users:")
    st.write(negative_summary)

