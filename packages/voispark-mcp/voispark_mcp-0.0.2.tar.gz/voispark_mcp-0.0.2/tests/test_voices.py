import unittest

from voispark_mcp.api.voices import list_all_voices, get_providers
from voispark_mcp.msg.voices_msg import VoicesListResponse, VoiceProvidersResponse


class TestVoices(unittest.IsolatedAsyncioTestCase):
    async def test_list_all_voices(self):
        resp = await list_all_voices("cartesia", "default")
        self.assertIsInstance(resp, dict)
        resp = VoicesListResponse.model_validate(resp)
        self.assertIsInstance(resp, VoicesListResponse)

    async def test_get_providers(self):
        resp = await get_providers()
        self.assertIsInstance(resp, dict)
        resp = VoiceProvidersResponse.model_validate(resp)
        self.assertIsInstance(resp, VoiceProvidersResponse)
