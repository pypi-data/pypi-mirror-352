try:
	from officeintegrator.src.com.zoho.officeintegrator.exception.sdk_exception import SDKException
	from officeintegrator.src.com.zoho.officeintegrator.util.constants import Constants
	from officeintegrator.src.com.zoho.api.authenticator.token import Token
	from officeintegrator.src.com.zoho.officeintegrator.dc.environment import Environment
except Exception:
	from ..exception import SDKException
	from ..util import Constants
	from ....zoho.api.authenticator.token import Token
	from .environment import Environment


class DataCenter(object):
	def __init__(self):
		"""Creates an instance of DataCenter"""
		pass



	class Production(Environment):
		def __init__(self, server_domain):
			"""
			Creates an instance of Production with the given parameters

			Parameters:
				server_domain (string) : A string representing the server_domain
			"""

			if server_domain is not None and not isinstance(server_domain, str):
				raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: server_domain EXPECTED TYPE: str', None, None)
			
			self.__server_domain = server_domain


		def get_url(self):
			"""
			The method to get Url

			Returns:
				string: A string representing the Url
			"""

			return '' + self.__server_domain + ''

		def get_dc(self):
			"""
			The method to get dc

			Returns:
				string: A string representing the dc
			"""

			return 'alldc'

		def get_location(self):
			"""
			The method to get location

			Returns:
				Location: An instance of Location
			"""

			return None

		def get_name(self):
			"""
			The method to get name

			Returns:
				string: A string representing the name
			"""

			return ''

		def get_value(self):
			"""
			The method to get value

			Returns:
				string: A string representing the value
			"""

			return ''
