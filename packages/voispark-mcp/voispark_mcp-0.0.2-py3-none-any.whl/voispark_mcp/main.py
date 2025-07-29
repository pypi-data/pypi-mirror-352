from contextlib import asynccontextmanager
from dataclasses import dataclass
import logging
from typing import AsyncIterator, Literal, Union
from mcp.server.fastmcp import FastMCP

from voispark_mcp.api.conversation import (
    get_conversation_models as _get_conversation_models,
    generate_conversation as _generate_conversation,
    get_speaker_details as _get_speaker_details,
    get_speakers as _get_speakers,
)
from voispark_mcp.api.tts import get_tts_models as _get_tts_models
from voispark_mcp.api.tts import generate_tts as _generate_tts
from voispark_mcp.api.voice_clone import (
    get_voice_clone_models as _get_voice_clone_models,
    clone_voice as _clone_voice,
)
from voispark_mcp.api.voice_changer import (
    get_voice_changer_models as _get_voice_changer_models,
    change_voice as _change_voice,
)
from voispark_mcp.api.voices import list_all_voices as _list_all_voices
from voispark_mcp.api.voices import get_providers as _get_providers
from voispark_mcp.api.history import (
    get_history_list as _get_history_list,
    get_history as _get_history,
)
from voispark_mcp.msg.conversation_msg import (
    GenerateConversationRequest,
    ConversationTurn,
    SpeakerConfigItem,
)
from voispark_mcp.msg.tts_msg import GenerateTTSRequest
from voispark_mcp.msg.voice_changer_msg import ChangeVoiceRequest
from voispark_mcp.msg.voice_clone_msg import (
    CartesiaVoiceCloneConfig,
    CloneVoiceRequest,
    MiniMaxVoiceCloneConfig,
)


@dataclass
class AppContext:
    pass


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    # Initialize on startup
    logging.info("Starting MCP server")
    try:
        yield AppContext()
    finally:
        # Cleanup on shutdown
        logging.info("Shutting down MCP server")


# Create an MCP server
mcp = FastMCP("Voispark MCP", lifespan=app_lifespan)


# -*- conversation -*-


@mcp.resource(uri="conversation://models")
async def get_conversation_models() -> str | dict:
    """
    Get all available conversation models and their parameters.
    This resource should be called first to retrieve model specifications
    before generating any conversations.
    """
    return await _get_conversation_models()


@mcp.tool()
async def generate_conversation(
    provider: str,
    conversation: list[ConversationTurn],
    speaker: list[SpeakerConfigItem],
) -> str | dict:
    """
    Generate AI conversation with specified parameters.

    Prerequisites:
    1. First call 'conversation://models' resource to get available providers and model parameters
    2. Call 'conversation://speakers' resource to get available speakers for configuration

    Args:
        provider: The conversation provider obtained from 'conversation://models'
        conversation: List of conversation turns defining the dialogue structure
        speaker: List of speaker configurations obtained from 'conversation://speakers'

    Returns:
        Task details with conversation generation status and task ID
    """
    request = GenerateConversationRequest(
        provider=provider, conversation=conversation, speaker=speaker
    )
    return await _generate_conversation(request)


@mcp.tool()
async def get_speaker_details(speaker_id: str) -> str | dict:
    """
    Get detailed information about a specific speaker.

    Prerequisites:
    1. Obtain speaker_id from 'conversation://speakers' resource first

    Args:
        speaker_id: The unique identifier of the speaker

    Returns:
        Detailed speaker information including voice characteristics and capabilities
    """
    return await _get_speaker_details(speaker_id)


@mcp.resource(uri="conversation://speakers")
async def get_speakers() -> str | dict:
    """
    Get all available speakers for conversation generation.
    This resource provides speaker configurations needed for conversation generation.
    Call this before using the generate_conversation tool to obtain valid speaker parameters.
    """
    return await _get_speakers()


# -*- text_to_speech -*-


@mcp.resource(uri="textToSpeech://models")
async def get_tts_models() -> str | dict:
    """
    Get all available TTS (Text-to-Speech) models and their configurations.
    This resource should be called first to retrieve provider information, model specifications,
    and voice parameters before generating any TTS audio.
    """
    return await _get_tts_models()


@mcp.tool()
async def generate_tts(
    provider: str,
    text: str,
    model_id: str,
    voice_id: str,
) -> str | dict:
    """
    Generate TTS (Text-to-Speech) audio from text input.

    Prerequisites:
    1. Call 'textToSpeech://models' resource to get available providers, models, and voices
    2. Optionally call 'voices://providers' and 'voices://{provider_id}/{voice_type}/list'
       to explore additional voice options

    Args:
        provider: TTS provider name obtained from 'textToSpeech://models'
        text: The text content to convert to speech
        model_id: The TTS model identifier from the provider's model list
        voice_id: The voice identifier compatible with the selected provider and model

    Returns:
        Task details with TTS generation status and audio file information
    """
    request = GenerateTTSRequest(
        provider=provider,
        text=text,
        model_id=model_id,
        voice_id=voice_id,
    )
    return await _generate_tts(request)


