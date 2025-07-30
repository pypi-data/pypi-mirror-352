
try:
    import os
    import re
    import json
    from officeintegrator.src.com.zoho.officeintegrator.util.datatype_converter import DataTypeConverter
    from officeintegrator.src.com.zoho.officeintegrator.exception import SDKException
    from officeintegrator.src.com.zoho.officeintegrator.util.constants import Constants
    from officeintegrator.src.com.zoho.officeintegrator.util.json_converter import JSONConverter as JConverter
    from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer

except Exception:
    import os
    import re
    import json
    from .datatype_converter import DataTypeConverter
    from ..exception import SDKException
    from .constants import Constants
    from .json_converter import JSONConverter
    from ..initializer import Initializer

class HeaderParamValidator(object):
    """
    This class validates the Header and Parameter values with the type accepted by the APIs.
    """

    def validate(self, name, class_name, value):
        class_name = self.get_class_name(class_name)
        if class_name in Initializer.json_details:
            class_object = Initializer.json_details[class_name]
            for key in class_object.keys():
                member_detail = class_object[key]
                key_name = member_detail[Constants.NAME]
                if name == key_name:
                    if Constants.STRUCTURE_NAME in member_detail:
                        if isinstance(value, list):
                            json_array = []
                            request_objects = list(value)
                            if len(request_objects) > 0:
                                for request_object in request_objects:
                                    json_array.append(JConverter(None).form_request(request_object, member_detail[
                                        Constants.STRUCTURE_NAME], None, None, None))
                            return json_array.__str__()
                        return JConverter(None).form_request(value, member_detail[Constants.STRUCTURE_NAME], None, None,
                                                             None).__str__()
                    return self.parse_data(value).__str__()

        for key, value1 in Constants.DATA_TYPE.items():
            if value1 == value.__class__:
                data_type = key
                break

        return DataTypeConverter.post_convert(value, data_type)

    @staticmethod
    def get_class_name(class_name):
        return class_name.rsplit('.', 1)[0].lower() + class_name[class_name.rfind('.'):]

    def parse_data(self, value, type):
        if type == Constants.MAP_NAMESPACE:
            json_object = {}
            request_object = dict(value)
            if len(request_object) > 0:
                for key, field_value in request_object.items():
                    json_object[key] = self.parse_data(field_value, type)
            return json_object
        elif type == Constants.LIST_NAMESPACE:
            json_array = []
            request_objects = list(value)
            if len(request_objects) > 0:
                for request_object in request_objects:
                    json_array.append(self.parse_data(request_object, type))
            return json_array
        else:
            DataTypeConverter.post_convert(value, type)

    def get_key_json_details(self, name, json_details):
        for key_name in json_details.keys():
            detail = json_details[key_name]

            if Constants.NAME in detail:
                if detail[Constants.NAME].lower() == name.lower():
                    return detail

    def get_file_name(self, name):
        sdk_name = 'officeintegrator.src.'
        name_split = str(name).split('.')
        class_name = name_split.pop()

        package_name = name_split.pop()
        pack_split = re.findall('[A-Z][^A-Z]*', package_name)
        if len(pack_split) == 0:
            sdk_package_name = package_name
        else:
            sdk_package_name = pack_split[0].lower()

            if len(pack_split) > 1:
                for i in range(1, len(pack_split)):
                    sdk_package_name += '_' + pack_split[i].lower()

        name_split = list(map(lambda x: x.lower(), name_split))
        sdk_name = sdk_name + '.'.join(name_split) + '.' + sdk_package_name + '.' + class_name
        if "operation" in sdk_name or "Operation" in sdk_name:
            return sdk_name.lower()
        else:
            return sdk_name

    @staticmethod
    def get_json_details():
        
        try:
            from officeintegrator.src.com.zoho.officeintegrator.initializer import Initializer
        except Exception:
            from ..initializer import Initializer

        if Initializer.json_details is None:
            dir_name = os.path.dirname(__file__)
            filename = os.path.join(dir_name, '..', '..', '..', '..',  Constants.JSON_DETAILS_FILE_PATH)

            with open(filename, mode='r') as JSON:
                Initializer.json_details = json.load(JSON)

        return Initializer.json_details
