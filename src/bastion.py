# SPDX-FileCopyrightText: © 2023 Kevin Lu, Luna Brand
# SPDX-Licence-Identifier: AGPL-3.0-or-later
import logging

from dotenv import load_dotenv

from clients import get_api_client
from limit_regulation import master_duel_limit_regulation
from mention import MentionsThread
from stream import SubmissionsThread, CommentsThread


def main():
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    api_client = get_api_client()
    master_duel_limit_regulation.set_client(api_client)
    submissions_thread = SubmissionsThread(api_client)
    comments_thread = CommentsThread(api_client)
    mentions_thread = MentionsThread(api_client)
    master_duel_limit_regulation.update(True)
    master_duel_limit_regulation.start()
    submissions_thread.start()
    comments_thread.start()
    mentions_thread.start()


if __name__ == "__main__":
    main()
