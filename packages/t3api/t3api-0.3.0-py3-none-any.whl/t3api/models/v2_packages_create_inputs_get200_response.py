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
from t3api.models.lab_testing_states import LabTestingStates
from t3api.models.metrc_location import MetrcLocation
from t3api.models.metrc_remediation_method import MetrcRemediationMethod
from t3api.models.metrc_tag import MetrcTag
from t3api.models.unit_of_measure import UnitOfMeasure
from typing import Optional, Set
from typing_extensions import Self

class V2PackagesCreateInputsGet200Response(BaseModel):
    """
    V2PackagesCreateInputsGet200Response
    """ # noqa: E501
    allowed_production_lab_testing_states: Optional[List[LabTestingStates]] = Field(default=None, alias="allowedProductionLabTestingStates")
    allowed_production_product_category_ids: Optional[List[StrictInt]] = Field(default=None, alias="allowedProductionProductCategoryIds")
    details: Optional[StrictStr] = None
    harvest_batches: Optional[StrictStr] = Field(default=None, alias="harvestBatches")
    is_product_destruction: Optional[StrictBool] = Field(default=None, alias="isProductDestruction")
    item_category_ids: Optional[StrictStr] = Field(default=None, alias="itemCategoryIds")
    items: Optional[List[StrictStr]] = None
    lab_test_batches: Optional[StrictStr] = Field(default=None, alias="labTestBatches")
    locations: Optional[List[MetrcLocation]] = None
    sublocations: Optional[List[StrictStr]] = None
    packages: Optional[List[StrictStr]] = None
    patient_affiliations: Optional[StrictStr] = Field(default=None, alias="patientAffiliations")
    plant_batches: Optional[StrictStr] = Field(default=None, alias="plantBatches")
    plants: Optional[StrictStr] = None
    remediation_methods: Optional[List[MetrcRemediationMethod]] = Field(default=None, alias="remediationMethods")
    submit_for_testing: Optional[StrictBool] = Field(default=None, alias="submitForTesting")
    tags: Optional[List[MetrcTag]] = None
    units_of_measure: Optional[List[UnitOfMeasure]] = Field(default=None, alias="unitsOfMeasure")
    __properties: ClassVar[List[str]] = ["allowedProductionLabTestingStates", "allowedProductionProductCategoryIds", "details", "harvestBatches", "isProductDestruction", "itemCategoryIds", "items", "labTestBatches", "locations", "sublocations", "packages", "patientAffiliations", "plantBatches", "plants", "remediationMethods", "submitForTesting", "tags", "unitsOfMeasure"]

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
        """Create an instance of V2PackagesCreateInputsGet200Response from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in locations (list)
        _items = []
        if self.locations:
            for _item_locations in self.locations:
                if _item_locations:
                    _items.append(_item_locations.to_dict())
            _dict['locations'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in remediation_methods (list)
        _items = []
        if self.remediation_methods:
            for _item_remediation_methods in self.remediation_methods:
                if _item_remediation_methods:
                    _items.append(_item_remediation_methods.to_dict())
            _dict['remediationMethods'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in tags (list)
        _items = []
        if self.tags:
            for _item_tags in self.tags:
                if _item_tags:
                    _items.append(_item_tags.to_dict())
            _dict['tags'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in units_of_measure (list)
        _items = []
        if self.units_of_measure:
            for _item_units_of_measure in self.units_of_measure:
                if _item_units_of_measure:
                    _items.append(_item_units_of_measure.to_dict())
            _dict['unitsOfMeasure'] = _items
        # set to None if details (nullable) is None
        # and model_fields_set contains the field
        if self.details is None and "details" in self.model_fields_set:
            _dict['details'] = None

        # set to None if harvest_batches (nullable) is None
        # and model_fields_set contains the field
        if self.harvest_batches is None and "harvest_batches" in self.model_fields_set:
            _dict['harvestBatches'] = None

        # set to None if item_category_ids (nullable) is None
        # and model_fields_set contains the field
        if self.item_category_ids is None and "item_category_ids" in self.model_fields_set:
            _dict['itemCategoryIds'] = None

        # set to None if lab_test_batches (nullable) is None
        # and model_fields_set contains the field
        if self.lab_test_batches is None and "lab_test_batches" in self.model_fields_set:
            _dict['labTestBatches'] = None

        # set to None if sublocations (nullable) is None
        # and model_fields_set contains the field
        if self.sublocations is None and "sublocations" in self.model_fields_set:
            _dict['sublocations'] = None

        # set to None if patient_affiliations (nullable) is None
        # and model_fields_set contains the field
        if self.patient_affiliations is None and "patient_affiliations" in self.model_fields_set:
            _dict['patientAffiliations'] = None

        # set to None if plant_batches (nullable) is None
        # and model_fields_set contains the field
        if self.plant_batches is None and "plant_batches" in self.model_fields_set:
            _dict['plantBatches'] = None

        # set to None if plants (nullable) is None
        # and model_fields_set contains the field
        if self.plants is None and "plants" in self.model_fields_set:
            _dict['plants'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of V2PackagesCreateInputsGet200Response from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "allowedProductionLabTestingStates": obj.get("allowedProductionLabTestingStates"),
            "allowedProductionProductCategoryIds": obj.get("allowedProductionProductCategoryIds"),
            "details": obj.get("details"),
            "harvestBatches": obj.get("harvestBatches"),
            "isProductDestruction": obj.get("isProductDestruction"),
            "itemCategoryIds": obj.get("itemCategoryIds"),
            "items": obj.get("items"),
            "labTestBatches": obj.get("labTestBatches"),
            "locations": [MetrcLocation.from_dict(_item) for _item in obj["locations"]] if obj.get("locations") is not None else None,
            "sublocations": obj.get("sublocations"),
            "packages": obj.get("packages"),
            "patientAffiliations": obj.get("patientAffiliations"),
            "plantBatches": obj.get("plantBatches"),
            "plants": obj.get("plants"),
            "remediationMethods": [MetrcRemediationMethod.from_dict(_item) for _item in obj["remediationMethods"]] if obj.get("remediationMethods") is not None else None,
            "submitForTesting": obj.get("submitForTesting"),
            "tags": [MetrcTag.from_dict(_item) for _item in obj["tags"]] if obj.get("tags") is not None else None,
            "unitsOfMeasure": [UnitOfMeasure.from_dict(_item) for _item in obj["unitsOfMeasure"]] if obj.get("unitsOfMeasure") is not None else None
        })
        return _obj


