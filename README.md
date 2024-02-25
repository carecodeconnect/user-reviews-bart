# App Store Review Analysis 📊

This Streamlit app provides insightful analysis of App Store reviews for any given app. By inputting the App Store URL, users can explore trends, sentiments, and summaries of reviews within a specified date range.

## Features 🚀

- **App Store URL Input**: Enter the URL of the app you want to analyze. 📱
- **Date Range Selection**: Choose the start and end dates for the review analysis. 📅
- **Review Analysis**: Summarize positive and negative reviews, generate word clouds, and visualize rating distributions. 📈
- **Summarization**: Uses `sshleifer/distilbart-cnn-12-6` model to provide concise summaries of review sentiments. 📝

## How to Use 🛠️

1. Visit the app at [App Store Review Analysis](https://user-reviews-bart.streamlit.app/).
2. Input the App Store URL of the app you're interested in analyzing.
3. Select the date range for the reviews you want to analyze.
4. Click "Analyze reviews" to fetch and analyze the reviews.
5. Explore the generated summaries, word clouds, and rating distributions.

## Installation and Local Setup 🖥️

To run this app locally, you'll need Python and Streamlit installed. Clone the repository, install dependencies, and start the app:

```bash
git clone https://github.com/carecodeconnect/user-reviews-bart.git
cd user-reviews-bart
pip install -r requirements.txt
streamlit run app.py
```

## Collaboration

Special thanks to @josh-nowak for contributions to the development and enhancement of this app.

## License 

This project is licensed under the MIT License