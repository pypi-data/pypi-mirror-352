import unittest

from voispark_mcp.api.tts import get_tts_models
from voispark_mcp.msg.tts_msg import TTSProviderListResponse


class TestTTS(unittest.IsolatedAsyncioTestCase):
    async def test_get_models(self):
        resp = await get_tts_models()
        self.assertIsInstance(resp, dict)
        resp = TTSProviderListResponse.model_validate(resp)
        self.assertIsInstance(resp, TTSProviderListResponse)
