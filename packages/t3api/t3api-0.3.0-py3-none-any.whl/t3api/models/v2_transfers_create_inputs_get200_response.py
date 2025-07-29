# coding: utf-8

"""
    T3 API

    ## WHAT IS THIS?  This API is part of the [Track & Trace Tools](https://trackandtrace.tools) platform. The API allows you to programmatically access all your Metrc data that is available on metrc.com  It is not related to the Metrc 3rd party API, does not use Metrc API keys, and is not affiliated with Metrc.  If you're looking for where to get started, check out the [T3 Wiki API Getting Started guide](https://github.com/classvsoftware/t3-wiki/wiki/T3-API-:-Getting-Started).  The T3 API is subject to the [Track & Trace Tools Terms of Use](https://www.trackandtrace.tools/terms-of-use).   ## FREE API ACCESS (LIMITED)  The T3 API features a limited number of free endpoints available to anyone with a Metrc login.  These can be found in the [Free](#/Free) section.  ## FULL API ACCESS  There are two ways to get premium access to the T3 API:  - **Subscribe to [T3+](https://trackandtrace.tools/plus)**  *OR*  - **Use a provided T3 API key (consulting clients only. [Reach out](mailto:matt@trackandtrace.tools) for more information.)**  ## AUTHENTICATION  The T3 API uses JSON Web Tokens (JWT) for request authentication. To obtain a JWT, use one of the following:  - **metrc.com login credentials:**   - **hostname**: (The website you use to login to metrc: `ca.metrc.com`, `or.metrc.com`, etc.)   - **username**: Your Metrc username   - **password**: Your Metrc password   - **otp**: A one-time password used for 2-factor authentication (Only applies to Michigan users)  *OR*  - **T3 API key**  Refer to the **Authentication** endpoints below for more information.  ## SECRET KEYS  Some endpoints support the use of secret key authentication. This allows you to use simple URLs to access your Metrc data.  ### Usage  Pass the `secretKey` returned from the request in the query string:  `?secretKey=<yourSecretKeyGoesHere>`  ### Generating Secret Keys  Refer to the [/v2/auth/secretkey](#/Authentication/post_v2_auth_secretkey) endpoint for information on generating secret keys.  [Secret Key Generation Tool](/v2/pages/secret-key)  [Sync Link Creation Tool](/v2/pages/sync-link)  ## SECURITY  The T3 API interacts with Metrc in a similar manner to the [Track & Trace Tools](https://chromewebstore.google.com/detail/track-trace-tools/dfljickgkbfaoiifheibjpejloipegcb) Chrome extension. The API login process is designed with a strong emphasis on security. Your Metrc login details are never stored, and the API backend employs robust encryption methods to protect your temporary Metrc session.  ### Key Security Measures:  - **Single-Use Login Credentials:**    - The T3 API uses your login credentials only once to authenticate with Metrc.   - After the Metrc login process is complete, your login credentials are immediately deleted from the system.   - You are required to enter your login credentials each time you access the T3 API, ensuring that your credentials are never stored.    - **Secure Temporary Session Storage:**    - The T3 API securely encrypts your logged-in Metrc session data. This data is only used when you make requests through the T3 API.   - The encrypted session data is automatically deleted after 24 hours, ensuring that your session information is not retained longer than necessary.  For any questions or concerns, please contact [matt@trackandtrace.tools](mailto:matt@trackandtrace.tools).  ## PRIVACY  The T3 API privacy model follows the same principles as the [Track & Trace Tools](https://chromewebstore.google.com/detail/track-trace-tools/dfljickgkbfaoiifheibjpejloipegcb) Chrome extension. The T3 API functions solely as a connector between you and Metrc, ensuring your privacy is protected.  - **No Data Collection:**    - The T3 API does not record, save, harvest, inspect, or analyze any of your data.   - All data interactions are ephemeral and occur in real-time, without permanent storage.  - **Secure and Private Access:**    - Your data is never shared with third parties. Unauthorized access to your login information or data is strictly prohibited.   - T3 employs industry-standard encryption protocols to safeguard all communications between the T3 API and Metrc.    - **User-Controlled Sessions:**    - Your Metrc login credentials and session are used exclusively by you. The T3 API will never initiate Metrc traffic without your explicit authorization.  - **Compliance and Best Practices:**   - T3's privacy practices are aligned with applicable data protection regulations, including GDPR and CCPA, ensuring that your data rights are respected.  The T3 API is subject to the [Track & Trace Tools Privacy Policy](https://trackandtrace.tools/privacy-policy). For any privacy-related inquiries, please contact [matt@trackandtrace.tools](mailto:matt@trackandtrace.tools).  ## PERMISSIONS  Each Metrc account has different permissions based on several factors:  - Permissions granted by your Metrc admin - Class of license (manufacturing, cultivation, etc) - US state the license operates in  Use the Permissions endpoints to determine which actions are available to you.  ## LICENSES  View a list of all licenses available to the current user:  `GET https://api.trackandtrace.tools/v2/licenses`  Only one license can be queried per request. Specify the target license with the required `licenseNumber` query parameter:  `GET https://api.trackandtrace.tools/v2/items?licenseNumber=LIC-00001`  ## RATE LIMITING  The API has a global default request rate limit of 600 requests/minute/user. Some routes have lower rate limits.  ## COLLECTIONS  All data is queried as collections. There are no individual object endpoints.  For example, you cannot find an individual object using an endpoint like `/plants/{plantId}`, individual objects must be queried by filtering the collection endpoint `/plants` for the exact `plantId`.   Collections are paginated, and can be filtered and sorted by individual object fields.  The JSON response object includes the following properties: - `data`: An array of objects, or any empty array - `page`: The requested page index - `pageSize`: The requested page size - `total`: The total number of items in this collection. Use this to determine how many pages are required to return the entire collection.  ### COLLECTION PAGINATION  Metrc data collections are queried as pages. Use the `page` and `pageSize` query parameters to indicate which page should be returned.  By default, `page=1` and `pageSize=100`.  Example: Return page 3 with a page size of 500:  `GET https://api.trackandtrace.tools/v2/items?licenseNumber=LIC-00001&page=3&pageSize=500`  ### COLLECTION SORTING  Metrc data collections can be sorted. Use the `sort` query parameter to indicate how the collection should be sorted.  Example: Sort items by `name` descending:  `GET https://api.trackandtrace.tools/v2/items?licenseNumber=LIC-00001&sort=name:desc`  ### COLLECTION FILTERING  Metrc data collections can be filtered. Use one or more `filter` query parameters to indicate how filters should be applied.  Example: Filter items that contain \"flower\" in the `name` field:  `GET https://api.trackandtrace.tools/v2/items?licenseNumber=LIC-00001&filter:name__contains=flower`  Multiple filters can be applied, and you can specify the logical operator (defaulting to \"and\"):  Example: Filter items that contain \"flower\" in the `name` field OR \"kush\" in the `name` field:  `GET https://api.trackandtrace.tools/v2/items?licenseNumber=LIC-00001&filter=name__contains:flower&filter=name__contains:kush&filterLogic=or`  #### FILTERING STRINGS  String fields support the following filter operators:  - `contains` - `doesnotcontain` - `eq` - `neq` - `startswith` - `endswith`  Example `?filter=name__contains:flower`  **Note: all string filters are case-insensitive**  #### FILTERING DATETIMES  Datetime fields support the following filter operators:  - `lt` - `lte` - `eq` - `neq` - `gt` - `gte`  Example: `?filter=harvestedDate__gte:2024-07-17T20:26:07.117Z`  **Note: all datetime filters use ISO8601 datetimes**  #### FILTERING BOOLEANS  Boolean fields support the following filter operators:  - `eq`  Example: `?filter=finished__eq:true`  ### LOADING FULL COLLECTIONS `pageSize` is limited to 500 in most cases, so you may need to load multiple pages if a license has a large number of packages.  Refer to [this example](https://github.com/classvsoftware/t3-api/blob/master/load_all_active_packages.py) for how to load a full collection in a python script.  ## USING THE API  The API can be used in any way you like, but writing simple scripts to accomplish common tasks is an excellent way to take advantage of it.  The full OpenAPI spec, which can be imported into Postman, can be found here: [/v2/spec/openapi.json](/v2/spec/openapi.json)  [**Lots** of example scripts that show how the use the T3 API can be found here](https://github.com/classvsoftware/t3-api)  ## CONTACT  - **Responsible Organization:** Class V LLC - **Responsible Developer:** Matt Frisbie - **Email:** [matt@trackandtrace.tools](mailto:matt@trackandtrace.tools) - **URL:** [https://trackandtrace.tools](https://trackandtrace.tools) - **Terms of Use:** [https://www.trackandtrace.tools/terms-of-use](https://www.trackandtrace.tools/terms-of-use) 

    The version of the OpenAPI document: v2
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from t3api.models.metrc_driver import MetrcDriver
from t3api.models.metrc_vehicle import MetrcVehicle
from t3api.models.unit_of_measure import UnitOfMeasure
from t3api.models.v2_transfers_create_inputs_get200_response_transfer_types_inner import V2TransfersCreateInputsGet200ResponseTransferTypesInner
from typing import Optional, Set
from typing_extensions import Self

class V2TransfersCreateInputsGet200Response(BaseModel):
    """
    V2TransfersCreateInputsGet200Response
    """ # noqa: E501
    adding: Optional[StrictBool] = Field(default=None, description="Indicates if the entity is being added.")
    days_wholesale_price_can_edit: Optional[StrictInt] = Field(default=None, description="Number of days the wholesale price can be edited.", alias="daysWholesalePriceCanEdit")
    default_phone_number_for_questions: Optional[StrictStr] = Field(default=None, description="Default phone number for questions.", alias="defaultPhoneNumberForQuestions")
    destination_facilities: Optional[List[Dict[str, Any]]] = Field(default=None, description="List of destination facilities.", alias="destinationFacilities")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional details.")
    drivers: Optional[List[MetrcDriver]] = Field(default=None, description="List of drivers associated with the entity.")
    edit_delivery_details_only: Optional[StrictBool] = Field(default=None, description="Indicates if only delivery details can be edited.", alias="editDeliveryDetailsOnly")
    edit_wholesale_price_only: Optional[StrictBool] = Field(default=None, description="Indicates if only the wholesale price can be edited.", alias="editWholesalePriceOnly")
    facilities: Optional[Dict[str, Any]] = Field(default=None, description="Details of the facilities.")
    is_outgoing_inactive: Optional[StrictBool] = Field(default=None, description="Indicates if the outgoing status is inactive.", alias="isOutgoingInactive")
    items: Optional[Dict[str, Any]] = Field(default=None, description="List of items.")
    packages: Optional[List[Dict[str, Any]]] = Field(default=None, description="List of packages.")
    selected_delivery_ids: Optional[List[StrictInt]] = Field(default=None, description="List of selected delivery IDs.", alias="selectedDeliveryIds")
    selected_transfer_ids: Optional[List[StrictInt]] = Field(default=None, description="List of selected transfer IDs.", alias="selectedTransferIds")
    selected_transfer_template_ids: Optional[Dict[str, Any]] = Field(default=None, description="List of selected transfer template IDs.", alias="selectedTransferTemplateIds")
    transfer_types: Optional[List[V2TransfersCreateInputsGet200ResponseTransferTypesInner]] = Field(default=None, description="List of transfer types.", alias="transferTypes")
    transporter_facilities: Optional[List[Dict[str, Any]]] = Field(default=None, description="List of transporter facilities.", alias="transporterFacilities")
    units_of_measure: Optional[List[UnitOfMeasure]] = Field(default=None, description="List of units of measure.", alias="unitsOfMeasure")
    vehicles: Optional[List[MetrcVehicle]] = Field(default=None, description="List of vehicles associated with the facility.")
    __properties: ClassVar[List[str]] = ["adding", "daysWholesalePriceCanEdit", "defaultPhoneNumberForQuestions", "destinationFacilities", "details", "drivers", "editDeliveryDetailsOnly", "editWholesalePriceOnly", "facilities", "isOutgoingInactive", "items", "packages", "selectedDeliveryIds", "selectedTransferIds", "selectedTransferTemplateIds", "transferTypes", "transporterFacilities", "unitsOfMeasure", "vehicles"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of V2TransfersCreateInputsGet200Response from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of each item in drivers (list)
        _items = []
        if self.drivers:
            for _item_drivers in self.drivers:
                if _item_drivers:
                    _items.append(_item_drivers.to_dict())
            _dict['drivers'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in transfer_types (list)
        _items = []
        if self.transfer_types:
            for _item_transfer_types in self.transfer_types:
                if _item_transfer_types:
                    _items.append(_item_transfer_types.to_dict())
            _dict['transferTypes'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in units_of_measure (list)
        _items = []
        if self.units_of_measure:
            for _item_units_of_measure in self.units_of_measure:
                if _item_units_of_measure:
                    _items.append(_item_units_of_measure.to_dict())
            _dict['unitsOfMeasure'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in vehicles (list)
        _items = []
        if self.vehicles:
            for _item_vehicles in self.vehicles:
                if _item_vehicles:
                    _items.append(_item_vehicles.to_dict())
            _dict['vehicles'] = _items
        # set to None if details (nullable) is None
        # and model_fields_set contains the field
        if self.details is None and "details" in self.model_fields_set:
            _dict['details'] = None

        # set to None if items (nullable) is None
        # and model_fields_set contains the field
        if self.items is None and "items" in self.model_fields_set:
            _dict['items'] = None

        # set to None if selected_transfer_template_ids (nullable) is None
        # and model_fields_set contains the field
        if self.selected_transfer_template_ids is None and "selected_transfer_template_ids" in self.model_fields_set:
            _dict['selectedTransferTemplateIds'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of V2TransfersCreateInputsGet200Response from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "adding": obj.get("adding"),
            "daysWholesalePriceCanEdit": obj.get("daysWholesalePriceCanEdit"),
            "defaultPhoneNumberForQuestions": obj.get("defaultPhoneNumberForQuestions"),
            "destinationFacilities": obj.get("destinationFacilities"),
            "details": obj.get("details"),
            "drivers": [MetrcDriver.from_dict(_item) for _item in obj["drivers"]] if obj.get("drivers") is not None else None,
            "editDeliveryDetailsOnly": obj.get("editDeliveryDetailsOnly"),
            "editWholesalePriceOnly": obj.get("editWholesalePriceOnly"),
            "facilities": obj.get("facilities"),
            "isOutgoingInactive": obj.get("isOutgoingInactive"),
            "items": obj.get("items"),
            "packages": obj.get("packages"),
            "selectedDeliveryIds": obj.get("selectedDeliveryIds"),
            "selectedTransferIds": obj.get("selectedTransferIds"),
            "selectedTransferTemplateIds": obj.get("selectedTransferTemplateIds"),
            "transferTypes": [V2TransfersCreateInputsGet200ResponseTransferTypesInner.from_dict(_item) for _item in obj["transferTypes"]] if obj.get("transferTypes") is not None else None,
            "transporterFacilities": obj.get("transporterFacilities"),
            "unitsOfMeasure": [UnitOfMeasure.from_dict(_item) for _item in obj["unitsOfMeasure"]] if obj.get("unitsOfMeasure") is not None else None,
            "vehicles": [MetrcVehicle.from_dict(_item) for _item in obj["vehicles"]] if obj.get("vehicles") is not None else None
        })
        return _obj


