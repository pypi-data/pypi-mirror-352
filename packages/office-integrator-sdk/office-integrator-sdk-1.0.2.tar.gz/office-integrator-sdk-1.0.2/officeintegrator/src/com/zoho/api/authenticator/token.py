import enum
from abc import abstractmethod, ABC

from officeintegrator.src.com.zoho.api.authenticator.parsable_enum import ParsableEnum


class Token(ABC):
    """
    The class to verify and set token to the APIHTTPConnector instance, to authenticate requests.
    """

    @abstractmethod
    def authenticate(self, url_connection, config): pass

    @abstractmethod
    def remove(self): pass

    @abstractmethod
    def generate_token(self): pass

    def get_id(self): pass

    def get_authentication_schema(self): pass

    class Location(ParsableEnum):
        HEADER = "HEADER"
        PARAM = "PARAM"
        VARIABLE = "VARIABLE"

        @classmethod
        def parse(cls, location):
            return super().parse(location)

    class AuthenticationType(ParsableEnum):
        OAUTH2 = "OAUTH2"
        TOKEN = "TOKEN"

        @classmethod
        def parse(cls, type):
            return super().parse(type)

        def get_name(self):
            return self.name
