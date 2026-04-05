# 🎬 Movie Recommendation System — Full Documentation

A beginner-friendly explanation of how this project works, what tools were used, and why.

---

## What Does This App Do?

This app connects to a **real movie database (TMDB)** and fetches 100 popular movies automatically.
You pick a movie you like, click **Recommend**, and it shows you **15 similar movies** with their posters — based on matching genres.

For example: if you pick **"Avatar"**, it will recommend other Action or Sci-Fi movies — because they share similar genres.

---

## How to Run the App

You only need to run **one file** — the setup script does everything for you:

### On Windows:
Double-click `setup.bat` or run it in your terminal:

```bash
setup.bat
```

It will automatically:
1. Install all required libraries
2. Ask you to paste your TMDB API key and save it
3. Launch the app in your browser

---

## What is a TMDB API Key?

TMDB (The Movie Database) is a free website that provides movie data.
To use it, you need a free API key (like a password that lets your app talk to their database).

**How to get one:**
1. Go to https://www.themoviedb.org/settings/api
2. Sign up for a free account
3. Request an API key — it's approved instantly
4. Paste it when `setup.bat` asks for it

---

## Tools & Libraries Used

### 1. `streamlit`
**What it is:** A tool that turns a Python script into a website/app — no web design knowledge needed.

**Why we used it:** Gives us a real interactive webpage with dropdowns, buttons, images, and styled text — all written in Python.

---

### 2. `pandas`
**What it is:** A tool for working with tables of data (like Excel, but in Python).

**Why we used it:** The movie data fetched from TMDB is stored as a table. Pandas makes it easy to look up rows, filter data, and access specific columns.

---

### 3. `scikit-learn` (sklearn)
**What it is:** A machine learning library. We use two specific tools from it:

- **`CountVectorizer`** — Converts text (like genre names) into numbers so a computer can understand and compare them.
- **`cosine_similarity`** — Measures how "similar" two movies are based on those numbers.

**Why we used it:** Computers can't directly compare words like "Action" and "Sci-Fi". We turn them into numbers first, then measure how close those numbers are to each other.

---

### 4. `requests`
**What it is:** A tool for making web requests — like fetching data from a website or API.

**Why we used it:** We use it to call the TMDB API and download the list of popular movies, their genres, and poster images.

---

### 5. `python-dotenv`
**What it is:** A tool that reads secret values (like API keys) from a `.env` file.

**Why we used it:** Instead of writing your API key directly in the code (which is unsafe), we store it in a separate `.env` file. This keeps your key private and out of your code.

---

## How the Code Works — Step by Step

### Step 1: Loading the API Key Safely

```python
load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
```

`load_dotenv()` reads the `.env` file and loads your API key into the app.
`os.getenv(...)` retrieves it by name. This way your key never appears in the code itself.

---

### Step 2: Fetching Real Movies from TMDB

```python
@st.cache_data
def fetch_movies():
    for page in range(1, 6):
        res = requests.get(f"{BASE_URL}/movie/popular?api_key={API_KEY}&page={page}")
        ...
```

This function calls the TMDB API 5 times (pages 1–5), getting 20 movies per page = **100 real popular movies**.

`@st.cache_data` means the app only fetches movies **once** — it remembers the result so it doesn't re-download every time you click something.

Each movie gives us:
- Title
- Genre(s)
- Poster image URL
- Rating (e.g. 7.8 / 10)
- Description (overview)
- Release year

---

### Step 3: Converting Genres into Numbers

```python
cv = CountVectorizer()
matrix = cv.fit_transform(movies["genre"])
```

`CountVectorizer` reads all the genre words across all movies and builds a vocabulary.
Then it converts each movie's genre into a row of numbers.

**Example (simplified):**

| Movie    | action | sci-fi | romance | drama |
|----------|--------|--------|---------|-------|
| Avatar   | 1      | 1      | 0       | 0     |
| Titanic  | 0      | 0      | 1       | 1     |
| Iron Man | 1      | 1      | 0       | 0     |

Now the computer can "see" that Avatar and Iron Man are very similar (both have action + sci-fi).

---

### Step 4: Measuring Similarity

```python
similarity = cosine_similarity(matrix)
```

Compares every movie against every other movie and gives a score between **0 and 1**:
- **1.0** = identical genres
- **0.0** = completely different genres

---

### Step 5: The Recommendation Function

