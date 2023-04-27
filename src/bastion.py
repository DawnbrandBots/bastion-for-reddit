# SPDX-FileCopyrightText: © 2023 Kevin Lu, Luna Brand
# SPDX-Licence-Identifier: AGPL-3.0-or-later
import logging
import re
from os import getenv
from platform import python_version
from threading import Thread
from typing import Any, Dict, List
from urllib.parse import quote_plus

import praw
from dotenv import load_dotenv
from httpx import Client
from praw.models import Comment
from prawcore import Forbidden


def user_agent() -> str:
    revision = getenv("REVISION")
    return f"Bastion/{revision} (by /u/BastionBotDev; +https://github.com/DawnbrandBots/bastion-for-reddit) praw/{praw.__version__} py/{python_version()}"


def get_reddit_client() -> praw.Reddit:
    return praw.Reddit(
        client_id=getenv("REDDIT_CLIENT_ID"),
        client_secret=getenv("REDDIT_CLIENT_SECRET"),
        username=getenv("REDDIT_USERNAME"),
        password=getenv("REDDIT_PASSWORD"),
        user_agent=user_agent()
    )


def run_on_submissions() -> None:
    logger = logging.getLogger("bastion-submissions")
    client = Client(http2=True, base_url=getenv("API_URL"))
    reddit = get_reddit_client()
    subreddits = reddit.subreddit(getenv("SUBREDDITS"))
    for submission in subreddits.stream.submissions():
        logger.info(
            f"{submission.id}|{submission.created_utc}|{submission.title}")
        summons = parse_summons(submission.selftext)
        logger.info(f"{submission.id}|{summons}")
        cards = get_cards(client, summons)
        logger.info(f"{submission.id}|{cards}")
        reply_with_cards(submission, logger, cards)


def run_on_comments() -> None:
    logger = logging.getLogger("bastion-comments")
    client = Client(http2=True, base_url=getenv("API_URL"))
    reddit = get_reddit_client()
    subreddits = reddit.subreddit(getenv("SUBREDDITS"))
    for comment in subreddits.stream.comments():
        logger.info(f"{comment.id}|{comment.created_utc}|{comment.body}")
        summons = parse_summons(comment.body)
        logger.info(f"{comment.id}|{summons}")
        cards = get_cards(client, summons)
        logger.info(f"{comment.id}|{cards}")
        reply_with_cards(comment, logger, cards)


def run_on_mentions() -> None:
    logger = logging.getLogger("bastion-mentions")
    client = Client(http2=True, base_url=getenv("API_URL"))
    reddit = get_reddit_client()
    subreddits = getenv("SUBREDDITS").split("+")
    for comment in reddit.inbox.mentions():
        logger.info(f"{comment.id}|{comment.created_utc}|{comment.body}")
        if comment.subreddit.display_name.lower() not in subreddits:
            summons = parse_summons(comment.body)
            logger.info(f"{comment.id}|{summons}")
            cards = get_cards(client, summons)
            logger.info(f"{comment.id}|{cards}")
            reply_with_cards(comment, logger, cards)


summon_regex = re.compile("{{([^}]+)}}")


def parse_summons(text: str) -> List[str]:
    return summon_regex.findall(text)


def get_cards(client: Client, names: List[str]) -> List[Dict[str, Any]]:
    return [client.get(f"/ocg-tcg/search?name={quote_plus(name)}").json() for name in names]


def format_limit_regulation(value: int | None) -> int | None:
    match value:
        case "Forbidden":
            return 0
        case "Limited":
            return 1
        case "Semi-Limited":
            return 2
        case "Unlimited":
            return 3
        case _:
            return None


def format_footer(card: Any) -> str:
    text = ""
    if card['password'] and card['konami_id']:
        text = f"Password: {card['password']} | Konami ID #{card['konami_id']}"
    elif not card['password'] and card['konami_id']:
        text = f"No password | Konami ID #{card['konami_id']}"
    elif card['password'] and not card['konami_id']:
        text = f"Password: {card['password']} | Not yet released"
    else:
        text = "Not yet released"

    if card.get('fake_password') != None:
        text += f"Placeholder ID: {card['fake_password']}"

    return f"^({text})"


