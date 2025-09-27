import sqlite3
from pathlib import Path

DB_PATH = Path("reddit_data/reddit_posts.db")

def show_results(top_k=3):
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM posts;")
    total_posts = cur.fetchone()[0]
    print(f"📊 Total posts: {total_posts}")

    print("\n📊 Cluster distribution:")
    cur.execute("SELECT cluster_id, COUNT(*) FROM clusters GROUP BY cluster_id ORDER BY cluster_id;")
    for cluster_id, count in cur.fetchall():
        print(f"  - Cluster {cluster_id}: {count} posts")

    print("\n📌 Representative posts per cluster:")
    cur.execute("""
        SELECT c.cluster_id, p.title, p.id, c.distance
        FROM clusters c
        JOIN posts p ON c.post_id = p.id
        ORDER BY c.cluster_id, c.distance ASC
    """)
    rows = cur.fetchall()

    clusters = {}
    for cluster_id, title, post_id, distance in rows:
        clusters.setdefault(cluster_id, []).append((title, post_id, distance))

    for cid, posts in clusters.items():
        print(f"\n=== Cluster {cid} ===")
        for title, post_id, dist in posts[:top_k]:
            print(f" - {title[:80]}... (id={post_id}, dist={dist:.3f})")

    conn.close()


if __name__ == "__main__":
    show_results(top_k=3)
