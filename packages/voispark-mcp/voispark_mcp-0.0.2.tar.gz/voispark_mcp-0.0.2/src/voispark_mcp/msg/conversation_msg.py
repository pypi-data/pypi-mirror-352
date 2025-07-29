from typing import Union, Literal, Optional
from pydantic import BaseModel, Field

from voispark_mcp.msg.audio_msg import AudioTaskDetails


class NariLabsConversationConfig(BaseModel):
    cfg_scale: float = Field(
        default=3.0,
        title="CFG Scale",
        description="Classifier-free guidance scale",
        json_schema_extra={"min_value": 1.0, "max_value": 10.0, "step": 0.1},
    )
    temperature: float = Field(
        default=1.3,
        title="Temperature",
        description="Temperature for generation",
        json_schema_extra={"min_value": 0.1, "max_value": 2.0, "step": 0.1},
    )
    top_p: float = Field(
        default=0.95,
        title="Top-p",
        description="Top-p (nucleus) sampling",
        json_schema_extra={"min_value": 0.1, "max_value": 1.0, "step": 0.05},
    )
    cfg_filter_top_k: int = Field(
        default=35,
        title="CFG Filter Top-k",
        description="Top-k filtering for classifier-free guidance",
        json_schema_extra={"min_value": 1, "max_value": 100, "step": 1},
    )


class SesameConversationConfig(BaseModel):
    temperature: float = Field(
        default=0.6,
        title="Temperature",
        description="Temperature for generation",
        json_schema_extra={"min_value": 0.1, "max_value": 1.5, "step": 0.1},
    )
    topk: int = Field(
        default=50,
        title="Top-k",
        description="Top-k for generation",
        json_schema_extra={"min_value": 5, "max_value": 200, "step": 5},
    )


class ConversationText(BaseModel):
    speaker_index: int
    text: str


class ConversationSpeaker(BaseModel):
    speaker_id: str
    speaker_name: str
    audio_text: str
    s3_key: str


class ConversationModelConfig(BaseModel):
    param_name: str
    param_display_name: str
    param_type: Literal["select", "float", "int", "boolean", "string"]
    default_value: float | int | str | bool
    description: str = ""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    options: Optional[list[str]] = None
    text_prompt: Optional[str] = None


class ConversationTurn(BaseModel):
    text: str
    speaker_index: int


class SpeakerIDItem(BaseModel):
    speaker_id: str


class SpeakerRawItem(BaseModel):
    speaker_name: str
    audio: str  # Base64 encoded audio
    audio_text: str


class SpeakerConfigItem(BaseModel):
    type: Literal["speaker_id", "raw"]
    speaker: Union[SpeakerIDItem, SpeakerRawItem]


class GenerateConversationRequest(BaseModel):
    provider: str
    conversation: list[ConversationTurn]
    speaker: list[SpeakerConfigItem]
    configs: Union[SesameConversationConfig, NariLabsConversationConfig, None] = None
    sync: bool = Field(
        default=True, description="sync should be true when using the API"
    )


class GenerateConversationResponse(BaseModel):
    task_id: str
    status: Literal["success", "failed"]
    details: Optional[AudioTaskDetails] = None
    error: Optional[str] = None


class GetSpeakersResponse(BaseModel):
    speakers: list[ConversationSpeaker]


class GetSpeakerDetailsResponse(BaseModel):
    speaker: ConversationSpeaker
    presigned_url: str


class ConversationModelItem(BaseModel):
    provider: str
    name: str
    description: str
    configs: list[ConversationModelConfig]


class ConversationModelsResponse(BaseModel):
    models: list[ConversationModelItem]
