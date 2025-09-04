"""Service for interacting with the ElevenLabs API."""
import os
import requests
from fastapi import HTTPException

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_API_URL_BASE = "https://api.elevenlabs.io/v1"

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
        "model_id": os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2"),
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    try:
        url = f"{ELEVENLABS_API_URL_BASE}/text-to-speech/{voice_id}"
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling ElevenLabs API: {e}")

def check_elevenlabs_api():
    """
    Checks if the ElevenLabs API is available.
    """
    if not ELEVENLABS_API_KEY:
        return {"status": "error", "message": "ELEVENLABS_API_KEY is not set."}

    headers = {"xi-api-key": ELEVENLABS_API_KEY}
    try:
        url = f"{ELEVENLABS_API_URL_BASE}/voices"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return {"status": "ok"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}
