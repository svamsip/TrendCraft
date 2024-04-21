import os
import pickle
import re

import pandas as pd
from catboost import CatBoostRegressor
from google.cloud import aiplatform
from google.oauth2 import service_account
from langchain_google_vertexai import VertexAI
from sklearn.metrics import mean_absolute_error

GCP_PROJECT_NAME = os.environ["GCP_PROJECT_NAME"]


def read_data(folder_path):

    csv_files = [file for file in os.listdir(folder_path) if file.endswith(".csv")]
    dfs = []

    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        dfs.append(df)

    data = pd.concat(dfs, ignore_index=True)
    return data


def duration_to_seconds(time_str):
    mapping = {"H": 3600, "M": 60, "S": 1}

    try:
        total_seconds = 0
        time_str = time_str[2:]
        d = ""
        for c in time_str:
            if c.isalpha():
                total_seconds += int(d) * mapping[c]
                d = ""
            else:
                d += c
    except:
        return None

    return total_seconds


def vectorize(text):
    with open("build/models/vectorizer_model.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    vectors = vectorizer.transform(text).toarray()
    return vectors


def apply_pca(vectors):
    with open("build/models/pca_model.pkl", "rb") as f:
        pca = pickle.load(f)

    train_projection = pca.transform(vectors)

    pca_vectors = pd.DataFrame(train_projection)
    pca_vectors.columns = [f"cat_{i}" for i in range(pca_vectors.shape[1])]
    return pca_vectors


def preprocess(data):
    data.drop_duplicates(subset=["videoId"], inplace=True)
    data["duration"] = data["duration"].apply(duration_to_seconds)
    data["description"] = (
        data["description"].fillna("").apply(lambda x: re.sub(r"http\S+", " ", x))
    )
    data["tags"] = data["tags"].fillna("")
    data["tags"] = (
        data["tags"].str.replace("[", "").str.replace("]", "").str.replace("'", "")
    )

    data.dropna(inplace=True)
    data["text"] = (
        data["title"]
        + " "
        + data["description"]
        + " "
        + data["channelTitle"]
        + " "
        + data["tags"]
    )

    data["num_words"] = data["text"].apply(lambda x: len(x.split()))
    data["num_characters"] = data["text"].apply(lambda x: len(x))

    data["publishedAt"] = pd.to_datetime(data["publishedAt"])
    data["trending_date"] = pd.to_datetime(data["trending_date"])

    for col in ["publishedAt", "trending_date"]:
        data[col] = pd.to_datetime(data[col], utc=True)
        data.loc[:, col + "_year"] = (data[col].dt.year).astype("category")
        data.loc[:, col + "_weekofyear"] = (data[col].dt.isocalendar().week).astype(
            "category"
        )
        data.loc[:, col + "_month"] = (data[col].dt.month).astype("category")
        data.loc[:, col + "_dayofweek"] = (data[col].dt.dayofweek).astype("category")
        data.loc[:, col + "_weekend"] = (
            (data[col].dt.weekday >= 5).astype(int)
        ).astype("category")

    data["video_age"] = (data["trending_date"] - data["publishedAt"]).dt.days.astype(
        "int"
    )

    data["Friday_Trending"] = [1 if a == 4 else 0 for a in data.trending_date_dayofweek]
    data["Thursday_Trending"] = [
        1 if a == 3 else 0 for a in data.trending_date_dayofweek
    ]
    data["Friday_Published"] = [1 if a == 4 else 0 for a in data.publishedAt_dayofweek]
    data["Sunday_Published"] = [1 if a == 6 else 0 for a in data.publishedAt_dayofweek]

    for col in [
        "categoryId",
        "Friday_Trending",
        "Thursday_Trending",
        "Friday_Published",
        "Sunday_Published",
    ]:
        data[col] = data[col].astype("category")

    data.drop(
        [
            "videoId",
            "channelId",
            "viewCount",
            "likeCount",
            "description",
            "title",
            "tags",
            "channelTitle",
            "publishedAt",
            "trending_date",
        ],
        axis=1,
        inplace=True,
    )

    return data


# def encode_data(data):
#     with open("build/models/encoder_dict.pkl", "rb") as f:
#         encoder_dict = pickle.load(f)

#     encoding_cols = list(data.select_dtypes("object").columns)

#     for col in encoding_cols:
#         le = encoder_dict[col]
#         data[col] = le.transform(data[col])


def predict(data):
    y_test = data["target"]
    x_test = data.drop(["target"], axis=1)
    model = CatBoostRegressor()
    model.load_model("build/models/catboost_model")
    y_pred = model.predict(x_test)
    score = mean_absolute_error(y_test, y_pred)
    return score


def suggest_title_description(title, description):

    description_prompt = f"""
    You are tasked with rewriting the description of a YouTube video to make it more catchy and trendy, enticing viewers to click on the video. 
    However, you must maintain the original content of the description without changing any information. Your goal is to repackage the description 
    in a way that captures attention, generates curiosity, and encourages engagement. Focus on using compelling language, captivating phrases, and 
    an engaging tone to make the description more appealing to a wider audience.

    Remember, your objective is not to alter the content of the description but to enhance its presentation to attract more viewers. Keep the original 
    message intact while infusing it with energy, excitement, and allure to entice users to click on the video.

    Remove any url links and promotional messages.

    Return only the description. The description should not be preceded or followed by any filler sentences.

    Given below are the title and description of the video. Use both of them to generate the new description.

    Video title: {title}

    Description: {description}
    """

    title_prompt = f"""
    You are tasked with rewriting the title of a YouTube video to make it more catchy and trendy, enticing viewers to click on the video. 
    However, you must maintain the original content of the title without changing any information. Your goal is to repackage the title 
    in a way that captures attention, generates curiosity, and encourages engagement. Focus on using compelling language, captivating phrases, and 
    an engaging tone to make the title more appealing to a wider audience.

    Remember, your objective is not to alter the content of the title but to enhance its presentation to attract more viewers. Keep the original 
    message intact while infusing it with energy, excitement, and allure to entice users to click on the video.

    Return only the title. The title should not be preceded or followed by any filler sentences.

    Given below are the title and description of the video. Use both of them to generate the new title.

    Video title: {title}

    Description: {description}
    """

    model = VertexAI(model_name="gemini-pro", project=GCP_PROJECT_NAME)
    new_description = model.invoke(description_prompt)
    new_title = model.invoke(title_prompt)
    return new_title, new_description


def suggest_hashtags(title, description):

    hashtags_prompt = f"""
    Suggest relevant hashtags for a YouTube video based on the provided description and title. 
    The hashtags should be concise, descriptive, and directly related to the content of the video. 
    Ensure that the hashtags are appropriate for the target audience and aligned with the video's topic. 
    Limit the number of hashtags to a maximum of 15.

    Return only the hashtags. The hashtags should not be preceded or followed by any filler sentences.

    Given below are the title and description of the video. Use both of them to generate the hashtags.

    Video title: {title}

    Description: {description}
    """

    model = VertexAI(model_name="gemini-pro", project=GCP_PROJECT_NAME)
    hashtags = model.invoke(hashtags_prompt)
    return hashtags
