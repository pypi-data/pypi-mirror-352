class Exceptions:
    class RequestError(Exception):
        '''Exception raised for general request errors.'''

        pass

    class RequestTimeoutError(Exception):
        '''Exception raised when a request times out.'''

        pass

    class ExtractJsonError(Exception):
        '''Exception raised when JSON extraction fails.'''

        pass

    class ExtractTextError(Exception):
        '''Exception raised when text extraction fails.'''

        pass
