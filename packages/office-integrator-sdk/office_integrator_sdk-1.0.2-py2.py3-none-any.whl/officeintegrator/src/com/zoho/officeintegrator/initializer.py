"""
Copyright (c) 2021, ZOHO CORPORATION PRIVATE LIMITED 
All rights reserved. 
 
   Licensed under the Apache License, Version 2.0 (the "License"); 
   you may not use this file except in compliance with the License. 
   You may obtain a copy of the License at 
 
       http://www.apache.org/licenses/LICENSE-2.0 
 
   Unless required by applicable law or agreed to in writing, software 
   distributed under the License is distributed on an "AS IS" BASIS, 
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
   See the License for the specific language governing permissions and 
   limitations under the License.
"""

try:
    import logging
    import os
    import json
    import threading
    from officeintegrator.src.com.zoho.officeintegrator.user_signature import UserSignature
    from officeintegrator.src.com.zoho.officeintegrator.exception.sdk_exception import SDKException
    from officeintegrator.src.com.zoho.officeintegrator.dc.environment import Environment
    from officeintegrator.src.com.zoho.officeintegrator.util.constants import Constants
    from officeintegrator.src.com.zoho.api.authenticator.token import Token
    from officeintegrator.src.com.zoho.officeintegrator.logger import Logger, SDKLogger
    from officeintegrator.src.com.zoho.officeintegrator.request_proxy import RequestProxy
    from officeintegrator.src.com.zoho.officeintegrator.sdk_config import SDKConfig

except Exception:
    import logging
    import os
    import json
    import threading
    from .user_signature import UserSignature
    from .exception.sdk_exception import SDKException
    from .dc.environment import Environment
    from .util.constants import Constants
    from officeintegrator.src.com.zoho.api.authenticator.token import Token
    from officeintegrator.src.com.zoho.officeintegrator.logger import Logger, SDKLogger
    from .request_proxy import RequestProxy
    from .sdk_config import SDKConfig


