# 🎬 Movie Recommendation System

A simple and interactive Content-Based Movie Recommendation System built using Machine Learning. It uses vectorization techniques (CountVectorizer) and cosine similarity to recommend movies similar to the one selected by the user.

## 🚀 Features

* Recommend movies based on similarity
* Clean and interactive UI using Streamlit
* Displays movie posters using API
* Fast and efficient recommendations using precomputed similarity matrix

---

## 🛠️ Tech Stack

* Python
* Pandas & NumPy
* Scikit-learn
* Streamlit
* TMDB API (for movie posters)

---

## 📂 Project Structure

```
Movie-Recommender-System/
│
├── app.py                # Main application file
├── movie_list.pkl       # Movie dataset
├── similarity.pkl       # Similarity matrix
├── requirements.txt     # Dependencies
└── README.md            # Project documentation
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```
git clone https://github.com/your-username/movie-recommender-system.git
cd movie-recommender-system
```

### 2. Install Dependencies

```
pip install -r requirements.txt
```

### 3. Add API Key

Replace your TMDB API key inside `app.py`:

```
api_key = "YOUR_API_KEY"
```

### 4. Run the Application

```
streamlit run app.py
```

---

## 🎯 How It Works

1. Movie data is preprocessed
2. Text vectorization (like CountVectorizer) is applied
3. Cosine similarity is calculated between movies
4. Top similar movies are recommended

---

## 📸 Screenshots

(Add screenshots here)

---

## 🧠 Future Improvements

* Add user authentication
* Deploy on cloud (Render / Streamlit Cloud)
* Improve recommendation accuracy
* Add filters (genre, rating, year)

---

## 🌐 Deployment

You can deploy this project using:

* Streamlit Cloud
* Render
* Heroku

---

## 🤝 Contributing

Feel free to fork this repository and contribute.

---

## 📧 Contact

For any queries, contact:
Amandeep Yadav

---

## ⭐ If you like this project

Give it a star on GitHub ⭐
