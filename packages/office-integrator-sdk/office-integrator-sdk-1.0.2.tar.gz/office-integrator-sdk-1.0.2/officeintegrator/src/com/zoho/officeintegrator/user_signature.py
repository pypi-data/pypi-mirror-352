
class UserSignature(object):

    """
    This class represents the Zoho User.
    """

    def __init__(self, name):

        """
        Creates an UserSignature class instance with the specified user_name.

        Parameters:
            name (str) : A string containing the user_name
        """

        self.__name = name

    def get_name(self):
        """
        This is a getter method to get __name.

        Returns:
            string: A string representing __name
        """

        return self.__name
