import json
import os
import pickle
import sys

import pandas as pd
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))


def main():
    st.title("Welcome to TrendCraft")
    st.header("The Ultimate Companion for Content Creators! 🚀")

    st.image("images/graphic.jpeg", width=500)

    st.write(
        """
    TrendCraft is a tool designed to help content creators optimize their videos for maximum engagement and virality on platforms like YouTube.
    
    Simply input information about your video, such as its title, description, category, duration, and hashtags, and TrendCraft will provide you with valuable insights and suggestions to enhance your video's performance.
    
    """
    )

    st.page_link(
        "pages/tool.py",
        label="Try the tool!!!",
        use_container_width=True,
        icon="\U0001F3A5",
    )

    st.header("How it Works", divider=True)
    st.write("Imagine you are Marques Brownlee.")
    st.write(
        "You just shot a video about Vision Pro. Now its time to publish it and cash in"
    )

    st.subheader("Step 1. Enter the title and description of your potential video")
    st.image("images/title_description.jpeg", use_column_width=True)
    st.subheader(
        "Step 2. Enter the date you will publish the video and the date for which you want to measure the engagement of your video"
    )
    st.image("images/date.jpeg", use_column_width=True)
    st.subheader(
        "Step 3. Enter channel title, potential hashtags and select category from the available options"
    )
    st.image("images/title_tags_category.jpeg", use_column_width=True)
    st.subheader("Step 4. Enter the duration of your video")
    st.image("images/duration.jpeg", use_column_width=True)
    st.subheader("Step 5. Click on Analyse Video")
    st.image("images/result.jpeg", use_column_width=True)
    st.image("images/suggested_title_desc.jpeg", use_column_width=True)
    st.image("images/suggested_tags.jpeg", use_column_width=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    st.header("Sounds too magical? Here's how it works under the hood")
    st.write(
        """
             We use a machine learning model that analyses the title, description and other metadata about your potential video and predicts the 
             like to view ratio on a given date after the publishing date.
             The model is trained regularly on a massive dataset of trending youtube videos and hence captures the dynamics of youtube's recommendation algorithm
             """
    )

    st.header("How do we suggest the title, description and hashtags?")
    st.write(
        """
             We find trending videos from our dataset that have high like-to-view ratio and are similar to your video in terms of description, title, category and duration. 
             And based on these videos, we use GenAI models to rephrase your video configurations.
             """
    )


if __name__ == "__main__":
    main()
