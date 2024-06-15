# Bastion bot for Reddit

A free and open-source Reddit bot for looking up cards and other useful information about the
_Yu-Gi-Oh! Trading Card Game_ and _Official Card Game_. This is a port of the
[Discord bot](https://github.com/DawnbrandBots/bastion-bot).

[Announcement post on /r/yugioh](https://reddit.com/r/yugioh/comments/139u4wb/the_bastion_card_bot_is_now_available_on_this/).

[![Build Docker image](https://github.com/DawnbrandBots/bastion-for-reddit/actions/workflows/docker.yml/badge.svg)](https://github.com/DawnbrandBots/bastion-for-reddit/actions/workflows/docker.yml)
[![Release to production (Compose)](https://github.com/DawnbrandBots/bastion-for-reddit/actions/workflows/release-compose.yml/badge.svg)](https://github.com/DawnbrandBots/bastion-for-reddit/actions/workflows/release-compose.yml)

## Usage

Summon [/u/BastionBotYuGiOh](https://reddit.com/u/BastionBotYuGiOh) in your submissions and comments on related subreddits
with doubled curly braces, e.g. `{{Tindangle Jhrelth}}`. This is a fuzzy search on OCG and TCG cards and their prereleases.
To summon Bastion elsewhere on Reddit, you can mention the bot user in your comments that contain curly brace search terms.
If [/u/BastionBotYuGiOh](https://reddit.com/u/BastionBotYuGiOh) is mentioned without any search terms, it will reply with
a short explanation about itself.

For bot safety, currently Bastion is tuned very conservatively to prevent bad behaviour,
so it will ignore any summons in replies to its comments,
there is a maximum of five card searches per submission or comment,
and it will comment a maximum of 10 times per submission, resetting when the program is restarted.

### Subreddits

- [/r/yugioh](https://reddit.com/r/yugioh)
- [/r/YuGiOhMemes](https://reddit.com/r/YuGiOhMemes)
- [/r/Yugioh101](https://reddit.com/r/Yugioh101)
- [/r/YuGiOhMasterDuel](https://reddit.com/r/YuGiOhMasterDuel)
- [/r/DuelLinks](https://reddit.com/r/DuelLinks)
- [/r/yugiohshowcase](https://reddit.com/r/yugiohshowcase)

## Getting started with development

Create a Python 3 [virtualenv](https://virtualenv.pypa.io) and install dependencies with
[pip-tools](https://github.com/jazzband/pip-tools):

```bash
virtualenv venv
. venv/bin/activate
pip install pip-tools
cd src
pip-sync
```

Configure a [`.env`](https://pypi.org/project/python-dotenv) file with the credentials for the Reddit bot account:

```dotenv
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USERNAME=BastionBotYuGiOh
REDDIT_PASSWORD=
SUBREDDITS=bastionbot
API_URL=
```

Run the bot with your IDE or in the shell!

```bash
python3 src/bastion.py
```

## Licence

Copyright © 2023–2024 Kevin Lu, Luna Brand.
See [COPYING](https://github.com/DawnbrandBots/bastion-for-reddit/blob/master/COPYING) for more details.

```
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

