from __future__ import annotations

import os

import aiohttp

from dataclasses import dataclass, fields, asdict

from livekit import api, rtc
from livekit.agents import (
    DEFAULT_API_CONNECT_OPTIONS,
    NOT_GIVEN,
    AgentSession,
    APIConnectOptions,
    NotGivenOr,
    utils,
)
from livekit.agents.voice.avatar import DataStreamAudioOutput
from livekit.agents.voice.room_io import ATTRIBUTE_PUBLISH_ON_BEHALF

from .api import AvatarioAPI, AvatarioException
from .log import logger

SAMPLE_RATE = 24000
_AVATAR_AGENT_IDENTITY = "avatario-avatar-agent"
_AVATAR_AGENT_NAME = "avatario-avatar-agent"


@dataclass
class VideoInfo:
    video_height: int = 720
    video_width: int = 1280
    custom_background_url: str = None

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if value is None:
                setattr(self, field.name, field.default)


class AvatarSession:
    """An Avatario avatar session"""

    def __init__(
        self,
        *,
        avatar_id: NotGivenOr[str] = NOT_GIVEN,
        video_info: NotGivenOr[VideoInfo] = NOT_GIVEN,
        api_key: NotGivenOr[str] = NOT_GIVEN,
        avatar_participant_identity: NotGivenOr[str] = NOT_GIVEN,
        avatar_participant_name: NotGivenOr[str] = NOT_GIVEN,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
    ) -> None:
        self._http_session: aiohttp.ClientSession | None = None
        self._conn_options = conn_options
        video_info = video_info if utils.is_given(video_info) else VideoInfo()

        self._api = AvatarioAPI(
            api_key=api_key,
            video_info=asdict(video_info),
            avatar_id=avatar_id,
            conn_options=conn_options,
            session=self._ensure_http_session(),
        )

        self._avatar_participant_identity = avatar_participant_identity or _AVATAR_AGENT_IDENTITY
        self._avatar_participant_name = avatar_participant_name or _AVATAR_AGENT_NAME

    def _ensure_http_session(self) -> aiohttp.ClientSession:
        if self._http_session is None:
            self._http_session = utils.http_context.http_session()

        return self._http_session

    async def start(
        self,
        agent_session: AgentSession,
        room: rtc.Room,
        *,
        livekit_url: NotGivenOr[str] = NOT_GIVEN,
        livekit_api_key: NotGivenOr[str] = NOT_GIVEN,
        livekit_api_secret: NotGivenOr[str] = NOT_GIVEN,
    ) -> None:
        livekit_url = livekit_url or os.getenv("LIVEKIT_URL")
        livekit_api_key = livekit_api_key or os.getenv("LIVEKIT_API_KEY")
        livekit_api_secret = livekit_api_secret or os.getenv("LIVEKIT_API_SECRET")
        
        if not livekit_url or not livekit_api_key or not livekit_api_secret:
            raise AvatarioException(
                "livekit_url, livekit_api_key, and livekit_api_secret must be set "
                "by arguments or environment variables"
            )


        livekit_token = (
            api.AccessToken(api_key=livekit_api_key, api_secret=livekit_api_secret)
            .with_kind("agent")
            .with_identity(self._avatar_participant_identity)
            .with_name(self._avatar_participant_name)
            .with_grants(api.VideoGrants(room_join=True, room=room.name))
            # allow the avatar agent to publish audio and video on behalf of your local agent
            .with_attributes({ATTRIBUTE_PUBLISH_ON_BEHALF: room.local_participant.identity})
            .to_jwt()
        )

        await self._api.start_session(
            livekit_agent_identity=room.local_participant.identity,
            properties={
                "url": livekit_url,
                "token": livekit_token,
            },
        )

        logger.debug("waiting for avatar agent to join the room")
        await utils.wait_for_participant(room=room, identity=self._avatar_participant_identity)

        agent_session.output.audio = DataStreamAudioOutput(
            room=room,
            destination_identity=self._avatar_participant_identity,
            sample_rate=SAMPLE_RATE,
        )
