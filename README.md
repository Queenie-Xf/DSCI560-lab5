# Reddit Data Processing and Clustering System (DSCI560_lab5)

This project implements an end-to-end Reddit data collection and clustering pipeline with interactive search capabilities. It integrates with the Reddit API via **PRAW**, performs comprehensive text and image preprocessing (including OCR with Tesseract), stores data in an **SQLite database**, and applies machine learning algorithms (TF-IDF, Doc2Vec, KMeans) for clustering and analysis. The system supports single-run processing, automated periodic updates, and interactive cluster-based search.

---

## 1. Environment Setup

### Requirements
- **Python**: 3.9 – 3.13 (recommended 3.11+)
- **SQLite3** (default on macOS/Linux, required for Windows users)
- **Tesseract OCR** (for image text extraction)

### Install Tesseract OCR
On macOS (Homebrew):
```bash
brew install tesseract
```

On Ubuntu/Debian:
```bash
sudo apt-get install tesseract-ocr
```

### Clone Repository and Virtual Environment
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

## 2. Data Processing Workflow

### 2.1 Single Run
Execute the entire pipeline for one batch of Reddit posts:
```bash
python direct_iphone_processing.py
```

Steps performed:
1. Fetch Reddit posts (via PRAW API).
2. Preprocess data (clean HTML/Markdown, mask usernames, timestamp conversion).
3. Extract text from images using **pytesseract** OCR.
4. Generate embeddings (TF-IDF, Doc2Vec).
5. Train and apply **KMeans clustering**.
6. Store results in SQLite database and output JSON/PKL files.

### 2.2 Automated Periodic Processing
Schedule multiple runs with custom interval and post count:
```bash
python automated_processor.py --subreddit iphone --posts 200 --interval 30 --runs 3
```
Parameters:
- `--subreddit`: Target subreddit (e.g., `iphone`)
- `--posts`: Number of posts per run (supports >1000 with pagination)
- `--interval`: Interval between runs (minutes)
- `--runs`: Total number of runs

### 2.3 Interactive Automation with Cluster Search
Run continuous data collection with interactive search between updates:
```bash
python interactive_automation.py 5 --posts 100 --subreddit iphone
```

This mode provides:
- Automated periodic data collection at specified intervals (in minutes)
- Interactive search prompt between updates
- Real-time cluster matching based on semantic similarity
- Visualization of search results with keyword analysis

**Commands:**
- Enter any search query (e.g., "battery problems", "screen quality") to find matching clusters
- `status` - View last update time, next update time, and system status
- `exit` or `quit` - Stop the automation

**Search Process:**
1. Your query is converted to a Doc2Vec embedding
2. System calculates similarity to all cluster centroids
3. Returns the closest matching cluster
4. Within that cluster, posts are ranked by similarity to your specific query
5. Displays top 5 most relevant posts with similarity scores
6. Generates visualization showing keyword distribution and post rankings

**Output:**
- Console display of cluster details, keywords, and top matching posts
- PNG visualization saved to `visualizations/cluster_<id>_search_result.png`
- Shows similarity scores for all clusters (debug mode)

---

## 3. Output Structure

All results are written to `reddit_data/`:

