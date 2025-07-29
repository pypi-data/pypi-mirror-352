import json
import os

import httpx

from .endpoint import Endpoint
from .exceptions import GatewayExceptions


class Gateway(GatewayExceptions):
    '''
    A class to interact with a gateway server for registering endpoints.
    '''

    def __init__(
        self, host: str | None = None, port: int | None = None, token: str | None = None
    ) -> None:
        '''
        Initializes the Gateway with the specified host, port, and token.

        Args:
            host (str | None):
                The host address of the gateway.
                If None, uses the environment variable 'GATEWAY_HOST'.
                If the environment variable is not set, defaults to 'localhost'.
            port (int | None):
                The port number of the gateway.
                If None, uses the environment variable 'GATEWAY_PORT'.
                If the environment variable is not set, defaults to 10000.
            token (str | None):
                The authentication token for the gateway.
                If None, uses the environment variable 'GATEWAY_TOKEN'.
                If the environment variable is not set, defaults to 'token'.
        '''

        self.host: str = host if host else os.getenv('GATEWAY_HOST', 'localhost')
        self.port: int = port if port else int(os.getenv('GATEWAY_PORT', '15000'))
        self.token: str = token if token else os.getenv('GATEWAY_TOKEN', 'token')
        self.register_endpoints_path: str = 'register-endpoints'

    @property
    def url(self) -> str:
        '''
        Constructs the base URL for the gateway server.

        Returns:
            str: The base URL for the gateway server.
        '''

        return f'http://{self.host}:{self.port}/'

    @property
    def register_endpoints_url(self) -> str:
        '''
        Constructs the full URL for endpoint registration.

        Returns:
            str: The full URL for the endpoint registration path.
        '''

        return f'{self.url}{self.register_endpoints_path}'

    async def register_endpoints(self, endpoints: list[Endpoint]) -> None:
        '''
        Registers the specified endpoints with the gateway server.

        Args:
            endpoints (list[Endpoint]):
                A list of Endpoint objects to be registered.

        Raises:
            ConnectionError:
                If the connection to the gateway server fails.
            AuthenticationError:
                If there is an issue with the provided token.
            RegistrationError:
                If the registration of endpoints fails.
        '''

        print(f'Gateway URL: {self.register_endpoints_url}')
        print(f'Gateway Token: {self.token}')
        print('Endpoints:')
        [print(f'   - {endpoint}') for endpoint in endpoints]

        try:
            async with httpx.AsyncClient() as client:
                client.headers = {'X-Gateway-Token': self.token}
                client.follow_redirects = False
                response: httpx.Response = await client.request(
                    method='POST',
                    url=self.register_endpoints_url,
                    content=json.dumps([e.model_dump() for e in endpoints]),
                )

                if response.status_code == 401:
                    raise self.AuthenticationError(
                        'Invalid authentication token provided.'
                    )

                if not response.status_code == 204:
                    status_code: int = response.status_code
                    raise self.RegistrationError(
                        f'Failed to register endpoints: {status_code}'
                    )

                print('Gateway: Sending endpoints sucess')
        except Exception as e:
            raise self.UnexpectedError(f'An unexpected error occurred: {e}') from e
