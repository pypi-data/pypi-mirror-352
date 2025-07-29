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

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional, Union
from typing import Optional, Set
from typing_extensions import Self

class MetrcTransferredPackage(BaseModel):
    """
    MetrcTransferredPackage
    """ # noqa: E501
    id: StrictInt = Field(description="Unique identifier for the item")
    hostname: Optional[StrictStr] = Field(default=None, description="The hostname this object was retrieved from")
    data_model: Optional[StrictStr] = Field(default=None, description="Name of this object's data model", alias="dataModel")
    retrieved_at: Optional[datetime] = Field(default=None, description="Timestamp of when this object was pulled from Metrc", alias="retrievedAt")
    license_number: Optional[StrictStr] = Field(default=None, description="License number used to access this object", alias="licenseNumber")
    index: Optional[StrictStr] = Field(default=None, description="Describes the current state of this object at the time it was returned from the API. This cannot be used to sort or filter.")
    package_id: StrictInt = Field(description="Identifier for the package", alias="packageId")
    recipient_facility_license_number: StrictStr = Field(description="License number of the recipient facility", alias="recipientFacilityLicenseNumber")
    recipient_facility_name: StrictStr = Field(description="Name of the recipient facility", alias="recipientFacilityName")
    manifest_number: StrictStr = Field(description="Manifest number associated with the shipment", alias="manifestNumber")
    package_label: StrictStr = Field(description="Label of the package", alias="packageLabel")
    source_harvest_names: Optional[StrictStr] = Field(default=None, description="Names of the source harvests", alias="sourceHarvestNames")
    source_package_labels: Optional[StrictStr] = Field(default=None, description="Labels of the source packages", alias="sourcePackageLabels")
    product_name: StrictStr = Field(description="Name of the product", alias="productName")
    product_category_name: StrictStr = Field(description="Category name of the product", alias="productCategoryName")
    item_strain_name: StrictStr = Field(description="Strain name of the item", alias="itemStrainName")
    lab_testing_state_name: StrictStr = Field(description="Lab testing status of the item", alias="labTestingStateName")
    shipped_quantity: Union[StrictFloat, StrictInt] = Field(description="Quantity shipped", alias="shippedQuantity")
    shipped_unit_of_measure_abbreviation: StrictStr = Field(description="Unit of measure for the shipped quantity", alias="shippedUnitOfMeasureAbbreviation")
    gross_weight: Union[StrictFloat, StrictInt] = Field(description="Gross weight of the package", alias="grossWeight")
    gross_unit_of_weight_abbreviation: StrictStr = Field(description="Unit of measure for the gross weight", alias="grossUnitOfWeightAbbreviation")
    shipper_wholesale_price: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Wholesale price from the shipper", alias="shipperWholesalePrice")
    received_quantity: Union[StrictFloat, StrictInt] = Field(description="Quantity received", alias="receivedQuantity")
    received_unit_of_measure_abbreviation: StrictStr = Field(description="Unit of measure for the received quantity", alias="receivedUnitOfMeasureAbbreviation")
    receiver_wholesale_price: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Wholesale price to the receiver", alias="receiverWholesalePrice")
    shipment_package_state_name: StrictStr = Field(description="State of the shipment package", alias="shipmentPackageStateName")
    actual_departure_date_time: Optional[datetime] = Field(default=None, description="Actual departure date and time", alias="actualDepartureDateTime")
    received_date_time: datetime = Field(description="Date and time when the package was received", alias="receivedDateTime")
    processing_job_type_name: Optional[StrictStr] = Field(default=None, alias="processingJobTypeName")
    external_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="externalId")
    __properties: ClassVar[List[str]] = ["id", "hostname", "dataModel", "retrievedAt", "licenseNumber", "index", "packageId", "recipientFacilityLicenseNumber", "recipientFacilityName", "manifestNumber", "packageLabel", "sourceHarvestNames", "sourcePackageLabels", "productName", "productCategoryName", "itemStrainName", "labTestingStateName", "shippedQuantity", "shippedUnitOfMeasureAbbreviation", "grossWeight", "grossUnitOfWeightAbbreviation", "shipperWholesalePrice", "receivedQuantity", "receivedUnitOfMeasureAbbreviation", "receiverWholesalePrice", "shipmentPackageStateName", "actualDepartureDateTime", "receivedDateTime", "processingJobTypeName", "externalId"]

    @field_validator('index')
    def index_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['TRANSFERRED_PACKAGE']):
            raise ValueError("must be one of enum values ('TRANSFERRED_PACKAGE')")
        return value

    @field_validator('lab_testing_state_name')
    def lab_testing_state_name_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['TestPassed', 'TestFailed', 'Pending']):
            raise ValueError("must be one of enum values ('TestPassed', 'TestFailed', 'Pending')")
        return value

    @field_validator('shipment_package_state_name')
    def shipment_package_state_name_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['Accepted', 'Rejected', 'Pending']):
            raise ValueError("must be one of enum values ('Accepted', 'Rejected', 'Pending')")
        return value

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
        """Create an instance of MetrcTransferredPackage from a JSON string"""
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
        # set to None if source_harvest_names (nullable) is None
        # and model_fields_set contains the field
        if self.source_harvest_names is None and "source_harvest_names" in self.model_fields_set:
            _dict['sourceHarvestNames'] = None

        # set to None if source_package_labels (nullable) is None
        # and model_fields_set contains the field
        if self.source_package_labels is None and "source_package_labels" in self.model_fields_set:
            _dict['sourcePackageLabels'] = None

        # set to None if shipper_wholesale_price (nullable) is None
        # and model_fields_set contains the field
        if self.shipper_wholesale_price is None and "shipper_wholesale_price" in self.model_fields_set:
            _dict['shipperWholesalePrice'] = None

        # set to None if receiver_wholesale_price (nullable) is None
        # and model_fields_set contains the field
        if self.receiver_wholesale_price is None and "receiver_wholesale_price" in self.model_fields_set:
            _dict['receiverWholesalePrice'] = None

        # set to None if actual_departure_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.actual_departure_date_time is None and "actual_departure_date_time" in self.model_fields_set:
            _dict['actualDepartureDateTime'] = None

        # set to None if processing_job_type_name (nullable) is None
        # and model_fields_set contains the field
        if self.processing_job_type_name is None and "processing_job_type_name" in self.model_fields_set:
            _dict['processingJobTypeName'] = None

        # set to None if external_id (nullable) is None
        # and model_fields_set contains the field
        if self.external_id is None and "external_id" in self.model_fields_set:
            _dict['externalId'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of MetrcTransferredPackage from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "hostname": obj.get("hostname"),
            "dataModel": obj.get("dataModel"),
            "retrievedAt": obj.get("retrievedAt"),
            "licenseNumber": obj.get("licenseNumber"),
            "index": obj.get("index"),
            "packageId": obj.get("packageId"),
            "recipientFacilityLicenseNumber": obj.get("recipientFacilityLicenseNumber"),
            "recipientFacilityName": obj.get("recipientFacilityName"),
            "manifestNumber": obj.get("manifestNumber"),
            "packageLabel": obj.get("packageLabel"),
            "sourceHarvestNames": obj.get("sourceHarvestNames"),
            "sourcePackageLabels": obj.get("sourcePackageLabels"),
            "productName": obj.get("productName"),
            "productCategoryName": obj.get("productCategoryName"),
            "itemStrainName": obj.get("itemStrainName"),
            "labTestingStateName": obj.get("labTestingStateName"),
            "shippedQuantity": obj.get("shippedQuantity"),
            "shippedUnitOfMeasureAbbreviation": obj.get("shippedUnitOfMeasureAbbreviation"),
            "grossWeight": obj.get("grossWeight"),
            "grossUnitOfWeightAbbreviation": obj.get("grossUnitOfWeightAbbreviation"),
            "shipperWholesalePrice": obj.get("shipperWholesalePrice"),
            "receivedQuantity": obj.get("receivedQuantity"),
            "receivedUnitOfMeasureAbbreviation": obj.get("receivedUnitOfMeasureAbbreviation"),
            "receiverWholesalePrice": obj.get("receiverWholesalePrice"),
            "shipmentPackageStateName": obj.get("shipmentPackageStateName"),
            "actualDepartureDateTime": obj.get("actualDepartureDateTime"),
            "receivedDateTime": obj.get("receivedDateTime"),
            "processingJobTypeName": obj.get("processingJobTypeName"),
            "externalId": obj.get("externalId")
        })
        return _obj


