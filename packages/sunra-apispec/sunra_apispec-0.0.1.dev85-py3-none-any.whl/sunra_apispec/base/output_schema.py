from typing import List, Optional
from pydantic import BaseModel, Field

class SunraFile(BaseModel):
    content_type: str = Field(
        ...,
        description='The mime type of the file.',
        title='Content Type',
    )
    file_name: str = Field(
        ...,
        description='The name of the file. It will be auto-generated if not provided.',
        title='File Name',
    )
    file_size: int = Field(
        ...,
        description='The size of the file in bytes.',
        title='File Size',
    )
    url: str = Field(
        ...,
        description='The URL where the file can be downloaded from.',
        title='Url',
    )
    width: Optional[int] = Field(
        None,
        description='The width of the file in pixels.',
        title='Width',
    )
    height: Optional[int] = Field(
        None,
        description='The height of the file in pixels.',
        title='Height',
    )


class VideoOutput(BaseModel):
    video: SunraFile

class ImageOutput(BaseModel):
    image: SunraFile

class ImagesOutput(BaseModel):
    images: List[SunraFile]

class AudioOutput(BaseModel):
    audio: SunraFile

class ModelOutput(BaseModel):
    model: SunraFile
