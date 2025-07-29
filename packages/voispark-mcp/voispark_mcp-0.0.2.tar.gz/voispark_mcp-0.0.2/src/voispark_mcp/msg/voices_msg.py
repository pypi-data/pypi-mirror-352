from pydantic import BaseModel
from typing import Literal

Ability = Literal["tts", "voice_changer", "voice_clone", "voice_generate"]


class Voice(BaseModel):
    id: str
    name: str
    description: str
    provider: str
    avatar_url: str = ""
    preview_url: str = ""


class VoicesListResponse(BaseModel):
    default_voices: list[Voice]
    user_voices: list[Voice]
    ip_voices: list[Voice]


class VoiceProvider(BaseModel):
    id: str
    name: str
    description: str
    abilities: list[Ability]


class VoiceProvidersResponse(BaseModel):
    providers: list[VoiceProvider]
