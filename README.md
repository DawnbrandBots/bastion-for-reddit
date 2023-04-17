# Bastion bot for Reddit

A free and open-source Reddit bot for looking up cards and other useful information about the
_Yu-Gi-Oh! Trading Card Game_ and _Official Card Game_. This is a port of the
[Discord bot](https://github.com/DawnbrandBots/bastion-bot).

## Getting started

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
REDDIT_USERNAME=
REDDIT_PASSWORD=
SUBREDDITS=yugioh+yugioh101
```

Run the bot with your IDE or in the shell!

```bash
python3 src/bastion.py
```

## Licence

Copyright © 2023 Kevin Lu, Luna Brand.
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

