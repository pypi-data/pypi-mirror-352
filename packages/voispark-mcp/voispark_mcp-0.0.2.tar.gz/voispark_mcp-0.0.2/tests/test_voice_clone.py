import unittest

from voispark_mcp.api.voice_clone import get_voice_clone_models
from voispark_mcp.msg.voice_clone_msg import VoiceCloneModelsResponse


class TestVoiceClone(unittest.IsolatedAsyncioTestCase):
    async def test_get_voice_clone_models(self):
        resp = await get_voice_clone_models()
        self.assertIsInstance(resp, dict)
        resp = VoiceCloneModelsResponse.model_validate(resp)
        self.assertIsInstance(resp, VoiceCloneModelsResponse)
