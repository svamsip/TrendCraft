"""
This script fetches, processes, and saves YouTube video data.

It fetches the most popular videos in the US for a given category, processes the data to extract relevant information,
and saves the data in a CSV file.

Functions:
    fetch_data(category): Fetches data for a given category from the YouTube API.
    process_data(data): Processes the fetched data to extract relevant information.
    save_data(rows): Saves the processed data in a CSV file.
    main(): Main function that calls the other functions and controls the flow of the script.
"""

import datetime

import numpy as np
import pandas as pd
import requests

# from tqdm import tqdm


def fetch_data(category):
    """
    Fetches data for a given category from the YouTube API.

    Args:
        category (int): The category ID to fetch data for.

    Returns:
        dict: The response from the YouTube API, or None if the request fails.
    """
    url = "https://youtube342.p.rapidapi.com/videos"
    querystring = {
        "part": "snippet,contentDetails,statistics",
        "chart": "mostPopular",
        "maxResults": "50",
        "regionCode": "US",
        "videoCategoryId": f"{category}",
    }
    headers = {
        "X-RapidAPI-Key": "40b85a42c8msh102e65cd306730bp1ee665jsncee38edae08d",
        "X-RapidAPI-Host": "youtube342.p.rapidapi.com",
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        print(f"Fetched data for categoryid = {category}")
        return response.json()
    except:
        print(f"Could not fetch data for categoryid = {category}")
        return None


def process_data(data):
    """
    Processes the fetched data to extract relevant information.

    Args:
        data (dict): The data fetched from the YouTube API.

    Returns:
        list: A list of rows, where each row is a list of video data.
    """
    rows = []
    # for video in tqdm(data["items"], total=len(data["items"])):
    for video in data["items"]:
        videoId = video.get("id")
        snippet = video.get("snippet", {})
        publishedAt = snippet.get("publishedAt")
        channelId = snippet.get("channelId")
        title = snippet.get("title")
        description = snippet.get("description")
        channelTitle = snippet.get("channelTitle")
        categoryId = snippet.get("categoryId")
        tags = snippet.get("tags")
        duration = video.get("contentDetails", {}).get("duration")
        statistics = video.get("statistics", {})
        viewCount = statistics.get("viewCount")
        likeCount = statistics.get("likeCount")
        if viewCount and likeCount:
            target = float(likeCount) / float(viewCount)
            trending_date = datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            row = [
                videoId,
                publishedAt,
                channelId,
                title,
                description,
                channelTitle,
                categoryId,
                tags,
                duration,
                viewCount,
                likeCount,
                target,
                trending_date,
            ]
            rows.append(row)
    return rows


def save_data(rows):
    """
    Saves the processed data in a CSV file.

    Args:
        rows (list): The processed data to save.
    """
    columns = [
        "videoId",
        "publishedAt",
        "channelId",
        "title",
        "description",
        "channelTitle",
        "categoryId",
        "tags",
        "duration",
        "viewCount",
        "likeCount",
        "target",
        "trending_date",
    ]
    training_data = pd.DataFrame(rows, columns=columns)
    date = datetime.datetime.now().strftime("%Y_%m_%d")
    training_data.to_csv(f"data/data_{date}.csv", index=False)
    print("Done. Data saved successfully")


def main():
    """
    Main function that calls the other functions and controls the flow of the script.
    """
    rows = []
    for category in range(1, 3, 1):
        data = fetch_data(category)
        if data is not None:
            rows.extend(process_data(data))
    save_data(rows)


if __name__ == "__main__":
    main()
