from typing import Union, Literal, Optional
from pydantic import BaseModel, Field

from voispark_mcp.msg.audio_msg import AudioTaskDetails


class VoiceChangerModelConfig(BaseModel):
    param_name: str
    param_type: Literal["select", "float", "int", "boolean", "string"]
    default_value: float | int | str | bool
    description: str = ""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    options: Optional[list[str]] = None
    text_prompt: Optional[str] = None


class SubModel(BaseModel):
    model_name: str
    """
    模型名称 model_id
    """
    credit: int
    """
    模型计费积分倍率
    """

    @property
    def model_id(self) -> str:
        return self.model_name


class VoiceChangerModel(BaseModel):
    provider: str
    model_list: list[SubModel]
    name: str
    description: str
    configs: list[VoiceChangerModelConfig]


class CartesiaVoiceChangerConfig(BaseModel): ...


class ElevenLabsVoiceChangerConfig(BaseModel):
    stability: float = Field(
        default=0.5,
        description="The stability of the voice changer model.",
        json_schema_extra={"min_value": 0.0, "max_value": 1.0, "step": 0.01},
    )
    similarity: float = Field(
        default=0.75,
        description="The similarity of the voice changer model.",
        json_schema_extra={"min_value": 0.0, "max_value": 1.0, "step": 0.01},
    )
    style_exaggeration: float = Field(
        default=0.0,
        description="The style exaggeration of the voice changer model.",
        json_schema_extra={"min_value": 0.0, "max_value": 1.0, "step": 0.01},
    )
    speaker_boost: bool = Field(
        default=True,
        description="Whether to use speaker boost for the voice changer model.",
    )
    remove_background_noise: bool = Field(
        default=False,
        description="Whether to remove background noise for the voice changer model.",
    )


class ChangeVoiceRequest(BaseModel):
    audio_data: str  # base64 encoded audio file
    provider: str
    model_id: str
    voice_id: str
    configs: Union[CartesiaVoiceChangerConfig, ElevenLabsVoiceChangerConfig, None] = (
        None
    )
    sync: bool = Field(
        default=True, description="sync should be true when using the API"
    )


class ChangeVoiceResponse(BaseModel):
    task_id: str
    status: Literal["success", "failed"]
    details: Optional[AudioTaskDetails] = None
    error: Optional[str] = None


class VoiceChangerModelsResponse(BaseModel):
    models: list[VoiceChangerModel]
