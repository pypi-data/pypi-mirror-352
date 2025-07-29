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
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional, Union
from typing import Optional, Set
from typing_extensions import Self

class MetrcDeliveryPackage(BaseModel):
    """
    MetrcDeliveryPackage
    """ # noqa: E501
    data_model: Optional[StrictStr] = Field(default=None, description="Name of this object's data model  Note: This cannot be used to sort or filter. ", alias="dataModel")
    hostname: Optional[StrictStr] = Field(default=None, description="The hostname this object was retrieved")
    retrieved_at: Optional[datetime] = Field(default=None, description="Timestamp of when this object was pulled from Metrc  Note: This cannot be used to sort or filter. ", alias="retrievedAt")
    license_number: Optional[StrictStr] = Field(default=None, description="License number used to access this object  Note: This cannot be used to sort or filter. ", alias="licenseNumber")
    index: Optional[StrictStr] = Field(default=None, description="Describes the current state of this object at the time it was returned from the API.   Note: This cannot be used to sort or filter. ")
    contains_remediated_product: Optional[StrictBool] = Field(default=None, alias="containsRemediatedProduct")
    donation_facility_license_number: Optional[StrictStr] = Field(default=None, alias="donationFacilityLicenseNumber")
    donation_facility_name: Optional[StrictStr] = Field(default=None, alias="donationFacilityName")
    gross_unit_of_weight_abbreviation: Optional[StrictStr] = Field(default=None, alias="grossUnitOfWeightAbbreviation")
    gross_weight: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="grossWeight")
    is_donation: Optional[StrictBool] = Field(default=None, alias="isDonation")
    is_testing_sample: Optional[StrictBool] = Field(default=None, alias="isTestingSample")
    is_trade_sample: Optional[StrictBool] = Field(default=None, alias="isTradeSample")
    is_trade_sample_persistent: Optional[StrictBool] = Field(default=None, alias="isTradeSamplePersistent")
    item_brand_name: Optional[StrictStr] = Field(default=None, alias="itemBrandName")
    item_serving_size: Optional[StrictStr] = Field(default=None, alias="itemServingSize")
    item_strain_name: Optional[StrictStr] = Field(default=None, alias="itemStrainName")
    item_supply_duration_days: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="itemSupplyDurationDays")
    item_unit_cbd_content: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="itemUnitCbdContent")
    item_unit_cbd_content_dose: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="itemUnitCbdContentDose")
    item_unit_cbd_content_dose_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, alias="itemUnitCbdContentDoseUnitOfMeasureAbbreviation")
    item_unit_cbd_content_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, alias="itemUnitCbdContentUnitOfMeasureAbbreviation")
    item_unit_cbd_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="itemUnitCbdPercent")
    item_unit_quantity: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="itemUnitQuantity")
    item_unit_quantity_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, alias="itemUnitQuantityUnitOfMeasureAbbreviation")
    item_unit_thc_content: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="itemUnitThcContent")
    item_unit_thc_content_dose: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="itemUnitThcContentDose")
    item_unit_thc_content_dose_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, alias="itemUnitThcContentDoseUnitOfMeasureAbbreviation")
    item_unit_thc_content_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, alias="itemUnitThcContentUnitOfMeasureAbbreviation")
    item_unit_thc_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="itemUnitThcPercent")
    item_unit_volume: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="itemUnitVolume")
    item_unit_volume_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, alias="itemUnitVolumeUnitOfMeasureAbbreviation")
    item_unit_weight: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="itemUnitWeight")
    item_unit_weight_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, alias="itemUnitWeightUnitOfMeasureAbbreviation")
    lab_testing_state_name: Optional[StrictStr] = Field(default=None, alias="labTestingStateName")
    multi_harvest: Optional[StrictBool] = Field(default=None, alias="multiHarvest")
    multi_package: Optional[StrictBool] = Field(default=None, alias="multiPackage")
    package_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="packageId")
    package_label: Optional[StrictStr] = Field(default=None, alias="packageLabel")
    package_type: Optional[StrictStr] = Field(default=None, alias="packageType")
    packaged_date: Optional[datetime] = Field(default=None, alias="packagedDate")
    product_category_name: Optional[StrictStr] = Field(default=None, alias="productCategoryName")
    product_name: Optional[StrictStr] = Field(default=None, alias="productName")
    product_requires_remediation: Optional[StrictBool] = Field(default=None, alias="productRequiresRemediation")
    production_batch_number: Optional[StrictStr] = Field(default=None, alias="productionBatchNumber")
    received_quantity: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="receivedQuantity")
    received_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, alias="receivedUnitOfMeasureAbbreviation")
    receiver_wholesale_price: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="receiverWholesalePrice")
    remediation_date: Optional[datetime] = Field(default=None, alias="remediationDate")
    shipment_package_state: Optional[StrictStr] = Field(default=None, alias="shipmentPackageState")
    shipped_quantity: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="shippedQuantity")
    shipped_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, alias="shippedUnitOfMeasureAbbreviation")
    shipper_wholesale_price: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="shipperWholesalePrice")
    source_harvest_names: Optional[StrictStr] = Field(default=None, alias="sourceHarvestNames")
    source_package_is_donation: Optional[StrictBool] = Field(default=None, alias="sourcePackageIsDonation")
    source_package_is_trade_sample: Optional[StrictBool] = Field(default=None, alias="sourcePackageIsTradeSample")
    source_package_labels: Optional[StrictStr] = Field(default=None, alias="sourcePackageLabels")
    trade_sample_facility_license_number: Optional[StrictStr] = Field(default=None, alias="tradeSampleFacilityLicenseNumber")
    trade_sample_facility_name: Optional[StrictStr] = Field(default=None, alias="tradeSampleFacilityName")
    sell_by_date: Optional[datetime] = Field(default=None, alias="sellByDate")
    processing_job_type_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="processingJobTypeId")
    in_transit_status: Optional[StrictStr] = Field(default=None, alias="inTransitStatus")
    is_in_transit: Optional[StrictBool] = Field(default=None, alias="isInTransit")
    expiration_date: Optional[datetime] = Field(default=None, alias="expirationDate")
    retail_id_qr_count: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="retailIdQrCount")
    lab_test_stage_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="labTestStageId")
    use_by_date: Optional[datetime] = Field(default=None, alias="useByDate")
    product_label: Optional[StrictStr] = Field(default=None, alias="productLabel")
    external_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="externalId")
    __properties: ClassVar[List[str]] = ["dataModel", "hostname", "retrievedAt", "licenseNumber", "index", "containsRemediatedProduct", "donationFacilityLicenseNumber", "donationFacilityName", "grossUnitOfWeightAbbreviation", "grossWeight", "isDonation", "isTestingSample", "isTradeSample", "isTradeSamplePersistent", "itemBrandName", "itemServingSize", "itemStrainName", "itemSupplyDurationDays", "itemUnitCbdContent", "itemUnitCbdContentDose", "itemUnitCbdContentDoseUnitOfMeasureAbbreviation", "itemUnitCbdContentUnitOfMeasureAbbreviation", "itemUnitCbdPercent", "itemUnitQuantity", "itemUnitQuantityUnitOfMeasureAbbreviation", "itemUnitThcContent", "itemUnitThcContentDose", "itemUnitThcContentDoseUnitOfMeasureAbbreviation", "itemUnitThcContentUnitOfMeasureAbbreviation", "itemUnitThcPercent", "itemUnitVolume", "itemUnitVolumeUnitOfMeasureAbbreviation", "itemUnitWeight", "itemUnitWeightUnitOfMeasureAbbreviation", "labTestingStateName", "multiHarvest", "multiPackage", "packageId", "packageLabel", "packageType", "packagedDate", "productCategoryName", "productName", "productRequiresRemediation", "productionBatchNumber", "receivedQuantity", "receivedUnitOfMeasureAbbreviation", "receiverWholesalePrice", "remediationDate", "shipmentPackageState", "shippedQuantity", "shippedUnitOfMeasureAbbreviation", "shipperWholesalePrice", "sourceHarvestNames", "sourcePackageIsDonation", "sourcePackageIsTradeSample", "sourcePackageLabels", "tradeSampleFacilityLicenseNumber", "tradeSampleFacilityName", "sellByDate", "processingJobTypeId", "inTransitStatus", "isInTransit", "expirationDate", "retailIdQrCount", "labTestStageId", "useByDate", "productLabel", "externalId"]

    @field_validator('index')
    def index_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['TRANSFERRED_PACKAGE']):
            raise ValueError("must be one of enum values ('TRANSFERRED_PACKAGE')")
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
        """Create an instance of MetrcDeliveryPackage from a JSON string"""
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
        # set to None if donation_facility_license_number (nullable) is None
        # and model_fields_set contains the field
        if self.donation_facility_license_number is None and "donation_facility_license_number" in self.model_fields_set:
            _dict['donationFacilityLicenseNumber'] = None

        # set to None if donation_facility_name (nullable) is None
        # and model_fields_set contains the field
        if self.donation_facility_name is None and "donation_facility_name" in self.model_fields_set:
            _dict['donationFacilityName'] = None

        # set to None if gross_weight (nullable) is None
        # and model_fields_set contains the field
        if self.gross_weight is None and "gross_weight" in self.model_fields_set:
            _dict['grossWeight'] = None

        # set to None if item_brand_name (nullable) is None
        # and model_fields_set contains the field
        if self.item_brand_name is None and "item_brand_name" in self.model_fields_set:
            _dict['itemBrandName'] = None

        # set to None if item_strain_name (nullable) is None
        # and model_fields_set contains the field
        if self.item_strain_name is None and "item_strain_name" in self.model_fields_set:
            _dict['itemStrainName'] = None

        # set to None if item_supply_duration_days (nullable) is None
        # and model_fields_set contains the field
        if self.item_supply_duration_days is None and "item_supply_duration_days" in self.model_fields_set:
            _dict['itemSupplyDurationDays'] = None

        # set to None if item_unit_cbd_content (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_cbd_content is None and "item_unit_cbd_content" in self.model_fields_set:
            _dict['itemUnitCbdContent'] = None

        # set to None if item_unit_cbd_content_dose (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_cbd_content_dose is None and "item_unit_cbd_content_dose" in self.model_fields_set:
            _dict['itemUnitCbdContentDose'] = None

        # set to None if item_unit_cbd_content_dose_unit_of_measure_abbreviation (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_cbd_content_dose_unit_of_measure_abbreviation is None and "item_unit_cbd_content_dose_unit_of_measure_abbreviation" in self.model_fields_set:
            _dict['itemUnitCbdContentDoseUnitOfMeasureAbbreviation'] = None

        # set to None if item_unit_cbd_content_unit_of_measure_abbreviation (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_cbd_content_unit_of_measure_abbreviation is None and "item_unit_cbd_content_unit_of_measure_abbreviation" in self.model_fields_set:
            _dict['itemUnitCbdContentUnitOfMeasureAbbreviation'] = None

        # set to None if item_unit_cbd_percent (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_cbd_percent is None and "item_unit_cbd_percent" in self.model_fields_set:
            _dict['itemUnitCbdPercent'] = None

        # set to None if item_unit_quantity (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_quantity is None and "item_unit_quantity" in self.model_fields_set:
            _dict['itemUnitQuantity'] = None

        # set to None if item_unit_quantity_unit_of_measure_abbreviation (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_quantity_unit_of_measure_abbreviation is None and "item_unit_quantity_unit_of_measure_abbreviation" in self.model_fields_set:
            _dict['itemUnitQuantityUnitOfMeasureAbbreviation'] = None

        # set to None if item_unit_thc_content (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_thc_content is None and "item_unit_thc_content" in self.model_fields_set:
            _dict['itemUnitThcContent'] = None

        # set to None if item_unit_thc_content_dose (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_thc_content_dose is None and "item_unit_thc_content_dose" in self.model_fields_set:
            _dict['itemUnitThcContentDose'] = None

        # set to None if item_unit_thc_content_dose_unit_of_measure_abbreviation (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_thc_content_dose_unit_of_measure_abbreviation is None and "item_unit_thc_content_dose_unit_of_measure_abbreviation" in self.model_fields_set:
            _dict['itemUnitThcContentDoseUnitOfMeasureAbbreviation'] = None

        # set to None if item_unit_thc_content_unit_of_measure_abbreviation (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_thc_content_unit_of_measure_abbreviation is None and "item_unit_thc_content_unit_of_measure_abbreviation" in self.model_fields_set:
            _dict['itemUnitThcContentUnitOfMeasureAbbreviation'] = None

        # set to None if item_unit_thc_percent (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_thc_percent is None and "item_unit_thc_percent" in self.model_fields_set:
            _dict['itemUnitThcPercent'] = None

        # set to None if item_unit_volume (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_volume is None and "item_unit_volume" in self.model_fields_set:
            _dict['itemUnitVolume'] = None

        # set to None if item_unit_volume_unit_of_measure_abbreviation (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_volume_unit_of_measure_abbreviation is None and "item_unit_volume_unit_of_measure_abbreviation" in self.model_fields_set:
            _dict['itemUnitVolumeUnitOfMeasureAbbreviation'] = None

        # set to None if item_unit_weight (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_weight is None and "item_unit_weight" in self.model_fields_set:
            _dict['itemUnitWeight'] = None

        # set to None if packaged_date (nullable) is None
        # and model_fields_set contains the field
        if self.packaged_date is None and "packaged_date" in self.model_fields_set:
            _dict['packagedDate'] = None

        # set to None if production_batch_number (nullable) is None
        # and model_fields_set contains the field
        if self.production_batch_number is None and "production_batch_number" in self.model_fields_set:
            _dict['productionBatchNumber'] = None

        # set to None if receiver_wholesale_price (nullable) is None
        # and model_fields_set contains the field
        if self.receiver_wholesale_price is None and "receiver_wholesale_price" in self.model_fields_set:
            _dict['receiverWholesalePrice'] = None

        # set to None if remediation_date (nullable) is None
        # and model_fields_set contains the field
        if self.remediation_date is None and "remediation_date" in self.model_fields_set:
            _dict['remediationDate'] = None

        # set to None if shipper_wholesale_price (nullable) is None
        # and model_fields_set contains the field
        if self.shipper_wholesale_price is None and "shipper_wholesale_price" in self.model_fields_set:
            _dict['shipperWholesalePrice'] = None

        # set to None if trade_sample_facility_license_number (nullable) is None
        # and model_fields_set contains the field
        if self.trade_sample_facility_license_number is None and "trade_sample_facility_license_number" in self.model_fields_set:
            _dict['tradeSampleFacilityLicenseNumber'] = None

        # set to None if trade_sample_facility_name (nullable) is None
        # and model_fields_set contains the field
        if self.trade_sample_facility_name is None and "trade_sample_facility_name" in self.model_fields_set:
            _dict['tradeSampleFacilityName'] = None

        # set to None if sell_by_date (nullable) is None
        # and model_fields_set contains the field
        if self.sell_by_date is None and "sell_by_date" in self.model_fields_set:
            _dict['sellByDate'] = None

        # set to None if processing_job_type_id (nullable) is None
        # and model_fields_set contains the field
        if self.processing_job_type_id is None and "processing_job_type_id" in self.model_fields_set:
            _dict['processingJobTypeId'] = None

        # set to None if expiration_date (nullable) is None
        # and model_fields_set contains the field
        if self.expiration_date is None and "expiration_date" in self.model_fields_set:
            _dict['expirationDate'] = None

        # set to None if retail_id_qr_count (nullable) is None
        # and model_fields_set contains the field
        if self.retail_id_qr_count is None and "retail_id_qr_count" in self.model_fields_set:
            _dict['retailIdQrCount'] = None

        # set to None if lab_test_stage_id (nullable) is None
        # and model_fields_set contains the field
        if self.lab_test_stage_id is None and "lab_test_stage_id" in self.model_fields_set:
            _dict['labTestStageId'] = None

        # set to None if use_by_date (nullable) is None
        # and model_fields_set contains the field
        if self.use_by_date is None and "use_by_date" in self.model_fields_set:
            _dict['useByDate'] = None

        # set to None if product_label (nullable) is None
        # and model_fields_set contains the field
        if self.product_label is None and "product_label" in self.model_fields_set:
            _dict['productLabel'] = None

        # set to None if external_id (nullable) is None
        # and model_fields_set contains the field
        if self.external_id is None and "external_id" in self.model_fields_set:
            _dict['externalId'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of MetrcDeliveryPackage from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "dataModel": obj.get("dataModel"),
            "hostname": obj.get("hostname"),
            "retrievedAt": obj.get("retrievedAt"),
            "licenseNumber": obj.get("licenseNumber"),
            "index": obj.get("index"),
            "containsRemediatedProduct": obj.get("containsRemediatedProduct"),
            "donationFacilityLicenseNumber": obj.get("donationFacilityLicenseNumber"),
            "donationFacilityName": obj.get("donationFacilityName"),
            "grossUnitOfWeightAbbreviation": obj.get("grossUnitOfWeightAbbreviation"),
            "grossWeight": obj.get("grossWeight"),
            "isDonation": obj.get("isDonation"),
            "isTestingSample": obj.get("isTestingSample"),
            "isTradeSample": obj.get("isTradeSample"),
            "isTradeSamplePersistent": obj.get("isTradeSamplePersistent"),
            "itemBrandName": obj.get("itemBrandName"),
            "itemServingSize": obj.get("itemServingSize"),
            "itemStrainName": obj.get("itemStrainName"),
            "itemSupplyDurationDays": obj.get("itemSupplyDurationDays"),
            "itemUnitCbdContent": obj.get("itemUnitCbdContent"),
            "itemUnitCbdContentDose": obj.get("itemUnitCbdContentDose"),
            "itemUnitCbdContentDoseUnitOfMeasureAbbreviation": obj.get("itemUnitCbdContentDoseUnitOfMeasureAbbreviation"),
            "itemUnitCbdContentUnitOfMeasureAbbreviation": obj.get("itemUnitCbdContentUnitOfMeasureAbbreviation"),
            "itemUnitCbdPercent": obj.get("itemUnitCbdPercent"),
            "itemUnitQuantity": obj.get("itemUnitQuantity"),
            "itemUnitQuantityUnitOfMeasureAbbreviation": obj.get("itemUnitQuantityUnitOfMeasureAbbreviation"),
            "itemUnitThcContent": obj.get("itemUnitThcContent"),
            "itemUnitThcContentDose": obj.get("itemUnitThcContentDose"),
            "itemUnitThcContentDoseUnitOfMeasureAbbreviation": obj.get("itemUnitThcContentDoseUnitOfMeasureAbbreviation"),
            "itemUnitThcContentUnitOfMeasureAbbreviation": obj.get("itemUnitThcContentUnitOfMeasureAbbreviation"),
            "itemUnitThcPercent": obj.get("itemUnitThcPercent"),
            "itemUnitVolume": obj.get("itemUnitVolume"),
            "itemUnitVolumeUnitOfMeasureAbbreviation": obj.get("itemUnitVolumeUnitOfMeasureAbbreviation"),
            "itemUnitWeight": obj.get("itemUnitWeight"),
            "itemUnitWeightUnitOfMeasureAbbreviation": obj.get("itemUnitWeightUnitOfMeasureAbbreviation"),
            "labTestingStateName": obj.get("labTestingStateName"),
            "multiHarvest": obj.get("multiHarvest"),
            "multiPackage": obj.get("multiPackage"),
            "packageId": obj.get("packageId"),
            "packageLabel": obj.get("packageLabel"),
            "packageType": obj.get("packageType"),
            "packagedDate": obj.get("packagedDate"),
            "productCategoryName": obj.get("productCategoryName"),
            "productName": obj.get("productName"),
            "productRequiresRemediation": obj.get("productRequiresRemediation"),
            "productionBatchNumber": obj.get("productionBatchNumber"),
            "receivedQuantity": obj.get("receivedQuantity"),
            "receivedUnitOfMeasureAbbreviation": obj.get("receivedUnitOfMeasureAbbreviation"),
            "receiverWholesalePrice": obj.get("receiverWholesalePrice"),
            "remediationDate": obj.get("remediationDate"),
            "shipmentPackageState": obj.get("shipmentPackageState"),
            "shippedQuantity": obj.get("shippedQuantity"),
            "shippedUnitOfMeasureAbbreviation": obj.get("shippedUnitOfMeasureAbbreviation"),
            "shipperWholesalePrice": obj.get("shipperWholesalePrice"),
            "sourceHarvestNames": obj.get("sourceHarvestNames"),
            "sourcePackageIsDonation": obj.get("sourcePackageIsDonation"),
            "sourcePackageIsTradeSample": obj.get("sourcePackageIsTradeSample"),
            "sourcePackageLabels": obj.get("sourcePackageLabels"),
            "tradeSampleFacilityLicenseNumber": obj.get("tradeSampleFacilityLicenseNumber"),
            "tradeSampleFacilityName": obj.get("tradeSampleFacilityName"),
            "sellByDate": obj.get("sellByDate"),
            "processingJobTypeId": obj.get("processingJobTypeId"),
            "inTransitStatus": obj.get("inTransitStatus"),
            "isInTransit": obj.get("isInTransit"),
            "expirationDate": obj.get("expirationDate"),
            "retailIdQrCount": obj.get("retailIdQrCount"),
            "labTestStageId": obj.get("labTestStageId"),
            "useByDate": obj.get("useByDate"),
            "productLabel": obj.get("productLabel"),
            "externalId": obj.get("externalId")
        })
        return _obj


