import json
import os
import pickle
import sys

import pandas as pd
import streamlit as st
from catboost import CatBoostRegressor
from google.cloud import aiplatform
from google.oauth2 import service_account

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from src.helper import (
    apply_pca,
    preprocess,
    suggest_hashtags,
    suggest_title_description,
    vectorize,
)

with open(os.environ["GOOGLE_APPLICATION_CREDENTIALS"], "r") as f:
    json_creds = json.load(f)

project_id = json_creds["project_id"]
credentials = service_account.Credentials.from_service_account_info(json_creds)
aiplatform.init(project=project_id, credentials=credentials)




def main():

    st.title("TrendCraft")
    st.subheader(f"The Ultimate Companion for Content Creators! 🚀")
    st.image("images/graphic.jpeg", width=500)
    # Input fields
    title = st.text_input("Title")
    description = st.text_area("Description")
    published_at = st.date_input("Published Date")
    trending_date = st.date_input("Trending Date")
    channel_title = st.text_input("Channel Title")
    hashtags = st.text_input("Hashtags")

    # Category dropdown
    category_options = [
        "Film & Animation",
        "Autos & Vehicles",
        "Music",
        "Pets & Animals",
        "Sports",
        "Short Movies",
        "Travel & Events",
        "Gaming",
        "Videoblogging",
        "People & Blogs",
        "Comedy",
        "Entertainment",
        "News & Politics",
        "Howto & Style",
        "Education",
        "Science & Technology",
        "Nonprofits & Activism",
        "Movies",
        "Anime/Animation",
        "Action/Adventure",
        "Classics",
        "Comedy",
        "Documentary",
        "Drama",
        "Family",
        "Foreign",
        "Horror",
        "Sci-Fi/Fantasy",
        "Thriller",
        "Shorts",
        "Shows",
        "Trailers",
    ]
    category = st.selectbox("Category", category_options)
    category_dict = {
        category: index + 1 for index, category in enumerate(category_options)
    }
    categoryId = category_dict[category]

    # Duration input fields
    st.subheader("Duration")
    hours = st.number_input("Hours", min_value=0)
    minutes = st.number_input("Minutes", min_value=0, max_value=59)
    seconds = st.number_input("Seconds", min_value=0, max_value=59)

    # Button to analyze video
    if st.button("Analyse Video"):
        # Store data in DataFrame
        data = {
            "videoId": [0],
            "publishedAt": [published_at],
            "channelId": [0],
            "title": [title],
            "description": [description],
            "channelTitle": [channel_title],
            "categoryId": [categoryId],
            "tags": [hashtags],
            "duration": [f"{hours}:{minutes}:{seconds}"],
            "viewCount": [0],
            "likeCount": [0],
            "target": [0],
            "trending_date": [trending_date],
        }
        data = pd.DataFrame(data)
        data = preprocess(data)

        test_text = data.text.tolist()
        data.drop(
            [
                "text",
            ],
            axis=1,
            inplace=True,
        )

        test_vectors = vectorize(test_text)
        test_vectors = apply_pca(test_vectors)
        data = pd.concat([data, test_vectors], axis=1)
        data.dropna(inplace=True)

        with open("build/models/cat_cols.pkl", "rb") as f:
            categorical_cols = pickle.load(f)

        y_train = data["target"]
        x_train = data.drop(["target"], axis=1)

        model = CatBoostRegressor(cat_features=categorical_cols)
        model.load_model("build/models/catboost_model")
        y_pred = model.predict(x_train)

        target = round(y_pred[0], 2)

        st.subheader(
            f"Hurray!! Your video is likely to get: {target * 100} likes per 100 views."
        )
        st.subheader(f"Try the below suggestions to make your video Viral!! 🔥")

        st.markdown("<hr>", unsafe_allow_html=True)
        new_title, new_description = suggest_title_description(title, description)
        st.subheader(f"Suggested title:")
        st.write(new_title)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader(f"Suggested description:")
        st.write(new_description)
        st.markdown("<hr>", unsafe_allow_html=True)
        hashtags = suggest_hashtags(title, description)
        st.subheader(f"Suggested hashtags:")
        st.write(hashtags)


if __name__ == "__main__":
    main()
