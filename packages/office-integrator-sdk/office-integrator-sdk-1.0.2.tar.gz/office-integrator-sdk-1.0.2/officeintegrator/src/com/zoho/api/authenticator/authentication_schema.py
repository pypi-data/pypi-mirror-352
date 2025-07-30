from abc import abstractmethod, ABC


class AuthenticationSchema(ABC):

    def get_authentication_type(self):
        pass

    def get_token_url(self):
        pass

    def get_refresh_url(self):
        pass

    def get_schema(self):
        pass
