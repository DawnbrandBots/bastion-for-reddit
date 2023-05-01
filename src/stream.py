# SPDX-FileCopyrightText: © 2023 Kevin Lu, Luna Brand
# SPDX-Licence-Identifier: AGPL-3.0-or-later
from abc import abstractmethod
from os import getenv
from typing import Generator, Generic, List, TypeVar, TYPE_CHECKING

from antiabuse import already_replied_to_comment, already_replied_to_submission
from card import parse_summons, get_cards, display_cards
from bot_thread import BotThread


if TYPE_CHECKING:
    from praw.models import Comment, Submission


Post = TypeVar("Post", "Comment", "Submission")


class StreamThread(Generic[Post], BotThread):
    @abstractmethod
    def _parse_summons(self, post: Post) -> List[str]:
        raise NotImplementedError

    def _main_loop(self, stream: Generator[Post, None, None]):
        for post in stream:
            self._logger.info(f"{post.id}|{post.permalink}|{post.created_utc}")
            summons = self._parse_summons(post)
            if len(summons):
                cards = get_cards(self._client, summons)
                self._logger.info(f"{post.id}|{cards}")
                if len(cards):
                    reply = display_cards(cards)
                    self._reply(post, reply)


class SubmissionsThread(StreamThread["Submission"]):
    def __init__(self) -> None:
        super().__init__(name="submissions")

    # @override
    def _parse_summons(self, post):
        summons = parse_summons(post.selftext)
        self._logger.info(f"{post.id}|{summons}")
        if len(summons) and already_replied_to_submission(post):
            self._logger.info(f"{post.id}|Skip")
            return []
        return summons

    # @override
    def run(self) -> None:
        subreddits = self._reddit.subreddit(getenv("SUBREDDITS"))
        self._logger.info("Starting")
        self._main_loop(subreddits.stream.submissions())


class CommentsThread(StreamThread["Comment"]):
    def __init__(self) -> None:
        super().__init__(name="comments")

    # @override
    def _parse_summons(self, post):
        summons = parse_summons(post.body)
        self._logger.info(f"{post.id}|{summons}")
        if len(summons) and already_replied_to_comment(post):
            self._logger.info(f"{post.id}|Skip")
            return []
        return summons

    # @override
    def run(self) -> None:
        subreddits = self._reddit.subreddit(getenv("SUBREDDITS"))
        self._logger.info("Starting")
        self._main_loop(subreddits.stream.comments())
