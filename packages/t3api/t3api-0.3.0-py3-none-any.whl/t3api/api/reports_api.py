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

from pydantic import Field, StrictStr, field_validator
from typing import List, Optional
from typing_extensions import Annotated
from t3api.models.v2_auth_secretkey_post200_response import V2AuthSecretkeyPost200Response
from t3api.models.v2_auth_secretkey_post_request import V2AuthSecretkeyPostRequest
from t3api.models.v2_harvests_active_report_get200_response import V2HarvestsActiveReportGet200Response
from t3api.models.v2_items_report_get200_response import V2ItemsReportGet200Response
from t3api.models.v2_packages_active_report_get200_response import V2PackagesActiveReportGet200Response
from t3api.models.v2_packages_transferred_report_get200_response import V2PackagesTransferredReportGet200Response
from t3api.models.v2_plantbatches_active_report_get200_response import V2PlantbatchesActiveReportGet200Response
from t3api.models.v2_plants_vegetative_report_get200_response import V2PlantsVegetativeReportGet200Response
from t3api.models.v2_sales_active_report_get200_response import V2SalesActiveReportGet200Response
from t3api.models.v2_strains_report_get200_response import V2StrainsReportGet200Response
from t3api.models.v2_transfers_incoming_manifest_report_get200_response import V2TransfersIncomingManifestReportGet200Response
from t3api.models.v2_transfers_outgoing_manifest_report_get200_response import V2TransfersOutgoingManifestReportGet200Response

from t3api.api_client import ApiClient, RequestSerialized
from t3api.api_response import ApiResponse
from t3api.rest import RESTResponseType


class ReportsApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client


    @validate_call
    def v2_auth_secretkey_post(
        self,
        v2_auth_secretkey_post_request: Annotated[V2AuthSecretkeyPostRequest, Field(description="JSON object containing your Metrc secret key details  Note: The `otpSeed` field is only needed if you are authenticating in Michigan. Otherwise, omit this property. ")],
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
    ) -> V2AuthSecretkeyPost200Response:
        """Generate a secret key that can be used for special T3 routes that support secrey key authentication.

        **Note: generating a new secret key will invalidate all previously generated keys**   The T3 API includes a page for generating secret keys [here](/v2/pages/secret-key) 

        :param v2_auth_secretkey_post_request: JSON object containing your Metrc secret key details  Note: The `otpSeed` field is only needed if you are authenticating in Michigan. Otherwise, omit this property.  (required)
        :type v2_auth_secretkey_post_request: V2AuthSecretkeyPostRequest
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

        _param = self._v2_auth_secretkey_post_serialize(
            v2_auth_secretkey_post_request=v2_auth_secretkey_post_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2AuthSecretkeyPost200Response",
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
    def v2_auth_secretkey_post_with_http_info(
        self,
        v2_auth_secretkey_post_request: Annotated[V2AuthSecretkeyPostRequest, Field(description="JSON object containing your Metrc secret key details  Note: The `otpSeed` field is only needed if you are authenticating in Michigan. Otherwise, omit this property. ")],
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
    ) -> ApiResponse[V2AuthSecretkeyPost200Response]:
        """Generate a secret key that can be used for special T3 routes that support secrey key authentication.

        **Note: generating a new secret key will invalidate all previously generated keys**   The T3 API includes a page for generating secret keys [here](/v2/pages/secret-key) 

        :param v2_auth_secretkey_post_request: JSON object containing your Metrc secret key details  Note: The `otpSeed` field is only needed if you are authenticating in Michigan. Otherwise, omit this property.  (required)
        :type v2_auth_secretkey_post_request: V2AuthSecretkeyPostRequest
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

        _param = self._v2_auth_secretkey_post_serialize(
            v2_auth_secretkey_post_request=v2_auth_secretkey_post_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2AuthSecretkeyPost200Response",
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
    def v2_auth_secretkey_post_without_preload_content(
        self,
        v2_auth_secretkey_post_request: Annotated[V2AuthSecretkeyPostRequest, Field(description="JSON object containing your Metrc secret key details  Note: The `otpSeed` field is only needed if you are authenticating in Michigan. Otherwise, omit this property. ")],
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
        """Generate a secret key that can be used for special T3 routes that support secrey key authentication.

        **Note: generating a new secret key will invalidate all previously generated keys**   The T3 API includes a page for generating secret keys [here](/v2/pages/secret-key) 

        :param v2_auth_secretkey_post_request: JSON object containing your Metrc secret key details  Note: The `otpSeed` field is only needed if you are authenticating in Michigan. Otherwise, omit this property.  (required)
        :type v2_auth_secretkey_post_request: V2AuthSecretkeyPostRequest
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

        _param = self._v2_auth_secretkey_post_serialize(
            v2_auth_secretkey_post_request=v2_auth_secretkey_post_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2AuthSecretkeyPost200Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v2_auth_secretkey_post_serialize(
        self,
        v2_auth_secretkey_post_request,
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
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if v2_auth_secretkey_post_request is not None:
            _body_params = v2_auth_secretkey_post_request


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/v2/auth/secretkey',
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
    def v2_harvests_active_report_get(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which plant fields should appear in the report data.")] = None,
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
    ) -> V2HarvestsActiveReportGet200Response:
        """Generate a report of all active harvests

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which plant fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_harvests_active_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2HarvestsActiveReportGet200Response",
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
    def v2_harvests_active_report_get_with_http_info(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which plant fields should appear in the report data.")] = None,
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
    ) -> ApiResponse[V2HarvestsActiveReportGet200Response]:
        """Generate a report of all active harvests

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which plant fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_harvests_active_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2HarvestsActiveReportGet200Response",
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
    def v2_harvests_active_report_get_without_preload_content(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which plant fields should appear in the report data.")] = None,
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
        """Generate a report of all active harvests

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which plant fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_harvests_active_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2HarvestsActiveReportGet200Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v2_harvests_active_report_get_serialize(
        self,
        license_number,
        secret_key,
        filter_logic,
        content_type,
        prepend_csv_metadata,
        sort,
        filter,
        fieldnames,
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
            
        if secret_key is not None:
            
            _query_params.append(('secretKey', secret_key))
            
        if filter_logic is not None:
            
            _query_params.append(('filterLogic', filter_logic))
            
        if content_type is not None:
            
            _query_params.append(('contentType', content_type))
            
        if prepend_csv_metadata is not None:
            
            _query_params.append(('prependCsvMetadata', prepend_csv_metadata))
            
        if sort is not None:
            
            _query_params.append(('sort', sort))
            
        if filter is not None:
            
            _query_params.append(('filter', filter))
            
        if fieldnames is not None:
            
            _query_params.append(('fieldnames', fieldnames))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json', 
                    'text/csv'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'BearerAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v2/harvests/active/report',
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
    def v2_harvests_inactive_report_get(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which plant fields should appear in the report data.")] = None,
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
    ) -> V2HarvestsActiveReportGet200Response:
        """Generate a report of all active harvests

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which plant fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_harvests_inactive_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2HarvestsActiveReportGet200Response",
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
    def v2_harvests_inactive_report_get_with_http_info(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which plant fields should appear in the report data.")] = None,
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
    ) -> ApiResponse[V2HarvestsActiveReportGet200Response]:
        """Generate a report of all active harvests

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which plant fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_harvests_inactive_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2HarvestsActiveReportGet200Response",
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
    def v2_harvests_inactive_report_get_without_preload_content(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which plant fields should appear in the report data.")] = None,
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
        """Generate a report of all active harvests

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which plant fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_harvests_inactive_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2HarvestsActiveReportGet200Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v2_harvests_inactive_report_get_serialize(
        self,
        license_number,
        secret_key,
        filter_logic,
        content_type,
        prepend_csv_metadata,
        sort,
        filter,
        fieldnames,
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
            
        if secret_key is not None:
            
            _query_params.append(('secretKey', secret_key))
            
        if filter_logic is not None:
            
            _query_params.append(('filterLogic', filter_logic))
            
        if content_type is not None:
            
            _query_params.append(('contentType', content_type))
            
        if prepend_csv_metadata is not None:
            
            _query_params.append(('prependCsvMetadata', prepend_csv_metadata))
            
        if sort is not None:
            
            _query_params.append(('sort', sort))
            
        if filter is not None:
            
            _query_params.append(('filter', filter))
            
        if fieldnames is not None:
            
            _query_params.append(('fieldnames', fieldnames))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json', 
                    'text/csv'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'BearerAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v2/harvests/inactive/report',
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
    def v2_items_report_get(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which item fields should appear in the report data.")] = None,
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
    ) -> V2ItemsReportGet200Response:
        """Generate a report of all active items

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which item fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_items_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2ItemsReportGet200Response",
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
    def v2_items_report_get_with_http_info(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which item fields should appear in the report data.")] = None,
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
    ) -> ApiResponse[V2ItemsReportGet200Response]:
        """Generate a report of all active items

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which item fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_items_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2ItemsReportGet200Response",
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
    def v2_items_report_get_without_preload_content(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which item fields should appear in the report data.")] = None,
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
        """Generate a report of all active items

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which item fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_items_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2ItemsReportGet200Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v2_items_report_get_serialize(
        self,
        license_number,
        secret_key,
        filter_logic,
        content_type,
        prepend_csv_metadata,
        sort,
        filter,
        fieldnames,
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
            
        if secret_key is not None:
            
            _query_params.append(('secretKey', secret_key))
            
        if filter_logic is not None:
            
            _query_params.append(('filterLogic', filter_logic))
            
        if content_type is not None:
            
            _query_params.append(('contentType', content_type))
            
        if prepend_csv_metadata is not None:
            
            _query_params.append(('prependCsvMetadata', prepend_csv_metadata))
            
        if sort is not None:
            
            _query_params.append(('sort', sort))
            
        if filter is not None:
            
            _query_params.append(('filter', filter))
            
        if fieldnames is not None:
            
            _query_params.append(('fieldnames', fieldnames))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json', 
                    'text/csv'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'BearerAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v2/items/report',
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
    def v2_packages_active_report_get(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which package fields should appear in the report data.")] = None,
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
    ) -> V2PackagesActiveReportGet200Response:
        """Generate a report of all active packages

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which package fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_packages_active_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PackagesActiveReportGet200Response",
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
    def v2_packages_active_report_get_with_http_info(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which package fields should appear in the report data.")] = None,
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
    ) -> ApiResponse[V2PackagesActiveReportGet200Response]:
        """Generate a report of all active packages

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which package fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_packages_active_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PackagesActiveReportGet200Response",
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
    def v2_packages_active_report_get_without_preload_content(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which package fields should appear in the report data.")] = None,
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
        """Generate a report of all active packages

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which package fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_packages_active_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PackagesActiveReportGet200Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v2_packages_active_report_get_serialize(
        self,
        license_number,
        secret_key,
        filter_logic,
        content_type,
        prepend_csv_metadata,
        sort,
        filter,
        fieldnames,
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
            
        if secret_key is not None:
            
            _query_params.append(('secretKey', secret_key))
            
        if filter_logic is not None:
            
            _query_params.append(('filterLogic', filter_logic))
            
        if content_type is not None:
            
            _query_params.append(('contentType', content_type))
            
        if prepend_csv_metadata is not None:
            
            _query_params.append(('prependCsvMetadata', prepend_csv_metadata))
            
        if sort is not None:
            
            _query_params.append(('sort', sort))
            
        if filter is not None:
            
            _query_params.append(('filter', filter))
            
        if fieldnames is not None:
            
            _query_params.append(('fieldnames', fieldnames))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json', 
                    'text/csv'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'BearerAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v2/packages/active/report',
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
    def v2_packages_intransit_report_get(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which package fields should appear in the report data.")] = None,
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
    ) -> V2PackagesActiveReportGet200Response:
        """Generate a report of all in-transit packages

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param fieldnames: Defines which package fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_packages_intransit_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            sort=sort,
            filter_logic=filter_logic,
            filter=filter,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PackagesActiveReportGet200Response",
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
    def v2_packages_intransit_report_get_with_http_info(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which package fields should appear in the report data.")] = None,
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
    ) -> ApiResponse[V2PackagesActiveReportGet200Response]:
        """Generate a report of all in-transit packages

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param fieldnames: Defines which package fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_packages_intransit_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            sort=sort,
            filter_logic=filter_logic,
            filter=filter,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PackagesActiveReportGet200Response",
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
    def v2_packages_intransit_report_get_without_preload_content(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which package fields should appear in the report data.")] = None,
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
        """Generate a report of all in-transit packages

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param fieldnames: Defines which package fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_packages_intransit_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            sort=sort,
            filter_logic=filter_logic,
            filter=filter,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PackagesActiveReportGet200Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v2_packages_intransit_report_get_serialize(
        self,
        license_number,
        secret_key,
        sort,
        filter_logic,
        filter,
        content_type,
        prepend_csv_metadata,
        fieldnames,
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
            
        if secret_key is not None:
            
            _query_params.append(('secretKey', secret_key))
            
        if sort is not None:
            
            _query_params.append(('sort', sort))
            
        if filter_logic is not None:
            
            _query_params.append(('filterLogic', filter_logic))
            
        if filter is not None:
            
            _query_params.append(('filter', filter))
            
        if content_type is not None:
            
            _query_params.append(('contentType', content_type))
            
        if prepend_csv_metadata is not None:
            
            _query_params.append(('prependCsvMetadata', prepend_csv_metadata))
            
        if fieldnames is not None:
            
            _query_params.append(('fieldnames', fieldnames))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json', 
                    'text/csv'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'BearerAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v2/packages/intransit/report',
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
    def v2_packages_transferred_report_get(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which package fields should appear in the report data.")] = None,
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
    ) -> V2PackagesTransferredReportGet200Response:
        """Generate a report of all transferred packages

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param fieldnames: Defines which package fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_packages_transferred_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            sort=sort,
            filter_logic=filter_logic,
            filter=filter,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PackagesTransferredReportGet200Response",
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
    def v2_packages_transferred_report_get_with_http_info(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which package fields should appear in the report data.")] = None,
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
    ) -> ApiResponse[V2PackagesTransferredReportGet200Response]:
        """Generate a report of all transferred packages

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param fieldnames: Defines which package fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_packages_transferred_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            sort=sort,
            filter_logic=filter_logic,
            filter=filter,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PackagesTransferredReportGet200Response",
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
    def v2_packages_transferred_report_get_without_preload_content(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which package fields should appear in the report data.")] = None,
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
        """Generate a report of all transferred packages

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param fieldnames: Defines which package fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_packages_transferred_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            sort=sort,
            filter_logic=filter_logic,
            filter=filter,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PackagesTransferredReportGet200Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v2_packages_transferred_report_get_serialize(
        self,
        license_number,
        secret_key,
        sort,
        filter_logic,
        filter,
        content_type,
        prepend_csv_metadata,
        fieldnames,
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
            
        if secret_key is not None:
            
            _query_params.append(('secretKey', secret_key))
            
        if sort is not None:
            
            _query_params.append(('sort', sort))
            
        if filter_logic is not None:
            
            _query_params.append(('filterLogic', filter_logic))
            
        if filter is not None:
            
            _query_params.append(('filter', filter))
            
        if content_type is not None:
            
            _query_params.append(('contentType', content_type))
            
        if prepend_csv_metadata is not None:
            
            _query_params.append(('prependCsvMetadata', prepend_csv_metadata))
            
        if fieldnames is not None:
            
            _query_params.append(('fieldnames', fieldnames))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json', 
                    'text/csv'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'BearerAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v2/packages/transferred/report',
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
    def v2_plantbatches_active_report_get(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which plant fields should appear in the report data.")] = None,
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
    ) -> V2PlantbatchesActiveReportGet200Response:
        """Generate a report of all active plant batches

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which plant fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_plantbatches_active_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PlantbatchesActiveReportGet200Response",
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
    def v2_plantbatches_active_report_get_with_http_info(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which plant fields should appear in the report data.")] = None,
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
    ) -> ApiResponse[V2PlantbatchesActiveReportGet200Response]:
        """Generate a report of all active plant batches

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which plant fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_plantbatches_active_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PlantbatchesActiveReportGet200Response",
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
    def v2_plantbatches_active_report_get_without_preload_content(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which plant fields should appear in the report data.")] = None,
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
        """Generate a report of all active plant batches

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which plant fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_plantbatches_active_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PlantbatchesActiveReportGet200Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v2_plantbatches_active_report_get_serialize(
        self,
        license_number,
        secret_key,
        filter_logic,
        content_type,
        prepend_csv_metadata,
        sort,
        filter,
        fieldnames,
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
            
        if secret_key is not None:
            
            _query_params.append(('secretKey', secret_key))
            
        if filter_logic is not None:
            
            _query_params.append(('filterLogic', filter_logic))
            
        if content_type is not None:
            
            _query_params.append(('contentType', content_type))
            
        if prepend_csv_metadata is not None:
            
            _query_params.append(('prependCsvMetadata', prepend_csv_metadata))
            
        if sort is not None:
            
            _query_params.append(('sort', sort))
            
        if filter is not None:
            
            _query_params.append(('filter', filter))
            
        if fieldnames is not None:
            
            _query_params.append(('fieldnames', fieldnames))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json', 
                    'text/csv'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'BearerAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v2/plantbatches/active/report',
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
    def v2_plants_flowering_report_get(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which plant fields should appear in the report data.")] = None,
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
    ) -> V2PlantsVegetativeReportGet200Response:
        """Generate a report of all flowering plants

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which plant fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_plants_flowering_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PlantsVegetativeReportGet200Response",
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
    def v2_plants_flowering_report_get_with_http_info(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which plant fields should appear in the report data.")] = None,
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
    ) -> ApiResponse[V2PlantsVegetativeReportGet200Response]:
        """Generate a report of all flowering plants

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which plant fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_plants_flowering_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PlantsVegetativeReportGet200Response",
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
    def v2_plants_flowering_report_get_without_preload_content(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which plant fields should appear in the report data.")] = None,
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
        """Generate a report of all flowering plants

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which plant fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_plants_flowering_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PlantsVegetativeReportGet200Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v2_plants_flowering_report_get_serialize(
        self,
        license_number,
        secret_key,
        filter_logic,
        content_type,
        prepend_csv_metadata,
        sort,
        filter,
        fieldnames,
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
            
        if secret_key is not None:
            
            _query_params.append(('secretKey', secret_key))
            
        if filter_logic is not None:
            
            _query_params.append(('filterLogic', filter_logic))
            
        if content_type is not None:
            
            _query_params.append(('contentType', content_type))
            
        if prepend_csv_metadata is not None:
            
            _query_params.append(('prependCsvMetadata', prepend_csv_metadata))
            
        if sort is not None:
            
            _query_params.append(('sort', sort))
            
        if filter is not None:
            
            _query_params.append(('filter', filter))
            
        if fieldnames is not None:
            
            _query_params.append(('fieldnames', fieldnames))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json', 
                    'text/csv'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'BearerAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v2/plants/flowering/report',
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
    def v2_plants_vegetative_report_get(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which plant fields should appear in the report data.")] = None,
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
    ) -> V2PlantsVegetativeReportGet200Response:
        """Generate a report of all vegetative plants

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which plant fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_plants_vegetative_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PlantsVegetativeReportGet200Response",
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
    def v2_plants_vegetative_report_get_with_http_info(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which plant fields should appear in the report data.")] = None,
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
    ) -> ApiResponse[V2PlantsVegetativeReportGet200Response]:
        """Generate a report of all vegetative plants

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which plant fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_plants_vegetative_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PlantsVegetativeReportGet200Response",
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
    def v2_plants_vegetative_report_get_without_preload_content(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which plant fields should appear in the report data.")] = None,
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
        """Generate a report of all vegetative plants

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which plant fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_plants_vegetative_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2PlantsVegetativeReportGet200Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v2_plants_vegetative_report_get_serialize(
        self,
        license_number,
        secret_key,
        filter_logic,
        content_type,
        prepend_csv_metadata,
        sort,
        filter,
        fieldnames,
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
            
        if secret_key is not None:
            
            _query_params.append(('secretKey', secret_key))
            
        if filter_logic is not None:
            
            _query_params.append(('filterLogic', filter_logic))
            
        if content_type is not None:
            
            _query_params.append(('contentType', content_type))
            
        if prepend_csv_metadata is not None:
            
            _query_params.append(('prependCsvMetadata', prepend_csv_metadata))
            
        if sort is not None:
            
            _query_params.append(('sort', sort))
            
        if filter is not None:
            
            _query_params.append(('filter', filter))
            
        if fieldnames is not None:
            
            _query_params.append(('fieldnames', fieldnames))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json', 
                    'text/csv'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'BearerAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v2/plants/vegetative/report',
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
    def v2_sales_active_report_get(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which sales receipt fields should appear in the report data.")] = None,
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
    ) -> V2SalesActiveReportGet200Response:
        """Generate a report of all active sales

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which sales receipt fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_sales_active_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2SalesActiveReportGet200Response",
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
    def v2_sales_active_report_get_with_http_info(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which sales receipt fields should appear in the report data.")] = None,
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
    ) -> ApiResponse[V2SalesActiveReportGet200Response]:
        """Generate a report of all active sales

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which sales receipt fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_sales_active_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2SalesActiveReportGet200Response",
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
    def v2_sales_active_report_get_without_preload_content(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which sales receipt fields should appear in the report data.")] = None,
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
        """Generate a report of all active sales

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which sales receipt fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_sales_active_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2SalesActiveReportGet200Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v2_sales_active_report_get_serialize(
        self,
        license_number,
        secret_key,
        filter_logic,
        content_type,
        prepend_csv_metadata,
        sort,
        filter,
        fieldnames,
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
            
        if secret_key is not None:
            
            _query_params.append(('secretKey', secret_key))
            
        if filter_logic is not None:
            
            _query_params.append(('filterLogic', filter_logic))
            
        if content_type is not None:
            
            _query_params.append(('contentType', content_type))
            
        if prepend_csv_metadata is not None:
            
            _query_params.append(('prependCsvMetadata', prepend_csv_metadata))
            
        if sort is not None:
            
            _query_params.append(('sort', sort))
            
        if filter is not None:
            
            _query_params.append(('filter', filter))
            
        if fieldnames is not None:
            
            _query_params.append(('fieldnames', fieldnames))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json', 
                    'text/csv'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'BearerAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v2/sales/active/report',
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
    def v2_strains_report_get(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which strain fields should appear in the report data.")] = None,
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
    ) -> V2StrainsReportGet200Response:
        """Generate a report of all active strains

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which strain fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_strains_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2StrainsReportGet200Response",
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
    def v2_strains_report_get_with_http_info(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which strain fields should appear in the report data.")] = None,
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
    ) -> ApiResponse[V2StrainsReportGet200Response]:
        """Generate a report of all active strains

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which strain fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_strains_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2StrainsReportGet200Response",
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
    def v2_strains_report_get_without_preload_content(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which strain fields should appear in the report data.")] = None,
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
        """Generate a report of all active strains

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which strain fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_strains_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2StrainsReportGet200Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v2_strains_report_get_serialize(
        self,
        license_number,
        secret_key,
        filter_logic,
        content_type,
        prepend_csv_metadata,
        sort,
        filter,
        fieldnames,
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
            
        if secret_key is not None:
            
            _query_params.append(('secretKey', secret_key))
            
        if filter_logic is not None:
            
            _query_params.append(('filterLogic', filter_logic))
            
        if content_type is not None:
            
            _query_params.append(('contentType', content_type))
            
        if prepend_csv_metadata is not None:
            
            _query_params.append(('prependCsvMetadata', prepend_csv_metadata))
            
        if sort is not None:
            
            _query_params.append(('sort', sort))
            
        if filter is not None:
            
            _query_params.append(('filter', filter))
            
        if fieldnames is not None:
            
            _query_params.append(('fieldnames', fieldnames))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json', 
                    'text/csv'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'BearerAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v2/strains/report',
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
    def v2_transfers_incoming_manifest_report_get(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which transfer manifest fields should appear in the report data.")] = None,
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
    ) -> V2TransfersIncomingManifestReportGet200Response:
        """Generate a report of all incoming transfer manifests

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which transfer manifest fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_transfers_incoming_manifest_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2TransfersIncomingManifestReportGet200Response",
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
    def v2_transfers_incoming_manifest_report_get_with_http_info(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which transfer manifest fields should appear in the report data.")] = None,
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
    ) -> ApiResponse[V2TransfersIncomingManifestReportGet200Response]:
        """Generate a report of all incoming transfer manifests

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which transfer manifest fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_transfers_incoming_manifest_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2TransfersIncomingManifestReportGet200Response",
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
    def v2_transfers_incoming_manifest_report_get_without_preload_content(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which transfer manifest fields should appear in the report data.")] = None,
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
        """Generate a report of all incoming transfer manifests

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which transfer manifest fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_transfers_incoming_manifest_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2TransfersIncomingManifestReportGet200Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v2_transfers_incoming_manifest_report_get_serialize(
        self,
        license_number,
        secret_key,
        filter_logic,
        content_type,
        prepend_csv_metadata,
        sort,
        filter,
        fieldnames,
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
            
        if secret_key is not None:
            
            _query_params.append(('secretKey', secret_key))
            
        if filter_logic is not None:
            
            _query_params.append(('filterLogic', filter_logic))
            
        if content_type is not None:
            
            _query_params.append(('contentType', content_type))
            
        if prepend_csv_metadata is not None:
            
            _query_params.append(('prependCsvMetadata', prepend_csv_metadata))
            
        if sort is not None:
            
            _query_params.append(('sort', sort))
            
        if filter is not None:
            
            _query_params.append(('filter', filter))
            
        if fieldnames is not None:
            
            _query_params.append(('fieldnames', fieldnames))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json', 
                    'text/csv'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'BearerAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v2/transfers/incoming/manifest/report',
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
    def v2_transfers_outgoing_manifest_report_get(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which transfer manifest fields should appear in the report data.")] = None,
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
    ) -> V2TransfersOutgoingManifestReportGet200Response:
        """Generate a report of all outgoing transfer manifests

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which transfer manifest fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_transfers_outgoing_manifest_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2TransfersOutgoingManifestReportGet200Response",
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
    def v2_transfers_outgoing_manifest_report_get_with_http_info(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which transfer manifest fields should appear in the report data.")] = None,
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
    ) -> ApiResponse[V2TransfersOutgoingManifestReportGet200Response]:
        """Generate a report of all outgoing transfer manifests

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which transfer manifest fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_transfers_outgoing_manifest_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2TransfersOutgoingManifestReportGet200Response",
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
    def v2_transfers_outgoing_manifest_report_get_without_preload_content(
        self,
        license_number: Annotated[StrictStr, Field(description="The unique identifier for the license associated with this request.")],
        secret_key: Annotated[Optional[StrictStr], Field(description="Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). ")] = None,
        filter_logic: Annotated[Optional[StrictStr], Field(description="Describes how the filters, if any, should be applied")] = None,
        content_type: Annotated[Optional[StrictStr], Field(description="Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* ")] = None,
        prepend_csv_metadata: Annotated[Optional[StrictStr], Field(description="Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. ")] = None,
        sort: Annotated[Optional[StrictStr], Field(description="Defines the collection sort order.")] = None,
        filter: Annotated[Optional[List[StrictStr]], Field(description="One or more collection filters.")] = None,
        fieldnames: Annotated[Optional[StrictStr], Field(description="Defines which transfer manifest fields should appear in the report data.")] = None,
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
        """Generate a report of all outgoing transfer manifests

        **Note: this endpoint supports secret key authentication.** 

        :param license_number: The unique identifier for the license associated with this request. (required)
        :type license_number: str
        :param secret_key: Your secret key, if you wish to authenticate via query params. Secret keys can be manually generated [here](/v2/pages/secret-key). 
        :type secret_key: str
        :param filter_logic: Describes how the filters, if any, should be applied
        :type filter_logic: str
        :param content_type: Specifies how the report should be formatted. Can be returned as json or csv. *This can also be defined in the Content-Type header* 
        :type content_type: str
        :param prepend_csv_metadata: Controls if the CSV header metadata should be included in the output. When set to false, only the column headers and data will be returned. 
        :type prepend_csv_metadata: str
        :param sort: Defines the collection sort order.
        :type sort: str
        :param filter: One or more collection filters.
        :type filter: List[str]
        :param fieldnames: Defines which transfer manifest fields should appear in the report data.
        :type fieldnames: str
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

        _param = self._v2_transfers_outgoing_manifest_report_get_serialize(
            license_number=license_number,
            secret_key=secret_key,
            filter_logic=filter_logic,
            content_type=content_type,
            prepend_csv_metadata=prepend_csv_metadata,
            sort=sort,
            filter=filter,
            fieldnames=fieldnames,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "V2TransfersOutgoingManifestReportGet200Response",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _v2_transfers_outgoing_manifest_report_get_serialize(
        self,
        license_number,
        secret_key,
        filter_logic,
        content_type,
        prepend_csv_metadata,
        sort,
        filter,
        fieldnames,
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
            
        if secret_key is not None:
            
            _query_params.append(('secretKey', secret_key))
            
        if filter_logic is not None:
            
            _query_params.append(('filterLogic', filter_logic))
            
        if content_type is not None:
            
            _query_params.append(('contentType', content_type))
            
        if prepend_csv_metadata is not None:
            
            _query_params.append(('prependCsvMetadata', prepend_csv_metadata))
            
        if sort is not None:
            
            _query_params.append(('sort', sort))
            
        if filter is not None:
            
            _query_params.append(('filter', filter))
            
        if fieldnames is not None:
            
            _query_params.append(('fieldnames', fieldnames))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json', 
                    'text/csv'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'BearerAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v2/transfers/outgoing/manifest/report',
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


