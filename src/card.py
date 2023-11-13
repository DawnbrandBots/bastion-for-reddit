# SPDX-FileCopyrightText: © 2023 Kevin Lu, Luna Brand
# SPDX-Licence-Identifier: AGPL-3.0-or-later
from os import getenv
import re
from typing import Any, List, Dict, TYPE_CHECKING
from urllib.parse import quote_plus

from footer import FOOTER
from limit_regulation import master_duel_limit_regulation


if TYPE_CHECKING:
    from httpx import Client


summon_regex = re.compile("{{([^}]+)}}")
# TODO: https://github.com/DawnbrandBots/bastion-for-reddit/issues/12
summon_limit = 5


def parse_summons(text: str) -> List[str]:
    """
    Returns a list of all unique tokens found enclosed by {{ }} in order of appearance,
    stripping surrounding whitespace and ignoring blanks and case-insensitive repeats.
    Currently limited to `summon_limit` items.
    """
    summons: List[str] = summon_regex.findall(text)
    summons = [summon.strip() for summon in summons]
    return list(dict.fromkeys(summon.lower() for summon in summons if summon))[:summon_limit]


def get_cards(client: "Client", names: List[str]) -> List[Dict[str, Any]]:
    # Could be parallelized, even in a synchronous context
    responses = [client.get(f"{getenv('API_URL')}/ocg-tcg/search?name={quote_plus(name)}") for name in names]
    return [response.json() for response in responses if response.status_code == 200]


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


# Has a global dependency
def get_master_duel_limit_regulation(card: Any) -> int | None:
    if not card.get("master_duel_rarity") or not card["konami_id"]:
        return
    regulation = master_duel_limit_regulation.get(card["konami_id"])
    if regulation is not None:
        return regulation
    return 3


MASTER_DUEL_RARITY = {
    "N": "Common",
    "R": "Rare",
    "SR": "Super Rare",
    "UR": "Ultra Rare"
}

def format_card_text(text: str | None) -> str:
    return text.replace("\n", "\n\n") if text else "\u200b"


def format_footer(card: Any) -> str:
    if card['password'] and card['konami_id']:
        text = f"Password: {card['password']} | Konami ID #{card['konami_id']}"
    elif not card['password'] and card['konami_id']:
        text = f"No password | Konami ID #{card['konami_id']}"
    elif card['password'] and not card['konami_id']:
        text = f"Password: {card['password']} | Not yet released"
    else:
        text = "Not yet released"
        if card.get('fake_password') is not None:
            text += f" | Placeholder ID: {card['fake_password']}"
    return f"^({text})"


def generate_card_display(card: Any) -> str:
    yugipedia_page = card['konami_id'] or quote_plus(card['name']['en'])
    yugipedia = f"https://yugipedia.com/wiki/{yugipedia_page}?utm_source=bastion&utm_medium=reddit"
    ygoprodeck_term = card['password'] or quote_plus(card['name']['en'])
    ygoprodeck = f"https://ygoprodeck.com/card/?search={ygoprodeck_term}&utm_source=bastion&utm_medium=reddit"

    full_text = f"## [{card['name']['en']}]({ygoprodeck})\n"

    links = ""
    if card.get('images'):
        image_link = f"https://yugipedia.com/wiki/Special:Redirect/file/{card['images'][0]['image']}?utm_source=bastion&utm_medium=reddit"
        links += f"[Card Image]({image_link}) | "
    if card['konami_id'] is not None:
        # Official database, does not work for zh locales
        official = f"https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=2&request_locale=en&cid={card['konami_id']}"
        rulings = f"https://www.db.yugioh-card.com/yugiohdb/faq_search.action?ope=4&request_locale=ja&cid={card['konami_id']}"
        links += f"[Official Konami DB]({official}) | [OCG Rulings]({rulings}) | "
    links += f"[Yugipedia]({yugipedia}) | [YGOPRODECK]({ygoprodeck})"

    description = ""

    limit_regulations = [
        {"label": "TCG: ", "value": format_limit_regulation(card["limit_regulation"].get("tcg"))},
        {"label": "OCG: ", "value": format_limit_regulation(card["limit_regulation"].get("ocg"))},
        {"label": "Speed: ", "value": card["limit_regulation"].get("speed")},
        {"label": "MD: ", "value": get_master_duel_limit_regulation(card)},
    ]

    limit_regulation_display = " / ".join(f"{reg['label']}{reg['value']}" for reg in limit_regulations if reg["value"] is not None)

    if len(limit_regulation_display) > 0:
        description += f"^(**Limit**: {limit_regulation_display})  \n"

    if card.get("master_duel_rarity"):
        md_rarity_code = card["master_duel_rarity"]
        md_rarity = MASTER_DUEL_RARITY[md_rarity_code]
        description += f"^(**Master Duel rarity**: {md_rarity} &#40;{md_rarity_code}&#41;)  \n"

    if card['card_type'] == "Monster":
        description += f"^(**Type**: {card['monster_type_line']})  \n"
        description += f"^(**Attribute**: {card['attribute']})  \n"

        if "rank" in card:
            description += f"^(**Rank**: {card['rank']} **ATK**: {card['atk']} **DEF**: {card['def']})"
        elif "link_arrows" in card:
            arrows = "".join(card['link_arrows'])
            description += f"^(**Link Rating**: {len(card['link_arrows'])} **ATK**: {card['atk']} **Link Arrows**: {arrows})"
        else:
            description += f"^(**Level**: {card['level']} **ATK**: {card['atk']} **DEF**: {card['def']})"

        if card.get('pendulum_scale') != None:
            formatted_scale = f"{card['pendulum_scale']} / {card['pendulum_scale']}"
            description += " "
            description += f"^(**Pendulum Scale**: {formatted_scale})"

        full_text += f"{description}\n\n"

        if card.get('pendulum_effect') != None:
            full_text += f"**Pendulum Effect**\n\n{format_card_text(card['pendulum_effect']['en'])}\n\n"

        full_text += f"**Card Text**\n\n{format_card_text(card['text']['en'])}"
    else:
        # Spells and Traps
        description += "\n\n"
        description += f"{card['property']} {card['card_type']}"
        full_text += f"{description}\n\n**Card Text**\n\n{format_card_text(card['text']['en'])}"

    full_text += f"\n\n{links}\n\n{format_footer(card)}"
    return full_text


def display_cards(cards: List[Any]) -> str:
    return "\n\n----\n\n".join(generate_card_display(card) for card in cards) + FOOTER
