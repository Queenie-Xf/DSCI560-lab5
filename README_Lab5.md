# 📘 Lab 5: Reddit Data Collection and Clustering

## 1. Environment Setup

### Requirements
- **Python**: 3.9 – 3.13 (recommended: 3.11+)
- **SQLite** (pre-installed on macOS/Linux; optional for Windows)
- **Tesseract OCR** (required for image text extraction)

### Install Tesseract OCR
On macOS (Homebrew):
```bash
brew install tesseract
```

On Ubuntu/Debian:
```bash
sudo apt-get install tesseract-ocr
```

### Clone Repository and Setup Virtual Environment
```bash
git clone <repo-url>
cd DSCI560-lab5

python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Download NLP Corpora
Required for **TextBlob** and **NLTK**:
```bash
python -m textblob.download_corpora
# or
python -m nltk.downloader punkt brown
```

---

## 2. Running the System

### Single Run Processing
Run the pipeline end-to-end on one batch of posts:
```bash
python direct_iphone_processing.py
```

This script:
- Connects to Reddit API
- Cleans and preprocesses text
- Generates TF-IDF & Doc2Vec embeddings
- Performs KMeans clustering
- Saves outputs under `reddit_data/`

### Automated Periodic Processing
Run multiple cycles with custom interval and post count:
```bash
python automated_processor.py --subreddit iphone --posts 200 --interval 30 --runs 3
```
- `--subreddit`: Subreddit name (e.g., `iphone`)
- `--posts`: Number of posts per run
- `--interval`: Interval between runs (minutes)
- `--runs`: Total number of runs

---

## 3. Output Structure

All results are stored in `reddit_data/`:

- **embeddings/**  
  - `*_clustering.pkl` – KMeans model  
  - `tfidf_vectorizer.pkl` – TF-IDF vectorizer  
  - `doc2vec_model.pkl` – Doc2Vec model  

- **metadata/**  
  - `*_clusters.json` – Cluster assignments and distances  
  - `summary.json` – Cluster summaries  

- **reddit_posts.db**  
  - SQLite database storing posts and cluster IDs  

⚠️ Do not commit this directory to GitHub. It is excluded via `.gitignore`.

---

## 4. Inspecting Results

### Check Cluster Sizes
```bash
sqlite3 reddit_data/reddit_posts.db "SELECT cluster_id, COUNT(*) FROM clusters GROUP BY cluster_id;"
```

### View Cluster Assignments
```bash
cat reddit_data/metadata/*_clusters.json | head -40
```

### Example: Get post IDs and titles
```bash
sqlite3 reddit_data/reddit_posts.db "SELECT post_id, title, cluster_id FROM posts LIMIT 10;"
```

---

## 5. Logging

Logs are written to:
```
logs/lab5.log
```

They include:
- Successful and failed post processing
- OCR warnings for corrupted images
- API retry attempts  

---

## 6. Notes

- Ensure `reddit_data/` is **not** committed to Git.  
- If you encounter `429 Too Many Requests`, the retry mechanism will back off automatically.  
- For OCR failures due to corrupted images, the system skips those posts gracefully.  

---

✅ With this setup, you can reproduce all Lab 5 requirements: **data collection, preprocessing, OCR, embeddings, clustering, storage, and automated scheduling**.
