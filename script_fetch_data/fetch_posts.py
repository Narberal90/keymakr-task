import aiohttp
import asyncio
import sqlite3
import logging
import csv
import argparse
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger()

DEFAULT_URL = "https://jsonplaceholder.typicode.com/posts/"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


DB_NAME = DATA_DIR / "posts.db"
CSV_FILE = DATA_DIR / "posts.csv"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    title TEXT,
    body TEXT
)
"""
)
conn.commit()


test_urls_bad_request = [
    "99999",
    "http://10.255.255.1",
    "https://invalid-url.test/",
    "https://invalid-url.com",
]


async def fetch_post(session, base_url, post_id):
    url = f"{base_url}{post_id}"
    try:
        async with session.get(url, timeout=5) as response:
            if response.status == 200:
                content_type = response.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    return await response.json()
                else:
                    logger.error(
                        f"Expected JSON, but got {content_type} instead. "
                        f"URL: {url}"
                    )
                    return
            else:
                logger.error(
                    f"Exception while fetching | {url} | "
                    f"Response status -> {response.status}"
                )
                return
    except asyncio.TimeoutError:
        logger.error(
            f"Timeout error while fetching {url}: "
            f"The request took too long to respond."
        )
        return
    except Exception as e:
        logger.error(f"Exception while fetching | {url} | Reason -> {e}")
        return


async def fetch_all_posts(base_url, post_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_post(session, base_url, post_id) for post_id in post_ids
        ]
        results = await asyncio.gather(*tasks)
        valid_results = [result for result in results if result is not None]
        logger.info(
            f"Fetched count: {len(post_ids)} | "
            f"Successfully: {len(valid_results)} | "
            f"Failed: {len(post_ids) - len(valid_results)}"
        )
        return valid_results


def save_to_db(posts):
    valid_posts = []

    for post in posts:
        if post:
            all_keys_exist = True
            for key in ["id", "userId", "title", "body"]:
                if key not in post:
                    all_keys_exist = False
                    break
            if all_keys_exist:
                valid_posts.append(post)

    cursor.executemany(
        """
    INSERT OR REPLACE INTO posts (id, user_id, title, body)
    VALUES (?, ?, ?, ?)
    """,
        [
            (post["id"], post["userId"], post["title"], post["body"])
            for post in valid_posts
        ],
    )
    conn.commit()
    logger.info("Data saved to database")


def save_to_csv(posts):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
        fieldnames = ["id", "userId", "title", "body"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(posts)
    logger.info("Data saved to CSV")


async def main(base_url, post_ids):
    posts = await fetch_all_posts(base_url, post_ids)
    if posts:
        save_to_db(posts)
        save_to_csv(posts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch posts from API")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Use test URLs instead of all posts",
    )

    parser.add_argument("--start", type=int, default=1, help="Start post ID")
    parser.add_argument("--end", type=int, default=20, help="End post ID")
    args = parser.parse_args()

    try:
        base_url = DEFAULT_URL if not args.test else ""
        if args.test:
            post_ids = test_urls_bad_request
        else:
            base_url = DEFAULT_URL
            post_ids = [i for i in range(args.start, args.end + 1)]

        asyncio.run(main(base_url, post_ids))
    finally:
        conn.close()
