from voispark_mcp.core.api_request import get
from voispark_mcp.core.error_code import ErrorCode
from voispark_mcp.msg.base_resp import BaseResponse
from voispark_mcp.msg.voices_msg import (
    VoiceProvidersResponse,
    VoicesListResponse,
)


async def list_all_voices(provider_id: str, voice_type: str):
    resp = await get(
        f"/api/voices/{provider_id}/list",
        query={"type": voice_type},
        response_model=BaseResponse[VoicesListResponse],
    )
    if resp is None:
        return "Failed to list all voices"
    if resp.code != ErrorCode.SUCCESS.code:
        return "Failed to list all voices"
    if resp.data is None:
        return "No voices found"
    return resp.data.model_dump()


async def get_providers():
    resp = await get(
        "/api/voices/providers", response_model=BaseResponse[VoiceProvidersResponse]
    )
    if resp is None:
        return "Failed to get voice providers"
    if resp.code != ErrorCode.SUCCESS.code:
        return "Failed to get voice providers"
    if resp.data is None:
        return "No voice providers found"
    return resp.data.model_dump()
