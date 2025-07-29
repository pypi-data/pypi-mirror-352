from pydantic import BaseModel


class AudioFormat(BaseModel):
    """音频格式"""

    container: str
    encoding: str
    sample_rate: int
    channel: int


class AudioTaskDetails(BaseModel):
    """音频任务详情"""

    url: str
    format: AudioFormat
