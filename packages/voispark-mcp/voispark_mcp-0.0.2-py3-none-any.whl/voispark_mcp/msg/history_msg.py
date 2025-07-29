from typing import Literal, Any
from pydantic import BaseModel

from voispark_mcp.msg.conversation_msg import ConversationSpeaker, ConversationText


class History(BaseModel):
    history_id: str
    user_id: str
    source: Literal["vc", "tts"]
    object_key: str
    voice_id: str
    voice_name: str
    provider: str
    model_id: str
    model_name: str
    created_at: int
    ref_text: str
    configs: dict[str, Any]


class ConversationHistory:
    history_id: str
    user_id: str
    provider: str
    configs: dict
    conversation: list[ConversationText]
    speakers: list[ConversationSpeaker]
    s3_key: str
    created_at: int


class HistoryListResponse(BaseModel):
    history_list: list[History] | list[ConversationHistory]
    total: int


class HistoryResponse(BaseModel):
    history: History | ConversationHistory
    presigned_url: str
