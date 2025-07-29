# coding: utf-8

"""
    T3 API

    ## WHAT IS THIS?  This API is part of the [Track & Trace Tools](https://trackandtrace.tools) platform. The API allows you to programmatically access all your Metrc data that is available on metrc.com  It is not related to the Metrc 3rd party API, does not use Metrc API keys, and is not affiliated with Metrc.  If you're looking for where to get started, check out the [T3 Wiki API Getting Started guide](https://github.com/classvsoftware/t3-wiki/wiki/T3-API-:-Getting-Started).  The T3 API is subject to the [Track & Trace Tools Terms of Use](https://www.trackandtrace.tools/terms-of-use).   ## FREE API ACCESS (LIMITED)  The T3 API features a limited number of free endpoints available to anyone with a Metrc login.  These can be found in the [Free](#/Free) section.  ## FULL API ACCESS  There are two ways to get premium access to the T3 API:  - **Subscribe to [T3+](https://trackandtrace.tools/plus)**  *OR*  - **Use a provided T3 API key (consulting clients only. [Reach out](mailto:matt@trackandtrace.tools) for more information.)**  ## AUTHENTICATION  The T3 API uses JSON Web Tokens (JWT) for request authentication. To obtain a JWT, use one of the following:  - **metrc.com login credentials:**   - **hostname**: (The website you use to login to metrc: `ca.metrc.com`, `or.metrc.com`, etc.)   - **username**: Your Metrc username   - **password**: Your Metrc password   - **otp**: A one-time password used for 2-factor authentication (Only applies to Michigan users)  *OR*  - **T3 API key**  Refer to the **Authentication** endpoints below for more information.  ## SECRET KEYS  Some endpoints support the use of secret key authentication. This allows you to use simple URLs to access your Metrc data.  ### Usage  Pass the `secretKey` returned from the request in the query string:  `?secretKey=<yourSecretKeyGoesHere>`  ### Generating Secret Keys  Refer to the [/v2/auth/secretkey](#/Authentication/post_v2_auth_secretkey) endpoint for information on generating secret keys.  [Secret Key Generation Tool](/v2/pages/secret-key)  [Sync Link Creation Tool](/v2/pages/sync-link)  ## SECURITY  The T3 API interacts with Metrc in a similar manner to the [Track & Trace Tools](https://chromewebstore.google.com/detail/track-trace-tools/dfljickgkbfaoiifheibjpejloipegcb) Chrome extension. The API login process is designed with a strong emphasis on security. Your Metrc login details are never stored, and the API backend employs robust encryption methods to protect your temporary Metrc session.  ### Key Security Measures:  - **Single-Use Login Credentials:**    - The T3 API uses your login credentials only once to authenticate with Metrc.   - After the Metrc login process is complete, your login credentials are immediately deleted from the system.   - You are required to enter your login credentials each time you access the T3 API, ensuring that your credentials are never stored.    - **Secure Temporary Session Storage:**    - The T3 API securely encrypts your logged-in Metrc session data. This data is only used when you make requests through the T3 API.   - The encrypted session data is automatically deleted after 24 hours, ensuring that your session information is not retained longer than necessary.  For any questions or concerns, please contact [matt@trackandtrace.tools](mailto:matt@trackandtrace.tools).  ## PRIVACY  The T3 API privacy model follows the same principles as the [Track & Trace Tools](https://chromewebstore.google.com/detail/track-trace-tools/dfljickgkbfaoiifheibjpejloipegcb) Chrome extension. The T3 API functions solely as a connector between you and Metrc, ensuring your privacy is protected.  - **No Data Collection:**    - The T3 API does not record, save, harvest, inspect, or analyze any of your data.   - All data interactions are ephemeral and occur in real-time, without permanent storage.  - **Secure and Private Access:**    - Your data is never shared with third parties. Unauthorized access to your login information or data is strictly prohibited.   - T3 employs industry-standard encryption protocols to safeguard all communications between the T3 API and Metrc.    - **User-Controlled Sessions:**    - Your Metrc login credentials and session are used exclusively by you. The T3 API will never initiate Metrc traffic without your explicit authorization.  - **Compliance and Best Practices:**   - T3's privacy practices are aligned with applicable data protection regulations, including GDPR and CCPA, ensuring that your data rights are respected.  The T3 API is subject to the [Track & Trace Tools Privacy Policy](https://trackandtrace.tools/privacy-policy). For any privacy-related inquiries, please contact [matt@trackandtrace.tools](mailto:matt@trackandtrace.tools).  ## PERMISSIONS  Each Metrc account has different permissions based on several factors:  - Permissions granted by your Metrc admin - Class of license (manufacturing, cultivation, etc) - US state the license operates in  Use the Permissions endpoints to determine which actions are available to you.  ## LICENSES  View a list of all licenses available to the current user:  `GET https://api.trackandtrace.tools/v2/licenses`  Only one license can be queried per request. Specify the target license with the required `licenseNumber` query parameter:  `GET https://api.trackandtrace.tools/v2/items?licenseNumber=LIC-00001`  ## RATE LIMITING  The API has a global default request rate limit of 600 requests/minute/user. Some routes have lower rate limits.  ## COLLECTIONS  All data is queried as collections. There are no individual object endpoints.  For example, you cannot find an individual object using an endpoint like `/plants/{plantId}`, individual objects must be queried by filtering the collection endpoint `/plants` for the exact `plantId`.   Collections are paginated, and can be filtered and sorted by individual object fields.  The JSON response object includes the following properties: - `data`: An array of objects, or any empty array - `page`: The requested page index - `pageSize`: The requested page size - `total`: The total number of items in this collection. Use this to determine how many pages are required to return the entire collection.  ### COLLECTION PAGINATION  Metrc data collections are queried as pages. Use the `page` and `pageSize` query parameters to indicate which page should be returned.  By default, `page=1` and `pageSize=100`.  Example: Return page 3 with a page size of 500:  `GET https://api.trackandtrace.tools/v2/items?licenseNumber=LIC-00001&page=3&pageSize=500`  ### COLLECTION SORTING  Metrc data collections can be sorted. Use the `sort` query parameter to indicate how the collection should be sorted.  Example: Sort items by `name` descending:  `GET https://api.trackandtrace.tools/v2/items?licenseNumber=LIC-00001&sort=name:desc`  ### COLLECTION FILTERING  Metrc data collections can be filtered. Use one or more `filter` query parameters to indicate how filters should be applied.  Example: Filter items that contain \"flower\" in the `name` field:  `GET https://api.trackandtrace.tools/v2/items?licenseNumber=LIC-00001&filter:name__contains=flower`  Multiple filters can be applied, and you can specify the logical operator (defaulting to \"and\"):  Example: Filter items that contain \"flower\" in the `name` field OR \"kush\" in the `name` field:  `GET https://api.trackandtrace.tools/v2/items?licenseNumber=LIC-00001&filter=name__contains:flower&filter=name__contains:kush&filterLogic=or`  #### FILTERING STRINGS  String fields support the following filter operators:  - `contains` - `doesnotcontain` - `eq` - `neq` - `startswith` - `endswith`  Example `?filter=name__contains:flower`  **Note: all string filters are case-insensitive**  #### FILTERING DATETIMES  Datetime fields support the following filter operators:  - `lt` - `lte` - `eq` - `neq` - `gt` - `gte`  Example: `?filter=harvestedDate__gte:2024-07-17T20:26:07.117Z`  **Note: all datetime filters use ISO8601 datetimes**  #### FILTERING BOOLEANS  Boolean fields support the following filter operators:  - `eq`  Example: `?filter=finished__eq:true`  ### LOADING FULL COLLECTIONS `pageSize` is limited to 500 in most cases, so you may need to load multiple pages if a license has a large number of packages.  Refer to [this example](https://github.com/classvsoftware/t3-api/blob/master/load_all_active_packages.py) for how to load a full collection in a python script.  ## USING THE API  The API can be used in any way you like, but writing simple scripts to accomplish common tasks is an excellent way to take advantage of it.  The full OpenAPI spec, which can be imported into Postman, can be found here: [/v2/spec/openapi.json](/v2/spec/openapi.json)  [**Lots** of example scripts that show how the use the T3 API can be found here](https://github.com/classvsoftware/t3-api)  ## CONTACT  - **Responsible Organization:** Class V LLC - **Responsible Developer:** Matt Frisbie - **Email:** [matt@trackandtrace.tools](mailto:matt@trackandtrace.tools) - **URL:** [https://trackandtrace.tools](https://trackandtrace.tools) - **Terms of Use:** [https://www.trackandtrace.tools/terms-of-use](https://www.trackandtrace.tools/terms-of-use) 

    The version of the OpenAPI document: v2
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501

import warnings
from pydantic import validate_call, Field, StrictFloat, StrictStr, StrictInt
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Annotated

from pydantic import Field, StrictBool, StrictBytes, StrictFloat, StrictInt, StrictStr, field_validator
from typing import List, Optional, Tuple, Union
from typing_extensions import Annotated
from t3api.models.v2_packages_labresult_batches_get200_response import V2PackagesLabresultBatchesGet200Response
from t3api.models.v2_packages_labresults_get200_response import V2PackagesLabresultsGet200Response

from t3api.api_client import ApiClient, RequestSerialized
from t3api.api_response import ApiResponse
from t3api.rest import RESTResponseType


class LabResultsApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client


    @validate_call
    def v2_packages_labresult_batches_get(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        package_id: Annotated[Union[StrictFloat, StrictInt], Field(description="ID of the target package")],
        page: Annotated[Optional[StrictInt], Field(description="The index of the page to be returned.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="The number of objects per page to be returned.")] = None,
        strict_pagination: Annotated[Optional[StrictBool], Field(description="Toggles strict pagination. Defaults to `false` (disabled)    - If enabled, requesting an out of bounds page will throw a 400.    - If disabled, requesting an out of bounds page will return a 200 and an empty page.")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> V2PackagesLabresultBatchesGet200Response:
        """List of package lab result batch objects for a single package


        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param package_id: ID of the target package (required)
        :type package_id: float
        :param page: The index of the page to be returned.
        :type page: int
        :param page_size: The number of objects per page to be returned.
        :type page_size: int
        :param strict_pagination: Toggles strict pagination. Defaults to `false` (disabled)    - If enabled, requesting an out of bounds page will throw a 400.    - If disabled, requesting an out of bounds page will return a 200 and an empty page.
        :type strict_pagination: bool
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v2_packages_labresult_batches_get_serialize(
            license_number=license_number,
            package_id=package_id,
            page=page,
            page_size=page_size,
            strict_pagination=strict_pagination,
            sort=sort,
            filter_logic=filter_logic,
            filter=filter,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PackagesLabresultBatchesGet200Response",
            '404': None,
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v2_packages_labresult_batches_get_with_http_info(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        package_id: Annotated[Union[StrictFloat, StrictInt], Field(description="ID of the target package")],
        page: Annotated[Optional[StrictInt], Field(description="The index of the page to be returned.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="The number of objects per page to be returned.")] = None,
        strict_pagination: Annotated[Optional[StrictBool], Field(description="Toggles strict pagination. Defaults to `false` (disabled)    - If enabled, requesting an out of bounds page will throw a 400.    - If disabled, requesting an out of bounds page will return a 200 and an empty page.")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[V2PackagesLabresultBatchesGet200Response]:
        """List of package lab result batch objects for a single package


        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param package_id: ID of the target package (required)
        :type package_id: float
        :param page: The index of the page to be returned.
        :type page: int
        :param page_size: The number of objects per page to be returned.
        :type page_size: int
        :param strict_pagination: Toggles strict pagination. Defaults to `false` (disabled)    - If enabled, requesting an out of bounds page will throw a 400.    - If disabled, requesting an out of bounds page will return a 200 and an empty page.
        :type strict_pagination: bool
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v2_packages_labresult_batches_get_serialize(
            license_number=license_number,
            package_id=package_id,
            page=page,
            page_size=page_size,
            strict_pagination=strict_pagination,
            sort=sort,
            filter_logic=filter_logic,
            filter=filter,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PackagesLabresultBatchesGet200Response",
            '404': None,
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v2_packages_labresult_batches_get_without_preload_content(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        package_id: Annotated[Union[StrictFloat, StrictInt], Field(description="ID of the target package")],
        page: Annotated[Optional[StrictInt], Field(description="The index of the page to be returned.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="The number of objects per page to be returned.")] = None,
        strict_pagination: Annotated[Optional[StrictBool], Field(description="Toggles strict pagination. Defaults to `false` (disabled)    - If enabled, requesting an out of bounds page will throw a 400.    - If disabled, requesting an out of bounds page will return a 200 and an empty page.")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """List of package lab result batch objects for a single package


        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param package_id: ID of the target package (required)
        :type package_id: float
        :param page: The index of the page to be returned.
        :type page: int
        :param page_size: The number of objects per page to be returned.
        :type page_size: int
        :param strict_pagination: Toggles strict pagination. Defaults to `false` (disabled)    - If enabled, requesting an out of bounds page will throw a 400.    - If disabled, requesting an out of bounds page will return a 200 and an empty page.
        :type strict_pagination: bool
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v2_packages_labresult_batches_get_serialize(
            license_number=license_number,
            package_id=package_id,
            page=page,
            page_size=page_size,
            strict_pagination=strict_pagination,
            sort=sort,
            filter_logic=filter_logic,
            filter=filter,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PackagesLabresultBatchesGet200Response",
            '404': None,
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v2_packages_labresult_batches_get_serialize(
        self,
        license_number,
        package_id,
        page,
        page_size,
        strict_pagination,
        sort,
        filter_logic,
        filter,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
            'filter': 'multi',
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if license_number is not None:
            
            _query_params.append(('licenseNumber', license_number))
            
        if package_id is not None:
            
            _query_params.append(('packageId', package_id))
            
        if page is not None:
            
            _query_params.append(('page', page))
            
        if page_size is not None:
            
            _query_params.append(('pageSize', page_size))
            
        if strict_pagination is not None:
            
            _query_params.append(('strictPagination', strict_pagination))
            
        if sort is not None:
            
            _query_params.append(('sort', sort))
            
        if filter_logic is not None:
            
            _query_params.append(('filterLogic', filter_logic))
            
        if filter is not None:
            
            _query_params.append(('filter', filter))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'BearerAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v2/packages/labresult-batches',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v2_packages_labresults_document_get(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        package_id: Annotated[Union[StrictFloat, StrictInt], Field(description="ID of the target package")],
        lab_test_result_document_file_id: Annotated[Union[StrictFloat, StrictInt], Field(description="ID of the target lab result")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> bytearray:
        """Get the COA PDF for a lab result.

        **NOTE: A single package might have hundreds of lab results, but most will share just one or two lab test result document IDs.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param package_id: ID of the target package (required)
        :type package_id: float
        :param lab_test_result_document_file_id: ID of the target lab result (required)
        :type lab_test_result_document_file_id: float
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v2_packages_labresults_document_get_serialize(
            license_number=license_number,
            package_id=package_id,
            lab_test_result_document_file_id=lab_test_result_document_file_id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "bytearray",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v2_packages_labresults_document_get_with_http_info(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        package_id: Annotated[Union[StrictFloat, StrictInt], Field(description="ID of the target package")],
        lab_test_result_document_file_id: Annotated[Union[StrictFloat, StrictInt], Field(description="ID of the target lab result")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[bytearray]:
        """Get the COA PDF for a lab result.

        **NOTE: A single package might have hundreds of lab results, but most will share just one or two lab test result document IDs.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param package_id: ID of the target package (required)
        :type package_id: float
        :param lab_test_result_document_file_id: ID of the target lab result (required)
        :type lab_test_result_document_file_id: float
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v2_packages_labresults_document_get_serialize(
            license_number=license_number,
            package_id=package_id,
            lab_test_result_document_file_id=lab_test_result_document_file_id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "bytearray",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v2_packages_labresults_document_get_without_preload_content(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        package_id: Annotated[Union[StrictFloat, StrictInt], Field(description="ID of the target package")],
        lab_test_result_document_file_id: Annotated[Union[StrictFloat, StrictInt], Field(description="ID of the target lab result")],
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get the COA PDF for a lab result.

        **NOTE: A single package might have hundreds of lab results, but most will share just one or two lab test result document IDs.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param package_id: ID of the target package (required)
        :type package_id: float
        :param lab_test_result_document_file_id: ID of the target lab result (required)
        :type lab_test_result_document_file_id: float
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v2_packages_labresults_document_get_serialize(
            license_number=license_number,
            package_id=package_id,
            lab_test_result_document_file_id=lab_test_result_document_file_id,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "bytearray",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v2_packages_labresults_document_get_serialize(
        self,
        license_number,
        package_id,
        lab_test_result_document_file_id,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if license_number is not None:
            
            _query_params.append(('licenseNumber', license_number))
            
        if package_id is not None:
            
            _query_params.append(('packageId', package_id))
            
        if lab_test_result_document_file_id is not None:
            
            _query_params.append(('labTestResultDocumentFileId', lab_test_result_document_file_id))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/pdf'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'BearerAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v2/packages/labresults/document',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def v2_packages_labresults_get(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        package_id: Annotated[Union[StrictFloat, StrictInt], Field(description="ID of the target package")],
        page: Annotated[Optional[StrictInt], Field(description="The index of the page to be returned.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="The number of objects per page to be returned.")] = None,
        strict_pagination: Annotated[Optional[StrictBool], Field(description="Toggles strict pagination. Defaults to `false` (disabled)    - If enabled, requesting an out of bounds page will throw a 400.    - If disabled, requesting an out of bounds page will return a 200 and an empty page.")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> V2PackagesLabresultsGet200Response:
        """List of package lab result objects for a single package


        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param package_id: ID of the target package (required)
        :type package_id: float
        :param page: The index of the page to be returned.
        :type page: int
        :param page_size: The number of objects per page to be returned.
        :type page_size: int
        :param strict_pagination: Toggles strict pagination. Defaults to `false` (disabled)    - If enabled, requesting an out of bounds page will throw a 400.    - If disabled, requesting an out of bounds page will return a 200 and an empty page.
        :type strict_pagination: bool
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v2_packages_labresults_get_serialize(
            license_number=license_number,
            package_id=package_id,
            page=page,
            page_size=page_size,
            strict_pagination=strict_pagination,
            sort=sort,
            filter_logic=filter_logic,
            filter=filter,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PackagesLabresultsGet200Response",
            '404': None,
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def v2_packages_labresults_get_with_http_info(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        package_id: Annotated[Union[StrictFloat, StrictInt], Field(description="ID of the target package")],
        page: Annotated[Optional[StrictInt], Field(description="The index of the page to be returned.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="The number of objects per page to be returned.")] = None,
        strict_pagination: Annotated[Optional[StrictBool], Field(description="Toggles strict pagination. Defaults to `false` (disabled)    - If enabled, requesting an out of bounds page will throw a 400.    - If disabled, requesting an out of bounds page will return a 200 and an empty page.")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[V2PackagesLabresultsGet200Response]:
        """List of package lab result objects for a single package


        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param package_id: ID of the target package (required)
        :type package_id: float
        :param page: The index of the page to be returned.
        :type page: int
        :param page_size: The number of objects per page to be returned.
        :type page_size: int
        :param strict_pagination: Toggles strict pagination. Defaults to `false` (disabled)    - If enabled, requesting an out of bounds page will throw a 400.    - If disabled, requesting an out of bounds page will return a 200 and an empty page.
        :type strict_pagination: bool
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v2_packages_labresults_get_serialize(
            license_number=license_number,
            package_id=package_id,
            page=page,
            page_size=page_size,
            strict_pagination=strict_pagination,
            sort=sort,
            filter_logic=filter_logic,
            filter=filter,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PackagesLabresultsGet200Response",
            '404': None,
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def v2_packages_labresults_get_without_preload_content(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        package_id: Annotated[Union[StrictFloat, StrictInt], Field(description="ID of the target package")],
        page: Annotated[Optional[StrictInt], Field(description="The index of the page to be returned.")] = None,
        page_size: Annotated[Optional[StrictInt], Field(description="The number of objects per page to be returned.")] = None,
        strict_pagination: Annotated[Optional[StrictBool], Field(description="Toggles strict pagination. Defaults to `false` (disabled)    - If enabled, requesting an out of bounds page will throw a 400.    - If disabled, requesting an out of bounds page will return a 200 and an empty page.")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """List of package lab result objects for a single package


        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param package_id: ID of the target package (required)
        :type package_id: float
        :param page: The index of the page to be returned.
        :type page: int
        :param page_size: The number of objects per page to be returned.
        :type page_size: int
        :param strict_pagination: Toggles strict pagination. Defaults to `false` (disabled)    - If enabled, requesting an out of bounds page will throw a 400.    - If disabled, requesting an out of bounds page will return a 200 and an empty page.
        :type strict_pagination: bool
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._v2_packages_labresults_get_serialize(
            license_number=license_number,
            package_id=package_id,
            page=page,
            page_size=page_size,
            strict_pagination=strict_pagination,
            sort=sort,
            filter_logic=filter_logic,
            filter=filter,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PackagesLabresultsGet200Response",
            '404': None,
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v2_packages_labresults_get_serialize(
        self,
        license_number,
        package_id,
        page,
        page_size,
        strict_pagination,
        sort,
        filter_logic,
        filter,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
            'filter': 'multi',
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if license_number is not None:
            
            _query_params.append(('licenseNumber', license_number))
            
        if package_id is not None:
            
            _query_params.append(('packageId', package_id))
            
        if page is not None:
            
            _query_params.append(('page', page))
            
        if page_size is not None:
            
            _query_params.append(('pageSize', page_size))
            
        if strict_pagination is not None:
            
            _query_params.append(('strictPagination', strict_pagination))
            
        if sort is not None:
            
            _query_params.append(('sort', sort))
            
        if filter_logic is not None:
            
            _query_params.append(('filterLogic', filter_logic))
            
        if filter is not None:
            
            _query_params.append(('filter', filter))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'BearerAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v2/packages/labresults',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )


