

try:
    import re
    import json
    import platform
    import urllib3
    import logging
    from officeintegrator.src.com.zoho.officeintegrator.util.api_http_connector import APIHTTPConnector
    from officeintegrator.src.com.zoho.officeintegrator.util.constants import Constants
    from officeintegrator.src.com.zoho.officeintegrator.util.api_response import APIResponse
    from officeintegrator.src.com.zoho.officeintegrator.header_map import HeaderMap
    from officeintegrator.src.com.zoho.officeintegrator.header import Header
    from officeintegrator.src.com.zoho.officeintegrator.parameter_map import ParameterMap
    from officeintegrator.src.com.zoho.officeintegrator.param import Param
    from officeintegrator.src.com.zoho.officeintegrator.exception import SDKException
    from officeintegrator.src.com.zoho.api.authenticator.token import Token


except Exception:
    import re
    import json
    import platform
    import urllib3
    import logging
    from .api_http_connector import APIHTTPConnector
    from .constants import Constants
    from .api_response import APIResponse
    from ..header_map import HeaderMap
    from ..header import Header
    from ..parameter_map import ParameterMap
    from ..param import Param
    from ..exception import SDKException
    from officeintegrator.src.com.zoho.api.authenticator.token import Token


class CommonAPIHandler(object):
    """
    This class to process the API request and its response.
    Construct the objects that are to be sent as parameters or request body with the API.
    The Request parameter, header and body objects are constructed here.
    Process the response JSON and converts it to relevant objects in the library.
    """
    logger = logging.getLogger('SDKLogger')

    def __init__(self):

        self.__api_path = None
        self.__header = HeaderMap()
        self.__param = ParameterMap()
        self.__request = None
        self.__http_method = None
        self.__module_api_name = None
        self.__content_type = None
        self.__category_method = None
        self.__mandatory_checker = None
        self.method_name = None
        self.operation_class_name = None

    def set_content_type(self, content_type):
        """
        The method to set the Content Type

        Parameters:
            content_type(str):  A string containing the Content Type
        """

        self.__content_type = content_type

    def set_api_path(self, api_path):
        """
        The method to set the API Path

        Parameters:
            api_path(str) : A string containing the API Path
        """

        self.__api_path = api_path

    def add_param(self, param_instance, param_value):

        """
        The method to add an API request parameter.

        Parameters:
            param_instance (Param) : A Param instance containing the API request parameter.
            param_value (object) : An object containing the API request parameter value.
        """

        if param_value is None:
            return

        if self.__param is None:
            self.__param = ParameterMap()

        self.__param.add(param_instance, param_value)

    def add_header(self, header_instance, header_value):
        """
        The method to add an API request header.

        Parameters:
            header_instance (Header) : A Header instance containing the API request header.
            header_value (object) : An object containing the API request header value.
        """

        if header_value is None:
            return

        if self.__header is None:
            self.__header = HeaderMap()

        self.__header.add(header_instance, header_value)

    def set_param(self, param):
        """
        The method to set the API request parameter map.

        Parameters:
            param(ParameterMap) : A ParameterMap class instance containing the API request parameters
        """

        if param is None:
            return

        if self.__param.request_parameters is not None and self.__param.request_parameters:
            self.__param.request_parameters.update(param.request_parameters)
        else:
            self.__param = param

    def get_module_api_name(self):
        """
        The method to get the Module API Name

        Returns:
            string: A string representing the Module API Name
        """

        return self.__module_api_name

    def set_module_api_name(self, module_api_name):
        """
        The method to set the Module API Name

        Parameters:
            module_api_name(str):  A string containing the Module API Name
        """

        self.__module_api_name = module_api_name

    def set_header(self, header):
        """
        The method to set the API request header map.

        Parameters:
            header(HeaderMap): A HeaderMap class instance containing the API request headers
        """

        if header is None:
            return

        if self.__header.request_headers is not None and self.__header.request_headers:
            self.__header.request_headers.update(header.request_headers)
        else:
            self.__header = header

    def set_request(self, request):
        """
        The method to set the request instance.

        Parameters:
            request(object): An object containing the request body

        """
        self.__request = request

    def set_http_method(self, http_method):
        """
        The method to set the HTTP Method

        Parameters:
            http_method(str):  A string containing the HTTP method.
        """

        self.__http_method = http_method

    def get_method_name(self):
        return self.build_name(self.method_name.split("_"), False)

    def set_method_name(self, method_name):
        self.method_name = method_name

    def get_operation_class_name(self):
        return self.operation_class_name

    def set_operation_class_name(self, operation_class_name):
        self.operation_class_name = "officeintegrator.src." + operation_class_name

    def api_call(self):

        """
        The method to construct API request and response details. To make the Zoho API calls.

        Returns:
            APIResponse: An instance of APIResponse representing the Zoho API response instance

        Raises:
            SDKException
        """

        try:
            from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer
        except Exception:
            from ..initializer import Initializer

        if Initializer.get_initializer() is None:
            raise SDKException(code=Constants.SDK_UNINITIALIZATION_ERROR,
                               message=Constants.SDK_UNINITIALIZATION_MESSAGE)

        connector = APIHTTPConnector()
        try:
            self.set_api_url(connector)
        except SDKException as e:
            CommonAPIHandler.logger.error(Constants.SET_API_URL_EXCEPTION + e.__str__())
            raise e
        except Exception as e:
            sdk_exception = SDKException(cause=e)
            CommonAPIHandler.logger.error(Constants.SET_API_URL_EXCEPTION + sdk_exception.__str__())
            raise sdk_exception

        connector.request_method = self.__http_method
        environment = Initializer.get_initializer().environment

        try:
            from ..dc.environment import Environment
            from officeintegrator.src.com.zoho.api.authenticator.token import Token
        except:
            from officeintegrator.src.com.zoho.officeintegrator.dc.environment import Environment
            from officeintegrator.src.com.zoho.api.authenticator.token import Token
        if self.__header is not None and len(self.__header.request_headers) > 0:
            connector.headers = self.__header.request_headers
            if isinstance(environment, Environment):
                if environment.get_location() is not None and environment.get_location().name.lower() == str(Token.Location.HEADER).lower():
                    connector.add_header(environment.get_name(), environment.get_value())

        if self.__param is not None and len(self.__param.request_parameters) > 0:
            connector.parameters = self.__param.request_parameters
            
            if environment.get_location() is not None and environment.get_location().name.lower() == str(Token.Location.PARAM).lower():
                connector.add_param(environment.get_name(), environment.get_value())

        try:
            if Initializer.get_initializer().tokens != None and len(Initializer.get_initializer().tokens) > 0:
                token_config = self.get_token()
                if isinstance(token_config[0], Token):
                    token_config[0].authenticate(connector, token_config[1])

        except SDKException as e:
            CommonAPIHandler.logger.info(Constants.AUTHENTICATION_EXCEPTION + e.__str__())
            raise e
        except Exception as e:
            sdk_exception = SDKException(cause=e)
            CommonAPIHandler.logger.error(Constants.AUTHENTICATION_EXCEPTION + sdk_exception.__str__())
            raise sdk_exception

        convert_instance = None

        if self.__http_method in [Constants.REQUEST_METHOD_PATCH, Constants.REQUEST_METHOD_POST,
                                       Constants.REQUEST_METHOD_PUT] and self.__request is not None:
            try:
                pack = self.get_class_name(False, None, None)
                if pack is not None:
                    convert_instance = self.get_converter_class_instance(self.__content_type.lower())
                    connector.content_type = self.__content_type
                    is_set = False
                    if isinstance(pack, dict):
                        if Constants.CLASSES in pack:
                            classes = pack[Constants.CLASSES]
                            if len(classes) == 1 and classes[0].lower() == object.__name__.lower():
                                connector.request_body = self.__request
                                is_set = True
                    if not is_set:
                        request = convert_instance.get_wrapped_request(self.__request, pack)
                        connector.request_body = request

            except SDKException as e:
                CommonAPIHandler.logger.info(Constants.FORM_REQUEST_EXCEPTION + e.__str__())
                raise e
            except Exception as e:
                sdk_exception = SDKException(cause=e)
                CommonAPIHandler.logger.error(Constants.FORM_REQUEST_EXCEPTION + sdk_exception.__str__())
                raise sdk_exception

        try:
            response = connector.fire_request(convert_instance)
            status_code = response.status_code
            header_map = self.get_headers(response.headers)
            content_type = response.headers[Constants.CONTENT_TYPE]
            mime_type = content_type.split(';')[0] if content_type else None
            convert_instance = self.get_converter_class_instance(mime_type.lower())
            pack = self.get_class_name(True, status_code, mime_type)
            return_object = None
            response_json = None
            if pack is not None:
                response_object = convert_instance.get_wrapped_response(response, pack)
                if response_object is not None and isinstance(response_object, list):
                    return_object = response_object[0]
                    if len(response_object) == 2:
                        response_json = response_object[1]
                else:
                    return_object = response_object

            return APIResponse(header_map, response.status_code, return_object, response_json)
        except SDKException as e:
            CommonAPIHandler.logger.info(Constants.API_CALL_EXCEPTION + e.__str__())
        except Exception as e:
            sdk_exception = SDKException(cause=e)
            CommonAPIHandler.logger.error(Constants.API_CALL_EXCEPTION + sdk_exception.__str__())
            raise sdk_exception

    def get_converter_class_instance(self, encode_type):
        try:
            from officeintegrator.src.com.zoho.officeintegrator.util.json_converter import JSONConverter
            from officeintegrator.src.com.zoho.officeintegrator.util.xml_converter import XMLConverter
            from officeintegrator.src.com.zoho.officeintegrator.util.form_data_converter import FormDataConverter
            from officeintegrator.src.com.zoho.officeintegrator.util.downloader import Downloader
        except Exception:
            from .json_converter import JSONConverter
            from .xml_converter import XMLConverter
            from .form_data_converter import FormDataConverter
            from .downloader import Downloader

        """
        This method to get a Converter class instance.
        :param encode_type: A str containing the API response content type.
        :return: A Converter class instance.
        """

        switcher = {

            "application/json": JSONConverter(self),

            "text/plain": JSONConverter(self),

            "application/ld+json": JSONConverter(self),

            "application/xml": XMLConverter(self),

            "text/xml": XMLConverter(self),

            "multipart/form-data": FormDataConverter(self),

            "application/x-download": Downloader(self),

            "image/png": Downloader(self),

            "image/jpeg": Downloader(self),

            "image/gif": Downloader(self),

            "image/tiff": Downloader(self),

            "image/svg+xml": Downloader(self),

            "image/bmp": Downloader(self),

            "image/webp": Downloader(self),

            "text/html": Downloader(self),

            "text/css": Downloader(self),

            "text/javascript": Downloader(self),

            "text/calendar": Downloader(self),

            "application/zip": Downloader(self),

            "application/pdf": Downloader(self),

            "application/java-archive": Downloader(self),

            "application/javascript": Downloader(self),

            "application/xhtml+xml": Downloader(self),

            "application/x-bzip": Downloader(self),

            "application/msword": Downloader(self),

            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": Downloader(self),

            "application/gzip": Downloader(self),

            "application/x-httpd-php": Downloader(self),

            "application/vnd.ms-powerpoint": Downloader(self),

            "application/vnd.rar": Downloader(self),

            "application/x-sh": Downloader(self),

            "application/x-tar": Downloader(self),

            "application/vnd.ms-excel": Downloader(self),

            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": Downloader(self),

            "application/x-7z-compressed": Downloader(self),

            "audio/mpeg": Downloader(self),

            "audio/x-ms-wma": Downloader(self),

            "audio/vnd.rn-realaudio": Downloader(self),

            "audio/x-wav": Downloader(self),

            "audio/3gpp": Downloader(self),

            "audio/3gpp2": Downloader(self),

            "video/mpeg": Downloader(self),

            "video/mp4": Downloader(self),

            "video/webm": Downloader(self),

            "video/3gpp": Downloader(self),

            "video/3gpp2": Downloader(self),

            "font/ttf": Downloader(self),

            "text/csv": Downloader(self),

            "application/octet-stream": Downloader(self),
        }

        return switcher.get(encode_type, None)

    def set_api_url(self, connector):
        try:
            from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer
        except Exception:
            from ..initializer import Initializer

        api_path = ''

        if Constants.HTTP in self.__api_path:
            if str(self.__api_path)[:1].__eq__('/'):
                self.__api_path = self.__api_path[1:]

            api_path = api_path + self.__api_path
        else:
            api_path = Initializer.get_initializer().environment.get_url()
            api_path = api_path + self.__api_path

        connector.url = api_path

    def get_mandatory_checker(self):
        """
        The method to get the Mandatory Checker

        Returns:
            bool: A boolean representing the Mandatory Checker.
        """
        return self.__mandatory_checker

    def set_mandatory_checker(self, mandatory_checker):
        """
        The method to set the Mandatory Checker

        Parameters:
            mandatory_checker(bool): A boolean containing the Mandatory Checker.
        """

        self.__mandatory_checker = mandatory_checker

    def get_http_method(self):
        """
        The method to get the HTTP Method

        Returns:
            string: A string representing the HTTP Method
        """

        return self.__http_method

    def get_category_method(self):
        """
        The method to get the Category Method

        Returns:
            string: A string representing the Category method.
        """

        return self.__category_method

    def set_category_method(self, category_method):
        """
        The method to set the Category Method

        Parameters:
            category_method(str):  A string containing the Category method.
        """

        self.__category_method = category_method

    def get_api_path(self):
        """
        The method to get the API Path

        Returns:
            string: A string representing the API Path
        """
        return self.__api_path

    def get_headers(self, headers):
        header_map = {}
        for key, value in headers.items():
            header_map[key] = value
        return header_map

    def get_class_name(self, is_response, status_code, mime_type):
        try:
            from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer
        except Exception:
            from ..initializer import Initializer

        json_details = Initializer.json_details
        operation_class_name_split = str(self.operation_class_name).split(".")
        module_name = self.modify_operation_packname(operation_class_name_split[len(operation_class_name_split) - 2])
        operation_class_name_split[len(operation_class_name_split) - 2] = module_name
        operation_class_name = str.join(".", operation_class_name_split)
        if operation_class_name.lower() in json_details:
            methods = json_details[operation_class_name.lower()]
            method_name = self.method_name
            if method_name in methods:
                method_details = methods[method_name]
                if is_response:
                    if Constants.RESPONSE in method_details:
                        response = method_details[Constants.RESPONSE]
                        if status_code.__str__() in response:
                            content_response = response[status_code.__str__()]
                            for content in content_response:
                                content_json = content
                                if mime_type in content_json:
                                    return content_json[mime_type]
                            CommonAPIHandler.logger.error(Constants.API_CALL_EXCEPTION)
                        else:
                            CommonAPIHandler.logger.error(Constants.API_CALL_EXCEPTION)
                else:
                    if Constants.REQUEST in method_details:
                        return self.get_request_class_name(method_details[Constants.REQUEST])
            else:
                CommonAPIHandler.logger.error(Constants.API_CALL_EXCEPTION)
        else:
            CommonAPIHandler.logger.error(Constants.API_CALL_EXCEPTION)
        return None

    def get_request_class_name(self, requests):
        try:
            from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer
            from officeintegrator.src.com.zoho.officeintegrator.util.converter import Converter
        except Exception:
            from ..initializer import Initializer
            from ..util.converter import Converter

        name = self.__request.__module__
        if isinstance(self.__request, list):
            name = self.__request[0].__module__
        for type in requests.keys():
            contents = requests[type]
            for content1 in contents:
                content = content1
                if Constants.INTERFACE in content and content[Constants.INTERFACE]:
                    interface_name = content[Constants.CLASSES][0].__str__()
                    if interface_name == name:
                        self.__content_type = type
                        return content
                    class_detail = Initializer.json_details[interface_name]
                    for group_type in class_detail.keys():
                        group_type_content = class_detail[group_type]
                        classes = group_type_content[Constants.CLASSES]
                        for class_name in classes:
                            if class_name.__str__() == name:
                                self.__content_type = type
                                return content
                else:
                    classes = content[Constants.CLASSES]
                    for class_name in classes:
                        class_name_list = class_name.split(".")
                        class_name_list[-1] = Converter.class_to_module(class_name_list[-1])
                        class_name = str.join(".", class_name_list)
                        if class_name.__str__() == name:
                            self.__content_type = type
                            return content
                    if len(classes) == 1 and classes[0].lower() == object.__name__.lower():
                        self.__content_type = type
                        return content
        return None


    def get_token(self):
        try:
            from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer
        except Exception:
            from ..initializer import Initializer
        authentication_types = self.get_request_method_details(self.operation_class_name)
        tokens = Initializer.get_initializer().tokens
        if authentication_types is not None:
            for token in tokens:
                for authentication_type in authentication_types:
                    authentication = authentication_type
                    schema_name = authentication[Constants.SCHEMA_NAME]
                    if schema_name.lower() == (token.get_authentication_schema().get_schema()).lower():
                        return [token, authentication]
        return [tokens[0], None]
    
    def modify_operation_packname(self, key_name):
        name_split = re.findall('[a-zA-Z][^A-Z]*', key_name)
        file_name = name_split[0].lower()
        if len(name_split) > 1:
            for i in range(1, len(name_split)):
                if len(name_split[i]) > 0:
                    file_name += '_' + name_split[i].lower()

        return file_name
    
    def get_request_method_details(self, operation_class_name):
        try:
            from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer
        except Exception:
            from ..initializer import Initializer
        try:
            operation_class_name_split = str(operation_class_name).split(".")
            module_name = self.modify_operation_packname(operation_class_name_split[len(operation_class_name_split) - 2])
            operation_class_name_split[len(operation_class_name_split) - 2] = module_name
            operation_class_name = str.join(".", operation_class_name_split)
            if operation_class_name.lower() in Initializer.json_details:
                class_details = Initializer.json_details[operation_class_name.lower()]
                method_name = self.method_name
                if method_name in class_details:
                    method_details = class_details[method_name]
                    if Constants.AUTHENTICATION in method_details:
                        return method_details[Constants.AUTHENTICATION]
                    elif Constants.AUTHENTICATION in class_details:
                        return class_details[Constants.AUTHENTICATION]
                    return None
                else:
                    raise SDKException(Constants.SDK_OPERATIONS_METHOD_DETAILS_NOT_FOUND_IN_JSON_DETAILS_FILE)
            else:
                raise SDKException(Constants.SDK_OPERATIONS_CLASS_DETAILS_NOT_FOUND_IN_JSON_DETAILS_FILE)
        except Exception as ex:
            exception = SDKException(cause=ex)
            CommonAPIHandler.logger.error(Constants.API_CALL_EXCEPTION + ex.__str__())
            raise ex

    @staticmethod
    def build_name(name, is_type):
        sdk_name = ""
        index = None
        if is_type:
            index = 0
        else:
            if len(name) == 0:
                sdk_name = name[0]
                sdk_name = sdk_name.replace("$", "") if "$" in sdk_name else sdk_name
            index = 1
        for name_index in range(index, len(name)):
            full_name = name[name_index]
            if len(full_name) == 0:
                first_letter_uppercase = CommonAPIHandler.get_field_name(full_name)
                if first_letter_uppercase == "api":
                    sdk_name = sdk_name + first_letter_uppercase.upper()
                else:
                    sdk_name = sdk_name + first_letter_uppercase

    @staticmethod
    def get_field_name(full_name):
        var_name = full_name
        if "$" in full_name:
            var_name = full_name.replace("$", "")
        elif "_" in full_name:
            var_name = full_name.replace("_", "")
        return (var_name[0].upper()) + var_name[1:]
