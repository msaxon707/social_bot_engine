import json
from pathlib import Path
from engine.utils import BASE_DIR, log, ensure_dir


def gather_generated():
    generated_dir = BASE_DIR / "generated"
    if not generated_dir.exists():
        return []

    rows = []
    for account_dir in generated_dir.iterdir():
        if not account_dir.is_dir():
            continue
        for date_dir in account_dir.iterdir():
            if not date_dir.is_dir():
                continue
            for f in date_dir.glob("*.json"):
                with open(f, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                rows.append({
                    "account": data.get("account"),
                    "topic": data.get("topic"),
                    "title": data.get("title"),
                    "generated_at": data.get("generated_at"),
                    "image_path": data.get("image_path"),
                    "video_path": data.get("video_path"),
                    "json_path": str(f)
                })
    return sorted(rows, key=lambda r: r["generated_at"], reverse=True)


def build_dashboard():
    rows = gather_generated()
    dash_dir = BASE_DIR / "dashboard"
    ensure_dir(dash_dir)
    out = dash_dir / "index.html"

    html_rows = []
    for r in rows[:200]:  # show last 200
        html_rows.append(f"""
        <tr>
          <td>{r['generated_at']}</td>
          <td>{r['account']}</td>
          <td>{r['topic']}</td>
          <td>{r['title']}</td>
          <td>{r['image_path'] or ''}</td>
          <td>{r['video_path'] or ''}</td>
          <td>{r['json_path']}</td>
        </tr>
        """)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <title>Social Bot Engine Dashboard</title>
      <style>
        body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif; padding: 20px; }}
        table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
        th, td {{ border: 1px solid #ccc; padding: 6px 8px; }}
        th {{ background: #f0f0f0; position: sticky; top: 0; }}
        tr:nth-child(even) {{ background: #fafafa; }}
      </style>
    </head>
    <body>
      <h1>Social Bot Engine - Generated Content</h1>
      <p>Total posts: {len(rows)}</p>
      <table>
        <thead>
          <tr>
            <th>Generated At</th>
            <th>Account</th>
            <th>Topic</th>
            <th>Title</th>
            <th>Image</th>
            <th>Video</th>
            <th>JSON</th>
          </tr>
        </thead>
        <tbody>
          {''.join(html_rows)}
        </tbody>
      </table>
    </body>
    </html>
    """

    with open(out, "w", encoding="utf-8") as f:
        f.write(html_content)

    log(f"Dashboard written to: {out}")


if __name__ == "__main__":
    build_dashboard()
