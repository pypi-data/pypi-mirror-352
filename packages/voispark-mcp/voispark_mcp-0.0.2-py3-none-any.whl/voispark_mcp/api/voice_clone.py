from voispark_mcp.core.api_request import get, post
from voispark_mcp.core.error_code import ErrorCode
from voispark_mcp.msg.base_resp import BaseResponse
from voispark_mcp.msg.voice_clone_msg import (
    VoiceCloneModelsResponse,
    CloneVoiceRequest,
    CloneVoiceResponse,
)


async def get_voice_clone_models():
    resp = await get(
        "/api/voice_clone/models", response_model=BaseResponse[VoiceCloneModelsResponse]
    )
    if resp is None:
        return "Failed to get voice clone models"
    if resp.code != ErrorCode.SUCCESS.code:
        return "Failed to get voice clone models"
    if resp.data is None:
        return "No voice clone models found"
    return resp.data.model_dump()


async def clone_voice(request: CloneVoiceRequest):
    resp = await post(
        "/api/voice_clone/clone",
        data=request,
        response_model=BaseResponse[CloneVoiceResponse],
    )
    if resp is None:
        return "Failed to clone voice"
    if resp.code != ErrorCode.SUCCESS.code:
        return "Failed to clone voice"
    if resp.data is None:
        return "No response data received for voice cloning"
    return resp.data.model_dump()