def generate_card_display(card: Any) -> str:
    yugipedia_page = card['konami_id'] or quote_plus(card['name']['en'])
    yugipedia = f"https://yugipedia.com/wiki/{yugipedia_page}?utm_source=bastion"
    ygoprodeck_term = card['password'] or quote_plus(card['name']['en'])
    ygoprodeck = f"https://ygoprodeck.com/card/?search={ygoprodeck_term}&utm_source=bastion"
    # Official database, does not work for zh locales
    official = f"https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=2&request_locale=en&cid={card['konami_id']}"
    rulings = f"https://www.db.yugioh-card.com/yugiohdb/faq_search.action?ope=4&request_locale=ja&cid={card['konami_id']}"

    full_text = ""

    title = f"## [{card['name']['en']}]({ygoprodeck})"

    full_text += title + "\n"

    links = f"### 🔗 Links\n[Official Konami DB]({official}) | [OCG Rulings]({rulings}) | [Yugipedia]({yugipedia}) | [YGOPRODECK]({ygoprodeck})"

    if card['konami_id'] == None:
        links = f"### 🔗 Links\n[Yugipedia]({yugipedia}) | [YGOPRODECK]({ygoprodeck})"

    description = ""

    limit_regulations = [
        {"label": "TCG: ", "value": format_limit_regulation(
            card["limit_regulation"].get("tcg"))},
        {"label": "OCG: ", "value": format_limit_regulation(
            card["limit_regulation"].get("ocg"))},
        {"label": "Speed: ", "value": format_limit_regulation(
            card["limit_regulation"].get("speed"))}
    ]

    limit_regulation_display = " / ".join(
        map(lambda l: f"{l['label']}{l['value']}", filter(lambda l: l['value'] != None, limit_regulations)))

    if len(limit_regulation_display) > 0:
        description += f"^(**Limit**: {limit_regulation_display})"

    description += "\n\n"
    if card['card_type'] == "Monster":
        description += f"^(**Type**: {card['monster_type_line']})"
        description += "\n\n"
        description += f"^(**Attribute**: {card['attribute']})"
        description += "\n\n"

        if "rank" in card:
            description += f"^(**Rank**: {card['rank']} **ATK**: {card['atk']} **DEF**: {card['def']})"
        elif "link_arrows" in card:
            arrows = "".join(card['link_arrows'])
            description += f"^(**Link Rating**: {len(card['link_arrows'])} **ATK**: {card['atk']} **Link Arrows**: {arrows})"
        else:
            description += f"^(**Level**: {card['level']} **ATK**: {card['atk']} **DEF**: {card['def']})"

        if card.get('pendulum_scale') != None:
            formattedScale = f"{card['pendulum_scale']} / {card['pendulum_scale']}"
            description += " "
            description += f"^(**Pendulum Scale**: {formattedScale})"

        full_text += description + "\n"

        if card.get('pendulum_effect') != None:
            full_text += "### Pendulum Effect\n" + \
                (card['pendulum_effect']['en'] or "\u200b") + "\n"

        full_text += "### Card Text\n" + (card['text']['en'] or "\u200b")
    else:
        # Spells and Traps

        description += "\n\n"
        description += f"{card['property']} {card['card_type']}"

        full_text += description + "\n\n"

        full_text += "### Card Effect\n" + (card['text']['en'] or "\u200b")

    full_text += "\n\n" + links + "\n\n"

    full_text += format_footer(card)

    return full_text


def reply_with_cards(
    target: praw.models.Submission | praw.models.Comment,
    logger: logging.Logger,
    cards: List[Dict[str, Any]]
) -> None:
    if len(cards):
        try:
            reply: Comment = target.reply(
                "\n\n----\n\n".join(generate_card_display(card) for card in cards))
            logger.info(f"{reply.id}")
            reply.disable_inbox_replies()
        except Forbidden as e:
            logger.warning(e)


def main():
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    submissions_thread = Thread(
        target=run_on_submissions, name="submissions")
    comments_thread = Thread(target=run_on_comments, name="comments")
    # mentions_thread = Thread(target=run_on_mentions, name="mentions")
    submissions_thread.start()
    comments_thread.start()


if __name__ == "__main__":
    main()
