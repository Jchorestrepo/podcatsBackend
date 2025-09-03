"""API routes for the Podcast Generator."""
import os
import uuid
import base64
import re
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional

from .services import gemini, elevenlabs, audio

# Define router
router = APIRouter()

# --- Helper Function ---
def sanitize_filename(title: str) -> str:
    """
    Sanitizes a string to be used as a valid filename.
    Replaces spaces with underscores and removes characters that are not
    alphanumeric, underscores, or hyphens.
    Limits the length to 200 characters to avoid issues with file systems.
    """
    s = title.strip().replace(' ', '_')
    s = re.sub(r'(?u)[^\w\-\_]', '', s)
    return s[:200]

# --- Pydantic Models for Request/Response ---

class Presenter(BaseModel):
    name: str = Field(..., description="Name of the presenter.")
    voice_id: str = Field(..., description="ElevenLabs voice ID for this presenter.")

class PresenterName(BaseModel):
    name: str = Field(..., description="Name of the presenter.")

class ScriptLine(BaseModel):
    speaker: str
    line: str

# Models for the new endpoints
class ScriptRequest(BaseModel):
    transcription: str = Field(..., description="The full text transcription to be converted into a podcast script.")
    style: str = Field("Conversacional", description="Style of the podcast (e.g., 'Educativo', 'Humorístico').")
    presenters: List[PresenterName] = Field(..., min_items=2, max_items=2, description="A list of exactly two presenters with their names.")

class ScriptResponse(BaseModel):
    title: str
    script: List[ScriptLine]

class AudioFromScriptRequest(BaseModel):
    title: str = Field(..., description="Title of the podcast.")
    script: List[ScriptLine] = Field(..., description="The script to be converted to audio.")
    presenters: List[Presenter] = Field(..., min_items=2, max_items=2, description="A list of presenters with their names and voice_ids.")
    return_base64: bool = Field(False, description="If true, returns the audio as a Base64 string instead of a URL.")

class AudioResponse(BaseModel):
    status: str
    audio_file_url: Optional[str] = None
    audio_base64: Optional[str] = None

# Model for the original all-in-one endpoint
class PodcastRequest(BaseModel):
    style: str = Field(..., description="Style of the podcast (e.g., 'Educativo', 'Humorístico').")
    presenters: List[Presenter] = Field(..., min_items=2, max_items=2, description="A list of exactly two presenters.")
    transcription: str = Field(..., description="The full text transcription to be converted into a podcast.")
    return_base64: bool = Field(False, description="If true, returns the audio as a Base64 string instead of a URL.")

class PodcastResponse(BaseModel):
    title: str
    status: str
    script: List[ScriptLine]
    audio_file_url: Optional[str] = None
    audio_base64: Optional[str] = None


# --- Directory Paths ---

FILES_DIR = "files"
os.makedirs(FILES_DIR, exist_ok=True)

# --- API Endpoints ---

@router.get("/health", summary="Health Check")
async def health_check():
    """A simple endpoint to verify that the service is running."""
    return {"status": "ok"}

# --- NEW ENDPOINTS ---

@router.post("/generate-script", response_model=ScriptResponse, summary="1. Generate Script from Transcription")
async def generate_script_only(request_data: ScriptRequest):
    """
    Receives a transcription and returns a structured JSON script without generating audio.
    """
    try:
        script_data = gemini.generate_script(
            transcription=request_data.transcription,
            style=request_data.style,
            presenters=[p.dict() for p in request_data.presenters]
        )
        return script_data
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/generate-audio-from-script", response_model=AudioResponse, summary="2. Generate Audio from a Script")
async def generate_audio_from_script(request_data: AudioFromScriptRequest, request: Request):
    """
    Receives a structured JSON script and generates the final audio file.
    """
    try:
        script = request_data.script
        voice_map = {p.name: p.voice_id for p in request_data.presenters}
        
        audio_chunks_paths = []
        podcast_id = str(uuid.uuid4())

        for i, line in enumerate(script):
            speaker_name = line.speaker
            dialogue = line.line
            
            voice_id = voice_map.get(speaker_name)
            if not voice_id:
                print(f"Warning: Speaker '{speaker_name}' not found in presenters list. Skipping line.")
                continue

            chunk_path = os.path.join(FILES_DIR, f"{podcast_id}_chunk_{i}.mp3")
            elevenlabs.generate_audio_for_line(dialogue, voice_id, chunk_path)
            audio_chunks_paths.append(chunk_path)

        sanitized_title = sanitize_filename(request_data.title)
        final_audio_filename = f"{sanitized_title}_{podcast_id}.mp3"
        final_audio_path = os.path.join(FILES_DIR, final_audio_filename)
        audio.combine_audio_files(audio_chunks_paths, final_audio_path)
        audio.cleanup_files(audio_chunks_paths)

        response_data = {"status": "success"}
        if request_data.return_base64:
            with open(final_audio_path, "rb") as audio_file:
                encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
            response_data["audio_base64"] = encoded_string
            audio.cleanup_files([final_audio_path])
        else:
            base_url = str(request.base_url)
            response_data["audio_file_url"] = f"{base_url}files/{final_audio_filename}"
            
        return response_data
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


# --- ORIGINAL ALL-IN-ONE ENDPOINT ---

@router.post("/generate-podcast", response_model=PodcastResponse, summary="Generate Full Podcast (All-in-One)")
async def generate_podcast(request_data: PodcastRequest, request: Request):
    """
    Main endpoint to generate a podcast from start to finish.
    """
    try:
        # 1. Generate script
        script_data = gemini.generate_script(
            transcription=request_data.transcription,
            style=request_data.style,
            presenters=[p.dict() for p in request_data.presenters]
        )
        title = script_data["title"]
        script = script_data["script"]

        # 2. Generate audio from the new script
        voice_map = {p.name: p.voice_id for p in request_data.presenters}
        audio_chunks_paths = []
        podcast_id = str(uuid.uuid4())

        for i, line in enumerate(script):
            speaker_name = line.get("speaker")
            dialogue = line.get("line")
            
            if not speaker_name or not dialogue:
                continue

            voice_id = voice_map.get(speaker_name)
            if not voice_id:
                print(f"Warning: Speaker '{speaker_name}' not found in presenters list. Skipping line.")
                continue

            chunk_path = os.path.join(FILES_DIR, f"{podcast_id}_chunk_{i}.mp3")
            elevenlabs.generate_audio_for_line(dialogue, voice_id, chunk_path)
            audio_chunks_paths.append(chunk_path)

        # 3. Combine and clean up
        sanitized_title = sanitize_filename(title)
        final_audio_filename = f"{sanitized_title}_{podcast_id}.mp3"
        final_audio_path = os.path.join(FILES_DIR, final_audio_filename)
        audio.combine_audio_files(audio_chunks_paths, final_audio_path)
        audio.cleanup_files(audio_chunks_paths)

        # 4. Prepare response
        response_data = {
            "title": title,
            "status": "success",
            "script": script,
        }

        if request_data.return_base64:
            with open(final_audio_path, "rb") as audio_file:
                encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
            response_data["audio_base64"] = encoded_string
            audio.cleanup_files([final_audio_path])
        else:
            base_url = str(request.base_url)
            response_data["audio_file_url"] = f"{base_url}files/{final_audio_filename}"
            
        return response_data

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get("/files/{filename}", summary="Serve Generated Audio Files")
async def get_file(filename: str):
    """
    Serves a generated audio file from the 'files' directory.
    """
    file_path = os.path.join(FILES_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg", filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found.")