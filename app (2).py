import streamlit as st
import pickle
import requests
import time
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="CineMatch — Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== LOAD DATA ==================
movies     = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# ================== SESSION STATE ==================
if 'history' not in st.session_state:
    st.session_state.history = []

# ================== API SESSION ==================
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Accept"    : "application/json"
})
API_KEY = "a75517ffaf83bb183818ce664cdcee13"

# ================== NETFLIX-STYLE CSS ==================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0a0a0a;
    color: #f0f0f0;
}
.stApp { background-color: #0a0a0a; }

.hero-title {
    font-family: 'Bebas Neue', cursive;
    font-size: 62px;
    letter-spacing: 4px;
    background: linear-gradient(135deg, #E50914, #ff6b35);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0px;
}
.hero-sub {
    color: #888;
    font-size: 15px;
    letter-spacing: 2px;
    margin-top: -8px;
    margin-bottom: 24px;
}
.movie-title-label {
    text-align: center;
    font-size: 13px;
    font-weight: 600;
    margin-top: 8px;
    color: #e0e0e0;
    letter-spacing: 0.5px;
}
.similarity-bar-wrap {
    background: #222;
    border-radius: 20px;
    height: 6px;
    margin: 6px 4px 2px 4px;
    overflow: hidden;
}
.similarity-bar {
    height: 6px;
    border-radius: 20px;
    background: linear-gradient(90deg, #E50914, #ff6b35);
}
.similarity-text {
    text-align: center;
    font-size: 11px;
    color: #888;
    margin-bottom: 4px;
}
.chip-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-top: 6px;
    justify-content: center;
}
.chip {
    background: #2a2a2a;
    border: 1px solid #3a3a3a;
    border-radius: 20px;
    padding: 2px 9px;
    font-size: 10px;
    color: #aaa;
}
.stars       { color: #f5c518; font-size: 13px; }
.rating-text { color: #aaa; font-size: 11px; margin-left: 4px; }
.section-header {
    font-family: 'Bebas Neue', cursive;
    font-size: 22px;
    letter-spacing: 2px;
    color: #E50914;
    border-left: 4px solid #E50914;
    padding-left: 12px;
    margin: 24px 0 16px 0;
}
[data-testid="stSidebar"] {
    background: #111 !important;
    border-right: 1px solid #222;
}
[data-testid="stSidebar"] * { color: #ccc !important; }
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextInput"] > div > div > input {
    background-color: #1a1a1a !important;
    border: 1px solid #333 !important;
    color: white !important;
    border-radius: 10px !important;
}
div.stButton > button {
    background: linear-gradient(135deg, #E50914, #b20710) !important;
    color: white !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 32px !important;
    width: 100% !important;
    letter-spacing: 1px;
    transition: opacity 0.2s;
}
div.stButton > button:hover { opacity: 0.88; }
[data-testid="stExpander"] {
    background: #161616 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 10px !important;
}
::-webkit-scrollbar       { width: 5px; }
::-webkit-scrollbar-track { background: #111; }
::-webkit-scrollbar-thumb { background: #E50914; border-radius: 4px; }
hr { border-color: #2a2a2a !important; }
.trailer-embed {
    border-radius: 10px;
    overflow: hidden;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
#       FEATURE 1: FETCH POSTER
# ==========================================
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    for attempt in range(3):
        try:
            response = session.get(url, timeout=10)
            if response.status_code == 429:
                time.sleep(3)
                continue
            if response.status_code == 404:
                return "https://placehold.co/300x450/1a1a1a/555?text=Not+Found"
            if response.status_code != 200:
                return "https://placehold.co/300x450/1a1a1a/555?text=API+Error"
            data        = response.json()
            poster_path = data.get('poster_path')
            return (
                "https://image.tmdb.org/t/p/w500/" + poster_path
                if poster_path
                else "https://placehold.co/300x450/1a1a1a/555?text=No+Poster"
            )
        except Exception:
            time.sleep(1)
    return "https://placehold.co/300x450/1a1a1a/555?text=Connection+Error"


# ==========================================
#    FEATURE 2: FETCH MOVIE DETAILS
# ==========================================
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    try:
        response = session.get(url, timeout=8)
        if response.status_code != 200:
            return {}
        data = response.json()
        return {
            "rating"    : data.get("vote_average", 0),
            "votes"     : data.get("vote_count", 0),
            "release"   : data.get("release_date", "N/A"),
            "runtime"   : data.get("runtime", 0),
            "overview"  : data.get("overview", "No overview available."),
            "genres"    : [g['name'] for g in data.get("genres", [])],
            "tagline"   : data.get("tagline", ""),
            "popularity": data.get("popularity", 0),
        }
    except:
        return {}


# ==========================================
#   FEATURE 7: FETCH TRAILER — FIXED ✅
# ==========================================
def fetch_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}&language=en-US"
    try:
        response = session.get(url, timeout=8)
        if response.status_code == 200:
            data = response.json()
            # Priority 1: Official Trailer on YouTube
            for v in data.get('results', []):
                if v['type'] == 'Trailer' and v['site'] == 'YouTube':
                    return f"https://www.youtube.com/watch?v={v['key']}"
            # Priority 2: Any YouTube video
            for v in data.get('results', []):
                if v['site'] == 'YouTube':
                    return f"https://www.youtube.com/watch?v={v['key']}"
        # Priority 3: Fallback YouTube search — ALWAYS works ✅
        title = movies[movies['movie_id'] == movie_id]['title'].values[0]
        return f"https://www.youtube.com/results?search_query={quote(title)}+official+trailer"
    except Exception as e:
        print(f"Trailer error: {e}")
        return None


# ==========================================
#    FEATURE 3: STAR RATING DISPLAY
# ==========================================
def show_stars(rating):
    if not rating:
        return "☆☆☆☆☆"
    filled = int(round(rating / 2))
    empty  = 5 - filled
    return "★" * filled + "☆" * empty


# ==========================================
#   FEATURE 10: EXPLAIN RECOMMENDATION
# ==========================================
def explain_recommendation(movie1, movie2):
    try:
        tags1     = set(movies[movies['title'] == movie1]['tags'].values[0].split())
        tags2     = set(movies[movies['title'] == movie2]['tags'].values[0].split())
        stopwords = {
            'the','a','an','and','or','of','in','to','is','it',
            'for','on','with','as','at','by','from','be','have',
            'had','not','are','was','hi','thi','onc'
        }
        common = (tags1 & tags2) - stopwords
        return [w.capitalize() for w in list(common)[:6]]
    except:
        return []


# ==========================================
#     FEATURE 4: HYBRID RECOMMEND
# ==========================================
def recommend_hybrid(movie, n=5):
    if movie not in movies['title'].values:
        return [], [], []

    movie_index = movies[movies['title'] == movie].index[0]
    distances   = similarity[movie_index]

    candidates = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:30]

    results = []
    for idx, sim_score in candidates:
        row = movies.iloc[idx]
        try:
            popularity = float(row.get('popularity', 0))
        except:
            popularity = 0
        hybrid_score = (0.75 * sim_score) + (0.25 * min(popularity / 500, 1.0))
        results.append((idx, hybrid_score, sim_score))

    results   = sorted(results, reverse=True, key=lambda x: x[1])[:n]
    names     = [movies.iloc[r[0]].title    for r in results]
    movie_ids = [movies.iloc[r[0]].movie_id for r in results]
    scores    = [r[2]                        for r in results]
    return names, movie_ids, scores


# ==========================================
#              SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("## 🎛️ Filters")
    st.markdown("---")

    # FEATURE 8: Mood selector — FIXED with stemmed keywords ✅
    st.markdown("**🎭 Mood / Genre**")
    mood_map = {
        "😂 Fun & Comedy"      : "comedi",       # stemmed ✅
        "😢 Emotional Drama"   : "drama",
        "😱 Thrilling Action"  : "action",
        "🚀 Sci-Fi Adventure"  : "sciencefict",  # stemmed ✅
        "🔪 Dark & Mysterious" : "thriller",
        "💕 Romance"           : "romanc",       # stemmed ✅
        "👨‍👩‍👧 Family"            : "famili",       # stemmed ✅
    }
    selected_mood = st.radio(
        "Pick your mood:",
        list(mood_map.keys()),
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")

    # FEATURE 5: Year & Rating sliders
    st.markdown("**📅 Release Year (from)**")
    min_year   = st.slider("yr", 1990, 2024, 2000, label_visibility="collapsed")

    st.markdown("**⭐ Minimum Rating**")
    min_rating = st.slider("rt", 0.0, 10.0, 5.0, step=0.5, label_visibility="collapsed")

    st.markdown("---")

    # FEATURE 9: Recently Viewed History
    st.markdown("**🕘 Recently Viewed**")
    if st.session_state.history:
        for h in reversed(st.session_state.history[-6:]):
            st.markdown(f"🎬 {h}")
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()
    else:
        st.markdown(
            "<span style='color:#555;font-size:13px'>No history yet</span>",
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown(
        "<span style='color:#444;font-size:11px'>Powered by TMDB API · Built with Streamlit</span>",
        unsafe_allow_html=True
    )


# ==========================================
#              MAIN UI
# ==========================================
st.markdown('<div class="hero-title">CineMatch</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">AI-POWERED MOVIE RECOMMENDATION ENGINE</div>',
    unsafe_allow_html=True
)

# FEATURE 6: Search bar
col_search, col_btn = st.columns([4, 1])
with col_search:
    search_text = st.text_input(
        "search",
        placeholder="🔍 Type a movie name to search...",
        label_visibility="collapsed"
    )
    if search_text:
        matches = movies[movies['title'].str.contains(search_text, case=False, na=False)]
        if len(matches) > 0:
            selected_movie = st.selectbox(
                "Did you mean?",
                matches['title'].values,
                label_visibility="collapsed"
            )
        else:
            st.warning("No movies found. Try a different name.")
            selected_movie = movies['title'].values[0]
    else:
        selected_movie = st.selectbox(
            "Or browse all movies:",
            movies['title'].values,
            label_visibility="collapsed"
        )

with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    recommend_clicked = st.button("🎯 Find Movies")


# ==========================================
#          ON RECOMMEND CLICK
# ==========================================
if recommend_clicked:
    # Add to history
    if selected_movie not in st.session_state.history:
        st.session_state.history.append(selected_movie)

    with st.spinner("🔍 Analyzing and fetching recommendations..."):
        names, movie_ids, scores = recommend_hybrid(selected_movie, n=5)

        with ThreadPoolExecutor(max_workers=5) as executor:
            posters = list(executor.map(fetch_poster, movie_ids))
            details = list(executor.map(fetch_movie_details, movie_ids))

    if not names:
        st.error("Movie not found in database. Please try another title.")
    else:
        # Section Header
        st.markdown(
            f'<div class="section-header">🎬 Because You Liked "{selected_movie}"</div>',
            unsafe_allow_html=True
        )

        # 5 Movie Cards
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.image(posters[i], use_container_width=True)

                # FEATURE 3: Stars
                d      = details[i]
                rating = d.get('rating', 0)
                st.markdown(
                    f'<div style="text-align:center">'
                    f'<span class="stars">{show_stars(rating)}</span>'
                    f'<span class="rating-text">{rating:.1f}/10</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # FEATURE 11: Similarity bar
                pct = int(scores[i] * 100)
                st.markdown(
                    f'<div class="similarity-bar-wrap">'
                    f'<div class="similarity-bar" style="width:{pct}%"></div>'
                    f'</div>'
                    f'<div class="similarity-text">{pct}% Match</div>',
                    unsafe_allow_html=True
                )

                # Title
                st.markdown(
                    f'<div class="movie-title-label">{names[i]}</div>',
                    unsafe_allow_html=True
                )

                # FEATURE 10: Keyword chips
                tags = explain_recommendation(selected_movie, names[i])
                if tags:
                    chips = '<div class="chip-wrap">' + "".join(
                        f'<span class="chip">{t}</span>' for t in tags
                    ) + '</div>'
                    st.markdown(chips, unsafe_allow_html=True)

        # Detailed expanders
        st.markdown(
            '<div class="section-header">📋 Movie Details & Trailers</div>',
            unsafe_allow_html=True
        )

        for i in range(5):
            d            = details[i]
            release_year = d.get('release', 'N/A')[:4] if d.get('release') else 'N/A'

            with st.expander(
                f"📽️  {names[i]}  ·  {show_stars(d.get('rating', 0))}  ·  {release_year}"
            ):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown("**⭐ Rating**")
                    st.markdown(
                        f"<span style='color:#E50914;font-size:22px;font-weight:bold'>"
                        f"{d.get('rating', 0):.1f}</span>"
                        f"<span style='color:#888'>/10 &nbsp;({d.get('votes', 0):,} votes)</span>",
                        unsafe_allow_html=True
                    )
                with c2:
                    st.markdown("**🕐 Runtime**")
                    st.markdown(
                        f"<span style='color:#E50914;font-size:22px;font-weight:bold'>"
                        f"{d.get('runtime', 0)}</span>"
                        f"<span style='color:#888'> min</span>",
                        unsafe_allow_html=True
                    )
                with c3:
                    st.markdown("**📅 Released**")
                    st.markdown(
                        f"<span style='color:#E50914;font-size:18px;font-weight:bold'>"
                        f"{d.get('release', 'N/A')}</span>",
                        unsafe_allow_html=True
                    )

                if d.get('tagline'):
                    st.markdown(
                        f"<i style='color:#888'>\"{d['tagline']}\"</i>",
                        unsafe_allow_html=True
                    )
                if d.get('overview'):
                    st.markdown("**📖 Overview**")
                    st.markdown(
                        f"<span style='color:#ccc;font-size:13px'>{d['overview']}</span>",
                        unsafe_allow_html=True
                    )
                if d.get('genres'):
                    genre_chips = " ".join(
                        f'<span class="chip">{g}</span>' for g in d['genres']
                    )
                    st.markdown(
                        f'<div class="chip-wrap" style="margin-top:10px">{genre_chips}</div>',
                        unsafe_allow_html=True
                    )

                st.markdown("<br>", unsafe_allow_html=True)

                # FEATURE 7: TRAILER — FULLY FIXED ✅
                try:
                    mid         = movies[movies['title'] == names[i]].iloc[0].movie_id
                    trailer_url = fetch_trailer(mid)
                except:
                    trailer_url = None

                if trailer_url:
                    st.link_button("▶️ Watch Trailer on YouTube", trailer_url)
                    # Embed trailer inline if direct YouTube link
                    if "watch?v=" in trailer_url:
                        video_id = trailer_url.split("watch?v=")[-1]
                        st.markdown(
                            f'<div class="trailer-embed">'
                            f'<iframe width="100%" height="220" '
                            f'src="https://www.youtube.com/embed/{video_id}" '
                            f'frameborder="0" allow="autoplay; encrypted-media" '
                            f'allowfullscreen></iframe>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        "<span style='color:#555;font-size:12px'>No trailer available</span>",
                        unsafe_allow_html=True
                    )


# ==========================================
#    MOOD SECTION — FIXED ✅
# ==========================================
st.markdown("---")
st.markdown(
    '<div class="section-header">🎭 Top Picks For Your Mood</div>',
    unsafe_allow_html=True
)
st.markdown(
    f"<span style='color:#888;font-size:13px'>Showing top-rated "
    f"<b style='color:#E50914'>{selected_mood}</b> movies from our collection</span>",
    unsafe_allow_html=True
)

mood_keyword = mood_map[selected_mood]
mood_movies  = movies[
    movies['tags'].str.contains(mood_keyword, case=False, na=False)
].head(5)

if len(mood_movies) > 0:
    mood_ids    = mood_movies['movie_id'].tolist()
    mood_titles = mood_movies['title'].tolist()

    with st.spinner("Loading mood picks..."):
        with ThreadPoolExecutor(max_workers=5) as executor:
            mood_posters = list(executor.map(fetch_poster, mood_ids))

    mood_cols = st.columns(5)
    for i, col in enumerate(mood_cols):
        if i < len(mood_titles):
            with col:
                st.image(mood_posters[i], use_container_width=True)
                st.markdown(
                    f'<div class="movie-title-label">{mood_titles[i]}</div>',
                    unsafe_allow_html=True
                )
else:
    st.info("No movies found for this mood. Try a different one!")


# ==========================================
#   FEATURE 11: SIMILARITY CHART
# ==========================================
if recommend_clicked and names:
    st.markdown("---")
    st.markdown(
        '<div class="section-header">📊 Similarity Analysis</div>',
        unsafe_allow_html=True
    )
    try:
        import plotly.graph_objects as go

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=names,
            y=[round(s * 100, 1) for s in scores],
            marker=dict(
                color=[round(s * 100, 1) for s in scores],
                colorscale=[[0, '#3a0000'], [0.5, '#990000'], [1, '#E50914']],
                showscale=False,
                line=dict(width=0)
            ),
            text=[f"{round(s * 100, 1)}%" for s in scores],
            textposition='outside',
            textfont=dict(color='white', size=13)
        ))
        fig.update_layout(
            title=dict(
                text=f"How Similar Are These Movies to '{selected_movie}'?",
                font=dict(color='white', size=16),
                x=0.02
            ),
            paper_bgcolor='#111',
            plot_bgcolor='#111',
            font=dict(color='#aaa'),
            xaxis=dict(tickfont=dict(color='#ccc', size=11), gridcolor='#222', linecolor='#333'),
            yaxis=dict(title="Match %", tickfont=dict(color='#888'), gridcolor='#222',
                       linecolor='#333', range=[0, 100]),
            height=360,
            margin=dict(t=60, b=40, l=40, r=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    except ImportError:
        st.info("Install plotly: pip install plotly")


# ==========================================
#              FOOTER
# ==========================================
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#333;font-size:12px;padding:20px'>"
    "CineMatch · Built with ❤️ using Streamlit & TMDB API · "
    "<a href='https://www.themoviedb.org' style='color:#555'>Data from TMDB</a>"
    "</div>",
    unsafe_allow_html=True
)
