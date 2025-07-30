class SDKConfig(object):
    """
    The class to configure the SDK.
    """

    def __init__(self, pick_list_validation=True, read_timeout=None, connect_timeout=None, socket_timeout=None):
        """
        Creates an instance of SDKConfig with the following parameters

        Parameters:
            pick_list_validation(bool): A bool representing pick_list_validation
            read_timeout(float): A Float representing read_timeout
            connect_timeout(float): A Float representing connect_timeout
            socket_timeout(float): A Float representing socket_timeout
        """
        self.__pick_list_validation = pick_list_validation
        self.__read_timeout = read_timeout
        self.__connect_timeout = connect_timeout
        self.__socket_timeout = socket_timeout

    def get_socket_timeout(self):
        """
        This is a getter method to get socket_timeout.

        Returns:
             Float: A Float representing socket_timeout.
        """

    def get_pick_list_validation(self):
        """
        This is a getter method to get pick_list_validation.

        Returns:
            bool: A bool representing pick_list_validation
        """
        return self.__pick_list_validation

    def get_read_timeout(self):
        """
        This is a getter method to get read_timeout.

        Returns:
            Float: A Float representing read_timeout
        """
        return self.__read_timeout

    def get_connect_timeout(self):
        """
        This is a getter method to get connect_timeout.

        Returns:
            Float: A Float representing connect_timeout
        """
        return self.__connect_timeout