class Initializer(object):
    """
    The class to initialize Zoho SDK.
    """

    def __init__(self):
        self.environment = None
        self.store = None
        self.tokens = None
        self.sdk_config = None
        self.request_proxy = None
        self.logger = None

    json_details = None
    initializer = None
    LOCAL = threading.local()
    LOCAL.init = None

    @staticmethod
    def initialize(environment, tokens, store=None, sdk_config=None, logger=None, proxy=None):

        """
        The method to initialize the SDK.

        Parameters:
            environment (DataCenter.Environment) : An Environment class instance containing the API base URL and Accounts URL.
            tokens (list) : list of Token class instance containing the OAuth client application information.
            store (TokenStore) : A TokenStore class instance containing the token store information.
            sdk_config (SDKConfig) : A SDKConfig class instance containing the configuration.
            logger (Logger): A Logger class instance containing the log file path and Logger type.
            proxy (RequestProxy) : A RequestProxy class instance containing the proxy properties of the user.
        """

        try:
            if not isinstance(environment, Environment):
                error = {Constants.FIELD: Constants.ENVIRONMENT,
                         Constants.EXPECTED_TYPE: Environment.__module__}

                raise SDKException(Constants.INITIALIZATION_ERROR, Constants.ENVIRONMENT_ERROR_MESSAGE, details=error)

            if tokens is not None and isinstance(tokens, list):
                for token in tokens:
                    if not isinstance(token, Token):
                        error = {Constants.FIELD: Constants.TOKEN, Constants.EXPECTED_TYPE: Token.__module__}

                        raise SDKException(Constants.INITIALIZATION_ERROR, Constants.TOKEN_ERROR_MESSAGE, details=error)

            try:
                from officeintegrator.src.com.zoho.api.authenticator.store.token_store import TokenStore
            except Exception:
                from officeintegrator.src.com.zoho.api.authenticator.store.token_store import TokenStore

            if store is not None and not isinstance(store, TokenStore):
                error = {Constants.FIELD: Constants.STORE, Constants.EXPECTED_TYPE: TokenStore.__module__}

                raise SDKException(Constants.INITIALIZATION_ERROR, Constants.STORE_ERROR_MESSAGE, details=error)

            if sdk_config is not None and not isinstance(sdk_config, SDKConfig):
                error = {Constants.FIELD: Constants.SDK_CONFIG, Constants.EXPECTED_TYPE: SDKConfig.__module__}

                raise SDKException(Constants.INITIALIZATION_ERROR, Constants.SDK_CONFIG_ERROR_MESSAGE, details=error)

            if proxy is not None and not isinstance(proxy, RequestProxy):
                error = {Constants.FIELD: Constants.USER_PROXY, Constants.EXPECTED_TYPE: RequestProxy.__module__}

                raise SDKException(Constants.INITIALIZATION_ERROR, Constants.REQUEST_PROXY_ERROR_MESSAGE, details=error)

            if store is None:
                try:
                    from officeintegrator.src.com.zoho.api.authenticator.store.file_store import FileStore
                    from officeintegrator.src.com.zoho.api.authenticator.oauth2 import OAuth2
                except Exception:
                    from officeintegrator.src.com.zoho.api.authenticator.store.file_store import FileStore
                    from officeintegrator.src.com.zoho.api.authenticator.oauth2 import OAuth2

                is_create = False

                for token_instance in tokens:
                    if isinstance(token_instance, OAuth2):
                        is_create = True
                        break
                
                if is_create:
                    store = FileStore(os.path.join(os.getcwd(), Constants.TOKEN_FILE))

            if sdk_config is None:
                sdk_config = SDKConfig()

            if logger is None:
                logger = Logger(Logger.Levels.NOTSET, None)

            SDKLogger.initialize(logger)

            try:
                json_details_path = os.path.join(os.path.dirname(__file__), '..', '..', '..',  Constants.JSON_DETAILS_FILE_PATH)
                if Initializer.json_details is None or len(Initializer.json_details) == 0:
                    with open(json_details_path, mode='r') as JSON:
                        Initializer.json_details = json.load(JSON)
            except Exception as e:
                raise SDKException(code=Constants.JSON_DETAILS_ERROR, cause=e)

            initializer = Initializer()

            initializer.environment = environment
            initializer.tokens = tokens
            initializer.store = store
            initializer.sdk_config = sdk_config
            initializer.request_proxy = proxy
            Initializer.initializer = initializer
            logging.getLogger('SDKLogger').info(Constants.INITIALIZATION_SUCCESSFUL + initializer.__str__())

        except SDKException as e:
            raise e

    def __str__(self):
        return Constants.IN_ENVIRONMENT + Initializer.get_initializer().environment.get_url() + '.'

    @staticmethod
    def get_initializer():

        """
        The method to get Initializer class instance.

        Returns:
            Initializer : An instance of Initializer
        """

        if getattr(Initializer.LOCAL, 'init', None) is not None:
            return getattr(Initializer.LOCAL, 'init')

        return Initializer.initializer

    @staticmethod
    def get_json(file_path):
        with open(file_path, mode="r") as JSON:
            file_contents = json.load(JSON)
            JSON.close()

        return file_contents

    @staticmethod
    def switch_user(environment=None, tokens=None, sdk_config=None, proxy=None):

        """
        The method to switch the different user in SDK environment.

        Parameters:
            environment (DataCenter.Environment) : An Environment class instance containing the API base URL and Accounts URL.
            tokens (list) : A list of A Token class instance containing the OAuth client application information.
            sdk_config (SDKConfig) : A SDKConfig class instance containing the configuration.
            proxy (RequestProxy) : A RequestProxy class instance containing the proxy properties of the user.
        """

        if Initializer.initializer is None:
            raise SDKException(Constants.SDK_UNINITIALIZATION_ERROR, Constants.SDK_UNINITIALIZATION_MESSAGE)

        if environment is not None and not isinstance(environment, Environment):
            error = {Constants.FIELD: Constants.ENVIRONMENT,
                     Constants.EXPECTED_TYPE: Environment.__module__}

            raise SDKException(Constants.SWITCH_USER_ERROR, Constants.ENVIRONMENT_ERROR_MESSAGE, details=error)
        if tokens is not None and isinstance(tokens, list):
            for token in tokens:
                if token is not None and not isinstance(token, Token):
                    error = {Constants.FIELD: Constants.TOKEN, Constants.EXPECTED_TYPE: Token.__module__}

                    raise SDKException(Constants.SWITCH_USER_ERROR, Constants.TOKEN_ERROR_MESSAGE, details=error)

        if sdk_config is not None and not isinstance(sdk_config, SDKConfig):
            error = {Constants.FIELD: Constants.SDK_CONFIG, Constants.EXPECTED_TYPE: SDKConfig.__module__}

            raise SDKException(Constants.SWITCH_USER_ERROR, Constants.SDK_CONFIG_ERROR_MESSAGE, details=error)

        if proxy is not None and not isinstance(proxy, RequestProxy):
            error = {Constants.FIELD: Constants.USER_PROXY, Constants.EXPECTED_TYPE: RequestProxy.__module__}

            raise SDKException(Constants.SWITCH_USER_ERROR, Constants.REQUEST_PROXY_ERROR_MESSAGE, details=error)

        previous_initializer = Initializer.get_initializer()

        initializer = Initializer()
        initializer.environment = previous_initializer.environment if environment is None else environment
        initializer.tokens = previous_initializer.tokens if tokens is None else tokens
        initializer.sdk_config = previous_initializer.sdk_config if sdk_config is None else sdk_config
        initializer.store = Initializer.initializer.store
        initializer.request_proxy = proxy

        Initializer.LOCAL.init = initializer

        logging.getLogger('SDKLogger').info(Constants.INITIALIZATION_SWITCHED + initializer.__str__())
