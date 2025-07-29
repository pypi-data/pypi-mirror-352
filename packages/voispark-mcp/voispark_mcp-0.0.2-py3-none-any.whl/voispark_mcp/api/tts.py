from voispark_mcp.core.api_request import get, post
from voispark_mcp.core.error_code import ErrorCode
from voispark_mcp.msg.base_resp import BaseResponse
from voispark_mcp.msg.tts_msg import (
    TTSProviderListResponse,
    GenerateTTSRequest,
    GenerateTTSResponse,
)


async def get_tts_models():
    resp = await get(
        "/api/tts/models",
        response_model=BaseResponse[TTSProviderListResponse],
    )
    if resp is None:
        return "Failed to get tts models"
    if resp.code != ErrorCode.SUCCESS.code:
        return "Failed to get tts models"
    if resp.data is None:
        return "No tts models found"
    return resp.data.model_dump()


async def generate_tts(request: GenerateTTSRequest):
    resp = await post(
        "/api/tts/generate",
        data=request,
        response_model=BaseResponse[GenerateTTSResponse],
    )
    if resp is None:
        return "Failed to generate TTS audio"
    if resp.code != ErrorCode.SUCCESS.code:
        return "Failed to generate TTS audio"
    if resp.data is None:
        return "No task ID received for generated TTS audio"
    return resp.data.model_dump()