```python
def recommend(movie_name):
    index = movies[movies["title"] == movie_name].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])[1:16]
    return [(movies.iloc[i], round(score * 100)) for i, score in distances]
```

1. Find the selected movie's row number in the table
2. Get its similarity scores against all other movies
3. Sort from highest to lowest
4. Skip the first result (the movie itself — always 100% similar to itself)
5. Return the next **15** most similar movies along with their match percentage

---

### Step 6: Dark Theme

The app uses a Netflix-style dark theme defined in `.streamlit/config.toml`:

```toml
[theme]
base = "dark"
primaryColor = "#E50914"
backgroundColor = "#141414"
secondaryBackgroundColor = "#1c1c1c"
textColor = "#FFFFFF"
```

This gives the app a black background with red accents — no extra code needed in `main.py`.

---

### Step 7: Sidebar — Genre Filter & Surprise Me

```python
selected_genre = st.sidebar.selectbox("Filter by Genre", ["All"] + all_genres)

if st.sidebar.button("🎲 Surprise Me"):
    st.session_state["surprise"] = filtered["title"].sample(1).values[0]
    st.rerun()
```

- **Genre Filter** — a dropdown in the sidebar that narrows the movie list to a specific genre before you pick one.
- **Surprise Me** — randomly picks a movie for you and auto-selects it in the dropdown. Great if you don't know what to watch.

---

### Step 8: Selected Movie Display

```python
col1, col2 = st.columns([1, 3])
with col1:
    st.image(selected["poster"], width=200)
with col2:
    st.subheader(f"{selected['title']} ({selected['year']})")
    st.caption(f"🎭 Genre: {selected['genre']}")
    st.caption(f"⭐ Rating: {selected['rating']} / 10")
    st.write(selected["overview"])
```

When you pick a movie, the app immediately shows:
- Poster image on the left
- Title with release year, genre, rating, and a short description on the right

---

### Step 9: Recommendation Cards with Color-Coded Match Badge

```python
match_color = "#00c853" if score >= 80 else "#ff9800" if score >= 50 else "#E50914"
```

The 15 recommended movies are displayed in **3 rows of 5**, each as a card showing:
- Poster
- Title + release year (on one line)
- Genre
- ⭐ Rating
- 🎯 Match % — color changes based on how close the match is:

| Color | Meaning |
|---|---|
| 🟢 Green | 80% or above — great match |
| 🟠 Orange | 50% to 79% — decent match |
| 🔴 Red | Below 50% — low match |

---

## Full Flow Summary

```
setup.bat runs
        ↓
Installs libraries + saves API key to .env
        ↓
App starts with Netflix-style dark theme
        ↓
Fetches 100 movies from TMDB (titles, genres, posters, ratings, descriptions, years)
        ↓
User filters by genre (optional) or clicks Surprise Me
        ↓
User picks a movie → app shows poster, genre, rating, and description
        ↓
User clicks Recommend
        ↓
App finds the 15 most similar movies by genre
        ↓
Displays them in 3 rows of 5 with posters, ratings, and color-coded match badges
```

---

## Project Structure

```
movie_recomendation/
│
├── main.py                  ← The entire app
├── setup.bat                ← Run this to install everything and launch the app
├── .env                     ← Your TMDB API key (created automatically by setup.bat)
├── .streamlit/
│   └── config.toml          ← Dark theme configuration
└── README.md                ← This documentation file
```

---

## Limitations & Possible Improvements

| Limitation | Possible Fix |
|---|---|
| Only fetches popular movies | Add search by any movie title using TMDB search API |
| Only uses genre for matching | Add cast, director, and description for better results |
| 100 movie limit | Increase pages fetched or add pagination |
| No trailer preview | Embed YouTube trailer using TMDB video endpoint |

---

## Key Concepts Glossary

| Term | Plain English Meaning |
|---|---|
| API | A way for two apps to talk to each other over the internet |
| API Key | A secret password that lets your app use another service |
| .env file | A hidden file that stores secret values like API keys |
| DataFrame | A table of data with rows and columns, like a spreadsheet |
| CountVectorizer | Converts words into numbers a computer can compare |
| Cosine Similarity | A score (0–1) measuring how alike two things are |
| Cache | Saved results so the app doesn't repeat the same work |
| Streamlit | A tool to build web apps using only Python |
| Session State | A way for Streamlit to remember values between button clicks |
