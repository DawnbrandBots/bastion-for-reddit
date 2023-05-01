from os import getenv
from typing import TYPE_CHECKING

from praw.models.util import stream_generator

from card import parse_summons, get_cards, display_cards
from footer import FOOTER
from bot_thread import BotThread


if TYPE_CHECKING:
    from praw.models import Comment


INFO = f"""Free and open source _Yu-Gi-Oh!_ bot. Use {{card name}} in your posts and comments to have me reply with card information.
Also works outside of Yu-Gi-Oh! subreddits if you mention me in the comment.
{FOOTER}
"""


class MentionsThread(BotThread):
    def __init__(self) -> None:
        super().__init__(name="mentions")

    # @override
    def run(self) -> None:
        subreddits = getenv("SUBREDDITS").split("+")
        self._logger.info("Starting")
        # Note: if a mention qualifies as a comment or post reply, it will not show up in this listing
        for comment in stream_generator(self._reddit.inbox.mentions):
            if not comment.new:
                self._logger.info(f"{comment.id}|{comment.context}|Skip")
                continue
            self._logger.info(f"{comment.id}|{comment.context}|{comment.created_utc}")
            comment.mark_read()
            summons = parse_summons(comment.body)
            self._logger.info(f"{comment.id}|{summons}")
            if not len(summons):
                self._reply(comment, INFO)
                continue
            if comment.subreddit.display_name.lower() not in subreddits:
                cards = get_cards(self._client, summons)
                self._logger.info(f"{comment.id}|{cards}")
                if not len(cards):
                    self._reply(comment, INFO)
                else:
                    reply = display_cards(cards)
                    self._reply(comment, reply)
            # Other case should be handled by CommentsThread
