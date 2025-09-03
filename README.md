# AI Podcast Generator

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/) [![FastAPI](https://img.shields.io/badge/FastAPI-black?logo=fastapi)](https://fastapi.tiangolo.com/) [![Docker](https://img.shields.io/badge/Docker-black?logo=docker)](https://www.docker.com/)

Un generador de podcasts impulsado por IA que transforma transcripciones de texto en conversaciones de audio atractivas con múltiples presentadores. Este proyecto utiliza la API de **Google Gemini** para la generación de guiones y la API de **ElevenLabs** para una síntesis de texto a voz realista.

## Características

- **Generación Dinámica de Guiones:** Convierte texto sin formato en un guion de podcast conversacional.
- **Personalidades de Presentadores:** Asigna personalidades únicas a cada presentador para guiar el tono y estilo del diálogo.
- **Soporte Multi-presentador:** Admite dos presentadores con voces y personalidades distintas.
- **Voces Realistas:** Aprovecha la API de ElevenLabs para una síntesis de voz de alta calidad y sonido natural.
- **Estilo Personalizable:** Permite especificar el estilo del podcast (ej. "Educativo", "Humorístico").
- **API Flexible:** Ofrece endpoints separados para generar solo el guion o para generar el podcast completo con audio.
- **Contenerizado:** Incluye `Dockerfile` y `docker-compose.yml` para una configuración y despliegue sencillos.

## Cómo Empezar

### 1. Prerrequisitos

- Docker y Docker Compose instalados.
- Una clave de API para Google Gemini.
- Una clave de API para ElevenLabs.

### 2. Configuración

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/tu-usuario/Podcats.git
    cd Podcats
    ```

2.  **Crea tu archivo de entorno:**
    Copia el archivo de ejemplo `.env.example` a un nuevo archivo llamado `.env`.
    ```bash
    # En Windows
    copy .env.example .env

    # En macOS / Linux
    cp .env.example .env
    ```

3.  **Añade tus claves de API:**
    Abre el archivo `.env` y reemplaza los valores de marcador de posición con tus claves de API reales.
    ```env
    # Rename this file to .env and fill in your API keys.

    # Get your API key from Google AI Studio
    # https://aistudio.google.com/app/apikey
    GEMINI_API_KEY=TU_API_KEY_DE_GEMINI

    # Get your API key from your ElevenLabs profile
    # https://elevenlabs.io/subscription
    ELEVENLABS_API_KEY=TU_API_KEY_DE_ELEVENLABS
    ```

### 3. Ejecutar la Aplicación

Una vez que tu archivo `.env` esté configurado, puedes iniciar la aplicación usando Docker Compose:

```bash
docker-compose up --build
```

El servidor se iniciará y la API estará disponible en `http://localhost:8000`.

## Documentación de la API

La documentación interactiva completa de la API (generada por Swagger UI) está disponible automáticamente una vez que el servidor está en marcha.

- **URL de la Documentación:** **[http://localhost:8000/docs](http://localhost:8000/docs)**

### Endpoints Principales

A continuación se muestran ejemplos de los endpoints más importantes.

---

#### `POST /generate-script`

Genera un guion de podcast a partir de una transcripción, teniendo en cuenta la personalidad de los presentadores.

- **Cuerpo de la Petición:**
  ```json
  {
    "transcription": "La IA está avanzando a un ritmo increíble. Los recientes avances en los modelos de lenguaje grandes han abierto nuevas posibilidades.",
    "style": "Noticias de Tecnología",
    "presenters": [
      {
        "name": "Alex",
        "personality": "Entusiasta de la tecnología, siempre optimista sobre el futuro."
      },
      {
        "name": "Sara",
        "personality": "Analista crítica y escéptica, se enfoca en las implicaciones éticas."
      }
    ]
  }
  ```

- **Respuesta Exitosa (200):**
  ```json
  {
    "title": "El Futuro de la Inteligencia Artificial",
    "script": [
      {
        "speaker": "Alex",
        "line": "¡Bienvenidos de nuevo a 'Tecno-Futuro'!"
      },
      {
        "speaker": "Sara",
        "line": "Hola a todos. Hoy tenemos un tema que genera tanto entusiasmo como debate."
      }
    ]
  }
  ```

---

#### `POST /generate-audio-from-script`

Genera un archivo de audio a partir de un guion y un conjunto de presentadores con sus IDs de voz.

- **Cuerpo de la Petición:**
  ```json
  {
    "title": "El Futuro de la Inteligencia Artificial",
    "script": [
      {
        "speaker": "Alex",
        "line": "¡Bienvenidos de nuevo a 'Tecno-Futuro'!"
      },
      {
        "speaker": "Sara",
        "line": "Hola a todos. Hoy tenemos un tema que genera tanto entusiasmo como debate."
      }
    ],
    "presenters": [
      {
        "name": "Alex",
        "voice_id": "21m00Tcm4TlvDq8ikWAM"
      },
      {
        "name": "Sara",
        "voice_id": "29vD33N1CtxCmqQRPOHJ"
      }
    ],
    "return_base64": false
  }
  ```

- **Respuesta Exitosa (200):**
  ```json
  {
    "status": "success",
    "audio_file_url": "http://localhost:8000/files/El_Futuro_de_la_Inteligencia_Artificial_....mp3"
  }
  ```

---

#### `GET /files/{filename}`

Sirve un archivo de audio generado previamente. El nombre del archivo se obtiene de la respuesta de los endpoints que generan audio.

---

#### `GET /health`

Un endpoint simple para verificar que el servicio está en funcionamiento.

- **Respuesta Exitosa (200):**
  ```json
  {
    "status": "ok"
  }
  ```