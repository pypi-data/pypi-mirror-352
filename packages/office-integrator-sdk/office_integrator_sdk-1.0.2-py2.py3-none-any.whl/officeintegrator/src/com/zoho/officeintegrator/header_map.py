try:
    from officeintegrator.src.com.zoho.officeintegrator.header import Header
    from officeintegrator.src.com.zoho.officeintegrator.exception import SDKException
    from officeintegrator.src.com.zoho.officeintegrator.util.constants import Constants
    from officeintegrator.src.com.zoho.officeintegrator.util.datatype_converter import DataTypeConverter

except Exception:
    from .header import Header
    from .exception.sdk_exception import SDKException
    from .util.constants import Constants
    from .util.datatype_converter import DataTypeConverter

class HeaderMap(object):

    """
    This class represents the HTTP header name and value.
    """

    def __init__(self):
        """Creates an instance of HeaderMap Class"""

        self.request_headers = dict()

    def add(self, header, value):

        """
        The method to add the parameter name and value.

        Parameters:
            header (Header): A Header class instance.
            value (object): An object containing the header value.
        """

        try:
            from officeintegrator.src.com.zoho.officeintegrator.util.header_param_validator import HeaderParamValidator
        except Exception:
            from .util import HeaderParamValidator

        if header is None:
            raise SDKException(Constants.HEADER_NONE_ERROR, Constants.HEADER_INSTANCE_NONE_ERROR)

        header_name = header.name

        if header_name is None:
            raise SDKException(Constants.HEADER_NAME_NONE_ERROR, Constants.HEADER_NAME_NULL_ERROR_MESSAGE)

        if value is None:
            raise SDKException(Constants.HEADER_NONE_ERROR, header_name + Constants.NONE_VALUE_ERROR_MESSAGE)

        header_class_name = header.class_name

        if header_class_name is not None:
            value = HeaderParamValidator().validate(header_name, header_class_name, value)
        else:
            try:
                value = DataTypeConverter.post_convert(value, type(value))
            except Exception as e:
                value = str(value)

        if header_name not in self.request_headers:
            self.request_headers[header_name] = str(value)

        else:
            header_value = self.request_headers[header_name]
            self.request_headers[header_name] = header_value + ',' + str(value)