- **embeddings/**
  - `*_clustering.pkl`: KMeans clustering model
  - `*_tfidf_vectorizer.pkl`: TF-IDF vectorizer
  - `*_doc2vec.model`: Trained Doc2Vec model

- **processed/**
  - `*_data.json`: Processed posts with embeddings and metadata
  - `*_data.pkl`: Pickle format of processed data

- **metadata/**
  - `*_clusters.json`: Cluster assignments (post_id → cluster_id)
  - `summary.json`: Cluster summary (representative posts & keywords)

- **reddit_posts.db**
  - SQLite database storing posts and cluster assignments

- **visualizations/**
  - `cluster_*_search_result.png`: Interactive search result visualizations
  - `enhanced_cluster_report.html`: Comprehensive cluster analysis report

⚠️ The `reddit_data/` directory is excluded via `.gitignore` and must not be committed.

---

## 4. Database Schema

### `posts` Table
```sql
CREATE TABLE posts (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    subreddit TEXT,
    title TEXT,
    content TEXT,
    cleaned_content TEXT,
    image_text TEXT,
    keywords TEXT,
    topics TEXT,
    extracted_urls TEXT,
    extracted_mentions TEXT,
    extracted_hashtags TEXT,
    features TEXT,
    embedding TEXT,
    created_datetime TEXT,
    processed_timestamp TEXT
);
```

### `clusters` Table
```sql
CREATE TABLE clusters (
    post_id TEXT,
    session_id TEXT,
    cluster_id INTEGER,
    distance REAL,
    PRIMARY KEY(post_id, session_id)
);
```

---

## 5. Scripts Overview

### `direct_iphone_processing.py`
- Runs the full pipeline once.
- Cleans data, generates embeddings, performs clustering.
- Saves results to `reddit_data/`.

### `reddit_data_processor.py`
- Core data processing module handling Reddit data fetching, OCR, and preprocessing.
- Includes robust API handling with pagination and retry/backoff logic.
- Supports reclustering of all existing posts on each run.

### `automated_processor.py`
- Automates repeated runs at fixed intervals.
- Logs execution progress and errors.
- Parameters: `--subreddit`, `--posts`, `--interval`, `--runs`.

### `interactive_automation.py`
- Combines automated periodic data collection with interactive cluster search.
- Runs data collection in background thread while providing search interface.
- Features:
  - Real-time cluster matching using Doc2Vec embeddings
  - Cosine similarity calculation for query-to-cluster matching
  - Post ranking within clusters based on query similarity
  - Automatic visualization generation
  - Status monitoring (last update, next update times)

### `database_connection.py`
- SQLite database connection manager with logging.
- Handles schema initialization and query execution.
- Supports parameterized queries and transaction management.

### `show_results.py`
- Utility script to inspect results from SQLite.
- Prints:
  - Total posts processed
  - Cluster distribution
  - Representative posts (closest to cluster centers)

### `generate_cluster_report.py`
- Generates comprehensive HTML reports of clustering results.
- Creates interactive visualizations including:
  - Cluster size distribution charts
  - Keyword frequency analysis per cluster
  - Representative posts with similarity scores
  - Cluster statistics and summaries

---

## 6. Logging

Logs are saved to:
```
logs/lab5.log
```

Recorded information includes:
- Successful and failed OCR operations
- Retry attempts for API requests
- Batch and run progress

---

## 7. Testing and Verification

### Verify Database Tables
```bash
sqlite3 reddit_data/reddit_posts.db ".tables"
```

### Count Posts
```bash
sqlite3 reddit_data/reddit_posts.db "SELECT COUNT(*) FROM posts;"
```

### Cluster Distribution
```bash
sqlite3 reddit_data/reddit_posts.db "SELECT cluster_id, COUNT(*) FROM clusters GROUP BY cluster_id;"
```

### Inspect Representative Posts
```bash
python show_results.py
```

### Generate Analysis Report
```bash
python generate_cluster_report.py
```
This creates `enhanced_cluster_report.html` with comprehensive visualizations.

### Test Interactive Search
```bash
python interactive_automation.py 5 --posts 50
```
Then enter test queries like:
- "battery life"
- "screen problems"
- "iOS updates"

The system will show similarity scores to all clusters and return the best match.

---

## 8. Submission Requirements

Per Lab 5 instructions:
- All code files
- README in PDF format (convert this markdown)
- `meeting_notes_<team_name>.pdf`
- Demonstration video (team members explain design and results)
- Detailed GitHub commit history with contributions per member

---

## 9. Key Features

This implementation includes:

### Data Collection & Processing
- Reddit API integration via PRAW with pagination support
- OCR text extraction from images using Tesseract
- Comprehensive text preprocessing (HTML/Markdown cleaning, username masking)
- Robust error handling with retry/backoff logic

### Machine Learning & Clustering
- TF-IDF vectorization with 300 features
- Doc2Vec embeddings (100 dimensions, 40 epochs)
- KMeans clustering with elbow method optimization
- Automatic small cluster merging for better distribution
- Full reclustering on each data update

### Interactive Search System
- Real-time semantic search using Doc2Vec embeddings
- Cosine similarity matching between queries and cluster centroids
- Within-cluster post ranking based on query relevance
- Multi-cluster similarity comparison (debug mode)
- Automatic visualization generation

### Data Persistence
- SQLite database with normalized schema
- JSON and pickle output formats
- Embedding storage as JSON arrays in database
- Session tracking for multiple processing runs

### Visualization & Reporting
- HTML cluster analysis reports with interactive charts
- PNG visualizations for search results
- Keyword frequency analysis
- Post similarity distributions
- Cluster size and statistics

### Automation
- Scheduled periodic data collection
- Background processing with foreground interaction
- Status monitoring and progress tracking
- Configurable intervals and batch sizes
