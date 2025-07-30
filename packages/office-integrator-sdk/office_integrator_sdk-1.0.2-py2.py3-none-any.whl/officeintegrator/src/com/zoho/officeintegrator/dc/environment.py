from officeintegrator.src.com.zoho.api.authenticator.token import Token
from abc import abstractmethod, ABC

class Environment(ABC):

    @abstractmethod
    def get_url(self):
        pass

    @abstractmethod
    def get_dc(self) -> str:
        pass

    @abstractmethod
    def get_location(self) -> 'Token.Location':
        pass

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_value(self):
        pass