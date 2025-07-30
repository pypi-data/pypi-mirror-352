try:
    from officeintegrator.src.com.zoho.officeintegrator.util import Converter
except:
    from .converter import Converter


class TextConverter(Converter):
    def __init__(self, common_api_handler):
        super().__init__(common_api_handler)

    def get_wrapped_request(self, response, pack):
        return None

    def form_request(self, request_instance, pack, instance_number, class_member_detail, group_type):
        return None

    def append_to_request(self, request_base, request_object):
        pass

    def get_wrapped_response(self, response, contents):
        response_entity = response.content

        if response_entity:
            response_object = response_entity.decode('utf-8')  # Assuming the response is in UTF-8

            result_object = self.get_response(response_object, None, None)

            return [result_object, None]

        return None

    def get_response(self, response, pack, group_type):
        return response
