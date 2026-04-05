import os
import random
import requests
import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_URL = "https://image.tmdb.org/t/p/w300"

@st.cache_data
def fetch_genre_map():
    res = requests.get(f"{BASE_URL}/genre/movie/list?api_key={API_KEY}&language=en-US")
    return {g["id"]: g["name"] for g in res.json().get("genres", [])}

@st.cache_data
def fetch_movies():
    genre_map = fetch_genre_map()
    titles, genres, posters, ids, ratings, overviews, years = [], [], [], [], [], [], []

    for page in range(1, 6):
        res = requests.get(f"{BASE_URL}/movie/popular?api_key={API_KEY}&language=en-US&page={page}")
        for movie in res.json().get("results", []):
            titles.append(movie["title"])
            genres.append(" ".join([genre_map.get(g, "") for g in movie["genre_ids"]]))
            posters.append(IMAGE_URL + movie["poster_path"] if movie.get("poster_path") else None)
            ids.append(movie["id"])
            ratings.append(round(movie.get("vote_average", 0), 1))
            overviews.append(movie.get("overview", "No description available."))
            years.append(movie.get("release_date", "")[:4])

    return pd.DataFrame({
        "title": titles, "genre": genres, "poster": posters,
        "id": ids, "rating": ratings, "overview": overviews, "year": years
    })

movies = fetch_movies()

cv = CountVectorizer()
matrix = cv.fit_transform(movies["genre"])
similarity = cosine_similarity(matrix)

def recommend(movie_name):
    index = movies[movies["title"] == movie_name].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])[1:16]
    return [(movies.iloc[i], round(score * 100)) for i, score in distances]

# ── Page config ──────────────────────────────────────────────
st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")
st.title("🎬 Movie Recommendation System")
st.markdown("---")

# ── Sidebar: Genre Filter + Surprise Me ──────────────────────
st.sidebar.header("🎭 Filter Options")
all_genres = sorted(set(" ".join(movies["genre"]).split()))
selected_genre = st.sidebar.selectbox("Filter by Genre", ["All"] + all_genres)

if st.sidebar.button("🎲 Surprise Me"):
    filtered = movies if selected_genre == "All" else movies[movies["genre"].str.contains(selected_genre)]
    st.session_state["surprise"] = filtered["title"].sample(1).values[0]
    st.rerun()

filtered_movies = movies if selected_genre == "All" else movies[movies["genre"].str.contains(selected_genre)]

# ── Movie Search ──────────────────────────────────────────────
default_movie = st.session_state.get("surprise", filtered_movies["title"].values[0])
if default_movie not in filtered_movies["title"].values:
    default_movie = filtered_movies["title"].values[0]

movie_name = st.selectbox(
    "🔍 Search or select a movie",
    filtered_movies["title"].values,
    index=list(filtered_movies["title"].values).index(default_movie)
)

# ── Selected Movie Card ───────────────────────────────────────
selected = movies[movies["title"] == movie_name].iloc[0]
col1, col2 = st.columns([1, 3])
with col1:
    if selected["poster"]:
        st.image(selected["poster"], width=200)
with col2:
    st.subheader(f"{selected['title']} ({selected['year']})")
    st.caption(f"🎭 Genre: {selected['genre']}")
    st.caption(f"⭐ Rating: {selected['rating']} / 10")
    st.write(selected["overview"])

st.markdown("---")

# ── Recommendations ───────────────────────────────────────────
if st.button("🎬 Recommend"):
    recommendations = recommend(movie_name)
    st.subheader("Recommended Movies:")
    for row_start in range(0, 15, 5):
        cols = st.columns(5)
        for col, (movie, score) in zip(cols, recommendations[row_start:row_start+5]):
            with col:
                match_color = "#00c853" if score >= 80 else "#ff9800" if score >= 50 else "#E50914"
                st.markdown(f"""
                    <div style="text-align:left;">
                        <img src="{movie['poster']}" width="100%" style="border-radius:8px; display:block;">
                        <p style="font-weight:bold; margin:6px 0 2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{movie['title']} ({movie['year']})</p>
                        <p style="color:gray; font-size:12px; margin:0;">🎭 {movie['genre']}</p>
                        <p style="color:#f5c518; font-size:12px; margin:2px 0;">⭐ {movie['rating']} / 10</p>
                        <p style="color:{match_color}; font-size:12px; margin:2px 0;">🎯 {score}% Match</p>
                    </div>
                """, unsafe_allow_html=True)
