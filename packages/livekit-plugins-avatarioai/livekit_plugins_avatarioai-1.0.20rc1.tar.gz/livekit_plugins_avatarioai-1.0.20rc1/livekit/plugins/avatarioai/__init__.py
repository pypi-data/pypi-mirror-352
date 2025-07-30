from .avatar import (
    VideoInfo,
    AvatarSession,
    AvatarioException
)
from .version import __version__

__all__ = [
    "AvatarioException",
    "AvatarSession",
    "VideoInfo"
    "__version__",
]

from livekit.agents import Plugin

from .log import logger


class AvatarioPlugin(Plugin):
    def __init__(self) -> None:
        super().__init__(__name__, __version__, __package__, logger)


Plugin.register_plugin(AvatarioPlugin())   
