# SPDX-FileCopyrightText: © 2023–2024 Kevin Lu, Luna Brand
# SPDX-Licence-Identifier: AGPL-3.0-or-later
from abc import abstractmethod
from os import getenv
from typing import Generator, Generic, List, TypeVar, TYPE_CHECKING

from antiabuse import (
    already_replied_to_comment,
    already_replied_to_submission,
    is_author_me,
    is_summon_chain,
)
from card import parse_summons, get_cards, display_cards
from bot_thread import BotThread, timestamp_to_iso

if TYPE_CHECKING:
    import httpx
    from praw.models import Comment, Submission


Post = TypeVar("Post", "Comment", "Submission")


class StreamThread(Generic[Post], BotThread):
    @abstractmethod
    def _parse_summons(self, post: Post) -> List[str]:
        raise NotImplementedError

    def _main_loop(self, stream: Generator[Post, None, None]):
        for post in stream:
            self._logger.info(
                f"{post.id}|{post.permalink}|{timestamp_to_iso(post.created_utc)}"
            )
            summons = self._parse_summons(post)
            if len(summons):
                cards = get_cards(self._client, summons)
                self._logger.info(f"{post.id}| cards: {cards}")
                if len(cards):
                    reply = display_cards(cards)
                    self._reply(post, reply)


class SubmissionsThread(StreamThread["Submission"]):
    def __init__(self, api_client: "httpx.Client") -> None:
        super().__init__(api_client, name="submissions")

    # @override
    def _parse_summons(self, submission):
        summons = parse_summons(submission.selftext)
        self._logger.info(f"{submission.id}| summons: {summons}")
        if len(summons) and already_replied_to_submission(submission):
            self._logger.info(f"{submission.id}: skip, already replied")
            return []
        return summons

    # @override
    def _run(self) -> None:
        subreddits = self._reddit.subreddit(getenv("SUBREDDITS"))
        self._main_loop(subreddits.stream.submissions())


class CommentsThread(StreamThread["Comment"]):
    def __init__(self, api_client: "httpx.Client") -> None:
        super().__init__(api_client, name="comments")

    # @override
    def _parse_summons(self, comment):
        if is_author_me(comment):
            self._logger.info(f"{comment.id}: skip, self")
            return []
        if (
            self._reply_counter[comment.submission.id]
            >= self.MAX_REPLIES_PER_SUBMISSION
        ):
            self._logger.warning(
                f"{comment.id}: skip, exceeded limit for {comment.submission.id}"
            )
            return []
        summons = parse_summons(comment.body)
        self._logger.info(f"{comment.id}| summons: {summons}")
        if len(summons):
            if already_replied_to_comment(comment):
                self._logger.info(f"{comment.id}: skip, already replied")
                return []
            if is_summon_chain(comment):
                self._logger.info(f"{comment.id}: skip, parent comment is me")
                return []
        return summons

    # @override
    def _run(self) -> None:
        subreddits = self._reddit.subreddit(getenv("SUBREDDITS"))
        self._main_loop(subreddits.stream.comments())
