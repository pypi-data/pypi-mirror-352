class GatewayExceptions:
    class UnexpectedError(Exception):
        '''
        Raised when an unexpected error occurs during interaction with the gateway.
        '''

    class ConnectionError(Exception):
        '''Raised when there is an error connecting to the gateway server.'''

    class AuthenticationError(Exception):
        '''Raised when there is an authentication error with the gateway server.'''

    class RegistrationError(Exception):
        '''Raised when endpoint registration fails.'''
