# SPDX-FileCopyrightText: © 2023–2024 Kevin Lu, Luna Brand
# SPDX-Licence-Identifier: AGPL-3.0-or-later
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from praw.models import Comment, Submission
    from praw.models.comment_forest import CommentForest


def is_author_me(comment: "Comment") -> bool:
    return (
        comment.author is not None
        and comment.author.name == comment._reddit.user.me().name
    )


def is_summon_chain(comment: "Comment") -> bool:
    """
    Returns True if the grandparent comment is authored by self, to prevent looping.
    This is naïve and will not prevent loops with more intervening comments,
    e.g. Bastion -> Bot A -> Bot B summons Bastion
    """
    if comment.is_root:
        return False
    return is_author_me(comment.parent())


def is_my_reply_in_comments(replies: "CommentForest") -> bool:
    for reply in replies:
        if is_author_me(reply):
            return True
    return False


def already_replied_to_submission(submission: "Submission") -> bool:
    return is_my_reply_in_comments(submission.comments)


def already_replied_to_comment(comment: "Comment") -> bool:
    # https://github.com/praw-dev/praw/issues/413#issuecomment-1092474360
    # https://praw.readthedocs.io/en/latest/code_overview/models/comment.html#praw.models.Comment.replies
    comment.refresh()
    return is_my_reply_in_comments(comment.replies)
