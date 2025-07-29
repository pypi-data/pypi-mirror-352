"""
Script to test the VoiceAgent using microphone input and speaker output.

This script initializes a VoiceAgent instance and allows users to interact with it via speech.
All audio-related operations (input/output handling) are abstracted away.

Requirements:
    pip install pyaudio python-dotenv

"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from agent_builder.builders.voice_agent_builder import VoiceAgentBuilder
from agent_builder.utils.audio_utils import AudioHandler

load_dotenv()

# API Configuration
AZURE_GPT4O_REALTIME_PREVIEW_URL = os.getenv("AZURE_GPT4O_REALTIME_PREVIEW_URL")
AZURE_GPT4O_REALTIME_PREVIEW_KEY = os.getenv("AZURE_GPT4O_REALTIME_PREVIEW_KEY")

INSTRUCTIONS = """
You are an assistant
"""

# User-defined audio parameters (can be modified)
FRAME_SIZE = 3200  # Adjust for lower latency if needed
RATE = 24000  # Sampling rate in Hz
CHANNELS = 1  # 1 = Mono, 2 = Stereo


async def main():
    # Logging Setup
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Build the VoiceAgent
    builder = (
        VoiceAgentBuilder()
        .set_api_key(AZURE_GPT4O_REALTIME_PREVIEW_KEY)
        .set_model_url(AZURE_GPT4O_REALTIME_PREVIEW_URL)
        .set_goal(INSTRUCTIONS)
    )
    voice_agent = builder.build()

    # Initialize Audio Handler
    audio_handler = AudioHandler(frame_size=FRAME_SIZE, rate=RATE, channels=CHANNELS)

    print("VoiceAgent is ready. Start speaking. Press Ctrl+C to stop.")

    # Start audio playback and input tasks
    playback_task = asyncio.create_task(audio_handler.play_audio())
    input_task = asyncio.create_task(
        voice_agent.ainvoke(
            audio_handler.audio_input_generator(), audio_handler.output_handler
        )
    )

    try:
        await input_task
    except Exception as e:
        logger.error(f"Error during agent interaction: {e}")
    finally:
        playback_task.cancel()
        await playback_task
        audio_handler.close()


if __name__ == "__main__":
    asyncio.run(main())