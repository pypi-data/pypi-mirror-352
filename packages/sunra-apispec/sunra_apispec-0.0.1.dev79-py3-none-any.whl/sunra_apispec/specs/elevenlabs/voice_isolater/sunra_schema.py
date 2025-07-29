from pydantic import BaseModel, Field
from pydantic import HttpUrl


class AudioIsolationInput(BaseModel):
    """Input schema for ElevenLabs Voice Isolater audio isolation."""
    
    audio: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Audio file URL."
    ) 