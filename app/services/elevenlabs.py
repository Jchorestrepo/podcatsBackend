"""Service for interacting with the ElevenLabs API."""
import os
import requests
from fastapi import HTTPException

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

def generate_audio_for_line(line: str, voice_id: str, output_path: str):
    """
    Generates audio for a single line of text using ElevenLabs API.

    Args:
        line: The text to convert to speech.
        voice_id: The ID of the ElevenLabs voice to use.
        output_path: The path to save the generated MP3 file.

    Raises:
        HTTPException: If the API key is missing or the API call fails.
    """
    if not ELEVENLABS_API_KEY:
        raise HTTPException(status_code=500, detail="ELEVENLABS_API_KEY is not set.")

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": line,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    try:
        response = requests.post(
            ELEVENLABS_API_URL.format(voice_id=voice_id),
            headers=headers,
            json=data,
            timeout=60
        )
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling ElevenLabs API: {e}")
