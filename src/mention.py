# SPDX-FileCopyrightText: © 2023 Kevin Lu, Luna Brand
# SPDX-Licence-Identifier: AGPL-3.0-or-later
from os import getenv
from typing import TYPE_CHECKING

from praw.models.util import stream_generator

from antiabuse import is_summon_chain
from bot_thread import BotThread, timestamp_to_iso
from card import parse_summons, get_cards, display_cards
from footer import FOOTER


if TYPE_CHECKING:
    import httpx


INFO = f"""Free and open source _Yu-Gi-Oh!_ bot. Use {{{{card name}}}} in your posts and comments to have me reply with card information.
Also works outside of Yu-Gi-Oh! subreddits if you mention me in the comment.
{FOOTER}
"""


class MentionsThread(BotThread):
    def __init__(self, api_client: "httpx.Client") -> None:
        super().__init__(api_client, name="mentions")

    # @override
    def _run(self) -> None:
        subreddits = getenv("SUBREDDITS").split("+")
        # Note: if a mention qualifies as a comment or post reply, it will not show up in this listing
        for comment in stream_generator(self._reddit.inbox.mentions):
            if not comment.new:
                self._logger.info(f"{comment.id}|{comment.context}| skip, read")
                continue
            self._logger.info(f"{comment.id}|{comment.context}|{timestamp_to_iso(comment.created_utc)}")
            comment.mark_read()
            if self._reply_counter[comment.submission.id] >= self.MAX_REPLIES_PER_SUBMISSION:
                self._logger.warning(f"{comment.id}: skip, exceeded limit for {comment.submission.id}")
                continue
            if is_summon_chain(comment):
                self._logger.info(f"{comment.id}: skip, parent comment is me")
                continue
            summons = parse_summons(comment.body)
            self._logger.info(f"{comment.id}| summons: {summons}")
            if not len(summons):
                self._reply(comment, INFO)
                continue
            if comment.subreddit.display_name.lower() not in subreddits:
                cards = get_cards(self._client, summons)
                self._logger.info(f"{comment.id}| cards: {cards}")
                if not len(cards):
                    self._reply(comment, INFO)
                else:
                    reply = display_cards(cards)
                    self._reply(comment, reply)
            # Other case should be handled by CommentsThread
