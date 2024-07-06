from typing import Any

from card import format_card_text
from limit_regulation import rush_duel_limit_regulation


def generate_rush_card_display(card: Any) -> str:
    yugipedia = (
        f"https://yugipedia.com/wiki/{card["konami_id"]}?utm_source=bastion&utm_medium=reddit"
        if card["konami_id"]
        else f"https://yugipedia.com/wiki/?curid={card["yugipedia_page_id"]}&utm_source=bastion&utm_medium=reddit"
    )
    rushcard = f"https://rushcard.io/card/?search={card["yugipedia_page_id"]}&utm_source=bastion&utm_medium=reddit"

    full_text = f"## [{card['name']['en']}]({rushcard})\n"

    # Links

    description = ""
    if card.get("legend"):
        description += "__**LEGEND**__\n"
    elif card["konami_id"]:
        limit_regulation_display = (
            rush_duel_limit_regulation.get(card["konami_id"]) or 3
        )
        description += f"^(**Limit**: {limit_regulation_display})  \n"

    if card["card_type"] == "Monster":
        description += f"^(**Type**: {card['monster_type_line']})  \n"
        description += f"^(**Attribute**: {card['attribute']})  \n"
        description += f"^(**Level**: {card['level']} **ATK**: {card['atk']} **DEF**: {card['def']})  \n"
        if "maximum_atk" in card:
            description += f"^(**MAXIMUM ATK**: {card['maximum_atk']})  \n"
        if card.get("summoning_condition"):
            description += f"\n{format_card_text(card["summoning_condition"]["en"])}"
        if "materials" in card:
            description += f"\n{format_card_text(card["materials"]["en"])}"
        if "Fusion" in card["monster_type_line"] and "text" in card:
            # This is effectively the localised materials line for non-Effect Fusion monsters
            description += f"\n{format_card_text(card["text"]["en"])}"

        full_text += f"{description}\n\n"

        if "requirement" in card:
            full_text += f"**[REQUIREMENT]**\n\n{format_card_text(card['requirement']['en'])}\n\n"
            effect_type = "EFFECT"
            if "Continuous" in card.get("effect_types", ""):
                effect_type = "CONTINUOUS EFFECT"
            elif "Multi-Choice" in card.get("effect_types", ""):
                effect_type = "MULTI-CHOICE EFFECT"
            full_text += (
                f"**[{effect_type}]**\n\n{format_card_text(card['effect']['en'])}\n\n"
            )
        elif "text" in card and "Fusion" not in card["monster_type_line"]:
            full_text += f"**Card Text**\n\n{format_card_text(card['text']['en'])}"
    else:
        # Spells and Traps
        description += "\n\n"
        description += f"{card['property']} {card['card_type']}"
        full_text += f"{description}\n\n"
        full_text += f"**[REQUIREMENT]**\n\n{format_card_text(card['requirement']['en'])}\n\n"
        full_text += f"**[EFFECT]**\n\n{format_card_text(card['effect']['en'])}\n\n"

    # Add Links
    full_text += f"Konami ID #{card['konami_id']}" if card["konami_id"] else "Not yet released"
    return full_text
