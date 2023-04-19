# SPDX-FileCopyrightText: © 2023 Kevin Lu, Luna Brand
# SPDX-Licence-Identifier: AGPL-3.0-or-later
import logging
import re
from os import getenv
from platform import python_version
from threading import Thread
from typing import Any, Dict, List
from urllib.parse import quote_plus

from dotenv import load_dotenv
from httpx import Client
import praw


def user_agent() -> str:
    revision = getenv("REVISION")
    return f"Bastion/{revision} (by /u/BastionBotDev; +https://github.com/DawnbrandBots/bastion-for-reddit) praw/{praw.__version__} py/{python_version()}"


def get_reddit_client() -> praw.Reddit:
    return praw.Reddit(
        client_id=getenv("REDDIT_CLIENT_ID"),
        client_secret=getenv("REDDIT_CLIENT_SECRET"),
        username=getenv("REDDIT_USERNAME"),
        password=getenv("REDDIT_PASSWORD"),
        user_agent=user_agent()
    )


def run_on_submissions() -> None:
    logger = logging.getLogger("bastion-submissions")
    client = Client(http2=True, base_url=getenv("API_URL"))
    reddit = get_reddit_client()
    subreddits = reddit.subreddit(getenv("SUBREDDITS"))
    for submission in subreddits.stream.submissions():
        logger.info(f"{submission.id}|{submission.created_utc}|{submission.title}")
        summons = parse_summons(submission.selftext)
        logger.info(f"{submission.id}|{summons}")
        cards = get_cards(client, summons)
        logger.info(f"{submission.id}|{cards}")


def run_on_comments() -> None:
    logger = logging.getLogger("bastion-comments")
    client = Client(http2=True, base_url=getenv("API_URL"))
    reddit = get_reddit_client()
    subreddits = reddit.subreddit(getenv("SUBREDDITS"))
    for comment in subreddits.stream.comments():
        logger.info(f"{comment.id}|{comment.created_utc}|{comment.body}")
        summons = parse_summons(comment.body)
        logger.info(f"{comment.id}|{summons}")
        cards = get_cards(client, summons)
        logger.info(f"{comment.id}|{cards}")


summon_regex = re.compile("{{([^}]+)}}")


def parse_summons(text: str) -> List[str]:
    return summon_regex.findall(text)


def get_cards(client: Client, names: List[str]) -> List[Dict[str, Any]]:
    return [client.get(f"/ocg-tcg/search?name={quote_plus(name)}").json() for name in names]


def main():
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    submissions_thread = Thread(target=run_on_submissions, name="submissions")
    comments_thread = Thread(target=run_on_comments, name="comments")
    submissions_thread.start()
    comments_thread.start()


if __name__ == "__main__":
    main()
