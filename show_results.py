# export_html_report.py
import os, sqlite3, html
from pathlib import Path
from datetime import datetime

DB_PATH = Path("reddit_data/reddit_posts.db")
OUT_PATH = Path("reddit_report.html")

def fetch_data(db_path: Path, top_k:int=5):
    if not db_path.exists():
        return {"error": f"Database not found at {db_path}"}
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM posts;")
    total_posts = cur.fetchone()[0]
    cur.execute("SELECT cluster_id, COUNT(*) FROM clusters GROUP BY cluster_id ORDER BY cluster_id;")
    distribution = [{"cluster_id": cid, "count": c} for cid, c in cur.fetchall()]
    cur.execute("""
        SELECT c.cluster_id, p.id, p.title, p.subreddit, c.distance
        FROM clusters c
        JOIN posts p ON c.post_id = p.id
        ORDER BY c.cluster_id, c.distance ASC
    """)
    reps = {}
    for cid, pid, title, subreddit, dist in cur.fetchall():
        reps.setdefault(cid, [])
        if len(reps[cid]) < top_k:
            reps[cid].append({"post_id": pid, "title": title or "", "subreddit": subreddit or "", "distance": float(dist)})
    conn.close()
    return {"total_posts": total_posts, "distribution": distribution, "representatives": reps, "generated_at": datetime.now().isoformat(timespec="seconds")}

def to_html(data: dict) -> str:
    css = """
    body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:24px;color:#111}
    h1{margin-bottom:0}.muted{color:#666}.grid{display:grid;grid-template-columns:1fr;gap:16px}
    .card{border:1px solid #e5e7eb;border-radius:12px;padding:16px;box-shadow:0 1px 2px rgba(0,0,0,.04)}
    table{width:100%;border-collapse:collapse}th,td{padding:8px 10px;border-bottom:1px solid #eee;text-align:left}
    th{background:#fafafa}.pill{display:inline-block;padding:2px 8px;border-radius:999px;background:#eef2ff;color:#3730a3;font-size:12px}
    .cid{font-weight:600}a{color:#2563eb;text-decoration:none}a:hover{text-decoration:underline}
    code{background:#f3f4f6;padding:2px 6px;border-radius:6px}
    """
    if "error" in data:
        body = f"""
        <h1>Reddit Clustering Report</h1>
        <p class="muted">Generated at {html.escape(datetime.now().isoformat(timespec='seconds'))}</p>
        <div class="card">
            <p><strong>⚠️ Could not find database</strong></p>
            <p>{html.escape(data['error'])}</p>
            <p>Please place the DB at <code>{html.escape(str(DB_PATH))}</code> and run again.</p>
        </div>
        """
        return f"<!doctype html><html><head><meta charset='utf-8'><title>Reddit Report</title><style>{css}</style></head><body>{body}</body></html>"
    dist_rows = "".join(f"<tr><td><span class='cid'>Cluster {d['cluster_id']}</span></td><td>{d['count']}</td></tr>" for d in data["distribution"])
    dist_table = f"""
    <div class="card">
      <h2>Cluster Distribution</h2>
      <table><thead><tr><th>Cluster</th><th>Posts</th></tr></thead><tbody>{dist_rows}</tbody></table>
    </div>"""
    rep_cards = []
    for cid, posts in data["representatives"].items():
        items = []
        for p in posts:
            url = f"https://www.reddit.com/comments/{p['post_id']}"
            items.append(f"<tr><td><a target='_blank' href='{html.escape(url)}'>{html.escape(p['title'][:120]) or '(no title)'}</a></td><td>{html.escape(p['subreddit'])}</td><td>{p['distance']:.3f}</td></tr>")
        rep_cards.append(f"""
        <div class="card">
          <h3>Cluster {cid} <span class="pill">Top {len(posts)} nearest</span></h3>
          <table><thead><tr><th>Title</th><th>Subreddit</th><th>Distance</th></tr></thead><tbody>{''.join(items)}</tbody></table>
        </div>""")
    body = f"""
    <h1>Reddit Clustering Report</h1>
    <p class="muted">Generated at {html.escape(data.get('generated_at',''))}</p>
    <div class="grid">
      <div class="card"><h2>Overview</h2><p>Total posts: <strong>{data['total_posts']}</strong></p></div>
      {dist_table}
      {''.join(rep_cards)}
    </div>"""
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Reddit Report</title><style>{css}</style></head><body>{body}</body></html>"

if __name__ == "__main__":
    data = fetch_data(DB_PATH, top_k=5)
    html_doc = to_html(data)
    OUT_PATH.write_text(html_doc, encoding="utf-8")
    print(f"Saved report to {OUT_PATH.resolve()}")

