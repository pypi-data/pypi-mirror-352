import unittest

from voispark_mcp.api.voice_changer import get_voice_changer_models
from voispark_mcp.msg.voice_changer_msg import VoiceChangerModelsResponse


class TestVoiceChanger(unittest.IsolatedAsyncioTestCase):
    async def test_get_voice_changer_models(self):
        resp = await get_voice_changer_models()
        self.assertIsInstance(resp, dict)
        resp = VoiceChangerModelsResponse.model_validate(resp)
        self.assertIsInstance(resp, VoiceChangerModelsResponse)
