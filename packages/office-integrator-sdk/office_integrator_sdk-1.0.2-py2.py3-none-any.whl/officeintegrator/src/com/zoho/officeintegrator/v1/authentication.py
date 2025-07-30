try:
	from officeintegrator.src.com.zoho.officeintegrator.exception.sdk_exception import SDKException
	from officeintegrator.src.com.zoho.officeintegrator.util.constants import Constants
	from officeintegrator.src.com.zoho.api.authenticator.authentication_schema import AuthenticationSchema
	from officeintegrator.src.com.zoho.api.authenticator.token import Token
except Exception:
	from ..exception import SDKException
	from ..util import Constants
	from ....zoho.api.authenticator.authentication_schema import AuthenticationSchema
	from ....zoho.api.authenticator.token import Token


class Authentication(object):
	def __init__(self):
		"""Creates an instance of Authentication"""
		pass



	class TokenFlow(AuthenticationSchema):
		pass

		def get_token_url(self):
			"""
			The method to get Token Url

			Returns:
				string: A string representing the Token_url
			"""

			return '/zest/v1/__internal/ticket'

		def get_authentication_url(self):
			"""
			The method to get Authentication Url

			Returns:
				string: A string representing the Authentication_url
			"""

			return ''

		def get_refresh_url(self):
			"""
			The method to get Refresh Url

			Returns:
				string: A string representing the Refresh_url
			"""

			return ''

		def get_schema(self):
			"""
			The method to get Schema

			Returns:
				string: A string representing the Schema
			"""

			return 'TokenFlow'

		def get_authentication_type(self):
			"""
			The method to get Authentication Type

			Returns:
				AuthenticationType: An instance of AuthenticationType
			"""

			return Token.AuthenticationType.TOKEN
