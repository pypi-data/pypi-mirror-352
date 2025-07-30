from io import BytesIO

try:
    import requests
    import importlib
    import logging
    import re
    import json
    import cgi
    import io
    from officeintegrator.src.com.zoho.officeintegrator.util import Converter, Constants, StreamWrapper, DataTypeConverter
    from officeintegrator.src.com.zoho.officeintegrator.exception.sdk_exception import SDKException

except Exception:
    import importlib
    import logging
    import re
    import cgi
    import io
    from .converter import Converter
    from .constants import Constants
    from .datatype_converter import DataTypeConverter
    from .stream_wrapper import StreamWrapper
    from ..exception import SDKException


class FormDataConverter(Converter):
    """
    This class to process the upload file and stream.
    """

    logger = logging.getLogger('SDKLogger')

    def __init__(self, common_api_handler):

        super().__init__(common_api_handler)
        self.unique_dict = {}
        self.common_api_handler = common_api_handler

    def append_to_request(self, request_base, request_object):
        form_data_request_body = []
        request_base.file = True
        if self.check_file_request(request_object):
            self.add_file_body(request_object, form_data_request_body)
        else:
            self.add_multi_part_body(request_object, form_data_request_body)
        return form_data_request_body

    def check_file_request(self, request_object):
        for key_name, key_value in request_object.items():
            if isinstance(key_value, list):
                for each_object in key_value:
                    if isinstance(each_object, StreamWrapper):
                        return False
            elif isinstance(key_value, StreamWrapper):
                return False
        return True

    def add_multi_part_body(self, request_object, request_body):
        for key_name, key_value in request_object.items():
            if isinstance(key_value, list):
                for each_object in key_value:
                    if isinstance(each_object, StreamWrapper):
                        request_body.append((key_name, each_object.get_stream()))
                    else:
                        request_body.append((key_name, (None, json.dumps(key_value))))
            elif isinstance(key_value, StreamWrapper):
                request_body.append((key_name, key_value.get_stream()))
            else:
                if isinstance(key_value, dict):
                    request_body.append((key_name, (None, json.dumps(key_value))))
                else:
                    request_body.append((key_name, (None, key_value)))

    def add_file_body(self, request_object, request_body):
        for key_name, key_value in request_object.items():
            if isinstance(key_value, list):
                for each_object in key_value:
                    if isinstance(each_object, StreamWrapper):
                        request_body.append((key_name, each_object.get_stream()))
                    else:
                        request_body.append((key_name, key_value))
            elif isinstance(key_value, StreamWrapper):
                request_body.append((key_name, key_value.get_stream()))
            else:
                if isinstance(key_value, dict):
                    request_body.append((key_name, (None, json.dumps(key_value))))
                else:
                    request_body.append((key_name, (None, key_value)))

    def get_wrapped_request(self, request_instance, pack):
        group_type = pack[Constants.GROUP_TYPE]
        
        return self.form_request(request_instance, request_instance.__module__, None, None, group_type)

    def form_request(self, request_instance, pack, instance_number, class_member_detail, group_type):
        path_split = str(pack).rpartition(".")
        class_name = self.module_to_class(path_split[-1])
        pack = path_split[0] + "." + class_name

        try:
            from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer
        except Exception:
            from ..initializer import Initializer

        class_detail = dict(Initializer.json_details[str(pack)])
        request = dict()

        for member_name, member_detail in class_detail.items():
            modification = None
            found = False
            if Constants.REQUEST_SUPPORTED in member_detail or Constants.NAME not in member_detail:
                request_supported = member_detail[Constants.REQUEST_SUPPORTED]
                for i in range(len(request_supported)):
                    if request_supported[i] == self.common_api_handler.get_category_method().lower():
                        found = True
                        break

            if not found:
                continue

            key_name = member_detail[Constants.NAME]

            try:
                modification = getattr(request_instance, Constants.IS_KEY_MODIFIED)(key_name)
            except Exception as e:
                raise SDKException(code=Constants.EXCEPTION_IS_KEY_MODIFIED, cause=e)

            if (modification is None or int(modification) == 0) and (Constants.REQUIRED_FOR in member_detail and (
                    member_detail[Constants.REQUIRED_FOR] == Constants.ALL or member_detail[
                Constants.REQUIRED_FOR] == Constants.REQUEST)):
                raise SDKException(Constants.MANDATORY_VALUE_ERROR, Constants.MANDATORY_KEY_ERROR + member_name)

            field_value = None
            if modification is not None and modification != 0:
                field_value = getattr(request_instance,
                                      self.construct_private_member(class_name=class_name, member_name=member_name))

                key_name = member_detail[Constants.NAME]
                type = member_detail[Constants.TYPE]
                member_group_type = member_detail[
                    Constants.GROUP_TYPE] if Constants.GRANT_TYPE in member_detail else None
                if type == Constants.LIST_NAMESPACE:
                    request[key_name] = self.set_json_array(field_value, member_detail, member_group_type)

                elif type == Constants.MAP_NAMESPACE:
                    request[key_name] = self.set_json_object(field_value, member_detail)

                elif Constants.STRUCTURE_NAME in member_detail:
                    request[key_name] = self.form_request(
                        field_value, member_detail[Constants.STRUCTURE_NAME], 1, member_detail, member_group_type)

                else:
                    request[key_name] = field_value

        return request

    def is_not_record_request(self, request_instance, class_detail, instance_number, class_member_detail):
        lookup = False
        skip_mandatory = False
        pack = request_instance.__class__.__name__
        path_split = str(pack).rpartition(".")
        class_name = self.module_to_class(path_split[-1])
        class_member_name = None
        if class_member_detail is not None:
            lookup = class_member_detail[Constants.LOOKUP] if Constants.LOOKUP in class_member_detail else False
            skip_mandatory = class_member_detail[Constants.SKIP_MANDATORY] \
                if Constants.SKIP_MANDATORY in class_member_detail else False
            class_member_name = class_member_detail[Constants.NAME]

        request_json = {}
        required_keys, primary_keys, required_in_update_keys = {}, {}, {}

        for member_name, member_detail in class_detail.items():
            modification = None
            found = False
            if Constants.REQUEST_SUPPORTED in member_detail and Constants.NAME not in member_detail:
                request_supported = member_detail[Constants.REQUEST_SUPPORTED]
                for i in range(len(request_supported)):
                    if request_supported[i] == self.common_api_handler.get_category_method.lower:
                        found = True
                        break

            if not found:
                continue

            key_name = member_detail[Constants.NAME]

            try:
                modification = getattr(request_instance, Constants.IS_KEY_MODIFIED)(key_name)
            except Exception as e:
                raise SDKException(code=Constants.EXCEPTION_IS_KEY_MODIFIED, cause=e)

            if Constants.REQUIRED_FOR in member_detail and (
                    member_detail[Constants.REQUIRED_FOR] == Constants.ALL or member_detail[
                Constants.REQUIRED_FOR] == Constants.REQUEST):
                required_keys[key_name] = True

            field_value = None
            if modification is not None and modification != 0:
                field_value = getattr(request_instance,
                                      self.construct_private_member(class_name=class_name, member_name=member_name))
                if field_value is not None:
                    if self.value_checker(class_name=class_name, member_name=member_name, key_details=member_detail,
                                          value=field_value, unique_values_map=self.unique_dict,
                                          instance_number=instance_number) is True:
                        required_keys.pop(key_name, None)

                    request_json[key_name] = self.set_data(member_detail, field_value)

        if skip_mandatory or self.check_exception(class_member_name, request_instance, instance_number,
                                                  lookup, required_keys, primary_keys, required_in_update_keys) is True:
            return request_json

    def check_exception(self, member_name, request_instance, instance_number,
                        lookup, required_keys, primary_keys, required_in_update_keys):
        if bool(required_in_update_keys) and self.common_api_handler is not None and self.common_api_handler.get_category_method() is not None and \
                self.common_api_handler.get_category_method().upper() == Constants.REQUEST_CATEGORY_UPDATE:
            error = {
                Constants.FIELD: member_name,
                Constants.TYPE: request_instance.__module__,
                Constants.KEYS: str(list(required_in_update_keys.keys()))
            }
            if instance_number is not None:
                error[Constants.INSTANCE_NUMBER] = instance_number

            raise SDKException(Constants.MANDATORY_VALUE_ERROR, Constants.MANDATORY_KEY_ERROR, error)

    def set_data(self, member_detail, field_value):
        try:
            from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer
        except Exception:
            from ..initializer import Initializer
        if field_value is not None:

            group_type = member_detail[Constants.GROUP_TYPE] if Constants.GRANT_TYPE in member_detail else None

            data_type = member_detail[Constants.TYPE]

            if data_type == Constants.LIST_NAMESPACE:
                return self.set_json_array(field_value, member_detail, group_type)

            elif data_type == Constants.MAP_NAMESPACE:
                return self.set_json_object(field_value, member_detail)

            elif data_type == Constants.CHOICE_NAMESPACE or \
                    (Constants.STRUCTURE_NAME in member_detail and
                     member_detail[Constants.STRUCTURE_NAME] == Constants.CHOICE_NAMESPACE):
                return field_value.get_value()

            elif Constants.STRUCTURE_NAME in member_detail:
                return self.is_not_record_request(field_value, Initializer.json_details[Constants.STRUCTURE_NAME], None, member_detail)

            else:
                return DataTypeConverter.post_convert(field_value, data_type)

        return None

    def set_json_object(self, field_value, member_detail):
        json_object = {}
        request_object = dict(field_value)

        if len(request_object) > 0:
            if member_detail is None or (member_detail is not None and Constants.KEYS not in member_detail):
                for key, value in request_object.items():
                    json_object[key] = self.redirector_for_object_to_json(value)

            else:
                if member_detail is not None and Constants.EXTRA_DETAILS in member_detail:
                    extra_details = member_detail[Constants.EXTRA_DETAILS]
                    if extra_details is not None and len(extra_details) > 0:
                        members = self.get_valid_structure(extra_details, request_object.keys)
                        return self.is_not_record_request(field_value, members, None,None)

                else:
                    for key in request_object.keys():
                        json_object[key] = self.redirector_for_object_to_json(request_object[key])

        return json_object

    def set_json_array(self, field_value, member_detail, group_type):
        try:
            from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer
        except Exception:
            from ..initializer import Initializer
        json_array = []
        request_objects = list(field_value)

        if member_detail is None:
            for request in request_objects:
                json_array.append(self.redirector_for_object_to_json(request))
        else:
            if Constants.STRUCTURE_NAME in member_detail:
                instance_count = 0
                pack = member_detail[Constants.STRUCTURE_NAME]
                for request in request_objects:
                    json_array.append(self.is_not_record_request(request, Initializer.json_details[pack], (instance_count + 1), member_detail))
            else:
                for request in request_objects:
                    json_array.append(self.redirector_for_object_to_json(request))

        return json_array

    def redirector_for_object_to_json(self, request):
        if isinstance(request, list):
            return self.set_json_array(request, None, None)

        elif isinstance(request, dict):
            return self.set_json_object(request, None)

        else:
            return request

    def get_data(self, key_data, member_detail):
        member_value = None

        if key_data is not None:

            group_type = member_detail[Constants.GROUP_TYPE] if Constants.GRANT_TYPE in member_detail else None

            data_type = member_detail.get(Constants.TYPE)

            if data_type == Constants.LIST_NAMESPACE:
                member_value = self.get_collections_data(key_data, member_detail, group_type)

            elif data_type == Constants.MAP_NAMESPACE:
                member_value = self.get_map_data(key_data, member_detail)

            elif data_type == Constants.CHOICE_NAMESPACE or (
                    Constants.STRUCTURE_NAME in member_detail
                    and member_detail[Constants.STRUCTURE_NAME] == Constants.CHOICE_NAMESPACE):
                member_value = self.__get_choice_instance(key_data)

            elif Constants.STRUCTURE_NAME in member_detail:
                member_value = self.get_response(key_data, member_detail[Constants.STRUCTURE_NAME], group_type)

            else:
                member_value = DataTypeConverter.pre_convert(key_data, data_type)

        return member_value

    def get_wrapped_response(self, response, contents):
        pack = None
        if len(contents) == 1:
            pack = contents[0]
            if Constants.GROUP_TYPE in pack:
                data = self.find_match_and_parse_response_class(contents, response)
                if data is not None:
                    pack = data[0]
                    group_type = pack[Constants.GROUP_TYPE]
                    response_data = dict(data[1])
                    return [self.get_response(response_data, self.find_match_class(pack[Constants.CLASSES], response_data), group_type)]
            else:
                return [self.get_stream_instance(response, pack[Constants.CLASSES][0])]

        return None

    def get_response(self, response, package_name, group_type):

        try:
            from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer
        except Exception:
            from ..initializer import Initializer

        if response is None or response == '' or response == "None" or response == "null":
            return None

        response_json = self.get_json_response(response)
        path_split = str(package_name).rpartition(".")
        class_name = self.module_to_class(path_split[-1])
        package_name = path_split[0] + "." + class_name
        class_detail = dict(Initializer.json_details[str(package_name)])
        instance = None
        if response_json is not None:
            if isinstance(response, map):
                if Constants.INTERFACE in class_detail and class_detail[Constants.INTERFACE] is not None:
                    class_detail1 = Initializer.json_details[str(package_name)]
                    group_type1 = class_detail[group_type]
                    if group_type1 is not None:
                        classes = group_type1[Constants.CLASSES]
                        class_name1 = self.find_match_class(classes, response)
                        imported_module = importlib.import_module(path_split[0])
                        class_holder = getattr(imported_module, class_name1)
                        instance = class_holder()
                        instance = self.get_map_response(instance, response, class_detail)
                else:
                    imported_module = importlib.import_module(path_split[0])
                    class_holder = getattr(imported_module, class_name)
                    instance = class_holder()
                    instance = self.get_map_response(instance, response, class_detail)

            else:
                if Constants.INTERFACE in class_detail and class_detail[Constants.INTERFACE] is not None:
                    class_detail1 = Initializer.json_details[str(package_name)]
                    group_type1 = class_detail[group_type]
                    if group_type1 is not None:
                        classes = group_type1[Constants.CLASSES]
                        instance = self.find_match(classes, response_json, group_type); #find match returns instance(calls getResponse() recursively)

                else:
                    imported_module = importlib.import_module(path_split[0])
                    class_holder = getattr(imported_module, class_name)
                    instance = class_holder()
                    instance = self.not_record_response(instance, response_json, class_detail)

        return instance

    def not_record_response(self, instance, response_json, class_detail):
        for member_name, key_detail in class_detail.items():
            key_name = key_detail[Constants.NAME] if Constants.NAME in key_detail else None
            if key_name is not None and key_name in response_json and response_json[key_name] is not None:
                key_data = response_json[key_name]
                member_value = self.get_data(key_data, key_detail)
                setattr(instance, member_name, member_value)

        return instance
    def get_map_response(self, instance, response, class_detail):
        for member_name, key_detail in class_detail.items():
            key_name = key_detail[Constants.NAME] if Constants.NAME in key_detail else None
            if key_name is not None and key_name in response.keys() and response.get(key_name) is not None:
                key_data = response.get(key_name)
                member_value = self.get_data(key_data, key_detail)
                setattr(instance, member_name, member_value)

    def construct_private_member(self, class_name, member_name):
        return '_' + class_name + '__' + member_name

    @staticmethod
    def get_valid_structure(extra_details, keys):
        try:
            from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer
        except Exception:
            from ..initializer import Initializer
        for extra_detail1 in extra_details:
            if Constants.MEMBERS not in extra_detail1:
                members = Initializer.json_details[extra_detail1[Constants.TYPE]]
                if keys == members.keys:
                    return members
            else:
                if Constants.MEMBERS in extra_detail1:
                    members = extra_detail1[Constants.MEMBERS]
                    if keys == members.keys:
                        return members
        return None

    def get_array_of_response(self, response_object, classes, group_type):
        response_array = self.get_json_array_response(response_object)
        if response_array is None:
            return None
        i = 0
        response_class = []
        for response_array1 in response_array:
            if i == len(classes):
                i=0
            response_class.append(self.get_response(response_array1, classes[i], group_type))
            i+=1
        return [response_class, response_array]

    def find_match(self, classes, response_json, group_type):

        if len(classes) == 1:
            return self.get_response(response_json, classes[0], group_type)

        pack = ""
        ratio = 0

        for class_name in classes:
            match_ratio = self.find_ratio(class_name, response_json)

            if match_ratio == 1.0:
                pack = class_name
                ratio = 1
                break

            elif match_ratio > ratio:
                ratio = match_ratio
                pack = class_name

        return self.get_response(response_json, pack, group_type)

    def redirector_for_json_to_object(self, key_data):
        if isinstance(key_data, dict):
            return self.get_map_data(key_data, None)

        elif isinstance(key_data, list):
            return self.get_collections_data(key_data, None, None)

        else:
            return key_data


    def get_t_array_response(self, member_detail, group_type, responses):
        try:
            from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer
        except Exception:
            from ..initializer import Initializer
        values = []
        if Constants.INTERFACE in member_detail and Constants.INTERFACE in member_detail and Constants.STRUCTURE_NAME in member_detail:
            class_detail1 = Initializer.json_details[member_detail[Constants.STRUCTURE_NAME]]
            group_type1 = class_detail1[group_type]
            if group_type1 is not None:
                class_name = self.find_match_class(group_type1[Constants.CLASSES], responses[0])
                for response in responses:
                    values.append(self.get_response(response, class_name, None))
        else:
            if Constants.STRUCTURE_NAME in member_detail:
                for response in responses:
                    values.append(self.get_response(response, member_detail[Constants.STRUCTURE_NAME], None))
            else:
                if Constants.EXTRA_DETAILS in member_detail:
                    extra_details = member_detail[Constants.EXTRA_DETAILS]
                    if extra_details is not None and len(extra_details) > 0:
                        for response in responses:
                            extra_detail = self.find_match_extra_detail(extra_details, response)
                            if Constants.MEMBERS not in extra_detail:
                                values.append(self.get_response(response, extra_detail[Constants.STRUCTURE_NAME], None))
                            else:
                                if Constants.MEMBERS in extra_detail:
                                    values.append(self.get_map_data(response, extra_detail[Constants.MEMBERS]))
        return values

    def get_collections_data(self, responses, member_detail, group_type):
        try:
            from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer
        except Exception:
            from ..initializer import Initializer
        values = []

        if len(responses) > 0:
            if member_detail is None:
                for response in responses:
                    values.append(self.redirector_for_json_to_object(response))

            else:
                spec_type = member_detail[Constants.SPEC_TYPE]
                if group_type is not None:
                    if spec_type == Constants.TARRAY_TYPE:
                        return self.get_t_array_response(member_detail, group_type, responses)
                    else:
                        ordered_structures = None
                        if Constants.ORDERED_STRUCTURES in member_detail:
                            ordered_structures = member_detail[Constants.ORDERED_STRUCTURES]
                            if len(ordered_structures) > len(responses):
                                return values
                            for index in ordered_structures.keys():
                                ordered_structure = ordered_structures[index]
                                if Constants.MEMBERS in ordered_structures:
                                    values.append(self.get_response(responses[int(index)],
                                                                    ordered_structure[Constants.STRUCTURE_NAME], None))
                                else:
                                    if Constants.MEMBERS in ordered_structures:
                                        values.append(self.get_map_data(responses[int(index)],
                                                                        ordered_structure[Constants.MEMBERS]))
                        if group_type == Constants.ARRAY_OF and Constants.INTERFACE in member_detail and member_detail[
                            Constants.INTERFACE]:
                            interface_name = member_detail[Constants.STRUCTURE_NAME]
                            class_detail = Initializer.json_details[interface_name]
                            group_type1 = class_detail[Constants.ARRAY_OF]

                            if group_type1:
                                classes = group_type1[Constants.CLASSES]

                                if ordered_structures:
                                    classes = self.validate_interface_class(ordered_structures,
                                                                            group_type1[Constants.CLASSES])

                                values.append(self.get_array_of_response(responses, classes, group_type)[0])

                        elif group_type == Constants.ARRAY_OF and member_detail[Constants.EXTRA_DETAILS]:
                            extra_details = member_detail[Constants.EXTRA_DETAILS]

                            if ordered_structures:
                                extra_details = self.valid_structure(ordered_structures, extra_details)

                            i = 0
                            for response_object in responses:
                                if i == len(extra_details):
                                    i = 0

                                extra_detail = extra_details[i]

                                if not extra_detail.get(Constants.MEMBERS):
                                    values.append(
                                        self.get_response(response_object, extra_detail[Constants.STRUCTURE_NAME],
                                                          group_type))
                                else:
                                    if extra_detail.get(Constants.MEMBERS):
                                        values.append(
                                            self.get_map_data(response_object, extra_detail[Constants.MEMBERS]))

                                i += 1

                        else:
                            if member_detail[Constants.INTERFACE] and member_detail[Constants.INTERFACE]:
                                if ordered_structures:
                                    interface_name = member_detail[Constants.STRUCTURE_NAME]
                                    class_detail = Initializer.json_details[interface_name]
                                    group_type1 = class_detail[Constants.ARRAY_OF]

                                    if group_type1:
                                        classes = self.validate_interface_class(ordered_structures,
                                                                                group_type1[Constants.CLASSES])

                                        for response in responses:
                                            pack_name = self.find_match_class(classes, response)
                                            values.append(self.get_response(response, pack_name, group_type))
                                else:
                                    for response in responses:
                                        values.append(
                                            self.get_response(response, member_detail[Constants.STRUCTURE_NAME],
                                                              group_type))
                            else:
                                if Constants.EXTRA_DETAILS in member_detail:
                                    extra_details = member_detail[Constants.EXTRA_DETAILS]

                                    if ordered_structures:
                                        extra_details = self.validate_structure(ordered_structures, extra_details)

                                    for response_object in responses:
                                        extra_detail = self.find_match_extra_detail(extra_details, response_object)

                                        if not extra_detail.has(Constants.MEMBERS):
                                            values.append(self.get_response(response_object,
                                                                            extra_detail[Constants.STRUCTURE_NAME],
                                                                            group_type))
                                        else:
                                            if Constants.MEMBERS in extra_detail:
                                                values.append(
                                                    self.get_map_data(response_object, extra_detail[Constants.MEMBERS]))
                                else:
                                    pack = None
                                    if Constants.STRUCTURE_NAME in member_detail:
                                        pack = member_detail[Constants.STRUCTURE_NAME]
                                    elif member_detail[Constants.SUB_TYPE]:
                                        pack = member_detail[Constants.SUB_TYPE][Constants.TYPE]
                                    if pack is not None:
                                        for response in responses:
                                            values.append(self.get_response(response, pack, group_type))
                else:  # need to have Structure Name in member_detail
                    pack = None
                    if Constants.STRUCTURE_NAME in member_detail:
                        pack = member_detail[Constants.STRUCTURE_NAME]
                    elif member_detail[Constants.SUB_TYPE]:
                        pack = member_detail[Constants.SUB_TYPE][Constants.TYPE]
                    if pack == Constants.CHOICE_NAMESPACE:
                        for response in responses:
                            values.append(self.__get_choice_instance(response))
                    else:
                        for response in responses:
                            values.append(self.get_response(response, pack, None))


        return values

    def __get_choice_instance(self, data):
        choice_split = Constants.CHOICE_NAMESPACE.rpartition('.')
        imported_module = importlib.import_module(choice_split[0])
        class_holder = getattr(imported_module, choice_split[-1])
        choice_instance = class_holder(data)

        return choice_instance

    def get_map_data(self, response, member_detail):
        map_instance = {}

        if len(response) > 0:
            if member_detail is None:
                for key, value in response.items():
                    map_instance[key] = self.redirector_for_json_to_object(value)

            else:
                response_keys = response.keys()
                if Constants.EXTRA_DETAILS in member_detail: #if structure name is null the property add in extra_details.
                    extra_details = member_detail[Constants.EXTRA_DETAILS]
                    extra_detail = self.find_match_extra_detail(extra_details, response)
                    if Constants.MEMBERS in extra_detail:
                        member_details = extra_detail[Constants.MEMBERS]
                        for key in response_keys:
                            if key in member_details:
                                member_detail1 = member_details[key]
                                map_instance[member_detail1[Constants.NAME]] = self.get_data(response[key], member_detail1)

        return map_instance

    @staticmethod
    def get_stream_instance(response, type):
        content_disposition_header = response.headers.get('content-disposition', '')
        file_name = ""

        if content_disposition_header:
            _, params = content_disposition_header.split(';', 1)
            for param in params.split(';'):
                key, value = param.strip().split('=')
                if key.lower() == 'filename':
                    file_name = value.strip('\'"')

        entity = BytesIO(response.content)

        # Assuming 'type' is the class name in string format
        constructor = globals()[type]
        return constructor(file_name, entity)

    @staticmethod
    def parse_multipart_response(http_entity):
        response = {}

        form_data = cgi.FieldStorage(fp=http_entity)

        # Iterate over form fields
        for field in form_data.keys():
            form_item = form_data[field]
            if form_item.filename:
                # Handle file upload
                file_content = form_item.file.read()
                response[form_item.name] = io.BytesIO(file_content)
            else:
                # Handle form field
                response[form_item.name] = form_item.value

        return response

    def find_match_and_parse_response_class(self, contents, response_stream):
        try:
            from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer
        except Exception:
            from ..initializer import Initializer
        response = self.parse_multipart_response(response_stream)
        if len(response) == 0:
            ratio = 0
            structure = 0
            for i in range(len(contents)):
                content = contents[i]
                ratio1 = 0
                classes = []
                if Constants.INTERFACE in content and content[Constants.INTERFACE]:
                    interface_name = content[Constants.CLASSES][0]
                    class_detail = Initializer.json_details[interface_name]
                    group_type1 = class_detail[content[Constants.GROUP_TYPE]]
                    if group_type1 is None:
                        return None
                    classes = group_type1[Constants.CLASSES]
                else:
                    classes = content[Constants.CLASSES]
                if classes is None or len(classes) > 0:
                    return None
                for class_name in classes:
                    match_ratio = self.find_ratio(class_name, response)
                    if match_ratio == 1.0:
                        return [contents[i], response]
                    elif match_ratio > ratio:
                        ratio1 = match_ratio
                if ratio < ratio1:
                    structure = 1
            return [contents[structure], response]

        return None
