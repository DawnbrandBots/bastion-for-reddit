# SPDX-FileCopyrightText: © 2023 Kevin Lu, Luna Brand
# SPDX-Licence-Identifier: AGPL-3.0-or-later
import logging
from os import getenv
from platform import python_version
from threading import Thread

from dotenv import load_dotenv
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
    reddit = get_reddit_client()
    subreddits = reddit.subreddit(getenv("SUBREDDITS"))
    for submission in subreddits.stream.submissions():
        logger.info(f"{submission.id}|{submission.created_utc}|{submission.title}")


def run_on_comments() -> None:
    logger = logging.getLogger("bastion-comments")
    reddit = get_reddit_client()
    subreddits = reddit.subreddit(getenv("SUBREDDITS"))
    for comment in subreddits.stream.comments():
        logger.info(f"{comment.id}|{comment.created_utc}|{comment.body}")


def main():
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    submissions_thread = Thread(target=run_on_submissions, name="submissions")
    comments_thread = Thread(target=run_on_comments, name="comments")
    submissions_thread.start()
    comments_thread.start()


if __name__ == "__main__":
    main()
