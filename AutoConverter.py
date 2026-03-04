import os
import requests
import pandas as pd
from datetime import datetime, timezone

# Get subdomain from environment
SUBDOMAIN = os.environ.get("SQUARESPACE_SUBDOMAIN")
if not SUBDOMAIN:
    raise RuntimeError("Missing SQUARESPACE_SUBDOMAIN env var (e.g. 'cooldomain').")

URL = f"https://{SUBDOMAIN}.squarespace.com/api/census-frontend/1/popular-content/pages"

# Gets the time frame of the previous month
def previous_month_range_millis(now=None):
    if now is None:
        now = datetime.now(timezone.utc)

    # Start of current month
    start_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Start of previous month
    if start_this_month.month == 1:
        start_prev_month = start_this_month.replace(year=start_this_month.year - 1, month=12)
    else:
        start_prev_month = start_this_month.replace(month=start_this_month.month - 1)

    start_millis = int(start_prev_month.timestamp() * 1000)
    end_millis = int(start_this_month.timestamp() * 1000)
    return start_millis, end_millis

# Retrieves squarespace API information
def fetch_popular_content(start_millis: int, end_millis: int) -> dict:
    params = {
        "limit": 100,
        "sortBy": "views",
        "isAscending": "false",
        "comparisonCode": "MoM",
        "granularity": "WEEKLY",
        "startMillis": start_millis,
        "endMillis": end_millis,
    }

    cookie = os.environ.get("SQUARESPACE_COOKIE")
    if not cookie:
        raise RuntimeError(
            "Missing SQUARESPACE_COOKIE env var. "
            "Set it to the Cookie header value from your browser."
        )

    headers = {
        "Cookie": cookie,
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
    }

    r = requests.get(URL, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()

def to_csv(pages: list, out_path: str) -> None:
    df = pd.json_normalize(pages)
    df.to_csv(out_path, index=False)

if __name__ == "__main__":
    print("///////////// Squarespace Blog Analytics Scraper /////////////")

    # Check for output directory
    out_dir = os.environ.get("OUTPUT_DIR")
    if not out_dir:
        raise RuntimeError("Missing OUTPUT_DIR env var (directory to write CSVs into).")

    os.makedirs(out_dir, exist_ok=True)

    # Get start and end times from prev month
    start_millis, end_millis = previous_month_range_millis()

    data = fetch_popular_content(start_millis, end_millis)
    pages: list = data.get("pages", [])

    # Filter irrelevant pages
    filtered_pages = [
        page for page in pages
        if page.get("path", "").startswith("/blog/") and page.get("page", "") != "Blog"
    ]

    # save output
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(out_dir, f"output_{ts}.csv")
    to_csv(filtered_pages, out_path)

    print(f"Completed output: {out_path}")