from typing import Callable, Literal

ToolName = Literal["register_factions", "register_locations"]
ToolHandler = Callable[[dict[str, list]], str]
ToolHandlerEntry = tuple[ToolName, ToolHandler]
