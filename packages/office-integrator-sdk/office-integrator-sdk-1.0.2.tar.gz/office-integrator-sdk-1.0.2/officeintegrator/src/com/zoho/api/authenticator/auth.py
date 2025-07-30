from .token import Token
from officeintegrator.src.com.zoho.officeintegrator.exception import SDKException
from officeintegrator.src.com.zoho.officeintegrator.util import Constants
from officeintegrator.src.com.zoho.api.authenticator.authentication_schema import AuthenticationSchema


class Auth(Token):
    parameter_map = {}
    header_map = {}

    def __init__(self, parameter_map=None, header_map=None, authentication_schema=None):
        self.parameter_map = parameter_map
        self.header_map = header_map
        self.authentication_schema = authentication_schema

    def get_authentication_schema(self):
        return self.authentication_schema

    def set_authentication_schema(self, authentication_schema):
        self.authentication_schema = authentication_schema

    def authenticate(self, url_connection, config):
        if len(self.header_map) > 0:
            for header in self.header_map.keys():
                url_connection.add_header(header, self.header_map.get(header))
        if len(self.parameter_map) > 0:
            for param in self.parameter_map.keys():
                url_connection.add_param(param, self.parameter_map.get(param))

    def remove(self):
        return super().remove()

    def get_id(self):
        return None
    
    def generate_token(self):
        return super().generate_token()

    class Builder:
        def __init__(self):
            self.parameter_map = {}
            self.header_map = {}
            self._authentication_schema = None

        def add_param(self, param_name, param_value):
            if param_name in self.parameter_map and len(self.parameter_map.get(param_name)) == 0:
                existing_param_value = self.parameter_map.get(param_name)
                existing_param_value = existing_param_value + "," + param_value
                self.parameter_map[param_name] = existing_param_value
            else:
                self.parameter_map[param_name] = param_value
            return self

        def add_header(self, header_name, header_value):
            if header_name in self.header_map and len(self.header_map.get(header_name)) == 0:
                existing_header_value = self.header_map.get(header_name)
                existing_header_value = existing_header_value + "," + header_value
                self.header_map[header_name] = existing_header_value
            else:
                self.header_map[header_name] = header_value
            return self

        def parameter_map(self, parameter_map):
            self.parameter_map = parameter_map
            return self

        def header_map(self, header_map):
            self.header_map = header_map
            return self

        def authentication_schema(self, _authentication_schema):
            if isinstance(_authentication_schema, AuthenticationSchema):
                self._authentication_schema = _authentication_schema
            return self

        def build(self):
            if self._authentication_schema is None:
                raise SDKException(Constants.MANDATORY_VALUE_ERROR,
                                   Constants.MANDATORY_KEY_ERROR + "-" + Constants.OAUTH_MANDATORY_KEYS_1)
            return Auth(parameter_map=self.parameter_map, header_map=self.header_map,
                        authentication_schema=self._authentication_schema)