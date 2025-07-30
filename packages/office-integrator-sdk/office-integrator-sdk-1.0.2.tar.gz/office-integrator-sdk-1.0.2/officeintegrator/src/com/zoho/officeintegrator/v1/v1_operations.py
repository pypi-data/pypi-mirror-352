try:
	from officeintegrator.src.com.zoho.officeintegrator.exception.sdk_exception import SDKException
	from officeintegrator.src.com.zoho.officeintegrator.util import APIResponse, CommonAPIHandler, Constants
except Exception:
	from ..exception import SDKException
	from ..util import APIResponse, CommonAPIHandler, Constants


class V1Operations(object):
	def __init__(self):
		"""Creates an instance of V1Operations"""
		pass

	def edit_pdf(self, request):
		"""
		The method to edit pdf

		Parameters:
			request (EditPdfParameters) : An instance of EditPdfParameters

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		try:
			from officeintegrator.src.com.zoho.officeintegrator.v1.edit_pdf_parameters import EditPdfParameters
		except Exception:
			from .edit_pdf_parameters import EditPdfParameters

		if request is not None and not isinstance(request, EditPdfParameters):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: request EXPECTED TYPE: EditPdfParameters', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/pdfeditor/officeapi/v1/pdf'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_POST)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_CREATE)
		handler_instance.set_request(request)
		handler_instance.set_method_name('edit_pdf')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def get_pdf_document_session(self, sessionid):
		"""
		The method to get pdf document session

		Parameters:
			sessionid (string) : A string representing the sessionid

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		if not isinstance(sessionid, str):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: sessionid EXPECTED TYPE: str', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/pdfeditor/officeapi/v1/sessions/'
		api_path = api_path + str(sessionid)
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_GET)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_READ)
		handler_instance.set_method_name('get_pdf_document_session')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def delete_pdf_document_session(self, sessionid):
		"""
		The method to delete pdf document session

		Parameters:
			sessionid (string) : A string representing the sessionid

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		if not isinstance(sessionid, str):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: sessionid EXPECTED TYPE: str', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/pdfeditor/officeapi/v1/sessions/'
		api_path = api_path + str(sessionid)
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_DELETE)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_READ)
		handler_instance.set_method_name('delete_pdf_document_session')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def get_pdf_document_info(self, documentid):
		"""
		The method to get pdf document info

		Parameters:
			documentid (string) : A string representing the documentid

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		if not isinstance(documentid, str):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: documentid EXPECTED TYPE: str', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/pdfeditor/officeapi/v1/pdf/'
		api_path = api_path + str(documentid)
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_GET)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_READ)
		handler_instance.set_method_name('get_pdf_document_info')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def delete_pdf_document(self, documentid):
		"""
		The method to delete pdf document

		Parameters:
			documentid (string) : A string representing the documentid

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		if not isinstance(documentid, str):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: documentid EXPECTED TYPE: str', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/pdfeditor/officeapi/v1/pdf/'
		api_path = api_path + str(documentid)
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_DELETE)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_READ)
		handler_instance.set_method_name('delete_pdf_document')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def create_document(self, request):
		"""
		The method to create document

		Parameters:
			request (CreateDocumentParameters) : An instance of CreateDocumentParameters

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		try:
			from officeintegrator.src.com.zoho.officeintegrator.v1.create_document_parameters import CreateDocumentParameters
		except Exception:
			from .create_document_parameters import CreateDocumentParameters

		if request is not None and not isinstance(request, CreateDocumentParameters):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: request EXPECTED TYPE: CreateDocumentParameters', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/writer/officeapi/v1/documents'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_POST)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_CREATE)
		handler_instance.set_request(request)
		handler_instance.set_method_name('create_document')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def create_document_preview(self, request):
		"""
		The method to create document preview

		Parameters:
			request (PreviewParameters) : An instance of PreviewParameters

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		try:
			from officeintegrator.src.com.zoho.officeintegrator.v1.preview_parameters import PreviewParameters
		except Exception:
			from .preview_parameters import PreviewParameters

		if request is not None and not isinstance(request, PreviewParameters):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: request EXPECTED TYPE: PreviewParameters', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/writer/officeapi/v1/document/preview'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_POST)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_CREATE)
		handler_instance.set_request(request)
		handler_instance.set_method_name('create_document_preview')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def create_watermark_document(self, request):
		"""
		The method to create watermark document

		Parameters:
			request (WatermarkParameters) : An instance of WatermarkParameters

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		try:
			from officeintegrator.src.com.zoho.officeintegrator.v1.watermark_parameters import WatermarkParameters
		except Exception:
			from .watermark_parameters import WatermarkParameters

		if request is not None and not isinstance(request, WatermarkParameters):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: request EXPECTED TYPE: WatermarkParameters', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/writer/officeapi/v1/document/watermark'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_POST)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_CREATE)
		handler_instance.set_request(request)
		handler_instance.set_method_name('create_watermark_document')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def create_mail_merge_template(self, request):
		"""
		The method to create mail merge template

		Parameters:
			request (MailMergeTemplateParameters) : An instance of MailMergeTemplateParameters

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		try:
			from officeintegrator.src.com.zoho.officeintegrator.v1.mail_merge_template_parameters import MailMergeTemplateParameters
		except Exception:
			from .mail_merge_template_parameters import MailMergeTemplateParameters

		if request is not None and not isinstance(request, MailMergeTemplateParameters):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: request EXPECTED TYPE: MailMergeTemplateParameters', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/writer/officeapi/v1/templates'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_POST)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_CREATE)
		handler_instance.set_request(request)
		handler_instance.set_method_name('create_mail_merge_template')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def get_merge_fields(self, request):
		"""
		The method to get merge fields

		Parameters:
			request (GetMergeFieldsParameters) : An instance of GetMergeFieldsParameters

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		try:
			from officeintegrator.src.com.zoho.officeintegrator.v1.get_merge_fields_parameters import GetMergeFieldsParameters
		except Exception:
			from .get_merge_fields_parameters import GetMergeFieldsParameters

		if request is not None and not isinstance(request, GetMergeFieldsParameters):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: request EXPECTED TYPE: GetMergeFieldsParameters', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/writer/officeapi/v1/fields'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_POST)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_READ)
		handler_instance.set_request(request)
		handler_instance.set_method_name('get_merge_fields')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def merge_and_deliver_via_webhook(self, request):
		"""
		The method to merge and deliver via webhook

		Parameters:
			request (MergeAndDeliverViaWebhookParameters) : An instance of MergeAndDeliverViaWebhookParameters

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		try:
			from officeintegrator.src.com.zoho.officeintegrator.v1.merge_and_deliver_via_webhook_parameters import MergeAndDeliverViaWebhookParameters
		except Exception:
			from .merge_and_deliver_via_webhook_parameters import MergeAndDeliverViaWebhookParameters

		if request is not None and not isinstance(request, MergeAndDeliverViaWebhookParameters):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: request EXPECTED TYPE: MergeAndDeliverViaWebhookParameters', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/writer/officeapi/v1/document/merge/webhook'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_POST)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_READ)
		handler_instance.set_request(request)
		handler_instance.set_method_name('merge_and_deliver_via_webhook')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def merge_and_download_document(self, request):
		"""
		The method to merge and download document

		Parameters:
			request (MergeAndDownloadDocumentParameters) : An instance of MergeAndDownloadDocumentParameters

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		try:
			from officeintegrator.src.com.zoho.officeintegrator.v1.merge_and_download_document_parameters import MergeAndDownloadDocumentParameters
		except Exception:
			from .merge_and_download_document_parameters import MergeAndDownloadDocumentParameters

		if request is not None and not isinstance(request, MergeAndDownloadDocumentParameters):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: request EXPECTED TYPE: MergeAndDownloadDocumentParameters', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/writer/officeapi/v1/document/merge'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_POST)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_CREATE)
		handler_instance.set_request(request)
		handler_instance.set_method_name('merge_and_download_document')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def create_fillable_template_document(self, request):
		"""
		The method to create fillable template document

		Parameters:
			request (CreateDocumentParameters) : An instance of CreateDocumentParameters

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		try:
			from officeintegrator.src.com.zoho.officeintegrator.v1.create_document_parameters import CreateDocumentParameters
		except Exception:
			from .create_document_parameters import CreateDocumentParameters

		if request is not None and not isinstance(request, CreateDocumentParameters):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: request EXPECTED TYPE: CreateDocumentParameters', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/writer/officeapi/v1/fillabletemplates'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_POST)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_CREATE)
		handler_instance.set_request(request)
		handler_instance.set_method_name('create_fillable_template_document')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def create_fillable_link(self, request):
		"""
		The method to create fillable link

		Parameters:
			request (FillableLinkParameters) : An instance of FillableLinkParameters

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		try:
			from officeintegrator.src.com.zoho.officeintegrator.v1.fillable_link_parameters import FillableLinkParameters
		except Exception:
			from .fillable_link_parameters import FillableLinkParameters

		if request is not None and not isinstance(request, FillableLinkParameters):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: request EXPECTED TYPE: FillableLinkParameters', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/writer/officeapi/v1/fillabletemplates/fillablelink'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_POST)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_CREATE)
		handler_instance.set_request(request)
		handler_instance.set_method_name('create_fillable_link')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def convert_document(self, request):
		"""
		The method to convert document

		Parameters:
			request (DocumentConversionParameters) : An instance of DocumentConversionParameters

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		try:
			from officeintegrator.src.com.zoho.officeintegrator.v1.document_conversion_parameters import DocumentConversionParameters
		except Exception:
			from .document_conversion_parameters import DocumentConversionParameters

		if request is not None and not isinstance(request, DocumentConversionParameters):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: request EXPECTED TYPE: DocumentConversionParameters', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/writer/officeapi/v1/document/convert'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_POST)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_CREATE)
		handler_instance.set_request(request)
		handler_instance.set_method_name('convert_document')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def combine_pdf(self, request):
		"""
		The method to combine pdf

		Parameters:
			request (CombinePdfParameters) : An instance of CombinePdfParameters

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		try:
			from officeintegrator.src.com.zoho.officeintegrator.v1.combine_pdf_parameters import CombinePdfParameters
		except Exception:
			from .combine_pdf_parameters import CombinePdfParameters

		if request is not None and not isinstance(request, CombinePdfParameters):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: request EXPECTED TYPE: CombinePdfParameters', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/writer/officeapi/v1/documents/pdf/combine'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_POST)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_CREATE)
		handler_instance.set_request(request)
		handler_instance.set_method_name('combine_pdf')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def compare_document(self, request):
		"""
		The method to compare document

		Parameters:
			request (CompareDocumentParameters) : An instance of CompareDocumentParameters

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		try:
			from officeintegrator.src.com.zoho.officeintegrator.v1.compare_document_parameters import CompareDocumentParameters
		except Exception:
			from .compare_document_parameters import CompareDocumentParameters

		if request is not None and not isinstance(request, CompareDocumentParameters):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: request EXPECTED TYPE: CompareDocumentParameters', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/writer/officeapi/v1/document/compare'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_POST)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_CREATE)
		handler_instance.set_request(request)
		handler_instance.set_method_name('compare_document')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def get_all_sessions(self, documentid):
		"""
		The method to get all sessions

		Parameters:
			documentid (string) : A string representing the documentid

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		if not isinstance(documentid, str):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: documentid EXPECTED TYPE: str', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/writer/officeapi/v1/documents/'
		api_path = api_path + str(documentid)
		api_path = api_path + '/sessions'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_GET)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_READ)
		handler_instance.set_method_name('get_all_sessions')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def get_session(self, sessionid):
		"""
		The method to get session

		Parameters:
			sessionid (string) : A string representing the sessionid

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		if not isinstance(sessionid, str):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: sessionid EXPECTED TYPE: str', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/writer/officeapi/v1/sessions/'
		api_path = api_path + str(sessionid)
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_GET)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_READ)
		handler_instance.set_method_name('get_session')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def delete_session(self, sessionid):
		"""
		The method to delete session

		Parameters:
			sessionid (string) : A string representing the sessionid

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		if not isinstance(sessionid, str):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: sessionid EXPECTED TYPE: str', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/writer/officeapi/v1/sessions/'
		api_path = api_path + str(sessionid)
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_DELETE)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_READ)
		handler_instance.set_method_name('delete_session')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def get_document_info(self, documentid):
		"""
		The method to get document info

		Parameters:
			documentid (string) : A string representing the documentid

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		if not isinstance(documentid, str):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: documentid EXPECTED TYPE: str', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/writer/officeapi/v1/documents/'
		api_path = api_path + str(documentid)
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_GET)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_READ)
		handler_instance.set_method_name('get_document_info')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def delete_document(self, documentid):
		"""
		The method to delete document

		Parameters:
			documentid (string) : A string representing the documentid

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		if not isinstance(documentid, str):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: documentid EXPECTED TYPE: str', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/writer/officeapi/v1/documents/'
		api_path = api_path + str(documentid)
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_DELETE)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_READ)
		handler_instance.set_method_name('delete_document')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def create_sheet(self, request):
		"""
		The method to create sheet

		Parameters:
			request (CreateSheetParameters) : An instance of CreateSheetParameters

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		try:
			from officeintegrator.src.com.zoho.officeintegrator.v1.create_sheet_parameters import CreateSheetParameters
		except Exception:
			from .create_sheet_parameters import CreateSheetParameters

		if request is not None and not isinstance(request, CreateSheetParameters):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: request EXPECTED TYPE: CreateSheetParameters', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/sheet/officeapi/v1/spreadsheet'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_POST)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_CREATE)
		handler_instance.set_request(request)
		handler_instance.set_method_name('create_sheet')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def create_sheet_preview(self, request):
		"""
		The method to create sheet preview

		Parameters:
			request (SheetPreviewParameters) : An instance of SheetPreviewParameters

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		try:
			from officeintegrator.src.com.zoho.officeintegrator.v1.sheet_preview_parameters import SheetPreviewParameters
		except Exception:
			from .sheet_preview_parameters import SheetPreviewParameters

		if request is not None and not isinstance(request, SheetPreviewParameters):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: request EXPECTED TYPE: SheetPreviewParameters', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/sheet/officeapi/v1/spreadsheet/preview'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_POST)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_CREATE)
		handler_instance.set_request(request)
		handler_instance.set_method_name('create_sheet_preview')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def download_sheet(self, documentid, request):
		"""
		The method to download sheet

		Parameters:
			documentid (string) : A string representing the documentid
			request (SheetDownloadParameters) : An instance of SheetDownloadParameters

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		try:
			from officeintegrator.src.com.zoho.officeintegrator.v1.sheet_download_parameters import SheetDownloadParameters
		except Exception:
			from .sheet_download_parameters import SheetDownloadParameters

		if not isinstance(documentid, str):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: documentid EXPECTED TYPE: str', None, None)
		
		if request is not None and not isinstance(request, SheetDownloadParameters):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: request EXPECTED TYPE: SheetDownloadParameters', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/sheet/officeapi/v1/spreadsheet/'
		api_path = api_path + str(documentid)
		api_path = api_path + '/download'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_POST)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_READ)
		handler_instance.set_request(request)
		handler_instance.set_method_name('download_sheet')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def convert_sheet(self, request):
		"""
		The method to convert sheet

		Parameters:
			request (SheetConversionParameters) : An instance of SheetConversionParameters

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		try:
			from officeintegrator.src.com.zoho.officeintegrator.v1.sheet_conversion_parameters import SheetConversionParameters
		except Exception:
			from .sheet_conversion_parameters import SheetConversionParameters

		if request is not None and not isinstance(request, SheetConversionParameters):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: request EXPECTED TYPE: SheetConversionParameters', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/sheet/officeapi/v1/spreadsheet/convert'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_POST)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_CREATE)
		handler_instance.set_request(request)
		handler_instance.set_method_name('convert_sheet')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def get_sheet_session(self, sessionid):
		"""
		The method to get sheet session

		Parameters:
			sessionid (string) : A string representing the sessionid

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		if not isinstance(sessionid, str):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: sessionid EXPECTED TYPE: str', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/sheet/officeapi/v1/sessions/'
		api_path = api_path + str(sessionid)
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_GET)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_READ)
		handler_instance.set_method_name('get_sheet_session')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def delete_sheet_session(self, sessionid):
		"""
		The method to delete sheet session

		Parameters:
			sessionid (string) : A string representing the sessionid

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		if not isinstance(sessionid, str):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: sessionid EXPECTED TYPE: str', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/sheet/officeapi/v1/session/'
		api_path = api_path + str(sessionid)
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_DELETE)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_READ)
		handler_instance.set_method_name('delete_sheet_session')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def delete_sheet(self, documentid):
		"""
		The method to delete sheet

		Parameters:
			documentid (string) : A string representing the documentid

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		if not isinstance(documentid, str):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: documentid EXPECTED TYPE: str', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/sheet/officeapi/v1/spreadsheet/'
		api_path = api_path + str(documentid)
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_DELETE)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_READ)
		handler_instance.set_method_name('delete_sheet')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def create_presentation(self, request):
		"""
		The method to create presentation

		Parameters:
			request (CreatePresentationParameters) : An instance of CreatePresentationParameters

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		try:
			from officeintegrator.src.com.zoho.officeintegrator.v1.create_presentation_parameters import CreatePresentationParameters
		except Exception:
			from .create_presentation_parameters import CreatePresentationParameters

		if request is not None and not isinstance(request, CreatePresentationParameters):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: request EXPECTED TYPE: CreatePresentationParameters', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/show/officeapi/v1/presentation'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_POST)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_CREATE)
		handler_instance.set_request(request)
		handler_instance.set_method_name('create_presentation')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def convert_presentation(self, request):
		"""
		The method to convert presentation

		Parameters:
			request (ConvertPresentationParameters) : An instance of ConvertPresentationParameters

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		try:
			from officeintegrator.src.com.zoho.officeintegrator.v1.convert_presentation_parameters import ConvertPresentationParameters
		except Exception:
			from .convert_presentation_parameters import ConvertPresentationParameters

		if request is not None and not isinstance(request, ConvertPresentationParameters):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: request EXPECTED TYPE: ConvertPresentationParameters', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/show/officeapi/v1/presentation/convert'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_POST)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_CREATE)
		handler_instance.set_request(request)
		handler_instance.set_method_name('convert_presentation')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def create_presentation_preview(self, request):
		"""
		The method to create presentation preview

		Parameters:
			request (PresentationPreviewParameters) : An instance of PresentationPreviewParameters

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		try:
			from officeintegrator.src.com.zoho.officeintegrator.v1.presentation_preview_parameters import PresentationPreviewParameters
		except Exception:
			from .presentation_preview_parameters import PresentationPreviewParameters

		if request is not None and not isinstance(request, PresentationPreviewParameters):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: request EXPECTED TYPE: PresentationPreviewParameters', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/show/officeapi/v1/presentation/preview'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_POST)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_CREATE)
		handler_instance.set_request(request)
		handler_instance.set_method_name('create_presentation_preview')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def get_presentation_session(self, sessionid):
		"""
		The method to get presentation session

		Parameters:
			sessionid (string) : A string representing the sessionid

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		if not isinstance(sessionid, str):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: sessionid EXPECTED TYPE: str', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/show/officeapi/v1/sessions/'
		api_path = api_path + str(sessionid)
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_GET)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_READ)
		handler_instance.set_method_name('get_presentation_session')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def delete_presentation_session(self, sessionid):
		"""
		The method to delete presentation session

		Parameters:
			sessionid (string) : A string representing the sessionid

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		if not isinstance(sessionid, str):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: sessionid EXPECTED TYPE: str', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/show/officeapi/v1/session/'
		api_path = api_path + str(sessionid)
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_DELETE)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_READ)
		handler_instance.set_method_name('delete_presentation_session')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def delete_presentation(self, documentid):
		"""
		The method to delete presentation

		Parameters:
			documentid (string) : A string representing the documentid

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		if not isinstance(documentid, str):
			raise SDKException(Constants.DATA_TYPE_ERROR, 'KEY: documentid EXPECTED TYPE: str', None, None)
		
		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/show/officeapi/v1/presentation/'
		api_path = api_path + str(documentid)
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_DELETE)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_READ)
		handler_instance.set_method_name('delete_presentation')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()

	def get_plan_details(self):
		"""
		The method to get plan details

		Returns:
			APIResponse: An instance of APIResponse

		Raises:
			SDKException
		"""

		handler_instance = CommonAPIHandler()
		api_path = ''
		api_path = api_path + '/api/v1/plan'
		handler_instance.set_api_path(api_path)
		handler_instance.set_http_method(Constants.REQUEST_METHOD_GET)
		handler_instance.set_category_method(Constants.REQUEST_CATEGORY_READ)
		handler_instance.set_method_name('get_plan_details')
		handler_instance.set_operation_class_name('com.zoho.officeintegrator.V1.V1Operations')
		return handler_instance.api_call()
