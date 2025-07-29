from voispark_mcp.core.api_request import get, post
from voispark_mcp.core.error_code import ErrorCode
from voispark_mcp.msg.base_resp import BaseResponse
from voispark_mcp.msg.conversation_msg import (
    ConversationModelsResponse,
    GenerateConversationRequest,
    GenerateConversationResponse,
    GetSpeakerDetailsResponse,
    GetSpeakersResponse,
)


async def get_conversation_models():
    resp = await get(
        "/api/conversation/models",
        response_model=BaseResponse[ConversationModelsResponse],
    )
    if resp is None:
        return "Failed to get conversation models"
    if resp.code != ErrorCode.SUCCESS.code:
        return "Failed to get conversation models"
    if resp.data is None:
        return "No conversation models found"
    return resp.data.model_dump()


async def generate_conversation(request: GenerateConversationRequest):
    resp = await post(
        "/api/conversation/generate",
        data=request,
        response_model=BaseResponse[GenerateConversationResponse],
    )
    if resp is None:
        return "Failed to generate conversation"
    if resp.code != ErrorCode.SUCCESS.code:
        return "Failed to generate conversation"
    if resp.data is None:
        return "No task ID received for generated conversation"
    return resp.data.model_dump()


async def get_speaker_details(speaker_id: str):
    resp = await get(
        f"/api/conversation/speakers/{speaker_id}",
        response_model=BaseResponse[GetSpeakerDetailsResponse],
    )
    if resp is None:
        return "Failed to get speaker details"
    if resp.code != ErrorCode.SUCCESS.code:
        return "Failed to get speaker details"
    if resp.data is None:
        return "No speaker details found"
    return resp.data.model_dump()


async def get_speakers():
    resp = await get(
        "/api/conversation/speakers",
        response_model=BaseResponse[GetSpeakersResponse],
    )
    if resp is None:
        return "Failed to get speakers"
    if resp.code != ErrorCode.SUCCESS.code:
        return "Failed to get speakers"
    if resp.data is None:
        return "No speakers found"
    return resp.data.model_dump()
