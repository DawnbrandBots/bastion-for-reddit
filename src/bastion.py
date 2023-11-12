# SPDX-FileCopyrightText: © 2023 Kevin Lu, Luna Brand
# SPDX-Licence-Identifier: AGPL-3.0-or-later
import logging

from dotenv import load_dotenv

from clients import get_api_client
from mention import MentionsThread
from stream import SubmissionsThread, CommentsThread


def main():
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    api_client = get_api_client()
    submissions_thread = SubmissionsThread(api_client)
    comments_thread = CommentsThread(api_client)
    mentions_thread = MentionsThread(api_client)
    submissions_thread.start()
    comments_thread.start()
    mentions_thread.start()


if __name__ == "__main__":
    main()
