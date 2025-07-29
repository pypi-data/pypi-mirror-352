from typing import Literal
from voispark_mcp.core.api_request import get
from voispark_mcp.core.error_code import ErrorCode
from voispark_mcp.msg.base_resp import BaseResponse
from voispark_mcp.msg.history_msg import HistoryListResponse, HistoryResponse


async def get_history_list(
    source: Literal["tts", "voice_changer", "conversation"] = "tts",
):
    resp = await get(
        "/api/history/list",
        query={"source": source},
        response_model=BaseResponse[HistoryListResponse],
    )
    if resp is None:
        return "Failed to get history list"
    if resp.code != ErrorCode.SUCCESS.code:
        return "Failed to get history list"
    if resp.data is None:
        return "No history list found"
    return resp.data.model_dump()


async def get_history(history_id: str):
    resp = await get(
        f"/api/history/{history_id}",
        response_model=BaseResponse[HistoryResponse],
    )
    if resp is None:
        return "Failed to get history"
    if resp.code != ErrorCode.SUCCESS.code:
        return "Failed to get history"
    if resp.data is None:
        return "No history found"
    return resp.data.model_dump()
