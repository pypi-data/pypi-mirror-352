import json

try:
    from abc import ABC, abstractmethod
    import logging
    import sys
    import zlib
    import base64
    import re
    import os
    import importlib
    from officeintegrator.src.com.zoho.officeintegrator.util import Choice, Constants
    from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer

except Exception:
    from abc import ABC, abstractmethod
    import logging
    import sys
    import zlib
    import base64
    import re
    import os
    import importlib
    from .choice import Choice
    from .constants import Constants
    from ..initializer import Initializer


class Converter(ABC):
    """
    This abstract class is to construct API request and response.
    """

    logger = logging.getLogger('SDKLogger')


    def __init__(self, common_api_handler):

        """
        Creates a Converter class instance with the CommonAPIHandler class instance.
        :param common_api_handler: A CommonAPIHandler class instance.
        """

        self.common_api_handler = common_api_handler

    @abstractmethod
    def get_response(self, response, pack, group_type):

        """
        This abstract method to process the API response.
        :param response: A object containing the API response contents or response.
        :param pack: A str containing the expected method return type.
        :return: A object representing the POJO class instance.
        """

        pass

    @abstractmethod
    def get_wrapped_request(self, response, pack):
        pass

    @abstractmethod
    def form_request(self, request_instance, pack, instance_number, class_member_detail, group_type):

        """
        This abstract method to construct the API request.
        :param request_instance: A Object containing the POJO class instance.
        :param pack: A str containing the expected method return type.
        :param instance_number: An int containing the POJO class instance list number.
        :param class_member_detail : A dict representing the member details
        :return: A object representing the API request body object.
        """

        pass

    @abstractmethod
    def append_to_request(self, request_base, request_object):

        """
        This abstract method to construct the API request body.
        :param request_base: A HttpEntityEnclosingRequestBase class instance.
        :param request_object: A object containing the API request body object.
        """

        pass

    @abstractmethod
    def get_wrapped_response(self, response, contents):

        """
        This abstract method to process the API response.
        :param response: A object containing the HttpResponse class instance.
        :param pack: A List containing the construct Objects.
        :return: A object representing the POJO class instance.
        """
        pass

    def value_checker(self, class_name, member_name, key_details, value, unique_values_map, instance_number):

        """
        This method is to validate if the input values satisfy the constraints for the respective fields.
        :param class_name: A str containing the class name.
        :param member_name: A str containing the member name.
        :param key_details: A JSON object containing the key JSON details.
        :param value: A object containing the key value.
        :param unique_values_map: A list containing the construct objects.
        :param instance_number: An int containing the POJO class instance list number.
        :return: A bool representing the key value is expected pattern, unique, length, and values.
        """

        try:
            from officeintegrator.src.com.zoho.officeintegrator.exception import SDKException
            from officeintegrator.src.com.zoho.officeintegrator.util.constants import Constants
            from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer

        except Exception:
            from ..exception import SDKException
            from .constants import Constants
            from ..initializer import Initializer

        details_jo = {}
        name = key_details[Constants.NAME]
        data_type = key_details[Constants.TYPE]
        check = True
        given_type = None

        if value is not None:
            if Constants.INTERFACE in key_details and key_details[Constants.INTERFACE]:
                interface_details = Initializer.get_initializer().json_details[key_details[Constants.STRUCTURE_NAME]]
                classes = interface_details[Constants.CLASSES]
                check = False
                for each_class in classes:
                    path_split = str(value.__class__.__module__).rpartition(".")
                    class_name = self.module_to_class(path_split[-1])
                    pack = path_split[0] + "." + class_name

                    if pack == each_class:
                        check = True
                        break
            else:
                given_type = value.__class__.__module__

        if data_type in Constants.DATA_TYPE:
            if isinstance(value, list) and Constants.STRUCTURE_NAME in key_details:
                structure_name = key_details[Constants.STRUCTURE_NAME]
                index = 0
                path_split = str(structure_name).rpartition('.')
                imported_module = importlib.import_module(path_split[0])
                class_holder = getattr(imported_module, path_split[-1])

                for each_instance in value:
                    if not isinstance(each_instance, class_holder):
                        check = False
                        instance_number = index
                        data_type = Constants.LIST_KEY + '[' + structure_name + ']'
                        given_type = each_instance.__module__
                        break

                    index = index + 1
            else:
                try:
                    from officeintegrator.src.com.zoho.officeintegrator.util import Utility
                except Exception:
                    from .utility import Utility

                check = Utility.check_data_type(value=value, type=data_type)

        elif value is not None and data_type.lower() != Constants.OBJECT_KEY:
            if data_type == "TimeZone":
                check = True
            else:
                path_split = str(data_type).rpartition('.')
                imported_module = importlib.import_module(path_split[0])
                class_holder = getattr(imported_module, path_split[-1])

                if not isinstance(value, class_holder):
                    check = False

        if not check:
            details_jo[Constants.FIELD] = name
            details_jo[Constants.CLASS] = class_name
            details_jo[Constants.ACCEPTED_TYPE] = data_type
            details_jo[Constants.GIVEN_TYPE] = given_type
            if instance_number is not None:
                details_jo[Constants.INDEX] = instance_number

            raise SDKException(code=Constants.TYPE_ERROR, details=details_jo)

        if Constants.VALUES in key_details and \
                (Constants.PICKLIST not in key_details
                 or (key_details[Constants.PICKLIST]
                     and Initializer.get_initializer().sdk_config.get_pick_list_validation())):
            values_ja = key_details[Constants.VALUES]

            if isinstance(value, list):
                value_1 = value
                for value_2 in value_1:
                    if isinstance(value_2, Choice):
                        choice = value_2
                        value_2 = choice.get_value()
                    if str(value_2) not in values_ja:
                        details_jo[Constants.FIELD] = member_name
                        details_jo[Constants.CLASS] = class_name
                        details_jo[Constants.GIVEN_VALUE] = value
                        details_jo[Constants.ACCEPTED_VALUES] = values_ja
                        if instance_number is not None:
                            details_jo[Constants.INDEX] = instance_number

                        raise SDKException(code=Constants.UNACCEPTED_VALUES_ERROR, details=details_jo)
            else:
                if isinstance(value, Choice):
                    value = value.get_value()

                if value not in values_ja:
                    details_jo[Constants.FIELD] = member_name
                    details_jo[Constants.CLASS] = class_name
                    details_jo[Constants.GIVEN_VALUE] = value
                    details_jo[Constants.ACCEPTED_VALUES] = values_ja
                    if instance_number is not None:
                        details_jo[Constants.INDEX] = instance_number

                    raise SDKException(code=Constants.UNACCEPTED_VALUES_ERROR, details=details_jo)

        if Constants.UNIQUE in key_details:
            if name not in unique_values_map:
                unique_values_map[name] = []

            values_array = unique_values_map[name]

            if value in values_array:
                details_jo[Constants.FIELD] = member_name
                details_jo[Constants.CLASS] = class_name
                details_jo[Constants.FIRST_INDEX] = values_array.index(value) + 1
                details_jo[Constants.NEXT_INDEX] = instance_number

                raise SDKException(code=Constants.UNIQUE_KEY_ERROR, details=details_jo)

            else:
                unique_values_map[name].append(value)

        if Constants.MIN_LENGTH in key_details or Constants.MAX_LENGTH in key_details:
            count = len(str(value))

            if isinstance(value, list):
                count = len(value)

            if Constants.MAX_LENGTH in key_details and count > key_details[Constants.MAX_LENGTH]:
                details_jo[Constants.FIELD] = member_name
                details_jo[Constants.CLASS] = class_name
                details_jo[Constants.GIVEN_LENGTH] = count
                details_jo[Constants.MAXIMUM_LENGTH] = key_details[Constants.MAX_LENGTH]

                raise SDKException(code=Constants.MAXIMUM_LENGTH_ERROR, details=details_jo)

            if Constants.MIN_LENGTH in key_details and count < key_details[Constants.MIN_LENGTH]:
                details_jo[Constants.FIELD] = member_name
                details_jo[Constants.CLASS] = class_name
                details_jo[Constants.GIVEN_LENGTH] = count
                details_jo[Constants.MINIMUM_LENGTH] = key_details[Constants.MIN_LENGTH]

                raise SDKException(code=Constants.MINIMUM_LENGTH_ERROR, details=details_jo)

        return True

    def module_to_class(self, module_name):
        class_name = module_name

        if "_" in module_name:
            class_name = ''
            module_split = str(module_name).split('_')
            for each_name in module_split:
                each_name = each_name.capitalize()
                class_name += each_name

        return class_name

    @staticmethod
    def get_json_array_response(response):
        response_string = str(response)

        if not response_string or response_string.lower() in {"null", "{}", "", " "}:
            return None

        return json.loads(response_string)

    @staticmethod
    def get_json_response(response):
        if isinstance(response, dict):
            response_string = json.dumps(response)
        else:
            response_string = str(response)

        if not response_string or response_string.lower() in {"null", "{}", "", " "}:
            return None

        response_string = response_string.replace("'", "\"")



        return json.loads(response_string)

    def find_match_response_class(self, contents, response_object):
        response = None
        if isinstance(response_object, dict):
            response = self.get_json_response(response_object)
        elif isinstance(response_object, list):
            response = self.get_json_array_response(response_object)[0]
        if response is not None:
            ratio = 0
            structure = 0
            for i in range(len(contents)):
                content = contents[i]
                ratio1 = 0
                classes = None
                if Constants.INTERFACE in content and content[Constants.INTERFACE]:
                    interface_name = content.get(Constants.CLASSES)[0]
                    class_detail = Initializer.json_details[interface_name]
                    group_type1 = class_detail[content[Constants.GROUP_TYPE]]
                    if group_type1 is None:
                        return None
                    classes = group_type1[Constants.CLASSES]
                else:
                    classes = content[Constants.CLASSES]
                if classes is None or len(Constants.CLASSES):
                    return None
                for class_name in classes:
                    match_ratio = self.find_ratio(class_name, response)
                    if match_ratio == 1.0:
                        return contents[i]
                    elif match_ratio > ratio1:
                        ratio1 = match_ratio
                if ratio < ratio1:
                    structure = i
            return contents[structure]
        return None

    def find_match_extra_detail(self, extra_details, response_object):
        ratio = 0
        index = 0
        for i in range(len(extra_details)):
            class_json = dict(extra_details[i])
            if Constants.MEMBERS not in class_json:
                match_ratio = self.find_ratio(class_json[Constants.STRUCTURE_NAME], response_object)
                if match_ratio == 1.0:
                    index = 1
                    break
                elif match_ratio > ratio:
                    index = 1
                    ratio = match_ratio
            else:
                if Constants.MEMBERS in class_json:
                    match_ratio = self.find_ratio(class_json[Constants.MEMBERS], response_object)
                    if match_ratio == 1.0:
                        index = 1
                        break
                    elif match_ratio > ratio:
                        index = i
                        ratio = match_ratio

        return dict(extra_details[index])

    def find_match_class(self, classes, response_json):
        pack = ""
        ratio = 0
        for class_name in classes:
            match_ratio = self.find_ratio(class_name, response_json)
            if match_ratio == 1.0:
                pack = class_name
                break
            elif match_ratio > ratio:
                pack = class_name
                ratio = match_ratio

        return pack

    def find_ratio(self, class_name, response_json):
        try:
            from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer
        except Exception:
            from ..initializer import Initializer

        class_detail = dict(Initializer.json_details[class_name]) if isinstance(class_name, str) else class_name

        total_points = len(class_detail.keys())
        matches = 0

        if total_points == 0:
            return 0

        else:
            for member_name in class_detail:
                member_detail = class_detail[member_name]
                key_name = member_detail[Constants.NAME] if Constants.NAME in member_detail else None
                if key_name is not None and key_name in response_json and response_json.get(key_name) is not None:
                    key_data = response_json[key_name]
                    data_type = type(key_data).__name__
                    structure_name = member_detail[
                        Constants.STRUCTURE_NAME] if Constants.STRUCTURE_NAME in member_detail else None

                    if isinstance(key_data, dict):
                        data_type = Constants.MAP_NAMESPACE

                    if isinstance(key_data, list):
                        data_type = Constants.LIST_NAMESPACE

                    if data_type == member_detail[Constants.TYPE] or (
                            member_detail[Constants.TYPE] in Constants.DATA_TYPE and
                            isinstance(key_data, Constants.DATA_TYPE.get(member_detail[Constants.TYPE]))):

                        matches += 1
                    elif key_name.lower() == Constants.COUNT.lower() and \
                            member_detail[Constants.TYPE].lower() == Constants.LONG_NAMESPACE.lower():
                        matches += 1
                    elif member_detail[Constants.TYPE] == Constants.CHOICE_NAMESPACE:
                        values = list(member_detail[Constants.VALUES])
                        for value in values:
                            if value == key_data:
                                matches += 1
                                break

                    if structure_name is not None and structure_name == member_detail[Constants.TYPE]:
                        if Constants.VALUES in member_detail:
                            for value in member_detail[Constants.VALUES]:
                                if value == key_data:
                                    matches += 1
                                    break
                        else:
                            matches += 1

        return matches / total_points

    @staticmethod
    def build_name(key_name):
        name_split = str(key_name).split('_')
        sdk_name = name_split[0].lower()

        if len(name_split) > 1:
            for i in range(1, len(name_split)):
                if len(name_split[i]) > 0:
                    sdk_name += '_' + name_split[i].lower()

        return sdk_name

    def validate_interface_class(self, ordered_structures, classes):
        valid_classes = []
        for class_name in classes:
            is_valid = False
            for index in ordered_structures.keys():
                ordered_structure = ordered_structures[index]
                if Constants.MEMBERS not in ordered_structure:
                    if class_name == ordered_structure[Constants.STRUCTURE_NAME]:
                        is_valid = True
                        break
            if not is_valid:
                valid_classes.append(class_name)

        return valid_classes


    def validate_structure(self, ordered_structures, extra_details):
        valid_structure = []
        for extra_detail in extra_details:
            extra_detail1 = extra_detail
            if Constants.MEMBERS in extra_detail1:
                is_valid = False
                for index in ordered_structures.keys():
                    ordered_structure = ordered_structures[index]
                    if Constants.MEMBERS not in ordered_structure:
                        extra_detail_structure_name = extra_detail1[Constants.STRUCTURE_NAME]
                        if extra_detail_structure_name == ordered_structure[Constants.STRUCTURE_NAME]:
                            is_valid = True
                            break
                if not is_valid:
                    valid_structure.append(extra_detail1)
            else:
                if Constants.MEMBERS in extra_detail1:
                    is_valid = True
                    for index in ordered_structures.keys():
                        ordered_structure = ordered_structures[index]
                        if Constants.MEMBERS in ordered_structure:
                            extra_detail_structure_members = extra_detail1[Constants.MEMBERS]
                            ordered_structure_members = ordered_structure[Constants.MEMBERS]
                            if len(extra_detail_structure_members) == len(ordered_structure_members):
                                for name in extra_detail_structure_members.keys():
                                    extra_detail_structure_member = extra_detail_structure_members[name]
                                    if name in ordered_structure_members:
                                        ordered_structure_member = ordered_structure_members[name]
                                        if Constants.TYPE in extra_detail_structure_member and Constants.TYPE in ordered_structure_member and not (extra_detail_structure_member[Constants.TYPE] == ordered_structure_member[Constants.TYPE]):
                                            is_valid = False
                                            break
                                    break
                    if not is_valid:
                        valid_structure.append(extra_detail1)

        return valid_structure

    @staticmethod
    def class_to_module(key_name):
        name_split = re.findall('[a-zA-Z][^A-Z]*', key_name)
        file_name = name_split[0].lower()
        if len(name_split) > 1:
            for i in range(1, len(name_split)):
                if len(name_split[i]) > 0:
                    file_name += '_' + name_split[i].lower()

        return file_name

