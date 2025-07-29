import os
from typing import Optional, Type, TypeVar

from pydantic import BaseModel

from aiohttp import ClientSession
import dotenv

dotenv.load_dotenv()

U = TypeVar("U", bound=BaseModel)
V = TypeVar("V", bound=BaseModel)

BASE_URL = os.getenv("VOISPARK_API_URL") or "https://api.voispark.com"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('VOISPARK_API_KEY')}",
}


async def get(
    path: str,
    query: Optional[dict] = None,
    response_model: Optional[Type[U]] = None,
) -> Optional[U]:
    async with ClientSession(headers=HEADERS, base_url=BASE_URL) as session:
        async with session.get(path, params=query) as response:
            if response_model:
                return response_model.model_validate_json(await response.text())
            return None


async def post(
    path: str,
    data: Optional[V] = None,
    response_model: Optional[Type[U]] = None,
) -> Optional[U]:
    async with ClientSession(headers=HEADERS, base_url=BASE_URL) as session:
        async with session.post(path, json=data) as response:
            if response_model:
                return response_model.model_validate_json(await response.text())
            return None


async def delete(
    path: str,
    response_model: Optional[Type[U]] = None,
) -> Optional[U]:
    async with ClientSession(headers=HEADERS, base_url=BASE_URL) as session:
        async with session.delete(path) as response:
            if response_model:
                return response_model.model_validate_json(await response.text())
            return None
