import os
from typing import Callable
from sunra_apispec.base.adapter_interface import IOpenAIAdapter
from sunra_apispec.base.output_schema import SunraFile
from ...sunra_schema import SpeechToTextInput, SpeechToTextOutput
from .schema import OpenAITranscribeInput, OpenAITranscribeOutput


class OpenAISpeechToTextAdapter(IOpenAIAdapter):
    """Adapter for OpenAI Speech-to-Text API."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra's SpeechToTextInput to OpenAI's input format."""
        # Validate the input data
        input_model = SpeechToTextInput.model_validate(data)
        
        # Create OpenAI input with mapped values
        openai_input = OpenAITranscribeInput(
            file=str(input_model.audio),  # Convert URL to string
            model="gpt-4o-transcribe"
        )
        
        # Convert to dict, excluding None values
        return {
            "file": openai_input.file,
            "model": openai_input.model
        }
    
    def get_request_url(self) -> str:
        """Return the OpenAI Transcribe API URL."""
        return "https://api.openai.com/v1/audio/transcriptions"
    
    def get_api_key(self) -> str:
        """Get the OpenAI API key from environment variables."""
        return os.getenv("OPENAI_API_KEY", None)
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert OpenAI transcription output to Sunra TextOutput format."""
        if isinstance(data, dict):
            # Validate the OpenAI response
            openai_output = OpenAITranscribeOutput.model_validate(data)
            
            # Convert to Sunra TextOutput format - we only need the text field
            return SpeechToTextOutput(text=openai_output.text).model_dump(exclude_none=True, by_alias=True)
        else:
            raise ValueError(f"Invalid output type: {type(data)}")
