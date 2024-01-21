# SPDX-FileCopyrightText: © 2023–2024 Kevin Lu
# SPDX-Licence-Identifier: AGPL-3.0-or-later
from datetime import datetime
import logging
from threading import Timer
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    import httpx


# https://github.com/DawnbrandBots/bastion-bot/blob/master/src/limit-regulation.ts
class UpdatingLimitRegulationVector:
    def __init__(self, url: str, api_client: "httpx.Client" = None) -> None:
        self._vector: Dict[int, int] = {}
        self._logger = logging.getLogger(__name__)
        self._url = url
        self._client = api_client
        self._timer = Timer(60000, self.update)

    # Post-initialization, remove when globals are removed
    def set_client(self, api_client: "httpx.Client") -> None:
        self._client = api_client

    def update(self, initial: bool = False) -> None:
        if initial or datetime.now().minute == 0:
            self._logger.info(f"Updating from [{self._url}]")
            try:
                response = self._client.get(self._url)
                regulation = response.json()["regulation"]
                self._vector = {
                    int(konami_id): limit for konami_id, limit in regulation.items()
                }
                self._logger.info(f"Read {len(self._vector)} entries")
            except Exception:
                self._logger.error(f"Failed GET [{self._url}]", exc_info=1)

    def get(self, konami_id: int) -> int | None:
        return self._vector.get(konami_id)

    def start(self) -> None:
        self._timer.start()

    def cancel(self) -> None:
        self._timer.cancel()


# Globals, to eventually remove
master_duel_limit_regulation = UpdatingLimitRegulationVector(
    "https://dawnbrandbots.github.io/yaml-yugi-limit-regulation/master-duel/current.vector.json"
)
rush_duel_limit_regulation = UpdatingLimitRegulationVector(
    "https://dawnbrandbots.github.io/yaml-yugi-limit-regulation/rush/current.vector.json"
)
