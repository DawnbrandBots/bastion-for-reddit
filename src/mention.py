from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from praw.models import Comment


def on_mentioned(comment: "Comment") -> None:
    reply: "Comment" = comment.reply("""Free and open source _Yu-Gi-Oh!_ bot. Use {{card name}} in your posts and comments to have me reply with card information.
Also works outside of Yu-Gi-Oh! subreddits if you mention me in the comment.

^by ^[/u/BastionBotDev](/u/BastionBotDev) ^|
^[GitHub](https://github.com/DawnbrandBots/bastion-for-reddit) ^|
^Licence: ^[GNU&nbsp;AGPL&nbsp;3.0+](https://choosealicense.com/licenses/agpl-3.0/) ^|
^[Patreon](https://www.patreon.com/alphakretinbots) ^|
^[Ko-fi](https://ko-fi.com/dawnbrandbots)
""")
    reply.disable_inbox_replies()
