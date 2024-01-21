# SPDX-FileCopyrightText: © 2023–2024 Kevin Lu, Luna Brand
# SPDX-Licence-Identifier: AGPL-3.0-or-later
from collections import Counter
from datetime import datetime, timezone
import logging
from threading import Thread
from typing import Union, TYPE_CHECKING

from prawcore import Forbidden
from praw.exceptions import RedditAPIException

from clients import get_reddit_client
from footer import FOOTER


if TYPE_CHECKING:
    import httpx
    from praw.models import Comment, Submission


class BotThread(Thread):
    # https://github.com/DawnbrandBots/bastion-for-reddit/issues/13
    MAX_REPLIES_PER_SUBMISSION = 10

    def __init__(self, api_client: "httpx.Client", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._logger = logging.getLogger(self.name)
        self._client = api_client
        self._reddit = get_reddit_client()
        # Actually irrelevant for SubmissionsThread
        self._reply_counter = Counter()

    def _reply(self, target: Union["Comment", "Submission"], text: str) -> None:
        try:
            reply: "Comment" = target.reply(text)
            self._logger.info(f"{target.id}: posted reply {reply.id}")
            if hasattr(target, "submission"):
                self._reply_counter[target.submission.id] += 1
            reply.disable_inbox_replies()
        except Forbidden as e:
            self._logger.warning(f"{target.id}: reply forbidden", exc_info=e)
        except RedditAPIException as e:
            for item in e.items:
                if item.error_type == "TOO_LONG":
                    self._logger.warning(f"{target.id}: reply too long", exc_info=e)
                    reply: "Comment" = target.reply(
                        f"Sorry, the cards are too long to fit into one comment.{FOOTER}"
                    )
                    self._logger.info(f"{target.id}: posted error {reply.id}")
                    self._reply_counter[target.submission.id] += 1
                    reply.disable_inbox_replies()
                    return
            self._logger.error(f"{target.id}: reply failure", exc_info=e)

    def _run(self) -> None:
        raise NotImplementedError

    def run(self) -> None:
        while True:
            self._logger.info("Starting")
            try:
                self._run()
            except Exception as e:
                self._logger.error("Exception in thread", exc_info=e)


def timestamp_to_iso(created_utc: float) -> str:
    return datetime.fromtimestamp(created_utc, timezone.utc).isoformat()