# -*- voice_changer -*-


@mcp.resource(uri="voiceChanger://models")
async def get_voice_changer_models() -> str | dict:
    """
    Get all available voice changer models and their configurations.
    This resource should be called first to retrieve provider information and model specifications
    before performing any voice transformation operations.
    """
    return await _get_voice_changer_models()


@mcp.tool()
async def change_voice(
    provider: str,
    model_id: str,
    voice_id: str,
    audio_data: str,
) -> str | dict:
    """
    Transform an existing audio file to use a different voice.

    Prerequisites:
    1. Call 'voiceChanger://models' resource to get available providers and models
    2. Optionally call 'voices://providers' and 'voices://{provider_id}/{voice_type}/list'
       to explore available target voices

    Args:
        provider: Voice changer provider name obtained from 'voiceChanger://models'
        model_id: The voice changer model identifier from the provider's model list
        voice_id: The target voice identifier to transform the audio into
        audio_data: Base64 encoded audio file to be transformed

    Returns:
        Task details with voice transformation status and processed audio information
    """
    request = ChangeVoiceRequest(
        provider=provider,
        model_id=model_id,
        voice_id=voice_id,
        audio_data=audio_data,
    )
    return await _change_voice(request)


# -*- voice_clone -*-


@mcp.resource(uri="voiceClone://models")
async def get_voice_clone_models() -> str | dict:
    """
    Get all available voice clone models and their configurations.
    This resource should be called first to retrieve provider information and model specifications
    before performing any voice cloning operations.
    """
    return await _get_voice_clone_models()


@mcp.tool()
async def clone_voice(
    provider: str,
    model_id: str,
    audio_data: str,
    configs: Union[CartesiaVoiceCloneConfig, MiniMaxVoiceCloneConfig],
) -> str | dict:
    """
    Clone a voice from an audio sample to create a new synthetic voice.

    Prerequisites:
    1. Call 'voiceClone://models' resource to get available providers and models
    2. Prepare audio sample (recommended: 10-30 seconds of clean speech)
    3. Configure provider-specific settings based on the selected model

    Args:
        provider: Voice clone provider name obtained from 'voiceClone://models'
        model_id: The voice clone model identifier from the provider's model list
        audio_data: Base64 encoded audio sample for voice cloning
        configs: Provider-specific configuration (CartesiaVoiceCloneConfig or MiniMaxVoiceCloneConfig)

    Returns:
        Voice clone task details with processing status and cloned voice information
    """
    request = CloneVoiceRequest(
        provider=provider, model_id=model_id, audio_data=audio_data, configs=configs
    )
    return await _clone_voice(request)


# -*- voices -*-


@mcp.resource(uri="voices://providers")
async def get_providers() -> str | dict:
    """
    Get all available voice providers and their supported capabilities.
    This resource provides information about different voice service providers
    and their supported features (TTS, voice changing, voice cloning, etc.).
    """
    return await _get_providers()


@mcp.resource(uri="voices://{provider_id}/{voice_type}/list")
async def list_all_voices(provider_id: str, voice_type: str) -> str | dict:
    """
    List all available voices from a specific provider for a given voice type.

    Prerequisites:
    1. Call 'voices://providers' resource first to get available provider_id values

    Args:
        provider_id: The voice provider identifier (e.g., 'elevenlabs', 'cartesia')
        voice_type: The type of voices to list (e.g., 'tts', 'voice_changer', 'voice_clone')

    Returns:
        List of voices with their IDs, names, descriptions, and preview URLs
    """
    return await _list_all_voices(provider_id, voice_type)


# -*- history -*-


@mcp.resource(uri="history://list")
async def get_history_list(
    source: Literal["tts", "voice_changer", "conversation"] = "tts",
) -> str | dict:
    """
    Get a list of historical tasks for a specific service type.
    This resource allows tracking and reviewing previously executed tasks.

    Args:
        source: The service type to get history for ('tts', 'voice_changer', 'conversation')

    Returns:
        List of historical tasks with their IDs, status, and basic information
    """
    return await _get_history_list(source)


@mcp.resource(uri="history://{history_id}")
async def get_history(history_id: str) -> str | dict:
    """
    Get detailed information about a specific historical task.

    Prerequisites:
    1. Call 'history://list' resource first to get available history_id values

    Args:
        history_id: The unique identifier of the historical task

    Returns:
        Detailed task information including parameters, status, results, and timestamps
    """
    return await _get_history(history_id)


def main():
    """Entry point for the voispark_mcp command."""
    mcp.run()
