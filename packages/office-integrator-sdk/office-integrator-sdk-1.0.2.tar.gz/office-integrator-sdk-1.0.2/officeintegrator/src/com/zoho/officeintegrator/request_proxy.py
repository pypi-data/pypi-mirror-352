try:
    from officeintegrator.src.com.zoho.officeintegrator.exception import SDKException
    from officeintegrator.src.com.zoho.officeintegrator.util.constants import Constants

except Exception:
    from .exception import SDKException
    from .util import Constants


class RequestProxy(object):
    def __init__(self, host, port, user_domain, user=None, password=""):

        """
        Creates a RequestProxy class instance with the specified parameters.

        Parameters:
            host(str): A String containing the hostname or address of the proxy server
            port(int): An Integer containing The port number of the proxy server
            user_domain(str) A String containing the domain of the proxy server
            user(str): A String containing the user name of the proxy server
            password(str) : A String containing the password of the proxy server. Default value is an empty string

        Raises:
            SDKException
        """

        if host is None:
            raise SDKException(Constants.USER_PROXY_ERROR, Constants.HOST_ERROR_MESSAGE)

        if port is None:
            raise SDKException(Constants.USER_PROXY_ERROR, Constants.PORT_ERROR_MESSAGE)

        self.__host = host
        self.__port = port
        self.__user_domain = user_domain
        self.__user = user
        self.__password = password

    def get_host(self):
        """
        This is a getter method to get __host.

        Returns:
            string: A string representing __host
        """

    def get_port(self):
        """
        This is a getter method to get __port.

        Returns:
            string: A string representing __port
        """

    def get_user(self):
        """
        This is a getter method to get __user.

        Returns:
            string: A string representing __user
        """

    def get_password(self):
        """
        This is a getter method to get __password.

        Returns:
            string: A string representing __password
        """

    def get_user_domain(self):
        """
        This is a getter method to get __user_domain

        Returns:
            string: A string representing __user_domain
        """
