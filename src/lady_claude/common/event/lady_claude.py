from enum import Enum


class LadyClaudeCommand(Enum):
    ASK = "ask"
    MINECRAFT = "minecraft"
    RECIPE = "recipe"


class LadyClaudeMinecraftOptionCommand(Enum):
    START = "start"
    STOP = "stop"
    STATUS = "status"
    BACKUP = "backup"


class LadyClaudeRecipeOptionCommand(Enum):
    REGIST = "regist"
    ASK = "ask"
    LIST = "list"
    DELETE = "delete"
