from io import BytesIO

try:
    import importlib
    import logging
    import json
    from officeintegrator.src.com.zoho.officeintegrator.util import Converter, Constants, JSONConverter
except Exception:
    import importlib
    import logging
    from .converter import Converter
    from .constants import Constants
    from .json_converter import JSONConverter


class Downloader(Converter):

    """
    This class to process the download file and stream response.
    """

    logger = logging.getLogger('SDKLogger')

    def __init__(self, common_api_handler):

        super().__init__(common_api_handler)
        self.unique_dict = {}
        self.common_api_handler = common_api_handler

    def get_wrapped_request(self, response, pack):

        return None

    def form_request(self, request_instance, pack, instance_number, class_member_detail, group_type):

        return None

    def append_to_request(self, request_base, request_object):

        return
    
    def get_wrapped_response(self, response, contents):
        if len(contents) >= 1:
            pack = contents[0]
            if Constants.INTERFACE in pack and pack[Constants.INTERFACE]:
                return [self.get_response(response, pack[Constants.CLASSES][0], pack[Constants.GROUP_TYPE])]
            else:
                class_name = pack[Constants.CLASSES][0]
                if Constants.FILE_BODY_WRAPPER in class_name:
                    return [self.get_response(response, class_name, None)]
                return [self.get_stream_instance(response, class_name)]

        return None

    def get_response(self, response, pack, group_type):

        try:
            from officeintegrator.src.com.zoho.officeintegrator import Initializer
        except Exception:
            from ..initializer import Initializer

        record_json_details = dict(Initializer.json_details[str(pack)])
        instance = None
        path_split = str(pack).rpartition(".")
        class_name = self.module_to_class(path_split[-1])
        pack = path_split[0] + "." + class_name

        if Constants.INTERFACE in record_json_details and record_json_details[Constants.INTERFACE] is not None:
            group_type_1 = record_json_details[group_type]
            if group_type_1 is not None:
                classes = group_type_1[Constants.CLASSES]
                for each_class in classes:
                    if Constants.FILE_BODY_WRAPPER in str(each_class):
                        return self.get_response(response, str(each_class), None)
            return instance

        else:
            instance = self.get_class(class_name, path_split[0])()

            for member_name, member_detail in record_json_details.items():
                data_type = member_detail[Constants.TYPE]
                instance_value = None

                if data_type == Constants.STREAM_WRAPPER_CLASS_PATH:
                    file_name = ''
                    content_disposition = response.headers[Constants.CONTENT_DISPOSITION]

                    if "'" in content_disposition:
                        start_index = content_disposition.rindex("'")
                        file_name = content_disposition[start_index + 1:]

                    elif '"' in content_disposition:
                        start_index = content_disposition.rindex('=')
                        file_name = content_disposition[start_index + 1:].replace('"', '')

                    stream_path_split = str(data_type).rpartition(".")
                    stream_class_name = self.module_to_class(stream_path_split[-1])
                    instance_value = self.get_class(stream_class_name, stream_path_split[0])(file_name, response)

                setattr(instance,
                        self.construct_private_member(class_name=class_name, member_name=member_name), instance_value)

            return instance

    @staticmethod
    def construct_private_member(class_name, member_name):
        return '_' + class_name + '__' + member_name

    @staticmethod
    def get_class(class_name, class_path):
        imported_module = importlib.import_module(class_path)
        class_holder = getattr(imported_module, class_name)
        return class_holder

    @staticmethod
    def get_stream_instance(response, type):

        content_disposition_header = response.headers.get('content-disposition', '')
        file_name = ""

        if "'" in content_disposition_header:
            start_index = content_disposition_header.rindex("'")
            file_name = content_disposition_header[start_index + 1:]

        elif '"' in content_disposition_header:
            start_index = content_disposition_header.rindex('=')
            file_name = content_disposition_header[start_index + 1:].replace('"', '')
            
        entity = BytesIO(response.content)
        path_split = str(type).rpartition(".")
        imported_module = importlib.import_module(path_split[0])
        class_holder = getattr(imported_module, path_split[-1])
        return class_holder(file_name, entity)

    @staticmethod
    def construct_private_member(class_name, member_name):
        return '_' + class_name + '__' + member_name

    @staticmethod
    def get_class(class_name, class_path):
        imported_module = importlib.import_module(class_path)
        class_holder = getattr(imported_module, class_name)
        return class_holder
