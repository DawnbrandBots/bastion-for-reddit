import logging
from threading import Thread
from typing import Union, TYPE_CHECKING

from prawcore import Forbidden

from clients import get_api_client, get_reddit_client


if TYPE_CHECKING:
    from praw.models import Comment, Submission


class BotThread(Thread):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._logger = logging.getLogger(self.name)
        self._client = get_api_client()
        self._reddit = get_reddit_client()

    def _reply(self, target: Union["Comment", "Submission"], text: str) -> None:
        try:
            reply: "Comment" = target.reply(text)
            self._logger.info(f"{target.id}: posted reply {reply.id}")
            reply.disable_inbox_replies()
        except Forbidden as e:
            self._logger.warning(f"{target.id}: reply forbidden", exc_info=e)
