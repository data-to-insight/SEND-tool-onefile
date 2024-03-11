import js
import pandas as pd
from pyodide.http import pyfetch

# 1. fetching CSV from and write it to memory
response = await pyfetch("https://raw.githubusercontent.com/amirtds/kaggle-netflix-tv-shows-and-movies/main/titles.csv")
if response.status == 200:
    with open("titles.csv", "wb") as f:
        f.write(await response.bytes())

# 2. load the csv file
all_titles = pd.read_csv("titles.csv")

# 3. sanitize the data
# drop unnecessary columns
all_titles = all_titles.drop(
    columns=[
        "age_certification",
        "seasons",
        "imdb_id",
    ]
)
# drop rows with null values for important columns
sanitized_titles = all_titles.dropna(
    subset=[
        "id",
        "title",
        "release_year",
        "genres",
        "production_countries",
        "imdb_score",
        "imdb_votes",
        "tmdb_score",
        "tmdb_popularity",
    ]
)
# Convert the DataFrame to a JSON object. ('orient="records"' returns a list of objects)
titles_list = sanitized_titles.head(10).to_json(orient="records")

# 4. set titles to first 10 titles to the state
js.window.appComponent.state.titles = titles_list
js.window.appComponent.render()
