import requests
from sunra_apispec.base.adapter_interface import IElevenLabsAdapter, RequestContentType
from sunra_apispec.base.output_schema import AudioOutput, SunraFile
from ...sunra_schema import AudioIsolationInput
from typing import Callable


class ElevenLabsVoiceIsolaterAdapter(IElevenLabsAdapter):
    """Adapter for ElevenLabs Voice Isolater audio isolation model."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's AudioIsolationInput to ElevenLabs API format."""
        # Validate the input data
        input_model = AudioIsolationInput.model_validate(data)

        response = requests.get(input_model.audio)
        audio_data = response.content

        return {
            "audio": ('audio.mp3', audio_data),
        }
        
    def get_request_content_type(self) -> RequestContentType:
        """Return the content type for the request."""
        return RequestContentType.FORM_DATA
    
    def get_request_url(self) -> str:
        """Return the base URL for ElevenLabs API."""
        return "https://api.elevenlabs.io/v1/audio-isolation"

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert ElevenLabs output to Sunra AudioOutput format."""
        if isinstance(data, str):
            sunra_file = processURLMiddleware(data)
            return AudioOutput(audio=sunra_file).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
