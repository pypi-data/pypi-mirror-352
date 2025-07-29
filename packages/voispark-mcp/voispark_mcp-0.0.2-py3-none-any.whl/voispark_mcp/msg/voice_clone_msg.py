from pydantic import BaseModel, Field
from typing import Union, Literal, Optional


class CartesiaVoiceCloneConfig(BaseModel):
    name: str = Field(
        default="",
        description="The name of the voice.",
        json_schema_extra={"is_required": True},
    )
    description: str = Field(
        default="",
        description="A description for the voice.",
        json_schema_extra={"is_required": False},
    )
    mode: Literal["similarity", "stability"] = Field(
        default="stability",
        description="Tradeoff between similarity and stability. Similarity clones sound more like the source clip, but may reproduce background noise. Stability clones always sound like a studio recording, but may not sound as similar to the source clip.",
        json_schema_extra={"is_required": False},
    )
    enhance: bool = Field(
        default=False,
        description="Whether to enhance the clip to improve its quality before cloning. Useful if the clip has background noise.",
        json_schema_extra={"is_required": False},
    )
    transcript: str = Field(
        default="",
        description="Optional transcript of the words spoken in the audio clip. Only used for similarity mode.",
        json_schema_extra={"is_required": False},
    )


class MiniMaxVoiceCloneConfig(BaseModel):
    name: str = Field(
        default="",
        description="The name of the voice.",
        json_schema_extra={"is_required": True},
    )
    description: str = Field(
        default="",
        description="A description for the voice.",
        json_schema_extra={"is_required": False},
    )
    need_noise_reduction: bool = Field(
        default=False,
        description="Audio cloning parameter. Whether to enable noise reduction. Defaults to false if not provided.",
        json_schema_extra={"is_required": False},
    )
    need_volume_normalization: bool = Field(
        default=False,
        description="Audio cloning parameter. Whether to enable volume normalization. Defaults to false if not provided.",
        json_schema_extra={"is_required": False},
    )


class VoiceCloneModelConfig(BaseModel):
    param_name: str
    param_type: Literal["select", "float", "int", "boolean", "string", "audio"]
    default_value: float | int | str | bool | None
    description: str = ""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    options: Optional[list[str]] = None
    text: Optional[str] = None
    is_required: bool = False


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


class VoiceCloneModel(BaseModel):
    provider: str
    model_list: list[SubModel]
    name: str
    description: str
    configs: list[VoiceCloneModelConfig]


class CloneVoiceRequest(BaseModel):
    audio_data: str  # base64 encoded audio file
    provider: str
    model_id: str
    configs: Union[CartesiaVoiceCloneConfig, MiniMaxVoiceCloneConfig]


class CloneVoiceResponse(BaseModel):
    id: str
    name: str
    description: str
    provider: str
    avatar_url: str = ""
    preview_url: str = ""


class VoiceCloneModelsResponse(BaseModel):
    models: list[VoiceCloneModel]
