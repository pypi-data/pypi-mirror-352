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
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Union
from typing import Optional, Set
from typing_extensions import Self

class MetrcTransaction(BaseModel):
    """
    MetrcTransaction
    """ # noqa: E501
    id: Optional[StrictInt] = Field(default=None, description="Unique identifier for the harvest")
    hostname: Optional[StrictStr] = Field(default=None, description="The hostname this object was retrieved from")
    data_model: Optional[StrictStr] = Field(default=None, description="Name of this object's data model", alias="dataModel")
    retrieved_at: Optional[datetime] = Field(default=None, description="Timestamp of when this object was pulled from Metrc", alias="retrievedAt")
    license_number: Optional[StrictStr] = Field(default=None, description="License number used to access this object", alias="licenseNumber")
    package_id: Optional[StrictInt] = Field(default=None, description="Unique identifier for the package", alias="packageId")
    trip_id: Optional[StrictInt] = Field(default=None, description="Identifier for the trip (nullable)", alias="tripId")
    trip_manifest_number: Optional[StrictStr] = Field(default=None, description="Trip manifest number (nullable)", alias="tripManifestNumber")
    package_label: Optional[StrictStr] = Field(default=None, description="Label associated with the package", alias="packageLabel")
    is_partial: Optional[StrictBool] = Field(default=None, description="Whether the package is partial (nullable)", alias="isPartial")
    has_partial: Optional[StrictBool] = Field(default=None, description="Whether the package has a partial item", alias="hasPartial")
    package_type: Optional[StrictStr] = Field(default=None, description="Type of the package", alias="packageType")
    product_name: Optional[StrictStr] = Field(default=None, description="Name of the product", alias="productName")
    product_category_name: Optional[StrictStr] = Field(default=None, description="Category of the product", alias="productCategoryName")
    item_strain_name: Optional[StrictStr] = Field(default=None, description="Strain name of the product (nullable)", alias="itemStrainName")
    item_brand_name: Optional[StrictStr] = Field(default=None, description="Brand name of the product (nullable)", alias="itemBrandName")
    item_unit_cbd_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Percentage of CBD in the item (nullable)", alias="itemUnitCbdPercent")
    item_unit_cbd_content: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="CBD content in the item (nullable)", alias="itemUnitCbdContent")
    item_unit_cbd_content_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, description="Abbreviation of the CBD content unit of measure (nullable)", alias="itemUnitCbdContentUnitOfMeasureAbbreviation")
    item_unit_cbd_content_dose: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="CBD content dose of the item (nullable)", alias="itemUnitCbdContentDose")
    item_unit_cbd_content_dose_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, description="Abbreviation of the CBD dose content unit of measure (nullable)", alias="itemUnitCbdContentDoseUnitOfMeasureAbbreviation")
    item_unit_thc_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Percentage of THC in the item (nullable)", alias="itemUnitThcPercent")
    item_unit_thc_content: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="THC content in the item (nullable)", alias="itemUnitThcContent")
    item_unit_thc_content_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, description="Abbreviation of the THC content unit of measure (nullable)", alias="itemUnitThcContentUnitOfMeasureAbbreviation")
    item_unit_thc_content_dose: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="THC content dose of the item (nullable)", alias="itemUnitThcContentDose")
    item_unit_thc_content_dose_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, description="Abbreviation of the THC dose content unit of measure (nullable)", alias="itemUnitThcContentDoseUnitOfMeasureAbbreviation")
    item_unit_volume: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Volume of the item (nullable)", alias="itemUnitVolume")
    item_unit_volume_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, description="Abbreviation of the volume unit of measure (nullable)", alias="itemUnitVolumeUnitOfMeasureAbbreviation")
    item_unit_weight: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Weight of the item", alias="itemUnitWeight")
    item_unit_weight_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, description="Abbreviation of the weight unit of measure", alias="itemUnitWeightUnitOfMeasureAbbreviation")
    item_serving_size: Optional[StrictStr] = Field(default=None, description="Serving size of the item", alias="itemServingSize")
    item_supply_duration_days: Optional[StrictInt] = Field(default=None, description="Supply duration in days (nullable)", alias="itemSupplyDurationDays")
    item_unit_quantity: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Quantity of the item (nullable)", alias="itemUnitQuantity")
    item_unit_quantity_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, description="Abbreviation of the quantity unit of measure (nullable)", alias="itemUnitQuantityUnitOfMeasureAbbreviation")
    quantity_sold: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Quantity of the item sold", alias="quantitySold")
    unit_of_measure_id: Optional[StrictInt] = Field(default=None, description="ID of the unit of measure", alias="unitOfMeasureId")
    unit_of_measure_name: Optional[StrictStr] = Field(default=None, description="Name of the unit of measure", alias="unitOfMeasureName")
    unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, description="Abbreviation of the unit of measure", alias="unitOfMeasureAbbreviation")
    unit_thc_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Percentage of THC in the unit (nullable)", alias="unitThcPercent")
    unit_thc_content: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="THC content in the unit (nullable)", alias="unitThcContent")
    unit_thc_content_unit_of_measure_id: Optional[StrictInt] = Field(default=None, description="Unit of measure ID for THC content (nullable)", alias="unitThcContentUnitOfMeasureId")
    unit_weight: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Weight of the unit", alias="unitWeight")
    unit_weight_unit_of_measure_id: Optional[StrictInt] = Field(default=None, description="Unit of measure ID for weight", alias="unitWeightUnitOfMeasureId")
    total_price: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Total price of the sale", alias="totalPrice")
    sales_delivery_state: Optional[StrictStr] = Field(default=None, description="Delivery state of the sale (nullable)", alias="salesDeliveryState")
    sales_delivery_state_name: Optional[StrictStr] = Field(default=None, description="Name of the delivery state (nullable)", alias="salesDeliveryStateName")
    is_trade_sample: Optional[StrictBool] = Field(default=None, description="Whether the sale was a trade sample", alias="isTradeSample")
    is_donation: Optional[StrictBool] = Field(default=None, description="Whether the sale was a donation", alias="isDonation")
    is_testing_sample: Optional[StrictBool] = Field(default=None, description="Whether the sale was a testing sample", alias="isTestingSample")
    product_requires_remediation: Optional[StrictBool] = Field(default=None, description="Whether the product requires remediation", alias="productRequiresRemediation")
    contains_remediated_product: Optional[StrictBool] = Field(default=None, description="Whether the product contains remediated items", alias="containsRemediatedProduct")
    remediation_date: Optional[datetime] = Field(default=None, description="Date of product remediation (nullable)", alias="remediationDate")
    is_archived: Optional[StrictBool] = Field(default=None, description="Whether the sale is archived", alias="isArchived")
    archived_date: Optional[datetime] = Field(default=None, description="Date when the sale was archived (nullable)", alias="archivedDate")
    recorded_date_time: Optional[datetime] = Field(default=None, description="Date and time when the sale was recorded", alias="recordedDateTime")
    recorded_by_user_name: Optional[StrictStr] = Field(default=None, description="Username of the person who recorded the sale (nullable)", alias="recordedByUserName")
    last_modified: Optional[datetime] = Field(default=None, description="Date and time when the sale was last modified", alias="lastModified")
    invoice_number: Optional[StrictStr] = Field(default=None, description="Invoice number of the sale (nullable)", alias="invoiceNumber")
    price: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Price of the sale (nullable)")
    excise_tax: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Excise tax applied to the sale (nullable)", alias="exciseTax")
    city_tax: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="City tax applied to the sale (nullable)", alias="cityTax")
    county_tax: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="County tax applied to the sale (nullable)", alias="countyTax")
    municipal_tax: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Municipal tax applied to the sale (nullable)", alias="municipalTax")
    discount_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Discount applied to the sale (nullable)", alias="discountAmount")
    sub_total: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Subtotal of the sale (nullable)", alias="subTotal")
    sales_tax: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Sales tax applied to the sale (nullable)", alias="salesTax")
    trade_sample_sale_verified: Optional[StrictBool] = Field(default=None, description="Whether the trade sample sale was verified (nullable)", alias="tradeSampleSaleVerified")
    recall_product_sale_verified: Optional[StrictBool] = Field(default=None, description="Whether the recall product sale was verified (nullable)", alias="recallProductSaleVerified")
    qr_code_document: Optional[StrictStr] = Field(default=None, alias="qrCodeDocument")
    __properties: ClassVar[List[str]] = ["id", "hostname", "dataModel", "retrievedAt", "licenseNumber", "packageId", "tripId", "tripManifestNumber", "packageLabel", "isPartial", "hasPartial", "packageType", "productName", "productCategoryName", "itemStrainName", "itemBrandName", "itemUnitCbdPercent", "itemUnitCbdContent", "itemUnitCbdContentUnitOfMeasureAbbreviation", "itemUnitCbdContentDose", "itemUnitCbdContentDoseUnitOfMeasureAbbreviation", "itemUnitThcPercent", "itemUnitThcContent", "itemUnitThcContentUnitOfMeasureAbbreviation", "itemUnitThcContentDose", "itemUnitThcContentDoseUnitOfMeasureAbbreviation", "itemUnitVolume", "itemUnitVolumeUnitOfMeasureAbbreviation", "itemUnitWeight", "itemUnitWeightUnitOfMeasureAbbreviation", "itemServingSize", "itemSupplyDurationDays", "itemUnitQuantity", "itemUnitQuantityUnitOfMeasureAbbreviation", "quantitySold", "unitOfMeasureId", "unitOfMeasureName", "unitOfMeasureAbbreviation", "unitThcPercent", "unitThcContent", "unitThcContentUnitOfMeasureId", "unitWeight", "unitWeightUnitOfMeasureId", "totalPrice", "salesDeliveryState", "salesDeliveryStateName", "isTradeSample", "isDonation", "isTestingSample", "productRequiresRemediation", "containsRemediatedProduct", "remediationDate", "isArchived", "archivedDate", "recordedDateTime", "recordedByUserName", "lastModified", "invoiceNumber", "price", "exciseTax", "cityTax", "countyTax", "municipalTax", "discountAmount", "subTotal", "salesTax", "tradeSampleSaleVerified", "recallProductSaleVerified", "qrCodeDocument"]

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
        """Create an instance of MetrcTransaction from a JSON string"""
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
        # set to None if trip_id (nullable) is None
        # and model_fields_set contains the field
        if self.trip_id is None and "trip_id" in self.model_fields_set:
            _dict['tripId'] = None

        # set to None if trip_manifest_number (nullable) is None
        # and model_fields_set contains the field
        if self.trip_manifest_number is None and "trip_manifest_number" in self.model_fields_set:
            _dict['tripManifestNumber'] = None

        # set to None if is_partial (nullable) is None
        # and model_fields_set contains the field
        if self.is_partial is None and "is_partial" in self.model_fields_set:
            _dict['isPartial'] = None

        # set to None if item_strain_name (nullable) is None
        # and model_fields_set contains the field
        if self.item_strain_name is None and "item_strain_name" in self.model_fields_set:
            _dict['itemStrainName'] = None

        # set to None if item_brand_name (nullable) is None
        # and model_fields_set contains the field
        if self.item_brand_name is None and "item_brand_name" in self.model_fields_set:
            _dict['itemBrandName'] = None

        # set to None if item_unit_cbd_percent (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_cbd_percent is None and "item_unit_cbd_percent" in self.model_fields_set:
            _dict['itemUnitCbdPercent'] = None

        # set to None if item_unit_cbd_content (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_cbd_content is None and "item_unit_cbd_content" in self.model_fields_set:
            _dict['itemUnitCbdContent'] = None

        # set to None if item_unit_cbd_content_unit_of_measure_abbreviation (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_cbd_content_unit_of_measure_abbreviation is None and "item_unit_cbd_content_unit_of_measure_abbreviation" in self.model_fields_set:
            _dict['itemUnitCbdContentUnitOfMeasureAbbreviation'] = None

        # set to None if item_unit_cbd_content_dose (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_cbd_content_dose is None and "item_unit_cbd_content_dose" in self.model_fields_set:
            _dict['itemUnitCbdContentDose'] = None

        # set to None if item_unit_cbd_content_dose_unit_of_measure_abbreviation (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_cbd_content_dose_unit_of_measure_abbreviation is None and "item_unit_cbd_content_dose_unit_of_measure_abbreviation" in self.model_fields_set:
            _dict['itemUnitCbdContentDoseUnitOfMeasureAbbreviation'] = None

        # set to None if item_unit_thc_percent (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_thc_percent is None and "item_unit_thc_percent" in self.model_fields_set:
            _dict['itemUnitThcPercent'] = None

        # set to None if item_unit_thc_content (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_thc_content is None and "item_unit_thc_content" in self.model_fields_set:
            _dict['itemUnitThcContent'] = None

        # set to None if item_unit_thc_content_unit_of_measure_abbreviation (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_thc_content_unit_of_measure_abbreviation is None and "item_unit_thc_content_unit_of_measure_abbreviation" in self.model_fields_set:
            _dict['itemUnitThcContentUnitOfMeasureAbbreviation'] = None

        # set to None if item_unit_thc_content_dose (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_thc_content_dose is None and "item_unit_thc_content_dose" in self.model_fields_set:
            _dict['itemUnitThcContentDose'] = None

        # set to None if item_unit_thc_content_dose_unit_of_measure_abbreviation (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_thc_content_dose_unit_of_measure_abbreviation is None and "item_unit_thc_content_dose_unit_of_measure_abbreviation" in self.model_fields_set:
            _dict['itemUnitThcContentDoseUnitOfMeasureAbbreviation'] = None

        # set to None if item_unit_volume (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_volume is None and "item_unit_volume" in self.model_fields_set:
            _dict['itemUnitVolume'] = None

        # set to None if item_unit_volume_unit_of_measure_abbreviation (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_volume_unit_of_measure_abbreviation is None and "item_unit_volume_unit_of_measure_abbreviation" in self.model_fields_set:
            _dict['itemUnitVolumeUnitOfMeasureAbbreviation'] = None

        # set to None if item_supply_duration_days (nullable) is None
        # and model_fields_set contains the field
        if self.item_supply_duration_days is None and "item_supply_duration_days" in self.model_fields_set:
            _dict['itemSupplyDurationDays'] = None

        # set to None if item_unit_quantity (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_quantity is None and "item_unit_quantity" in self.model_fields_set:
            _dict['itemUnitQuantity'] = None

        # set to None if item_unit_quantity_unit_of_measure_abbreviation (nullable) is None
        # and model_fields_set contains the field
        if self.item_unit_quantity_unit_of_measure_abbreviation is None and "item_unit_quantity_unit_of_measure_abbreviation" in self.model_fields_set:
            _dict['itemUnitQuantityUnitOfMeasureAbbreviation'] = None

        # set to None if unit_thc_percent (nullable) is None
        # and model_fields_set contains the field
        if self.unit_thc_percent is None and "unit_thc_percent" in self.model_fields_set:
            _dict['unitThcPercent'] = None

        # set to None if unit_thc_content (nullable) is None
        # and model_fields_set contains the field
        if self.unit_thc_content is None and "unit_thc_content" in self.model_fields_set:
            _dict['unitThcContent'] = None

        # set to None if unit_thc_content_unit_of_measure_id (nullable) is None
        # and model_fields_set contains the field
        if self.unit_thc_content_unit_of_measure_id is None and "unit_thc_content_unit_of_measure_id" in self.model_fields_set:
            _dict['unitThcContentUnitOfMeasureId'] = None

        # set to None if sales_delivery_state (nullable) is None
        # and model_fields_set contains the field
        if self.sales_delivery_state is None and "sales_delivery_state" in self.model_fields_set:
            _dict['salesDeliveryState'] = None

        # set to None if sales_delivery_state_name (nullable) is None
        # and model_fields_set contains the field
        if self.sales_delivery_state_name is None and "sales_delivery_state_name" in self.model_fields_set:
            _dict['salesDeliveryStateName'] = None

        # set to None if remediation_date (nullable) is None
        # and model_fields_set contains the field
        if self.remediation_date is None and "remediation_date" in self.model_fields_set:
            _dict['remediationDate'] = None

        # set to None if archived_date (nullable) is None
        # and model_fields_set contains the field
        if self.archived_date is None and "archived_date" in self.model_fields_set:
            _dict['archivedDate'] = None

        # set to None if recorded_by_user_name (nullable) is None
        # and model_fields_set contains the field
        if self.recorded_by_user_name is None and "recorded_by_user_name" in self.model_fields_set:
            _dict['recordedByUserName'] = None

        # set to None if invoice_number (nullable) is None
        # and model_fields_set contains the field
        if self.invoice_number is None and "invoice_number" in self.model_fields_set:
            _dict['invoiceNumber'] = None

        # set to None if price (nullable) is None
        # and model_fields_set contains the field
        if self.price is None and "price" in self.model_fields_set:
            _dict['price'] = None

        # set to None if excise_tax (nullable) is None
        # and model_fields_set contains the field
        if self.excise_tax is None and "excise_tax" in self.model_fields_set:
            _dict['exciseTax'] = None

        # set to None if city_tax (nullable) is None
        # and model_fields_set contains the field
        if self.city_tax is None and "city_tax" in self.model_fields_set:
            _dict['cityTax'] = None

        # set to None if county_tax (nullable) is None
        # and model_fields_set contains the field
        if self.county_tax is None and "county_tax" in self.model_fields_set:
            _dict['countyTax'] = None

        # set to None if municipal_tax (nullable) is None
        # and model_fields_set contains the field
        if self.municipal_tax is None and "municipal_tax" in self.model_fields_set:
            _dict['municipalTax'] = None

        # set to None if discount_amount (nullable) is None
        # and model_fields_set contains the field
        if self.discount_amount is None and "discount_amount" in self.model_fields_set:
            _dict['discountAmount'] = None

        # set to None if sub_total (nullable) is None
        # and model_fields_set contains the field
        if self.sub_total is None and "sub_total" in self.model_fields_set:
            _dict['subTotal'] = None

        # set to None if sales_tax (nullable) is None
        # and model_fields_set contains the field
        if self.sales_tax is None and "sales_tax" in self.model_fields_set:
            _dict['salesTax'] = None

        # set to None if trade_sample_sale_verified (nullable) is None
        # and model_fields_set contains the field
        if self.trade_sample_sale_verified is None and "trade_sample_sale_verified" in self.model_fields_set:
            _dict['tradeSampleSaleVerified'] = None

        # set to None if recall_product_sale_verified (nullable) is None
        # and model_fields_set contains the field
        if self.recall_product_sale_verified is None and "recall_product_sale_verified" in self.model_fields_set:
            _dict['recallProductSaleVerified'] = None

        # set to None if qr_code_document (nullable) is None
        # and model_fields_set contains the field
        if self.qr_code_document is None and "qr_code_document" in self.model_fields_set:
            _dict['qrCodeDocument'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of MetrcTransaction from a dict"""
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
            "packageId": obj.get("packageId"),
            "tripId": obj.get("tripId"),
            "tripManifestNumber": obj.get("tripManifestNumber"),
            "packageLabel": obj.get("packageLabel"),
            "isPartial": obj.get("isPartial"),
            "hasPartial": obj.get("hasPartial"),
            "packageType": obj.get("packageType"),
            "productName": obj.get("productName"),
            "productCategoryName": obj.get("productCategoryName"),
            "itemStrainName": obj.get("itemStrainName"),
            "itemBrandName": obj.get("itemBrandName"),
            "itemUnitCbdPercent": obj.get("itemUnitCbdPercent"),
            "itemUnitCbdContent": obj.get("itemUnitCbdContent"),
            "itemUnitCbdContentUnitOfMeasureAbbreviation": obj.get("itemUnitCbdContentUnitOfMeasureAbbreviation"),
            "itemUnitCbdContentDose": obj.get("itemUnitCbdContentDose"),
            "itemUnitCbdContentDoseUnitOfMeasureAbbreviation": obj.get("itemUnitCbdContentDoseUnitOfMeasureAbbreviation"),
            "itemUnitThcPercent": obj.get("itemUnitThcPercent"),
            "itemUnitThcContent": obj.get("itemUnitThcContent"),
            "itemUnitThcContentUnitOfMeasureAbbreviation": obj.get("itemUnitThcContentUnitOfMeasureAbbreviation"),
            "itemUnitThcContentDose": obj.get("itemUnitThcContentDose"),
            "itemUnitThcContentDoseUnitOfMeasureAbbreviation": obj.get("itemUnitThcContentDoseUnitOfMeasureAbbreviation"),
            "itemUnitVolume": obj.get("itemUnitVolume"),
            "itemUnitVolumeUnitOfMeasureAbbreviation": obj.get("itemUnitVolumeUnitOfMeasureAbbreviation"),
            "itemUnitWeight": obj.get("itemUnitWeight"),
            "itemUnitWeightUnitOfMeasureAbbreviation": obj.get("itemUnitWeightUnitOfMeasureAbbreviation"),
            "itemServingSize": obj.get("itemServingSize"),
            "itemSupplyDurationDays": obj.get("itemSupplyDurationDays"),
            "itemUnitQuantity": obj.get("itemUnitQuantity"),
            "itemUnitQuantityUnitOfMeasureAbbreviation": obj.get("itemUnitQuantityUnitOfMeasureAbbreviation"),
            "quantitySold": obj.get("quantitySold"),
            "unitOfMeasureId": obj.get("unitOfMeasureId"),
            "unitOfMeasureName": obj.get("unitOfMeasureName"),
            "unitOfMeasureAbbreviation": obj.get("unitOfMeasureAbbreviation"),
            "unitThcPercent": obj.get("unitThcPercent"),
            "unitThcContent": obj.get("unitThcContent"),
            "unitThcContentUnitOfMeasureId": obj.get("unitThcContentUnitOfMeasureId"),
            "unitWeight": obj.get("unitWeight"),
            "unitWeightUnitOfMeasureId": obj.get("unitWeightUnitOfMeasureId"),
            "totalPrice": obj.get("totalPrice"),
            "salesDeliveryState": obj.get("salesDeliveryState"),
            "salesDeliveryStateName": obj.get("salesDeliveryStateName"),
            "isTradeSample": obj.get("isTradeSample"),
            "isDonation": obj.get("isDonation"),
            "isTestingSample": obj.get("isTestingSample"),
            "productRequiresRemediation": obj.get("productRequiresRemediation"),
            "containsRemediatedProduct": obj.get("containsRemediatedProduct"),
            "remediationDate": obj.get("remediationDate"),
            "isArchived": obj.get("isArchived"),
            "archivedDate": obj.get("archivedDate"),
            "recordedDateTime": obj.get("recordedDateTime"),
            "recordedByUserName": obj.get("recordedByUserName"),
            "lastModified": obj.get("lastModified"),
            "invoiceNumber": obj.get("invoiceNumber"),
            "price": obj.get("price"),
            "exciseTax": obj.get("exciseTax"),
            "cityTax": obj.get("cityTax"),
            "countyTax": obj.get("countyTax"),
            "municipalTax": obj.get("municipalTax"),
            "discountAmount": obj.get("discountAmount"),
            "subTotal": obj.get("subTotal"),
            "salesTax": obj.get("salesTax"),
            "tradeSampleSaleVerified": obj.get("tradeSampleSaleVerified"),
            "recallProductSaleVerified": obj.get("recallProductSaleVerified"),
            "qrCodeDocument": obj.get("qrCodeDocument")
        })
        return _obj


