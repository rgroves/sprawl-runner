from sprawl_runner import data
from sprawl_runner.game.states.game_state import GameState
from sprawl_runner.game.states.play_scene import PlayScene


class InitializeGameWorld(GameState):
    def action(self) -> GameState:
        faction_gen_instructions = data.load_data("faction-gen-instructions.txt")
        self.game.message_bus.process_tool_message_async(faction_gen_instructions)

        location_gen_instructions = data.load_data("location-gen-instructions.txt")
        self.game.message_bus.process_tool_message_async(location_gen_instructions)
        return WaitForGameWorldReady()


class WaitForGameWorldReady(GameState):
    EXPECTED = 8

    def action(self) -> GameState:
        import time

        total_items = len(self.game.factions) + len(self.game.locations)
        self.emit(f"... waiting for game world initialization: {total_items} ...")
        self.game.message_bus.resolve_async_tool_messages()

        if total_items == self.EXPECTED:
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
            next_state: GameState = PlayScene()
        else:
            next_state = self
            time.sleep(2)

        return next_state
