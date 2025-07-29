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

class MetrcItem(BaseModel):
    """
    MetrcItem
    """ # noqa: E501
    id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The item ID")
    hostname: Optional[StrictStr] = Field(default=None, description="The hostname this object was retrieved from")
    data_model: Optional[StrictStr] = Field(default=None, description="Name of this object's data model", alias="dataModel")
    retrieved_at: Optional[datetime] = Field(default=None, description="Timestamp of when this object was pulled from Metrc", alias="retrievedAt")
    license_number: Optional[StrictStr] = Field(default=None, description="License number used to access this object", alias="licenseNumber")
    index: Optional[StrictStr] = Field(default=None, description="Describes the current state of this object at the time it was returned from the API. This cannot be used to sort or filter.")
    facility_license_number: Optional[StrictStr] = Field(default=None, description="The facility license number", alias="facilityLicenseNumber")
    facility_name: Optional[StrictStr] = Field(default=None, description="The facility name", alias="facilityName")
    name: Optional[StrictStr] = Field(default=None, description="The item name")
    product_category_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The product category ID", alias="productCategoryId")
    product_category_name: Optional[StrictStr] = Field(default=None, description="The product category name", alias="productCategoryName")
    product_category_type_name: Optional[StrictStr] = Field(default=None, description="The product category type name", alias="productCategoryTypeName")
    expiration_date_configuration: Optional[StrictStr] = Field(default=None, description="The expiration date configuration", alias="expirationDateConfiguration")
    expiration_configuration_state: Optional[StrictStr] = Field(default=None, description="The expiration configuration state", alias="expirationConfigurationState")
    expiration_date_days_in_advance: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The number of days in advance for the expiration date", alias="expirationDateDaysInAdvance")
    sell_by_date_configuration: Optional[StrictStr] = Field(default=None, description="The sell by date configuration", alias="sellByDateConfiguration")
    sell_by_configuration_state: Optional[StrictStr] = Field(default=None, description="The sell by configuration state", alias="sellByConfigurationState")
    sell_by_date_days_in_advance: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The number of days in advance for the sell by date", alias="sellByDateDaysInAdvance")
    use_by_date_configuration: Optional[StrictStr] = Field(default=None, description="The use by date configuration", alias="useByDateConfiguration")
    use_by_configuration_state: Optional[StrictStr] = Field(default=None, description="The use by configuration state", alias="useByConfigurationState")
    use_by_date_days_in_advance: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The number of days in advance for the use by date", alias="useByDateDaysInAdvance")
    quantity_type_name: Optional[StrictStr] = Field(default=None, description="The quantity type name", alias="quantityTypeName")
    default_lab_testing_state_name: Optional[StrictStr] = Field(default=None, description="The default lab testing state name", alias="defaultLabTestingStateName")
    unit_of_measure_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit of measure ID", alias="unitOfMeasureId")
    unit_of_measure_name: Optional[StrictStr] = Field(default=None, description="The unit of measure name", alias="unitOfMeasureName")
    approval_status_name: Optional[StrictStr] = Field(default=None, description="The approval status name", alias="approvalStatusName")
    approval_status_date_time: Optional[datetime] = Field(default=None, description="The date and time of approval status", alias="approvalStatusDateTime")
    strain_name: Optional[StrictStr] = Field(default=None, description="The strain name", alias="strainName")
    item_brand_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The item brand ID", alias="itemBrandId")
    item_brand_name: Optional[StrictStr] = Field(default=None, description="The item brand name", alias="itemBrandName")
    administration_method: Optional[StrictStr] = Field(default=None, description="The method of administration", alias="administrationMethod")
    unit_cbd_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit CBD percentage", alias="unitCbdPercent")
    unit_cbd_content_dose: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit CBD content dose", alias="unitCbdContentDose")
    unit_cbd_content_dose_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, description="The unit CBD content dose unit of measure abbreviation", alias="unitCbdContentDoseUnitOfMeasureAbbreviation")
    unit_thc_percent: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit THC percentage", alias="unitThcPercent")
    unit_thc_content_unit_of_measure_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit THC content unit of measure ID", alias="unitThcContentUnitOfMeasureId")
    unit_thc_content_dose_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, description="The unit THC content dose unit of measure abbreviation", alias="unitThcContentDoseUnitOfMeasureAbbreviation")
    unit_weight: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit weight", alias="unitWeight")
    serving_size: Optional[StrictStr] = Field(default=None, description="The serving size", alias="servingSize")
    number_of_doses: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The number of doses", alias="numberOfDoses")
    unit_quantity: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit quantity", alias="unitQuantity")
    unit_quantity_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, description="The unit quantity unit of measure abbreviation", alias="unitQuantityUnitOfMeasureAbbreviation")
    public_ingredients: Optional[StrictStr] = Field(default=None, description="The public ingredients", alias="publicIngredients")
    description: Optional[StrictStr] = Field(default=None, description="The item description")
    allergens: Optional[StrictStr] = Field(default=None, description="The allergens present in the item")
    product_images: Optional[List[StrictStr]] = Field(default=None, description="A list of product images", alias="productImages")
    product_photo_description: Optional[StrictStr] = Field(default=None, description="Description of the product photo", alias="productPhotoDescription")
    label_images: Optional[List[StrictStr]] = Field(default=None, description="A list of label images", alias="labelImages")
    label_photo_description: Optional[StrictStr] = Field(default=None, description="Description of the label photo", alias="labelPhotoDescription")
    packaging_images: Optional[List[StrictStr]] = Field(default=None, description="A list of packaging images", alias="packagingImages")
    packaging_photo_description: Optional[StrictStr] = Field(default=None, description="Description of the packaging photo", alias="packagingPhotoDescription")
    product_pdf_documents: Optional[List[StrictStr]] = Field(default=None, description="A list of product PDF documents", alias="productPDFDocuments")
    is_used: Optional[StrictBool] = Field(default=None, description="Indicates if the item is used", alias="isUsed")
    is_archived: Optional[StrictBool] = Field(default=None, description="Indicates if the item is archived", alias="isArchived")
    last_modified: Optional[datetime] = Field(default=None, description="The last modified date and time", alias="lastModified")
    processing_job_category_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The processing job category ID", alias="processingJobCategoryId")
    processing_job_category_name: Optional[StrictStr] = Field(default=None, description="The processing job category name", alias="processingJobCategoryName")
    supply_duration_days: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The supply duration in days", alias="supplyDurationDays")
    unit_cbd_percent_override: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Override value for the unit CBD percentage", alias="unitCbdPercentOverride")
    unit_cbd_content: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit CBD content", alias="unitCbdContent")
    unit_cbd_content_override: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Override value for the unit CBD content", alias="unitCbdContentOverride")
    unit_cbd_content_dose_uo_mid: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit CBD content dose UoM ID", alias="unitCbdContentDoseUoMId")
    unit_cbd_content_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, description="The unit CBD content unit of measure abbreviation", alias="unitCbdContentUnitOfMeasureAbbreviation")
    unit_cbd_content_unit_of_measure_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit CBD content unit of measure ID", alias="unitCbdContentUnitOfMeasureId")
    unit_cbd_content_uo_mid: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit CBD content UoM ID", alias="unitCbdContentUoMId")
    unit_thc_content: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit THC content", alias="unitThcContent")
    unit_thc_content_override: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Override value for the unit THC content", alias="unitThcContentOverride")
    unit_thc_content_dose: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit THC content dose", alias="unitThcContentDose")
    unit_thc_content_dose_unit_of_measure_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit THC content dose unit of measure ID", alias="unitThcContentDoseUnitOfMeasureId")
    unit_thc_content_dose_uo_mid: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit THC content dose UoM ID", alias="unitThcContentDoseUoMId")
    unit_thc_content_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, description="The unit THC content unit of measure abbreviation", alias="unitThcContentUnitOfMeasureAbbreviation")
    unit_thc_content_uo_mid: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit THC content UoM ID", alias="unitThcContentUoMId")
    unit_weight_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, description="The unit weight unit of measure abbreviation", alias="unitWeightUnitOfMeasureAbbreviation")
    unit_weight_unit_of_measure_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit weight unit of measure ID", alias="unitWeightUnitOfMeasureId")
    unit_weight_uo_mid: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit weight UoM ID", alias="unitWeightUoMId")
    unit_volume: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit volume", alias="unitVolume")
    unit_volume_unit_of_measure_abbreviation: Optional[StrictStr] = Field(default=None, description="The unit volume unit of measure abbreviation", alias="unitVolumeUnitOfMeasureAbbreviation")
    unit_volume_unit_of_measure_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit volume unit of measure ID", alias="unitVolumeUnitOfMeasureId")
    unit_volume_uo_mid: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit volume UoM ID", alias="unitVolumeUoMId")
    public_ingredients_override: Optional[StrictStr] = Field(default=None, description="Override value for the public ingredients", alias="publicIngredientsOverride")
    allergens_override: Optional[StrictStr] = Field(default=None, description="Override value for the allergens present in the item", alias="allergensOverride")
    description_override: Optional[StrictStr] = Field(default=None, description="Override value for the item description", alias="descriptionOverride")
    global_product_name: Optional[StrictStr] = Field(default=None, description="The global product name", alias="globalProductName")
    product_brand_name: Optional[StrictStr] = Field(default=None, description="The product brand name", alias="productBrandName")
    administration_method_override: Optional[StrictStr] = Field(default=None, description="Override value for the method of administration", alias="administrationMethodOverride")
    unit_cbd_content_dose_unit_of_measure_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The unit CBD content dose unit of measure ID", alias="unitCbdContentDoseUnitOfMeasureId")
    strain_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The strain ID", alias="strainId")
    product_category_requires_approval: Optional[StrictBool] = Field(default=None, description="Indicates if the item's product category requires approval", alias="productCategoryRequiresApproval")
    packaging_photo_description_override: Optional[StrictStr] = Field(default=None, alias="packagingPhotoDescriptionOverride")
    packaging_photo_override: Optional[StrictStr] = Field(default=None, alias="packagingPhotoOverride")
    label_photo_description_override: Optional[StrictStr] = Field(default=None, alias="labelPhotoDescriptionOverride")
    product_photo_description_override: Optional[StrictStr] = Field(default=None, alias="productPhotoDescriptionOverride")
    brand_name: Optional[StrictStr] = Field(default=None, alias="brandName")
    product_photo_override: Optional[StrictStr] = Field(default=None, alias="productPhotoOverride")
    global_product_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="globalProductId")
    label_photo_override: Optional[StrictStr] = Field(default=None, alias="labelPhotoOverride")
    processing_job_type_id: Optional[StrictStr] = Field(default=None, alias="processingJobTypeId")
    processing_job_type_name: Optional[StrictStr] = Field(default=None, alias="processingJobTypeName")
    unit_thc_percent_override: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="unitThcPercentOverride")
    __properties: ClassVar[List[str]] = ["id", "hostname", "dataModel", "retrievedAt", "licenseNumber", "index", "facilityLicenseNumber", "facilityName", "name", "productCategoryId", "productCategoryName", "productCategoryTypeName", "expirationDateConfiguration", "expirationConfigurationState", "expirationDateDaysInAdvance", "sellByDateConfiguration", "sellByConfigurationState", "sellByDateDaysInAdvance", "useByDateConfiguration", "useByConfigurationState", "useByDateDaysInAdvance", "quantityTypeName", "defaultLabTestingStateName", "unitOfMeasureId", "unitOfMeasureName", "approvalStatusName", "approvalStatusDateTime", "strainName", "itemBrandId", "itemBrandName", "administrationMethod", "unitCbdPercent", "unitCbdContentDose", "unitCbdContentDoseUnitOfMeasureAbbreviation", "unitThcPercent", "unitThcContentUnitOfMeasureId", "unitThcContentDoseUnitOfMeasureAbbreviation", "unitWeight", "servingSize", "numberOfDoses", "unitQuantity", "unitQuantityUnitOfMeasureAbbreviation", "publicIngredients", "description", "allergens", "productImages", "productPhotoDescription", "labelImages", "labelPhotoDescription", "packagingImages", "packagingPhotoDescription", "productPDFDocuments", "isUsed", "isArchived", "lastModified", "processingJobCategoryId", "processingJobCategoryName", "supplyDurationDays", "unitCbdPercentOverride", "unitCbdContent", "unitCbdContentOverride", "unitCbdContentDoseUoMId", "unitCbdContentUnitOfMeasureAbbreviation", "unitCbdContentUnitOfMeasureId", "unitCbdContentUoMId", "unitThcContent", "unitThcContentOverride", "unitThcContentDose", "unitThcContentDoseUnitOfMeasureId", "unitThcContentDoseUoMId", "unitThcContentUnitOfMeasureAbbreviation", "unitThcContentUoMId", "unitWeightUnitOfMeasureAbbreviation", "unitWeightUnitOfMeasureId", "unitWeightUoMId", "unitVolume", "unitVolumeUnitOfMeasureAbbreviation", "unitVolumeUnitOfMeasureId", "unitVolumeUoMId", "publicIngredientsOverride", "allergensOverride", "descriptionOverride", "globalProductName", "productBrandName", "administrationMethodOverride", "unitCbdContentDoseUnitOfMeasureId", "strainId", "productCategoryRequiresApproval", "packagingPhotoDescriptionOverride", "packagingPhotoOverride", "labelPhotoDescriptionOverride", "productPhotoDescriptionOverride", "brandName", "productPhotoOverride", "globalProductId", "labelPhotoOverride", "processingJobTypeId", "processingJobTypeName", "unitThcPercentOverride"]

    @field_validator('index')
    def index_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['ACTIVE_ITEM']):
            raise ValueError("must be one of enum values ('ACTIVE_ITEM')")
        return value

    @field_validator('expiration_date_configuration')
    def expiration_date_configuration_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['Off', 'Optional']):
            raise ValueError("must be one of enum values ('Off', 'Optional')")
        return value

    @field_validator('expiration_configuration_state')
    def expiration_configuration_state_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['Off']):
            raise ValueError("must be one of enum values ('Off')")
        return value

    @field_validator('sell_by_date_configuration')
    def sell_by_date_configuration_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['Off', 'Optional']):
            raise ValueError("must be one of enum values ('Off', 'Optional')")
        return value

    @field_validator('sell_by_configuration_state')
    def sell_by_configuration_state_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['Off']):
            raise ValueError("must be one of enum values ('Off')")
        return value

    @field_validator('use_by_date_configuration')
    def use_by_date_configuration_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['Off', 'Optional']):
            raise ValueError("must be one of enum values ('Off', 'Optional')")
        return value

    @field_validator('use_by_configuration_state')
    def use_by_configuration_state_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['Off']):
            raise ValueError("must be one of enum values ('Off')")
        return value

    @field_validator('quantity_type_name')
    def quantity_type_name_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['WeightBased', 'CountBased', 'VolumeBased']):
            raise ValueError("must be one of enum values ('WeightBased', 'CountBased', 'VolumeBased')")
        return value

    @field_validator('default_lab_testing_state_name')
    def default_lab_testing_state_name_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['NotRequired', 'NotSubmitted']):
            raise ValueError("must be one of enum values ('NotRequired', 'NotSubmitted')")
        return value

    @field_validator('approval_status_name')
    def approval_status_name_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['Approved']):
            raise ValueError("must be one of enum values ('Approved')")
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
        """Create an instance of MetrcItem from a JSON string"""
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
        # set to None if facility_license_number (nullable) is None
        # and model_fields_set contains the field
        if self.facility_license_number is None and "facility_license_number" in self.model_fields_set:
            _dict['facilityLicenseNumber'] = None

        # set to None if facility_name (nullable) is None
        # and model_fields_set contains the field
        if self.facility_name is None and "facility_name" in self.model_fields_set:
            _dict['facilityName'] = None

        # set to None if expiration_date_days_in_advance (nullable) is None
        # and model_fields_set contains the field
        if self.expiration_date_days_in_advance is None and "expiration_date_days_in_advance" in self.model_fields_set:
            _dict['expirationDateDaysInAdvance'] = None

        # set to None if sell_by_date_days_in_advance (nullable) is None
        # and model_fields_set contains the field
        if self.sell_by_date_days_in_advance is None and "sell_by_date_days_in_advance" in self.model_fields_set:
            _dict['sellByDateDaysInAdvance'] = None

        # set to None if use_by_date_days_in_advance (nullable) is None
        # and model_fields_set contains the field
        if self.use_by_date_days_in_advance is None and "use_by_date_days_in_advance" in self.model_fields_set:
            _dict['useByDateDaysInAdvance'] = None

        # set to None if strain_name (nullable) is None
        # and model_fields_set contains the field
        if self.strain_name is None and "strain_name" in self.model_fields_set:
            _dict['strainName'] = None

        # set to None if item_brand_name (nullable) is None
        # and model_fields_set contains the field
        if self.item_brand_name is None and "item_brand_name" in self.model_fields_set:
            _dict['itemBrandName'] = None

        # set to None if unit_cbd_percent (nullable) is None
        # and model_fields_set contains the field
        if self.unit_cbd_percent is None and "unit_cbd_percent" in self.model_fields_set:
            _dict['unitCbdPercent'] = None

        # set to None if unit_cbd_content_dose (nullable) is None
        # and model_fields_set contains the field
        if self.unit_cbd_content_dose is None and "unit_cbd_content_dose" in self.model_fields_set:
            _dict['unitCbdContentDose'] = None

        # set to None if unit_cbd_content_dose_unit_of_measure_abbreviation (nullable) is None
        # and model_fields_set contains the field
        if self.unit_cbd_content_dose_unit_of_measure_abbreviation is None and "unit_cbd_content_dose_unit_of_measure_abbreviation" in self.model_fields_set:
            _dict['unitCbdContentDoseUnitOfMeasureAbbreviation'] = None

        # set to None if unit_thc_percent (nullable) is None
        # and model_fields_set contains the field
        if self.unit_thc_percent is None and "unit_thc_percent" in self.model_fields_set:
            _dict['unitThcPercent'] = None

        # set to None if unit_thc_content_unit_of_measure_id (nullable) is None
        # and model_fields_set contains the field
        if self.unit_thc_content_unit_of_measure_id is None and "unit_thc_content_unit_of_measure_id" in self.model_fields_set:
            _dict['unitThcContentUnitOfMeasureId'] = None

        # set to None if unit_thc_content_dose_unit_of_measure_abbreviation (nullable) is None
        # and model_fields_set contains the field
        if self.unit_thc_content_dose_unit_of_measure_abbreviation is None and "unit_thc_content_dose_unit_of_measure_abbreviation" in self.model_fields_set:
            _dict['unitThcContentDoseUnitOfMeasureAbbreviation'] = None

        # set to None if unit_weight (nullable) is None
        # and model_fields_set contains the field
        if self.unit_weight is None and "unit_weight" in self.model_fields_set:
            _dict['unitWeight'] = None

        # set to None if number_of_doses (nullable) is None
        # and model_fields_set contains the field
        if self.number_of_doses is None and "number_of_doses" in self.model_fields_set:
            _dict['numberOfDoses'] = None

        # set to None if unit_quantity (nullable) is None
        # and model_fields_set contains the field
        if self.unit_quantity is None and "unit_quantity" in self.model_fields_set:
            _dict['unitQuantity'] = None

        # set to None if unit_quantity_unit_of_measure_abbreviation (nullable) is None
        # and model_fields_set contains the field
        if self.unit_quantity_unit_of_measure_abbreviation is None and "unit_quantity_unit_of_measure_abbreviation" in self.model_fields_set:
            _dict['unitQuantityUnitOfMeasureAbbreviation'] = None

        # set to None if last_modified (nullable) is None
        # and model_fields_set contains the field
        if self.last_modified is None and "last_modified" in self.model_fields_set:
            _dict['lastModified'] = None

        # set to None if processing_job_category_id (nullable) is None
        # and model_fields_set contains the field
        if self.processing_job_category_id is None and "processing_job_category_id" in self.model_fields_set:
            _dict['processingJobCategoryId'] = None

        # set to None if processing_job_category_name (nullable) is None
        # and model_fields_set contains the field
        if self.processing_job_category_name is None and "processing_job_category_name" in self.model_fields_set:
            _dict['processingJobCategoryName'] = None

        # set to None if supply_duration_days (nullable) is None
        # and model_fields_set contains the field
        if self.supply_duration_days is None and "supply_duration_days" in self.model_fields_set:
            _dict['supplyDurationDays'] = None

        # set to None if unit_cbd_percent_override (nullable) is None
        # and model_fields_set contains the field
        if self.unit_cbd_percent_override is None and "unit_cbd_percent_override" in self.model_fields_set:
            _dict['unitCbdPercentOverride'] = None

        # set to None if unit_cbd_content (nullable) is None
        # and model_fields_set contains the field
        if self.unit_cbd_content is None and "unit_cbd_content" in self.model_fields_set:
            _dict['unitCbdContent'] = None

        # set to None if unit_cbd_content_override (nullable) is None
        # and model_fields_set contains the field
        if self.unit_cbd_content_override is None and "unit_cbd_content_override" in self.model_fields_set:
            _dict['unitCbdContentOverride'] = None

        # set to None if unit_cbd_content_dose_uo_mid (nullable) is None
        # and model_fields_set contains the field
        if self.unit_cbd_content_dose_uo_mid is None and "unit_cbd_content_dose_uo_mid" in self.model_fields_set:
            _dict['unitCbdContentDoseUoMId'] = None

        # set to None if unit_cbd_content_unit_of_measure_abbreviation (nullable) is None
        # and model_fields_set contains the field
        if self.unit_cbd_content_unit_of_measure_abbreviation is None and "unit_cbd_content_unit_of_measure_abbreviation" in self.model_fields_set:
            _dict['unitCbdContentUnitOfMeasureAbbreviation'] = None

        # set to None if unit_cbd_content_unit_of_measure_id (nullable) is None
        # and model_fields_set contains the field
        if self.unit_cbd_content_unit_of_measure_id is None and "unit_cbd_content_unit_of_measure_id" in self.model_fields_set:
            _dict['unitCbdContentUnitOfMeasureId'] = None

        # set to None if unit_cbd_content_uo_mid (nullable) is None
        # and model_fields_set contains the field
        if self.unit_cbd_content_uo_mid is None and "unit_cbd_content_uo_mid" in self.model_fields_set:
            _dict['unitCbdContentUoMId'] = None

        # set to None if unit_thc_content (nullable) is None
        # and model_fields_set contains the field
        if self.unit_thc_content is None and "unit_thc_content" in self.model_fields_set:
            _dict['unitThcContent'] = None

        # set to None if unit_thc_content_override (nullable) is None
        # and model_fields_set contains the field
        if self.unit_thc_content_override is None and "unit_thc_content_override" in self.model_fields_set:
            _dict['unitThcContentOverride'] = None

        # set to None if unit_thc_content_dose (nullable) is None
        # and model_fields_set contains the field
        if self.unit_thc_content_dose is None and "unit_thc_content_dose" in self.model_fields_set:
            _dict['unitThcContentDose'] = None

        # set to None if unit_thc_content_dose_unit_of_measure_id (nullable) is None
        # and model_fields_set contains the field
        if self.unit_thc_content_dose_unit_of_measure_id is None and "unit_thc_content_dose_unit_of_measure_id" in self.model_fields_set:
            _dict['unitThcContentDoseUnitOfMeasureId'] = None

        # set to None if unit_thc_content_dose_uo_mid (nullable) is None
        # and model_fields_set contains the field
        if self.unit_thc_content_dose_uo_mid is None and "unit_thc_content_dose_uo_mid" in self.model_fields_set:
            _dict['unitThcContentDoseUoMId'] = None

        # set to None if unit_thc_content_unit_of_measure_abbreviation (nullable) is None
        # and model_fields_set contains the field
        if self.unit_thc_content_unit_of_measure_abbreviation is None and "unit_thc_content_unit_of_measure_abbreviation" in self.model_fields_set:
            _dict['unitThcContentUnitOfMeasureAbbreviation'] = None

        # set to None if unit_thc_content_uo_mid (nullable) is None
        # and model_fields_set contains the field
        if self.unit_thc_content_uo_mid is None and "unit_thc_content_uo_mid" in self.model_fields_set:
            _dict['unitThcContentUoMId'] = None

        # set to None if unit_weight_unit_of_measure_abbreviation (nullable) is None
        # and model_fields_set contains the field
        if self.unit_weight_unit_of_measure_abbreviation is None and "unit_weight_unit_of_measure_abbreviation" in self.model_fields_set:
            _dict['unitWeightUnitOfMeasureAbbreviation'] = None

        # set to None if unit_weight_unit_of_measure_id (nullable) is None
        # and model_fields_set contains the field
        if self.unit_weight_unit_of_measure_id is None and "unit_weight_unit_of_measure_id" in self.model_fields_set:
            _dict['unitWeightUnitOfMeasureId'] = None

        # set to None if unit_weight_uo_mid (nullable) is None
        # and model_fields_set contains the field
        if self.unit_weight_uo_mid is None and "unit_weight_uo_mid" in self.model_fields_set:
            _dict['unitWeightUoMId'] = None

        # set to None if unit_volume (nullable) is None
        # and model_fields_set contains the field
        if self.unit_volume is None and "unit_volume" in self.model_fields_set:
            _dict['unitVolume'] = None

        # set to None if unit_volume_unit_of_measure_abbreviation (nullable) is None
        # and model_fields_set contains the field
        if self.unit_volume_unit_of_measure_abbreviation is None and "unit_volume_unit_of_measure_abbreviation" in self.model_fields_set:
            _dict['unitVolumeUnitOfMeasureAbbreviation'] = None

        # set to None if unit_volume_unit_of_measure_id (nullable) is None
        # and model_fields_set contains the field
        if self.unit_volume_unit_of_measure_id is None and "unit_volume_unit_of_measure_id" in self.model_fields_set:
            _dict['unitVolumeUnitOfMeasureId'] = None

        # set to None if unit_volume_uo_mid (nullable) is None
        # and model_fields_set contains the field
        if self.unit_volume_uo_mid is None and "unit_volume_uo_mid" in self.model_fields_set:
            _dict['unitVolumeUoMId'] = None

        # set to None if public_ingredients_override (nullable) is None
        # and model_fields_set contains the field
        if self.public_ingredients_override is None and "public_ingredients_override" in self.model_fields_set:
            _dict['publicIngredientsOverride'] = None

        # set to None if allergens_override (nullable) is None
        # and model_fields_set contains the field
        if self.allergens_override is None and "allergens_override" in self.model_fields_set:
            _dict['allergensOverride'] = None

        # set to None if description_override (nullable) is None
        # and model_fields_set contains the field
        if self.description_override is None and "description_override" in self.model_fields_set:
            _dict['descriptionOverride'] = None

        # set to None if global_product_name (nullable) is None
        # and model_fields_set contains the field
        if self.global_product_name is None and "global_product_name" in self.model_fields_set:
            _dict['globalProductName'] = None

        # set to None if product_brand_name (nullable) is None
        # and model_fields_set contains the field
        if self.product_brand_name is None and "product_brand_name" in self.model_fields_set:
            _dict['productBrandName'] = None

        # set to None if administration_method_override (nullable) is None
        # and model_fields_set contains the field
        if self.administration_method_override is None and "administration_method_override" in self.model_fields_set:
            _dict['administrationMethodOverride'] = None

        # set to None if unit_cbd_content_dose_unit_of_measure_id (nullable) is None
        # and model_fields_set contains the field
        if self.unit_cbd_content_dose_unit_of_measure_id is None and "unit_cbd_content_dose_unit_of_measure_id" in self.model_fields_set:
            _dict['unitCbdContentDoseUnitOfMeasureId'] = None

        # set to None if packaging_photo_description_override (nullable) is None
        # and model_fields_set contains the field
        if self.packaging_photo_description_override is None and "packaging_photo_description_override" in self.model_fields_set:
            _dict['packagingPhotoDescriptionOverride'] = None

        # set to None if packaging_photo_override (nullable) is None
        # and model_fields_set contains the field
        if self.packaging_photo_override is None and "packaging_photo_override" in self.model_fields_set:
            _dict['packagingPhotoOverride'] = None

        # set to None if label_photo_description_override (nullable) is None
        # and model_fields_set contains the field
        if self.label_photo_description_override is None and "label_photo_description_override" in self.model_fields_set:
            _dict['labelPhotoDescriptionOverride'] = None

        # set to None if product_photo_description_override (nullable) is None
        # and model_fields_set contains the field
        if self.product_photo_description_override is None and "product_photo_description_override" in self.model_fields_set:
            _dict['productPhotoDescriptionOverride'] = None

        # set to None if brand_name (nullable) is None
        # and model_fields_set contains the field
        if self.brand_name is None and "brand_name" in self.model_fields_set:
            _dict['brandName'] = None

        # set to None if product_photo_override (nullable) is None
        # and model_fields_set contains the field
        if self.product_photo_override is None and "product_photo_override" in self.model_fields_set:
            _dict['productPhotoOverride'] = None

        # set to None if global_product_id (nullable) is None
        # and model_fields_set contains the field
        if self.global_product_id is None and "global_product_id" in self.model_fields_set:
            _dict['globalProductId'] = None

        # set to None if label_photo_override (nullable) is None
        # and model_fields_set contains the field
        if self.label_photo_override is None and "label_photo_override" in self.model_fields_set:
            _dict['labelPhotoOverride'] = None

        # set to None if processing_job_type_id (nullable) is None
        # and model_fields_set contains the field
        if self.processing_job_type_id is None and "processing_job_type_id" in self.model_fields_set:
            _dict['processingJobTypeId'] = None

        # set to None if processing_job_type_name (nullable) is None
        # and model_fields_set contains the field
        if self.processing_job_type_name is None and "processing_job_type_name" in self.model_fields_set:
            _dict['processingJobTypeName'] = None

        # set to None if unit_thc_percent_override (nullable) is None
        # and model_fields_set contains the field
        if self.unit_thc_percent_override is None and "unit_thc_percent_override" in self.model_fields_set:
            _dict['unitThcPercentOverride'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of MetrcItem from a dict"""
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
            "facilityLicenseNumber": obj.get("facilityLicenseNumber"),
            "facilityName": obj.get("facilityName"),
            "name": obj.get("name"),
            "productCategoryId": obj.get("productCategoryId"),
            "productCategoryName": obj.get("productCategoryName"),
            "productCategoryTypeName": obj.get("productCategoryTypeName"),
            "expirationDateConfiguration": obj.get("expirationDateConfiguration"),
            "expirationConfigurationState": obj.get("expirationConfigurationState"),
            "expirationDateDaysInAdvance": obj.get("expirationDateDaysInAdvance"),
            "sellByDateConfiguration": obj.get("sellByDateConfiguration"),
            "sellByConfigurationState": obj.get("sellByConfigurationState"),
            "sellByDateDaysInAdvance": obj.get("sellByDateDaysInAdvance"),
            "useByDateConfiguration": obj.get("useByDateConfiguration"),
            "useByConfigurationState": obj.get("useByConfigurationState"),
            "useByDateDaysInAdvance": obj.get("useByDateDaysInAdvance"),
            "quantityTypeName": obj.get("quantityTypeName"),
            "defaultLabTestingStateName": obj.get("defaultLabTestingStateName"),
            "unitOfMeasureId": obj.get("unitOfMeasureId"),
            "unitOfMeasureName": obj.get("unitOfMeasureName"),
            "approvalStatusName": obj.get("approvalStatusName"),
            "approvalStatusDateTime": obj.get("approvalStatusDateTime"),
            "strainName": obj.get("strainName"),
            "itemBrandId": obj.get("itemBrandId"),
            "itemBrandName": obj.get("itemBrandName"),
            "administrationMethod": obj.get("administrationMethod"),
            "unitCbdPercent": obj.get("unitCbdPercent"),
            "unitCbdContentDose": obj.get("unitCbdContentDose"),
            "unitCbdContentDoseUnitOfMeasureAbbreviation": obj.get("unitCbdContentDoseUnitOfMeasureAbbreviation"),
            "unitThcPercent": obj.get("unitThcPercent"),
            "unitThcContentUnitOfMeasureId": obj.get("unitThcContentUnitOfMeasureId"),
            "unitThcContentDoseUnitOfMeasureAbbreviation": obj.get("unitThcContentDoseUnitOfMeasureAbbreviation"),
            "unitWeight": obj.get("unitWeight"),
            "servingSize": obj.get("servingSize"),
            "numberOfDoses": obj.get("numberOfDoses"),
            "unitQuantity": obj.get("unitQuantity"),
            "unitQuantityUnitOfMeasureAbbreviation": obj.get("unitQuantityUnitOfMeasureAbbreviation"),
            "publicIngredients": obj.get("publicIngredients"),
            "description": obj.get("description"),
            "allergens": obj.get("allergens"),
            "productImages": obj.get("productImages"),
            "productPhotoDescription": obj.get("productPhotoDescription"),
            "labelImages": obj.get("labelImages"),
            "labelPhotoDescription": obj.get("labelPhotoDescription"),
            "packagingImages": obj.get("packagingImages"),
            "packagingPhotoDescription": obj.get("packagingPhotoDescription"),
            "productPDFDocuments": obj.get("productPDFDocuments"),
            "isUsed": obj.get("isUsed"),
            "isArchived": obj.get("isArchived"),
            "lastModified": obj.get("lastModified"),
            "processingJobCategoryId": obj.get("processingJobCategoryId"),
            "processingJobCategoryName": obj.get("processingJobCategoryName"),
            "supplyDurationDays": obj.get("supplyDurationDays"),
            "unitCbdPercentOverride": obj.get("unitCbdPercentOverride"),
            "unitCbdContent": obj.get("unitCbdContent"),
            "unitCbdContentOverride": obj.get("unitCbdContentOverride"),
            "unitCbdContentDoseUoMId": obj.get("unitCbdContentDoseUoMId"),
            "unitCbdContentUnitOfMeasureAbbreviation": obj.get("unitCbdContentUnitOfMeasureAbbreviation"),
            "unitCbdContentUnitOfMeasureId": obj.get("unitCbdContentUnitOfMeasureId"),
            "unitCbdContentUoMId": obj.get("unitCbdContentUoMId"),
            "unitThcContent": obj.get("unitThcContent"),
            "unitThcContentOverride": obj.get("unitThcContentOverride"),
            "unitThcContentDose": obj.get("unitThcContentDose"),
            "unitThcContentDoseUnitOfMeasureId": obj.get("unitThcContentDoseUnitOfMeasureId"),
            "unitThcContentDoseUoMId": obj.get("unitThcContentDoseUoMId"),
            "unitThcContentUnitOfMeasureAbbreviation": obj.get("unitThcContentUnitOfMeasureAbbreviation"),
            "unitThcContentUoMId": obj.get("unitThcContentUoMId"),
            "unitWeightUnitOfMeasureAbbreviation": obj.get("unitWeightUnitOfMeasureAbbreviation"),
            "unitWeightUnitOfMeasureId": obj.get("unitWeightUnitOfMeasureId"),
            "unitWeightUoMId": obj.get("unitWeightUoMId"),
            "unitVolume": obj.get("unitVolume"),
            "unitVolumeUnitOfMeasureAbbreviation": obj.get("unitVolumeUnitOfMeasureAbbreviation"),
            "unitVolumeUnitOfMeasureId": obj.get("unitVolumeUnitOfMeasureId"),
            "unitVolumeUoMId": obj.get("unitVolumeUoMId"),
            "publicIngredientsOverride": obj.get("publicIngredientsOverride"),
            "allergensOverride": obj.get("allergensOverride"),
            "descriptionOverride": obj.get("descriptionOverride"),
            "globalProductName": obj.get("globalProductName"),
            "productBrandName": obj.get("productBrandName"),
            "administrationMethodOverride": obj.get("administrationMethodOverride"),
            "unitCbdContentDoseUnitOfMeasureId": obj.get("unitCbdContentDoseUnitOfMeasureId"),
            "strainId": obj.get("strainId"),
            "productCategoryRequiresApproval": obj.get("productCategoryRequiresApproval"),
            "packagingPhotoDescriptionOverride": obj.get("packagingPhotoDescriptionOverride"),
            "packagingPhotoOverride": obj.get("packagingPhotoOverride"),
            "labelPhotoDescriptionOverride": obj.get("labelPhotoDescriptionOverride"),
            "productPhotoDescriptionOverride": obj.get("productPhotoDescriptionOverride"),
            "brandName": obj.get("brandName"),
            "productPhotoOverride": obj.get("productPhotoOverride"),
            "globalProductId": obj.get("globalProductId"),
            "labelPhotoOverride": obj.get("labelPhotoOverride"),
            "processingJobTypeId": obj.get("processingJobTypeId"),
            "processingJobTypeName": obj.get("processingJobTypeName"),
            "unitThcPercentOverride": obj.get("unitThcPercentOverride")
        })
        return _obj


