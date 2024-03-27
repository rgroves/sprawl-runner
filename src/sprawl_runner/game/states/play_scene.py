from __future__ import annotations

from sprawl_runner import data
from sprawl_runner.game.states.end_game import EndGame
from sprawl_runner.game.states.game_state import GameState


class PlayScene(GameState):
    def action(self) -> GameState | None:
        opening_scene_instructions = data.load_data("opening-scene-instructions.txt")
        locations = ""
        for location in [job_loc for job_loc in self.game.locations if job_loc["type"] == "Employment"]:
            locations += f"- {location['name']} - {location['description']}\n"

        print(f"{self.game.locations=}")  # noqa: T201
        print(f"{locations=}")  # noqa: T201

        message = self.game.message_bus.process_narrative_message(
            opening_scene_instructions.format(locations=locations)
        )

        self.emit(f"\n\n=> {message}\n\n")

        player_input = ""
        count = 0

        while player_input != "q":
            while player_input == "":
                player_input = input(f">{count}> ")

            if player_input != "q":
                message = self.game.message_bus.process_narrative_message(player_input)
                self.emit(f"\n\n=> {message}\n\n")
                player_input = ""

            count += 1
        return EndGame()
