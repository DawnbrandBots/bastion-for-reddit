# SPDX-FileCopyrightText: © 2023 Kevin Lu, Luna Brand
# SPDX-Licence-Identifier: AGPL-3.0-or-later
import logging

from dotenv import load_dotenv

from mention import MentionsThread
from stream import SubmissionsThread, CommentsThread


def main():
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    submissions_thread = SubmissionsThread()
    comments_thread = CommentsThread()
    mentions_thread = MentionsThread()
    submissions_thread.start()
    comments_thread.start()
    mentions_thread.start()


if __name__ == "__main__":
    main()
