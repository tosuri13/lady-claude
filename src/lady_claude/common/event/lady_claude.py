from enum import Enum


class LadyClaudeCommand(Enum):
    ASK = "ask"
    MINECRAFT = "minecraft"


class LadyClaudeMinecraftOptionCommand(Enum):
    START = "start"
    STOP = "stop"
    STATUS = "status"
