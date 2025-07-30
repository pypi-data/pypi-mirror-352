try:
    from officeintegrator.src.com.zoho.officeintegrator.exception import SDKException

except Exception:
    from ..exception import SDKException


class Utility(object):
    """
    This class handles module field details.
    """

    @staticmethod
    def get_json_object(json, key):
        for key_in_json in json.keys():
            if key_in_json.lower() == key.lower():
                return json[key_in_json]

        return None
    
    @staticmethod
    def check_data_type(value, type):
        try:
            from officeintegrator.src.com.zoho.officeintegrator.util import Constants
        except Exception:
            from .constants import Constants
        if value is None:
            return False
        if type.lower() == Constants.OBJECT.lower():
            return True
        type = Constants.DATA_TYPE.get(type)
        class_name = value.__class__
        if class_name == type:
            return True
        else:
            return False