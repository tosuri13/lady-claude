from enum import Enum


class InteractionType(Enum):
    PING = 1
    APPLICATION_COMMAND = 2


class InteractionResponseType(Enum):
    PONG = 1
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
