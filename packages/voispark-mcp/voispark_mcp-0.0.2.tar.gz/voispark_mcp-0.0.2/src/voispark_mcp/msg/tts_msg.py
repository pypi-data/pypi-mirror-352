from typing import Union, Literal, Optional

from pydantic import BaseModel, Field

from voispark_mcp.msg.audio_msg import AudioTaskDetails


class TTSModelConfig(BaseModel):
    param_name: str
    param_type: Literal["select", "float", "int", "boolean", "string"]
    default_value: float | int | str | bool
    description: str = ""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    options: Optional[list[str]] = None
    text_prompt: Optional[str] = None
    require: bool = False


class SubModel(BaseModel):
    model_name: str
    """
    模型名称 model_id
    """
    credit: int
    """
    模型计费积分倍率
    """
    supported_languages: list[str]
    """
    支持的语言列表
    """

    @property
    def model_id(self) -> str:
        return self.model_name


class CartesiaTTSConfig(BaseModel):
    speed: Literal["slowest", "slow", "normal", "fast", "fastest"] = Field(
        default="normal", description="Controls the speed of the generated audio."
    )
    emotion_prefix: Literal[
        "anger", "positivity", "surprise", "sadness", "curiosity", "normal"
    ] = Field(
        default="normal",
        description="Specifies the emotion prefix for the generated audio.",
    )
    emotion_suffix: Literal["lowest", "low", "normal", "high", "highest"] = Field(
        default="normal",
        description="Specifies the emotion suffix intensity for the generated audio.",
    )


class ElevenLabsTTSConfig(BaseModel):
    stability: float = Field(
        default=0.5,
        description="The stability of the TTS model.",
        json_schema_extra={"min_value": 0.0, "max_value": 1.0, "step": 0.01},
    )
    similarity_boost: float = Field(
        default=0.75,
        description="The similarity boost of the TTS model.",
        json_schema_extra={"min_value": 0.0, "max_value": 1.0, "step": 0.01},
    )
    style: float = Field(
        default=0.0,
        description="The style of the TTS model.",
        json_schema_extra={"min_value": 0.0, "max_value": 1.0, "step": 0.01},
    )
    use_speaker_boost: bool = Field(
        default=True, description="Whether to use speaker boost for the TTS model."
    )
    speed: float = Field(
        default=1.0,
        description="The speed of the TTS model.",
        json_schema_extra={"min_value": 0.7, "max_value": 1.2, "step": 0.01},
    )


class FishAudioConfig(BaseModel):
    speed: float = Field(
        default=1.0,
        description="Speed of the speech",
        json_schema_extra={"min_value": 0.5, "max_value": 2.0, "step": 0.1},
    )
    volume: float = Field(
        default=0.0,
        description="Volume of the speech",
        json_schema_extra={"min_value": -5.0, "max_value": 5.0, "step": 0.1},
    )
    normalize: bool = Field(default=True, description="Normalize the speech")


class MinimaxConfig(BaseModel):
    speed: float = Field(
        default=1.0,
        json_schema_extra={"min_value": 0.5, "max_value": 2.0, "step": 0.1},
        description="Controls the speed of the speech.",
    )
    vol: float = Field(
        default=1.0,
        json_schema_extra={"min_value": 0.1, "max_value": 10.0, "step": 0.1},
        description="Controls the volume of the speech.",
    )
    pitch: int = Field(
        default=0,
        json_schema_extra={"min_value": -12, "max_value": 12, "step": 1},
        description="Controls the pitch of the speech.",
    )
    emotion: Literal[
        "happy", "sad", "angry", "fearful", "disgusted", "surprised", "neutral"
    ] = Field(default="neutral", description="Specifies the emotion of the speech.")


DEFAULT_OPENAI_INSTRUCTIONS = """\
Personality/affect: a high-energy cheerleader helping with administrative tasks 

Voice: Enthusiastic, and bubbly, with an uplifting and motivational quality.

Tone: Encouraging and playful, making even simple tasks feel exciting and fun.

Dialect: Casual and upbeat, using informal phrasing and pep talk-style expressions.

Pronunciation: Crisp and lively, with exaggerated emphasis on positive words to keep the energy high.

Features: Uses motivational phrases, cheerful exclamations, and an energetic rhythm to create a sense of excitement and engagement."""


class OpenAIConfig(BaseModel):
    instructions: str = Field(
        default=DEFAULT_OPENAI_INSTRUCTIONS,
        description="The instructions for the TTS model.",
        json_schema_extra={"require": True},
    )
    speed: float = Field(
        default=1.0,
        description="The speed of the TTS model.",
        json_schema_extra={
            "min_value": 0.25,
            "max_value": 4.0,
            "step": 0.01,
            "require": True,
        },
    )


class OrpheusConfig(BaseModel):
    temperature: float = Field(
        default=0.6,
        description="Temperature for generation",
        json_schema_extra={"min_value": 0.1, "max_value": 1.5, "step": 0.1},
    )
    top_p: float = Field(
        default=0.95,
        description="Top P for nucleus sampling",
        json_schema_extra={"min_value": 0.1, "max_value": 1.0, "step": 0.05},
    )
    repetition_penalty: float = Field(
        default=1.1,
        description="Repetition penalty",
        json_schema_extra={"min_value": 1.0, "max_value": 2.0, "step": 0.1},
    )


class ProviderItem(BaseModel):
    provider: str
    model_list: list[SubModel]
    name: str
    description: str
    configs: list[TTSModelConfig]


class TTSProviderListResponse(BaseModel):
    models: list[ProviderItem]


class GenerateTTSRequest(BaseModel):
    text: str
    provider: str
    model_id: str
    voice_id: str
    configs: Union[
        CartesiaTTSConfig,
        ElevenLabsTTSConfig,
        OpenAIConfig,
        FishAudioConfig,
        OrpheusConfig,
        MinimaxConfig,
        None,
    ] = None
    sync: bool = Field(
        default=True, description="sync should be true when using the API"
    )


class GenerateTTSResponse(BaseModel):
    task_id: str
    status: Literal["success", "failed"]
    details: Optional[AudioTaskDetails] = None
    error: Optional[str] = None
