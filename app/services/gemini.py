"""Service for interacting with the Google Gemini API."""
import os
import requests
import json
from fastapi import HTTPException

# It's better to get the key here where it's used.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL_BASE = "https://generativelanguage.googleapis.com/v1beta"

def generate_script(transcription: str, style: str, presenters: list[dict]) -> dict:
    """
    Generates a conversational script using the Gemini API.

    Args:
        transcription: The source text to base the script on.
        style: The desired style of the podcast (e.g., "Educativo").
        presenters: A list of presenters with their names.

    Returns:
        A dictionary containing the title and the script.
    
    Raises:
        HTTPException: If the API key is missing or the API call fails.
    """
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set.")

    presenter_names = " y ".join([p["name"] for p in presenters])
    
    prompt = f"""
    Actúa como un guionista experto de podcasts.
    Tu tarea es transformar la siguiente transcripción en un guion conversacional y dinámico para un podcast.
    El guion debe ser para dos presentadores: {presenter_names}.
    El estilo del podcast es: {style}.

    Reglas estrictas para el formato de salida:
    1.  La salida DEBE ser un objeto JSON válido.
    2.  El objeto JSON principal debe tener dos claves: "title" y "script".
    3.  El valor de "title" debe ser un título creativo y corto para el podcast, basado en la transcripción.
    4.  El valor de "script" debe ser una lista de objetos.
    5.  Cada objeto en la lista "script" debe tener dos claves: "speaker" y "line".
    6.  El valor de "speaker" debe ser exactamente uno de los nombres de los presentadores.
    7.  El valor de "line" debe ser el diálogo para ese presentador.
    8.  No incluyas texto, explicaciones o markdown fuera del JSON. La respuesta debe ser solo el JSON.

    Ejemplo de formato de salida:
    {{
      "title": "El Futuro de la Inteligencia Artificial",
      "script": [
        {{ "speaker": "{presenters[0]['name']}", "line": "Bienvenidos a nuestro podcast." }},
        {{ "speaker": "{presenters[1]['name']}", "line": "Hoy, exploraremos un tema fascinante." }}
      ]
    }}

    Transcripción original:
    ---
    {transcription}
    ---
    """

    headers = {
        "Content-Type": "application/json",
    }
    params = {
        "key": GEMINI_API_KEY
    }
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "response_mime_type": "application/json",
        }
    }

    try:
        url = f"{GEMINI_API_URL_BASE}/models/gemini-1.5-flash:generateContent"
        response = requests.post(url, headers=headers, params=params, json=data, timeout=120)
        response.raise_for_status()
        
        # The response from Gemini should be a JSON string, which needs to be parsed.
        response_text = response.json()['candidates'][0]['content']['parts'][0]['text']
        response_data = json.loads(response_text)
        
        if not isinstance(response_data, dict) or "title" not in response_data or "script" not in response_data:
            raise ValueError("La respuesta de Gemini no tiene el formato esperado de {{'title': ..., 'script': ...}}.")

        return response_data

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling Gemini API: {e}")
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f"Error processing Gemini response: {e}. Response text: {response.text}")

def check_gemini_api():
    """
    Checks if the Gemini API is available.
    """
    if not GEMINI_API_KEY:
        return {"status": "error", "message": "GEMINI_API_KEY is not set."}

    params = {"key": GEMINI_API_KEY}
    try:
        url = f"{GEMINI_API_URL_BASE}/models"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return {"status": "ok"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}
