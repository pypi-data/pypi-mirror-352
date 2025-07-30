
try:
    import threading
    import logging
    import enum
    import json
    import time
    import requests
    from .token import Token
    from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer
    from officeintegrator.src.com.zoho.officeintegrator.util.api_http_connector import APIHTTPConnector
    from officeintegrator.src.com.zoho.officeintegrator.exception import SDKException
    from officeintegrator.src.com.zoho.officeintegrator.util.constants import Constants
    from officeintegrator.src.com.zoho.officeintegrator.user_signature import UserSignature
    from officeintegrator.src.com.zoho.api.authenticator.authentication_schema import AuthenticationSchema

except Exception as e:
    import threading
    import logging
    import enum
    import json
    import time
    import requests
    from .token import Token
    from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer
    from officeintegrator.src.com.zoho.officeintegrator.util.api_http_connector import APIHTTPConnector
    from officeintegrator.src.com.zoho.officeintegrator.exception.sdk_exception import SDKException
    from officeintegrator.src.com.zoho.officeintegrator.util.constants import Constants
    from .authentication_schema import AuthenticationSchema


class OAuth2(Token):
    """
    This class maintains the tokens and authenticates every request.
    """

    logger = logging.getLogger('SDKLogger')
    lock = threading.Lock()

    def __init__(self, client_id=None, client_secret=None, grant_token=None, refresh_token=None, redirect_url=None,
                 id=None, access_token=None, user_signature=None, authentication_schema=None):

        """
        Creates an OAuthToken class instance with the specified parameters.

        Parameters:
            client_id (str) : A string containing the OAuth client id.
            client_secret (str) : A string containing the OAuth client secret.
            grant_token (str) : A string containing the GRANT token.
            refresh_token (str) : A string containing the REFRESH token.
            redirect_url (str) : A string containing the OAuth redirect URL. Default value is None
            id (str) : A string containing the Id. Default value is None
            user_signature(UserSignature) : An instance of UserSignature
            authentication_schema(AuthenticationSchema) : An instance of AuthenticationSchema
        """

        error = {}

        if grant_token is None and refresh_token is None and id is None and access_token is None and user_signature is None:
            raise SDKException(code=Constants.MANDATORY_VALUE_ERROR, message=Constants.MANDATORY_KEY_ERROR,
                               details=Constants.OAUTH_MANDATORY_KEYS)

        if id is None and access_token is None and user_signature is None:
            if not isinstance(client_id, str):
                error[Constants.FIELD] = Constants.CLIENT_ID
                error[Constants.EXPECTED_TYPE] = Constants.STRING
                error[Constants.CLASS] = OAuth2.__name__
                raise SDKException(code=Constants.TOKEN_ERROR, details=error)

            if not isinstance(client_secret, str):
                error[Constants.FIELD] = Constants.CLIENT_SECRET
                error[Constants.EXPECTED_TYPE] = Constants.STRING
                error[Constants.CLASS] = OAuth2.__name__
                raise SDKException(code=Constants.TOKEN_ERROR, details=error)

            if grant_token is not None and not isinstance(grant_token, str):
                error[Constants.FIELD] = Constants.GRANT_TOKEN
                error[Constants.EXPECTED_TYPE] = Constants.STRING
                error[Constants.CLASS] = OAuth2.__name__
                raise SDKException(code=Constants.TOKEN_ERROR, details=error)

            if refresh_token is not None and not isinstance(refresh_token, str):
                error[Constants.FIELD] = Constants.REFRESH_TOKEN
                error[Constants.EXPECTED_TYPE] = Constants.STRING
                error[Constants.CLASS] = OAuth2.__name__
                raise SDKException(code=Constants.TOKEN_ERROR, details=error)

            if redirect_url is not None and not isinstance(redirect_url, str):
                error[Constants.FIELD] = Constants.REDIRECT_URI
                error[Constants.EXPECTED_TYPE] = Constants.STRING
                error[Constants.CLASS] = OAuth2.__name__
                raise SDKException(code=Constants.TOKEN_ERROR, details=error)

        if id is not None and not isinstance(id, str):
            error[Constants.FIELD] = Constants.ID
            error[Constants.EXPECTED_TYPE] = Constants.STRING
            error[Constants.CLASS] = OAuth2.__name__
            raise SDKException(code=Constants.TOKEN_ERROR, details=error)

        if access_token is not None and not isinstance(access_token, str):
            error[Constants.FIELD] = Constants.ACCESS_TOKEN
            error[Constants.EXPECTED_TYPE] = Constants.STRING
            error[Constants.CLASS] = OAuth2.__name__
            raise SDKException(code=Constants.TOKEN_ERROR, details=error)

        if user_signature is not None and not isinstance(user_signature, UserSignature):
            error[Constants.FIELD] = Constants.USER_NAME
            error[Constants.EXPECTED_TYPE] = Constants.USER_SIGNATURE_ERROR_MESSAGE
            error[Constants.CLASS] = OAuth2.__name__
            raise SDKException(code=Constants.TOKEN_ERROR, details=error)

        if authentication_schema is not None and not isinstance(authentication_schema, AuthenticationSchema):
            error[Constants.FIELD] = Constants.AUTHENTICATION_SCHEMA
            error[Constants.EXPECTED_TYPE] = Constants.AUTHENTICATION_SCHEMA_ERROR_MESSAGE
            error[Constants.CLASS] = OAuth2.__name__
            raise SDKException(code=Constants.TOKEN_ERROR, details=error)

        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__redirect_url = redirect_url
        self.__grant_token = grant_token
        self.__refresh_token = refresh_token
        self.__id = id
        self.__access_token = access_token
        self.__expires_in = None
        self.__user_signature = user_signature
        self.__authentication_schema = authentication_schema

    def get_client_id(self):
        """
        This is a getter method to get __client_id.

        Returns:
            string: A string representing __client_id
        """

        return self.__client_id

    def get_client_secret(self):
        """
        This is a getter method to get __client_secret.

        Returns:
            string: A string representing __client_secret
        """

        return self.__client_secret

    def get_redirect_url(self):
        """
        This is a getter method to get __redirect_url.

        Returns:
            string: A string representing __redirect_url
        """

        return self.__redirect_url

    def get_grant_token(self):
        """
        This is a getter method to get __grant_token.

        Returns:
            string: A string representing __grant_token
        """
        return self.__grant_token

    def get_refresh_token(self):
        """
        This is a getter method to get __refresh_token.

        Returns:
            string: A string representing __refresh_token
        """

        return self.__refresh_token

    def get_access_token(self):
        """
        This is a getter method to get __access_token.

        Returns:
            string: A string representing __access_token
        """

        return self.__access_token

    def get_id(self):
        """
        This is a getter method to get __id.

        Returns:
            string: A string representing __id
        """

        return self.__id

    def get_expires_in(self):
        """
        This is a getter method to get __expires_in.

        Returns:
            string: A string representing __expires_in
        """

        return self.__expires_in

    def get_user_signature(self):
        """
        This is a getter method to get __user_signature

        Returns:
            user_signature(UserSignature) : An instance of UserSignature
        """

        return self.__user_signature

    def set_grant_token(self, grant_token):
        """
        This is a setter method to set __grant_token.

        """
        self.__grant_token = grant_token

    def set_refresh_token(self, refresh_token):
        """
        This is a setter method to set __refresh_token.

        """
        self.__refresh_token = refresh_token

    def set_redirect_url(self, redirect_url):
        """
        This is a setter method to set __redirect_url.

        """
        self.__redirect_url = redirect_url

    def set_access_token(self, access_token):
        """
        This is a setter method to set __access_token.

        """

        self.__access_token = access_token

    def set_client_id(self, client_id):
        """
        This is a setter method to set __client_id.

        """

        self.__client_id = client_id

    def set_client_secret(self, client_secret):
        """
        This is a setter method to set __client_secret.

        """

        self.__client_secret = client_secret

    def set_id(self, id):
        """
        This is a setter method to set __id.

        """

        self.__id = id

    def set_expires_in(self, expires_in):
        """
        This is a setter method to set __expires_in.

        """

        self.__expires_in = expires_in

    def set_user_signature(self, user_signature):
        """
        This is a setter method to set __user_signature.

        """

        self.__user_signature = user_signature

    def set_authentication_schema(self, authentication_schema):
        """
        This is a setter method to set __authentication_schema
        """
        self.__authentication_schema = authentication_schema

    def get_authentication_schema(self):
        """
          This is a getter method to get __authentication_schema

          Returns:
              authentication_schema(AuthenticationSchema) : An instance of AuthenticationSchema
          """
        return self.__authentication_schema

    def generate_token(self):
        self.get_token()

    def get_token(self):
        refresh_url = self.__authentication_schema.get_refresh_url()
        token_url = self.__authentication_schema.get_token_url()
        initializer = Initializer.get_initializer()
        store = initializer.store

        oauth_token = None
        if self.get_id() is not None:
            oauth_token = store.find_token_by_id(self.get_id())
            self.merge_objects(self, oauth_token)
        else:
            oauth_token = store.find_token(self)
        if oauth_token is None:
            if self.get_user_signature() is not None:
                self.check_token_details()
            oauth_token = self

        if oauth_token.get_access_token() is None or len(oauth_token.get_access_token()) == 0:
            if oauth_token.get_refresh_token() is not None and len(oauth_token.get_refresh_token()) > 0:
                logging.getLogger("SDKLogger").info(Constants.ACCESS_TOKEN_USING_REFRESH_TOKEN_MESSAGE)
                oauth_token.refresh_access_token(oauth_token, store, refresh_url)
            else:
                logging.getLogger("SDKLogger").info(Constants.ACCESS_TOKEN_USING_GRANT_TOKEN_MESSAGE)
                oauth_token.generate_access_token(oauth_token, store, token_url)
        elif (oauth_token.get_expires_in() is not None and len(oauth_token.get_expires_in()) > 0 and int(
                oauth_token.get_expires_in()) - int(time.time() * 1000) < 5000):
            logging.getLogger("SDKLogger").info(Constants.REFRESH_TOKEN_MESSAGE)
            oauth_token.refresh_access_token(oauth_token, store, refresh_url)
        elif oauth_token.get_expires_in() is None and oauth_token.get_access_token() is not None and \
                oauth_token.get_id() is None:
            store.save_token(oauth_token)
        return oauth_token.get_access_token()

    def check_token_details(self):
        if self.are_all_objects_null([self.__grant_token, self.__refresh_token]):
            raise SDKException(Constants.MANDATORY_VALUE_ERROR, Constants.GET_TOKEN_BY_USER_NAME_ERROR + " - " +
                               str.join(", ", Constants.OAUTH_MANDATORY_KEYS2))
        return True

    @staticmethod
    def are_all_objects_null(object1):
        for obj in object1:
            if obj is not None:
                return False
        return True

    @staticmethod
    def merge_objects(first, second):
        try:
            fields = dir(first)
            for field1 in fields:
                if any(field2 in field1 for field2 in Constants.OAUTH_TOKEN_FIELDS):
                    if not field1.startswith('__'):
                        value1 = getattr(first, field1)
                        value2 = getattr(second, field1)
                        value = value1 if value1 is not None else value2
                        setattr(first, field1, value)

        except Exception as ex:
            raise SDKException(Constants.MERGE_OBJECT, cause=ex)

    def authenticate(self, url_connection, config):
        if config is not None:
            token_config = config
            if Constants.LOCATION in token_config and Constants.NAME in token_config:
                if token_config[Constants.LOCATION].lower() == Constants.HEADER:
                    url_connection.add_header(token_config[Constants.NAME], Constants.OAUTH_HEADER_PREFIX + self.get_token())
                elif token_config[Constants.LOCATION].lower() == Constants.PARAM:
                    url_connection.add_param(token_config[Constants.NAME], Constants.OAUTH_HEADER_PREFIX + self.get_token())
        else:
            url_connection.add_header(Constants.AUTHORIZATION, Constants.OAUTH_HEADER_PREFIX + self.get_token())

    def refresh_access_token(self, oauth_token, store, url):
        try:
            body = {
                Constants.REFRESH_TOKEN: self.__refresh_token,
                Constants.CLIENT_ID: self.__client_id,
                Constants.CLIENT_SECRET: self.__client_secret,
                Constants.GRANT_TYPE: Constants.REFRESH_TOKEN
            }

            response = requests.post(url, data=body, params=None, headers=None, allow_redirects=False).json()
            self.parse_response(response)
            logging.getLogger("SDKLogger").info(self.to_string(url))
            store.save_token(oauth_token)

        except SDKException as ex:
            raise ex

        except Exception as ex:
            raise SDKException(code=Constants.SAVE_TOKEN_ERROR, cause=ex)

        return self

    def generate_access_token(self, oauth_token, store, url):
        try:
            body = {
                Constants.CLIENT_ID: self.__client_id,
                Constants.CLIENT_SECRET: self.__client_secret,
                Constants.REDIRECT_URI: self.__redirect_url if self.__redirect_url is not None else None,
                Constants.GRANT_TYPE: Constants.GRANT_TYPE_AUTH_CODE,
                Constants.CODE: self.__grant_token
            }

            headers = dict()
            headers[Constants.USER_AGENT_KEY] = Constants.USER_AGENT
            response = requests.post(url, data=body, params=None, headers=headers, allow_redirects=True).json()
            self.parse_response(response)
            logging.getLogger("SDKLogger").info(self.to_string(url))
            store.save_token(oauth_token)

        except SDKException as ex:
            raise ex

        except Exception as ex:
            raise SDKException(code=Constants.SAVE_TOKEN_ERROR, cause=ex)

        return self

    def to_string(self, url):
        return "POST - " + Constants.URL + " = " + url + "."

    def parse_response(self, response):
        response_json = dict(response)

        if Constants.ACCESS_TOKEN not in response_json:
            raise SDKException(code=Constants.INVALID_TOKEN_ERROR, message=str(response_json.get(
                Constants.ERROR_KEY)) if Constants.ERROR_KEY in response_json else Constants.NO_ACCESS_TOKEN_ERROR)

        self.__access_token = response_json.get(Constants.ACCESS_TOKEN)
        self.__expires_in = str(int(time.time() * 1000) + self.get_token_expires_in(response=response_json))

        if Constants.REFRESH_TOKEN in response_json:
            self.__refresh_token = response_json.get(Constants.REFRESH_TOKEN)

        return self

    @staticmethod
    def get_token_expires_in(response):
        return int(response[Constants.EXPIRES_IN]) if Constants.EXPIRES_IN_SEC in response else int(
            response[Constants.EXPIRES_IN]) * 1000

    def remove(self):
        try:
            if Initializer.get_initializer() is None:
                raise SDKException(Constants.SDK_UNINITIALIZATION_ERROR, Constants.SDK_UNINITIALIZATION_MESSAGE)
            Initializer.get_initializer().store.delete_token(self.get_id())
            return True
        except Exception as e:
            raise SDKException(cause=e)
