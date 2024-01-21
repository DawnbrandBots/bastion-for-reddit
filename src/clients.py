# SPDX-FileCopyrightText: © 2023–2024 Kevin Lu, Luna Brand
# SPDX-Licence-Identifier: AGPL-3.0-or-later
from os import getenv
from platform import python_version
from typing import Literal

import httpx
import praw


def user_agent(client: Literal["praw", "httpx"]) -> str:
    revision = getenv("REVISION")
    if client == "praw":
        client_version = praw.__version__
    else:
        client_version = httpx.__version__
    return f"Bastion/{revision} (by /u/BastionBotDev; +https://github.com/DawnbrandBots/bastion-for-reddit) {client}/{client_version} py/{python_version()}"


def get_reddit_client() -> praw.Reddit:
    return praw.Reddit(
        client_id=getenv("REDDIT_CLIENT_ID"),
        client_secret=getenv("REDDIT_CLIENT_SECRET"),
        username=getenv("REDDIT_USERNAME"),
        password=getenv("REDDIT_PASSWORD"),
        user_agent=user_agent("praw"),
    )


def get_api_client() -> httpx.Client:
    return httpx.Client(http2=True, headers={"User-Agent": user_agent("httpx")})
