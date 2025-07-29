import os
from typing import Literal

from pydantic import BaseModel, field_serializer


class Endpoint(BaseModel):
    '''
    Represents an HTTP endpoint provided by a service.

    Attributes:
        service_name (str | None):
            The name of the service that the endpoint belongs to.
            If set to None, the value will be attempted to be loaded
            from the environment variable 'SERVICE_NAME' during serialization.
            Default is None
        port (int):
            The port number on which the service is available. Default is 10000
        path (str):
            The path of the endpoint within the service.
        method (Literal['GET', 'POST', 'PUT', 'DELETE']):
            The HTTP method used for requests to the endpoint.
            Must be one of 'GET', 'POST', 'PUT', or 'DELETE'. Defaults to 'GET'.
        required_session (bool):
            Whether an active session is required to access this endpoint.
            Default is True.
    '''

    service_name: str | None = None
    port: int = 10000
    path: str
    method: Literal['GET', 'POST', 'PUT', 'DELETE'] = 'GET'
    required_session: bool = True

    @field_serializer('service_name')
    def serialize_id(self, value: str | None) -> str:
        if isinstance(value, str):
            return value
        env_value: str | None = value or os.getenv('SERVICE_NAME', None)
        if env_value is None:
            raise Exception(
                'service_name is None and SERVICE_NAME environment variable is not set'
            )
        return env_value
