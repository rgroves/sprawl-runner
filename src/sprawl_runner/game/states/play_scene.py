from __future__ import annotations

from sprawl_runner.game.states.end_game import EndGame
from sprawl_runner.game.states.game_state import GameState


class PlayScene(GameState):
    def action(self) -> GameState | None:
        self.emit("In PlayScene")
        self.emit("\n\n---Factions---")
        for faction in self.game.factions:
            self.emit(f"***{faction['name']}***")
            self.emit(f" - {faction['description']}")
            self.emit(f" - {faction['motivation']}")

        self.emit("\n\n---Locations---")
        for location in self.game.locations:
            self.emit(f"***{location['name']}***")
            self.emit(f" - {location['type']}")
            self.emit(f" - {location['description']}")

        return EndGame()
