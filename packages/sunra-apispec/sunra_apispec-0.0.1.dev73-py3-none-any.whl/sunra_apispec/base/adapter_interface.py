from enum import Enum
from typing import Callable

from sunra_apispec.base.output_schema import SunraFile


class RequestContentType(Enum):
    JSON = "application/json"
    FORM_DATA = "multipart/form-data"
    URL_ENCODED = "application/x-www-form-urlencoded"
    TEXT = "text/plain"
    BINARY = "application/octet-stream"
    

class ServiceProviderEnum(Enum):
    FAL = "fal"
    REPLICATE = "replicate"
    MINIMAX = "minimax"
    BLACK_FOREST_LABS = "black_forest_labs"
    VIDU = "vidu"
    VOLCENGINE = "volcengine"
    OPENAI = "openai"
    ELEVENLABS = "elevenlabs"


class IFalAdapter:
    def __init__(self):
       pass

    def convert_input(self, data) -> dict:
        pass

    def convert_output(
        self, 
        data, 
        processURLMiddleware: Callable[[str], SunraFile]
    ) -> dict:
        pass
    
    def get_request_url(self) -> str:
        pass

    def get_status_url(self, task_id: str) -> str:
        pass

    def get_result_url(self, task_id: str) -> str:
        pass

class IReplicateAdapter:
    def __init__(self):
        pass

    def convert_input(self, data) -> dict:
        pass

    def convert_output(
        self, 
        data, 
        processURLMiddleware: Callable[[str], SunraFile]
    ) -> dict:
        pass
    
    def get_request_url(self) -> str:
        pass

    def get_status_url(self, prediction_id: str) -> str:
        pass


class IMinimaxAdapter:
    def __init__(self):
        pass

    def convert_input(self, data) -> dict:
        pass

    def convert_output(
        self, 
        data, 
        processURLMiddleware: Callable[[str], SunraFile]
    ) -> dict:
        pass

    def get_request_url(self) -> str:
        pass

    def get_status_url(self, task_id: str) -> str:
        pass

    def get_file_url(self, file_id: str) -> str:
        pass


class IBlackForestLabsAdapter:
    def __init__(self):
        pass

    def convert_input(self, data) -> dict:
        pass

    def convert_output(
        self, 
        data, 
        processURLMiddleware: Callable[[str], SunraFile]
    ) -> dict:
        pass

    def get_bfl_model(self) -> str:
        pass


class IViduAdapter:
    def __init__(self):
        pass

    def convert_input(self, data) -> dict:
        pass

    def convert_output(
        self, 
        data, 
        processURLMiddleware: Callable[[str], SunraFile]
    ) -> dict:
        pass
    
    def get_request_url(self) -> str:
        pass


class IVolcengineAdapter:
    def __init__(self):
        pass
    
    def convert_input(self, data) -> dict:
        pass
    
    def convert_output(
        self, 
        data, 
        processURLMiddleware: Callable[[str], SunraFile]
    ) -> dict:
        pass

    def get_request_url(self) -> str:
        pass

    def get_status_url(self, task_id: str) -> str:
        pass


class IOpenAIAdapter:
    def __init__(self):
        pass
    
    def convert_input(self, data) -> dict:
        pass
    
    def convert_output(
        self, 
        data, 
        processURLMiddleware: Callable[[str], SunraFile]
    ) -> dict:
        pass

    def get_request_url(self) -> str:
        pass
    
    def get_api_key(self) -> str:
        pass


class IElevenLabsAdapter:
    def __init__(self):
        pass
    
    def convert_input(self, data) -> dict:
        pass
    
    def convert_output(
        self, 
        data, 
        processURLMiddleware: Callable[[str], SunraFile]
    ) -> dict:
        pass

    def get_request_content_type(self) -> RequestContentType:
        pass

    def get_request_url(self) -> str:
        pass



BaseAdapter = (
    IFalAdapter
    | IReplicateAdapter
    | IMinimaxAdapter
    | IBlackForestLabsAdapter
    | IViduAdapter
    | IVolcengineAdapter
    | IOpenAIAdapter
    | IElevenLabsAdapter
)
