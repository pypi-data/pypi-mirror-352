import requests
from typing import Callable
from sunra_apispec.base.adapter_interface import IElevenLabsAdapter, RequestContentType
from sunra_apispec.base.output_schema import SunraFile
from ...sunra_schema import SpeechToTextInput, TranscriptionOutput
from .schema import (
    ElevenLabsScribeV1Input,
)


# Language code mapping from description.md
LANGUAGE_CODE_MAP = {
    "Arabic": "ar",
    "Chinese": "zh",
    "English": "en",
    "French": "fr",
    "German": "de",
    "Hindi": "hi",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Portuguese": "pt",
    "Russian": "ru",
    "Spanish": "es",
    "Turkish": "tr",
    "Bengali": "bn",
    "Dutch": "nl",
    "Indonesian": "id",
    "Persian": "fa",
    "Swahili": "sw",
    "Thai": "th",
    "Vietnamese": "vi"
}


class ElevenLabsScribeV1Adapter(IElevenLabsAdapter):
    """Adapter for ElevenLabs Scribe V1 speech-to-text model."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's SpeechToTextInput to ElevenLabs API format."""
        # Validate the input data
        input_model = SpeechToTextInput.model_validate(data)
        
        # Get language code from language name if provided
        language_code = LANGUAGE_CODE_MAP.get(input_model.language)
        if not language_code:
            raise ValueError(f"Invalid language: {input_model.language}")

        self.request_url = f"https://api.elevenlabs.io/v1/speech-to-text"

        response = requests.get(input_model.audio)
        audio_data = response.content
        
        return {
            "file": ('audio.mp3', audio_data),
            "model_id": (None, "scribe_v1"),
            "language_code": (None, language_code),
            "tag_audio_events": (None, input_model.tag_audio_events),
            "diarize": (None, input_model.speaker_diarization),
        }
    
    def get_request_content_type(self) -> RequestContentType:
        """Return the content type for the request."""
        return RequestContentType.FORM_DATA
    
    def get_request_url(self) -> str:
        """Return the base URL for ElevenLabs API."""
        return self.request_url

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert the ElevenLabs output to Sunra TranscriptionOutput format."""
        # ElevenLabs Scribe returns transcription data in JSON format
        if isinstance(data, dict):
            return TranscriptionOutput.model_validate(data).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
