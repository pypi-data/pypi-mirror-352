try:
    from .converter import Converter
    import logging

except Exception:
    from .converter import Converter
    import logging


class XMLConverter(Converter):

    """
    This class processes the API response object to the POJO object and POJO object to an XML object.
    """

    logger = logging.getLogger('SDKLogger')

    def __init__(self, common_api_handler):

        super().__init__(common_api_handler)

        self.unique_dict = {}

        self.count = 0

        self.common_api_handler = common_api_handler

    def get_wrapped_request(self, response, pack):

        return None

    def form_request(self, request_instance, pack, instance_number, class_member_detail, group_type):

        return None

    def append_to_request(self, request_base, request_object):

        return None

    def get_wrapped_response(self, response, pack):

        return None

    def get_response(self, response, pack, group_type):

        return None
