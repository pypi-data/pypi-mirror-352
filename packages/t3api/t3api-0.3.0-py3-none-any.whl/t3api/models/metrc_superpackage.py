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
from t3api.models.metrc_history import MetrcHistory
from t3api.models.metrc_item import MetrcItem
from t3api.models.metrc_package_lab_result_batch import MetrcPackageLabResultBatch
from t3api.models.metrc_package_source_harvest import MetrcPackageSourceHarvest
from t3api.models.metrc_superpackage_all_of_metadata import MetrcSuperpackageAllOfMetadata
from t3api.models.unit_of_measure_abbreviation import UnitOfMeasureAbbreviation
from typing import Optional, Set
from typing_extensions import Self

class MetrcSuperpackage(BaseModel):
    """
    MetrcSuperpackage
    """ # noqa: E501
    id: Optional[StrictInt] = Field(default=None, description="The unique identifier for the package.")
    hostname: Optional[StrictStr] = Field(default=None, description="The hostname this object was retrieved from")
    data_model: Optional[StrictStr] = Field(default=None, description="Name of this object's data model", alias="dataModel")
    retrieved_at: Optional[datetime] = Field(default=None, description="Timestamp of when this object was pulled from Metrc", alias="retrievedAt")
    license_number: Optional[StrictStr] = Field(default=None, description="License number used to access this object", alias="licenseNumber")
    index: Optional[StrictStr] = Field(default=None, description="The current state of the package, such as ACTIVE, ONHOLD, INACTIVE, or INTRANSIT.")
    archived_date: Optional[datetime] = Field(default=None, description="The date and time when the package was archived, if applicable.", alias="archivedDate")
    contains_remediated_product: Optional[StrictBool] = Field(default=None, description="Indicates if the package contains remediated product.", alias="containsRemediatedProduct")
    donation_facility_license_number: Optional[StrictStr] = Field(default=None, description="The license number of the facility where the donation occurred, if applicable.", alias="donationFacilityLicenseNumber")
    donation_facility_name: Optional[StrictStr] = Field(default=None, description="The name of the facility where the donation occurred, if applicable.", alias="donationFacilityName")
    facility_license_number: Optional[StrictStr] = Field(default=None, description="The license number of the facility associated with the package.", alias="facilityLicenseNumber")
    facility_name: Optional[StrictStr] = Field(default=None, description="The name of the facility associated with the package.", alias="facilityName")
    finished_date: Optional[datetime] = Field(default=None, description="The date and time when the package was finished, if applicable.", alias="finishedDate")
    initial_lab_testing_state: Optional[StrictStr] = Field(default=None, description="The initial state of lab testing for the package, such as NotRequired, TestPassed, or NotSubmitted.", alias="initialLabTestingState")
    is_archived: Optional[StrictBool] = Field(default=None, description="Indicates if the package is archived.", alias="isArchived")
    is_donation: Optional[StrictBool] = Field(default=None, description="Indicates if the package was a donation.", alias="isDonation")
    is_donation_persistent: Optional[StrictBool] = Field(default=None, description="Indicates if the donation status of the package is persistent.", alias="isDonationPersistent")
    is_finished: Optional[StrictBool] = Field(default=None, description="Indicates if the package is marked as finished.", alias="isFinished")
    is_in_transit: Optional[StrictBool] = Field(default=None, description="Indicates if the package is currently in transit.", alias="isInTransit")
    is_on_hold: Optional[StrictBool] = Field(default=None, description="Indicates if the package is on hold.", alias="isOnHold")
    is_process_validation_testing_sample: Optional[StrictBool] = Field(default=None, description="Indicates if the package is a sample for process validation testing.", alias="isProcessValidationTestingSample")
    is_production_batch: Optional[StrictBool] = Field(default=None, description="Indicates if the package is part of a production batch.", alias="isProductionBatch")
    is_testing_sample: Optional[StrictBool] = Field(default=None, description="Indicates if the package is a testing sample.", alias="isTestingSample")
    is_trade_sample: Optional[StrictBool] = Field(default=None, description="Indicates if the package is a trade sample.", alias="isTradeSample")
    is_trade_sample_persistent: Optional[StrictBool] = Field(default=None, description="Indicates if the trade sample status of the package is persistent.", alias="isTradeSamplePersistent")
    item: Optional[MetrcItem] = None
    item_from_facility_license_number: Optional[StrictStr] = Field(default=None, description="The license number of the facility from which the item originated.", alias="itemFromFacilityLicenseNumber")
    item_from_facility_name: Optional[StrictStr] = Field(default=None, description="The name of the facility from which the item originated.", alias="itemFromFacilityName")
    lab_testing_state_date: Optional[datetime] = Field(default=None, description="The date when the lab testing state was last updated.", alias="labTestingStateDate")
    lab_testing_state_name: Optional[StrictStr] = Field(default=None, description="The current state of lab testing for the package.", alias="labTestingStateName")
    lab_testing_recorded_date: Optional[datetime] = Field(default=None, description="The date and time when the lab testing results were recorded.", alias="labTestingRecordedDate")
    lab_testing_performed_date: Optional[datetime] = Field(default=None, description="The date and time when the lab testing was performed.", alias="labTestingPerformedDate")
    lab_test_stage_id: Optional[StrictInt] = Field(default=None, description="The identifier for the stage of the lab test, if applicable.", alias="labTestStageId")
    lab_test_result_expiration_date_time: Optional[datetime] = Field(default=None, description="The expiration date and time of the lab test result, if applicable.", alias="labTestResultExpirationDateTime")
    label: Optional[StrictStr] = Field(default=None, description="The label identifier for the package.")
    last_modified: Optional[datetime] = Field(default=None, description="The date and time when the package details were last modified.", alias="lastModified")
    location_name: Optional[StrictStr] = Field(default=None, description="The name of the location where the package is stored.", alias="locationName")
    sublocation_name: Optional[StrictStr] = Field(default=None, alias="sublocationName")
    location_type_name: Optional[StrictStr] = Field(default=None, description="The type of location where the package is stored.", alias="locationTypeName")
    multi_harvest: Optional[StrictBool] = Field(default=None, description="Indicates if the package contains material from multiple harvests.", alias="multiHarvest")
    multi_package: Optional[StrictBool] = Field(default=None, description="Indicates if the package is part of multiple packages.", alias="multiPackage")
    multi_production_batch: Optional[StrictBool] = Field(default=None, description="Indicates if the package is part of multiple production batches.", alias="multiProductionBatch")
    note: Optional[StrictStr] = Field(default=None, description="Additional notes or comments about the package.")
    package_type: Optional[StrictStr] = Field(default=None, description="The type of package, such as ImmaturePlant or Product.", alias="packageType")
    packaged_by_facility_license_number: Optional[StrictStr] = Field(default=None, description="The license number of the facility where the package was created.", alias="packagedByFacilityLicenseNumber")
    packaged_by_facility_name: Optional[StrictStr] = Field(default=None, description="The name of the facility where the package was created.", alias="packagedByFacilityName")
    packaged_date: Optional[datetime] = Field(default=None, description="The date when the package was created.", alias="packagedDate")
    patient_license_number: Optional[StrictStr] = Field(default=None, description="The license number of the patient, if applicable.", alias="patientLicenseNumber")
    product_requires_remediation: Optional[StrictBool] = Field(default=None, description="Indicates if the product in the package requires remediation.", alias="productRequiresRemediation")
    production_batch_number: Optional[StrictStr] = Field(default=None, description="The number of the production batch associated with the package.", alias="productionBatchNumber")
    quantity: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The quantity of the product in the package.")
    received_date_time: Optional[datetime] = Field(default=None, description="The date and time when the package was received, if applicable.", alias="receivedDateTime")
    received_from_facility_license_number: Optional[StrictStr] = Field(default=None, description="The license number of the facility from which the package was received, if applicable.", alias="receivedFromFacilityLicenseNumber")
    received_from_facility_name: Optional[StrictStr] = Field(default=None, description="The name of the facility from which the package was received, if applicable.", alias="receivedFromFacilityName")
    received_from_manifest_number: Optional[StrictStr] = Field(default=None, description="The manifest number associated with the received package, if applicable.", alias="receivedFromManifestNumber")
    remediation_date: Optional[datetime] = Field(default=None, description="The date when the product in the package was remediated, if applicable.", alias="remediationDate")
    source_harvest_names: Optional[StrictStr] = Field(default=None, description="The names of the harvests from which the package was created.", alias="sourceHarvestNames")
    source_package_is_donation: Optional[StrictBool] = Field(default=None, description="Indicates if the source package was a donation.", alias="sourcePackageIsDonation")
    source_package_is_trade_sample: Optional[StrictBool] = Field(default=None, description="Indicates if the source package was a trade sample.", alias="sourcePackageIsTradeSample")
    source_package_labels: Optional[StrictStr] = Field(default=None, description="The labels of the source packages used to create the current package.", alias="sourcePackageLabels")
    source_production_batch_numbers: Optional[StrictStr] = Field(default=None, description="The numbers of the production batches from which the package was created.", alias="sourceProductionBatchNumbers")
    trade_sample_facility_name: Optional[StrictStr] = Field(default=None, description="The name of the facility where the trade sample was created, if applicable.", alias="tradeSampleFacilityName")
    trade_sample_facility_license_number: Optional[StrictStr] = Field(default=None, description="The license number of the facility where the trade sample was created, if applicable.", alias="tradeSampleFacilityLicenseNumber")
    transfer_manifest_number: Optional[StrictStr] = Field(default=None, description="The manifest number associated with the transfer of the package.", alias="transferManifestNumber")
    unit_of_measure_abbreviation: Optional[UnitOfMeasureAbbreviation] = Field(default=None, alias="unitOfMeasureAbbreviation")
    unit_of_measure_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The ID of the unit of measure used for the package quantity.", alias="unitOfMeasureId")
    unit_of_measure_quantity_type: Optional[StrictStr] = Field(default=None, description="The type of quantity measurement used, such as WeightBased, CountBased, or VolumeBased.", alias="unitOfMeasureQuantityType")
    source_harvest_count: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The number of harvests from which the package was created.", alias="sourceHarvestCount")
    source_package_count: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The number of source packages used to create the current package.", alias="sourcePackageCount")
    source_processing_job_count: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The number of processing jobs involved in creating the package.", alias="sourceProcessingJobCount")
    source_processing_job_numbers: Optional[StrictStr] = Field(default=None, description="The numbers of the processing jobs involved in creating the package.", alias="sourceProcessingJobNumbers")
    source_processing_job_names: Optional[StrictStr] = Field(default=None, description="The names of the processing jobs involved in creating the package.", alias="sourceProcessingJobNames")
    multi_processing_job: Optional[StrictBool] = Field(default=None, description="Indicates if multiple processing jobs were involved in creating the package.", alias="multiProcessingJob")
    expiration_date: Optional[datetime] = Field(default=None, description="The expiration date of the product in the package, if applicable.", alias="expirationDate")
    sell_by_date: Optional[datetime] = Field(default=None, description="The sell-by date of the product in the package, if applicable.", alias="sellByDate")
    use_by_date: Optional[datetime] = Field(default=None, description="The use-by date of the product in the package, if applicable.", alias="useByDate")
    lab_test_result_document_file_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The file ID of the lab test result document, if available.", alias="labTestResultDocumentFileId")
    is_on_retailer_delivery: Optional[StrictBool] = Field(default=None, description="Indicates if the package is on a retailer delivery.", alias="isOnRetailerDelivery")
    package_for_product_destruction: Optional[StrictBool] = Field(default=None, description="Indicates if the package is intended for product destruction.", alias="packageForProductDestruction")
    has_partial: Optional[StrictBool] = Field(default=None, description="Indicates if the package has partial status.", alias="hasPartial")
    is_partial: Optional[StrictBool] = Field(default=None, description="Indicates if the package is a partial package.", alias="isPartial")
    in_transit_status: Optional[StrictStr] = Field(default=None, description="The current transit status of the package.", alias="inTransitStatus")
    processing_job_type_id: Optional[StrictInt] = Field(default=None, description="The identifier for the type of processing job, if applicable.", alias="processingJobTypeId")
    is_on_recall: Optional[StrictBool] = Field(default=None, alias="isOnRecall")
    decontamination_date: Optional[StrictStr] = Field(default=None, alias="decontaminationDate")
    contains_decontaminated_product: Optional[StrictBool] = Field(default=None, alias="containsDecontaminatedProduct")
    product_requires_decontamination: Optional[StrictBool] = Field(default=None, alias="productRequiresDecontamination")
    product_label: Optional[StrictStr] = Field(default=None, alias="productLabel")
    lab_test_stage: Optional[StrictStr] = Field(default=None, alias="labTestStage")
    external_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="externalId")
    metadata: Optional[MetrcSuperpackageAllOfMetadata] = None
    source_harvests: Optional[List[MetrcPackageSourceHarvest]] = Field(default=None, description="A list of this package's source harvests", alias="sourceHarvests")
    lab_result_batches: Optional[List[MetrcPackageLabResultBatch]] = Field(default=None, description="A list of this package's lab result batches", alias="labResultBatches")
    history: Optional[List[MetrcHistory]] = Field(default=None, description="A list of this package's history")
    __properties: ClassVar[List[str]] = ["id", "hostname", "dataModel", "retrievedAt", "licenseNumber", "index", "archivedDate", "containsRemediatedProduct", "donationFacilityLicenseNumber", "donationFacilityName", "facilityLicenseNumber", "facilityName", "finishedDate", "initialLabTestingState", "isArchived", "isDonation", "isDonationPersistent", "isFinished", "isInTransit", "isOnHold", "isProcessValidationTestingSample", "isProductionBatch", "isTestingSample", "isTradeSample", "isTradeSamplePersistent", "item", "itemFromFacilityLicenseNumber", "itemFromFacilityName", "labTestingStateDate", "labTestingStateName", "labTestingRecordedDate", "labTestingPerformedDate", "labTestStageId", "labTestResultExpirationDateTime", "label", "lastModified", "locationName", "sublocationName", "locationTypeName", "multiHarvest", "multiPackage", "multiProductionBatch", "note", "packageType", "packagedByFacilityLicenseNumber", "packagedByFacilityName", "packagedDate", "patientLicenseNumber", "productRequiresRemediation", "productionBatchNumber", "quantity", "receivedDateTime", "receivedFromFacilityLicenseNumber", "receivedFromFacilityName", "receivedFromManifestNumber", "remediationDate", "sourceHarvestNames", "sourcePackageIsDonation", "sourcePackageIsTradeSample", "sourcePackageLabels", "sourceProductionBatchNumbers", "tradeSampleFacilityName", "tradeSampleFacilityLicenseNumber", "transferManifestNumber", "unitOfMeasureAbbreviation", "unitOfMeasureId", "unitOfMeasureQuantityType", "sourceHarvestCount", "sourcePackageCount", "sourceProcessingJobCount", "sourceProcessingJobNumbers", "sourceProcessingJobNames", "multiProcessingJob", "expirationDate", "sellByDate", "useByDate", "labTestResultDocumentFileId", "isOnRetailerDelivery", "packageForProductDestruction", "hasPartial", "isPartial", "inTransitStatus", "processingJobTypeId", "isOnRecall", "decontaminationDate", "containsDecontaminatedProduct", "productRequiresDecontamination", "productLabel", "labTestStage", "externalId", "metadata", "sourceHarvests", "labResultBatches", "history"]

    @field_validator('index')
    def index_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['ACTIVE_PACKAGE', 'ONHOLD_PACKAGE', 'INACTIVE_PACKAGE', 'INTRANSIT_PACKAGE']):
            raise ValueError("must be one of enum values ('ACTIVE_PACKAGE', 'ONHOLD_PACKAGE', 'INACTIVE_PACKAGE', 'INTRANSIT_PACKAGE')")
        return value

    @field_validator('initial_lab_testing_state')
    def initial_lab_testing_state_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['NotRequired', 'TestPassed', 'NotSubmitted']):
            raise ValueError("must be one of enum values ('NotRequired', 'TestPassed', 'NotSubmitted')")
        return value

    @field_validator('package_type')
    def package_type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['ImmaturePlant', 'Product']):
            raise ValueError("must be one of enum values ('ImmaturePlant', 'Product')")
        return value

    @field_validator('unit_of_measure_quantity_type')
    def unit_of_measure_quantity_type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['WeightBased', 'CountBased', 'VolumeBased']):
            raise ValueError("must be one of enum values ('WeightBased', 'CountBased', 'VolumeBased')")
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
        """Create an instance of MetrcSuperpackage from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of item
        if self.item:
            _dict['item'] = self.item.to_dict()
        # override the default output from pydantic by calling `to_dict()` of metadata
        if self.metadata:
            _dict['metadata'] = self.metadata.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in source_harvests (list)
        _items = []
        if self.source_harvests:
            for _item_source_harvests in self.source_harvests:
                if _item_source_harvests:
                    _items.append(_item_source_harvests.to_dict())
            _dict['sourceHarvests'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in lab_result_batches (list)
        _items = []
        if self.lab_result_batches:
            for _item_lab_result_batches in self.lab_result_batches:
                if _item_lab_result_batches:
                    _items.append(_item_lab_result_batches.to_dict())
            _dict['labResultBatches'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in history (list)
        _items = []
        if self.history:
            for _item_history in self.history:
                if _item_history:
                    _items.append(_item_history.to_dict())
            _dict['history'] = _items
        # set to None if archived_date (nullable) is None
        # and model_fields_set contains the field
        if self.archived_date is None and "archived_date" in self.model_fields_set:
            _dict['archivedDate'] = None

        # set to None if donation_facility_license_number (nullable) is None
        # and model_fields_set contains the field
        if self.donation_facility_license_number is None and "donation_facility_license_number" in self.model_fields_set:
            _dict['donationFacilityLicenseNumber'] = None

        # set to None if donation_facility_name (nullable) is None
        # and model_fields_set contains the field
        if self.donation_facility_name is None and "donation_facility_name" in self.model_fields_set:
            _dict['donationFacilityName'] = None

        # set to None if facility_license_number (nullable) is None
        # and model_fields_set contains the field
        if self.facility_license_number is None and "facility_license_number" in self.model_fields_set:
            _dict['facilityLicenseNumber'] = None

        # set to None if facility_name (nullable) is None
        # and model_fields_set contains the field
        if self.facility_name is None and "facility_name" in self.model_fields_set:
            _dict['facilityName'] = None

        # set to None if finished_date (nullable) is None
        # and model_fields_set contains the field
        if self.finished_date is None and "finished_date" in self.model_fields_set:
            _dict['finishedDate'] = None

        # set to None if lab_testing_performed_date (nullable) is None
        # and model_fields_set contains the field
        if self.lab_testing_performed_date is None and "lab_testing_performed_date" in self.model_fields_set:
            _dict['labTestingPerformedDate'] = None

        # set to None if lab_test_stage_id (nullable) is None
        # and model_fields_set contains the field
        if self.lab_test_stage_id is None and "lab_test_stage_id" in self.model_fields_set:
            _dict['labTestStageId'] = None

        # set to None if lab_test_result_expiration_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.lab_test_result_expiration_date_time is None and "lab_test_result_expiration_date_time" in self.model_fields_set:
            _dict['labTestResultExpirationDateTime'] = None

        # set to None if location_name (nullable) is None
        # and model_fields_set contains the field
        if self.location_name is None and "location_name" in self.model_fields_set:
            _dict['locationName'] = None

        # set to None if sublocation_name (nullable) is None
        # and model_fields_set contains the field
        if self.sublocation_name is None and "sublocation_name" in self.model_fields_set:
            _dict['sublocationName'] = None

        # set to None if location_type_name (nullable) is None
        # and model_fields_set contains the field
        if self.location_type_name is None and "location_type_name" in self.model_fields_set:
            _dict['locationTypeName'] = None

        # set to None if received_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.received_date_time is None and "received_date_time" in self.model_fields_set:
            _dict['receivedDateTime'] = None

        # set to None if received_from_facility_license_number (nullable) is None
        # and model_fields_set contains the field
        if self.received_from_facility_license_number is None and "received_from_facility_license_number" in self.model_fields_set:
            _dict['receivedFromFacilityLicenseNumber'] = None

        # set to None if received_from_facility_name (nullable) is None
        # and model_fields_set contains the field
        if self.received_from_facility_name is None and "received_from_facility_name" in self.model_fields_set:
            _dict['receivedFromFacilityName'] = None

        # set to None if received_from_manifest_number (nullable) is None
        # and model_fields_set contains the field
        if self.received_from_manifest_number is None and "received_from_manifest_number" in self.model_fields_set:
            _dict['receivedFromManifestNumber'] = None

        # set to None if remediation_date (nullable) is None
        # and model_fields_set contains the field
        if self.remediation_date is None and "remediation_date" in self.model_fields_set:
            _dict['remediationDate'] = None

        # set to None if trade_sample_facility_name (nullable) is None
        # and model_fields_set contains the field
        if self.trade_sample_facility_name is None and "trade_sample_facility_name" in self.model_fields_set:
            _dict['tradeSampleFacilityName'] = None

        # set to None if trade_sample_facility_license_number (nullable) is None
        # and model_fields_set contains the field
        if self.trade_sample_facility_license_number is None and "trade_sample_facility_license_number" in self.model_fields_set:
            _dict['tradeSampleFacilityLicenseNumber'] = None

        # set to None if expiration_date (nullable) is None
        # and model_fields_set contains the field
        if self.expiration_date is None and "expiration_date" in self.model_fields_set:
            _dict['expirationDate'] = None

        # set to None if sell_by_date (nullable) is None
        # and model_fields_set contains the field
        if self.sell_by_date is None and "sell_by_date" in self.model_fields_set:
            _dict['sellByDate'] = None

        # set to None if use_by_date (nullable) is None
        # and model_fields_set contains the field
        if self.use_by_date is None and "use_by_date" in self.model_fields_set:
            _dict['useByDate'] = None

        # set to None if lab_test_result_document_file_id (nullable) is None
        # and model_fields_set contains the field
        if self.lab_test_result_document_file_id is None and "lab_test_result_document_file_id" in self.model_fields_set:
            _dict['labTestResultDocumentFileId'] = None

        # set to None if package_for_product_destruction (nullable) is None
        # and model_fields_set contains the field
        if self.package_for_product_destruction is None and "package_for_product_destruction" in self.model_fields_set:
            _dict['packageForProductDestruction'] = None

        # set to None if processing_job_type_id (nullable) is None
        # and model_fields_set contains the field
        if self.processing_job_type_id is None and "processing_job_type_id" in self.model_fields_set:
            _dict['processingJobTypeId'] = None

        # set to None if decontamination_date (nullable) is None
        # and model_fields_set contains the field
        if self.decontamination_date is None and "decontamination_date" in self.model_fields_set:
            _dict['decontaminationDate'] = None

        # set to None if product_label (nullable) is None
        # and model_fields_set contains the field
        if self.product_label is None and "product_label" in self.model_fields_set:
            _dict['productLabel'] = None

        # set to None if lab_test_stage (nullable) is None
        # and model_fields_set contains the field
        if self.lab_test_stage is None and "lab_test_stage" in self.model_fields_set:
            _dict['labTestStage'] = None

        # set to None if external_id (nullable) is None
        # and model_fields_set contains the field
        if self.external_id is None and "external_id" in self.model_fields_set:
            _dict['externalId'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of MetrcSuperpackage from a dict"""
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
            "archivedDate": obj.get("archivedDate"),
            "containsRemediatedProduct": obj.get("containsRemediatedProduct"),
            "donationFacilityLicenseNumber": obj.get("donationFacilityLicenseNumber"),
            "donationFacilityName": obj.get("donationFacilityName"),
            "facilityLicenseNumber": obj.get("facilityLicenseNumber"),
            "facilityName": obj.get("facilityName"),
            "finishedDate": obj.get("finishedDate"),
            "initialLabTestingState": obj.get("initialLabTestingState"),
            "isArchived": obj.get("isArchived"),
            "isDonation": obj.get("isDonation"),
            "isDonationPersistent": obj.get("isDonationPersistent"),
            "isFinished": obj.get("isFinished"),
            "isInTransit": obj.get("isInTransit"),
            "isOnHold": obj.get("isOnHold"),
            "isProcessValidationTestingSample": obj.get("isProcessValidationTestingSample"),
            "isProductionBatch": obj.get("isProductionBatch"),
            "isTestingSample": obj.get("isTestingSample"),
            "isTradeSample": obj.get("isTradeSample"),
            "isTradeSamplePersistent": obj.get("isTradeSamplePersistent"),
            "item": MetrcItem.from_dict(obj["item"]) if obj.get("item") is not None else None,
            "itemFromFacilityLicenseNumber": obj.get("itemFromFacilityLicenseNumber"),
            "itemFromFacilityName": obj.get("itemFromFacilityName"),
            "labTestingStateDate": obj.get("labTestingStateDate"),
            "labTestingStateName": obj.get("labTestingStateName"),
            "labTestingRecordedDate": obj.get("labTestingRecordedDate"),
            "labTestingPerformedDate": obj.get("labTestingPerformedDate"),
            "labTestStageId": obj.get("labTestStageId"),
            "labTestResultExpirationDateTime": obj.get("labTestResultExpirationDateTime"),
            "label": obj.get("label"),
            "lastModified": obj.get("lastModified"),
            "locationName": obj.get("locationName"),
            "sublocationName": obj.get("sublocationName"),
            "locationTypeName": obj.get("locationTypeName"),
            "multiHarvest": obj.get("multiHarvest"),
            "multiPackage": obj.get("multiPackage"),
            "multiProductionBatch": obj.get("multiProductionBatch"),
            "note": obj.get("note"),
            "packageType": obj.get("packageType"),
            "packagedByFacilityLicenseNumber": obj.get("packagedByFacilityLicenseNumber"),
            "packagedByFacilityName": obj.get("packagedByFacilityName"),
            "packagedDate": obj.get("packagedDate"),
            "patientLicenseNumber": obj.get("patientLicenseNumber"),
            "productRequiresRemediation": obj.get("productRequiresRemediation"),
            "productionBatchNumber": obj.get("productionBatchNumber"),
            "quantity": obj.get("quantity"),
            "receivedDateTime": obj.get("receivedDateTime"),
            "receivedFromFacilityLicenseNumber": obj.get("receivedFromFacilityLicenseNumber"),
            "receivedFromFacilityName": obj.get("receivedFromFacilityName"),
            "receivedFromManifestNumber": obj.get("receivedFromManifestNumber"),
            "remediationDate": obj.get("remediationDate"),
            "sourceHarvestNames": obj.get("sourceHarvestNames"),
            "sourcePackageIsDonation": obj.get("sourcePackageIsDonation"),
            "sourcePackageIsTradeSample": obj.get("sourcePackageIsTradeSample"),
            "sourcePackageLabels": obj.get("sourcePackageLabels"),
            "sourceProductionBatchNumbers": obj.get("sourceProductionBatchNumbers"),
            "tradeSampleFacilityName": obj.get("tradeSampleFacilityName"),
            "tradeSampleFacilityLicenseNumber": obj.get("tradeSampleFacilityLicenseNumber"),
            "transferManifestNumber": obj.get("transferManifestNumber"),
            "unitOfMeasureAbbreviation": obj.get("unitOfMeasureAbbreviation"),
            "unitOfMeasureId": obj.get("unitOfMeasureId"),
            "unitOfMeasureQuantityType": obj.get("unitOfMeasureQuantityType"),
            "sourceHarvestCount": obj.get("sourceHarvestCount"),
            "sourcePackageCount": obj.get("sourcePackageCount"),
            "sourceProcessingJobCount": obj.get("sourceProcessingJobCount"),
            "sourceProcessingJobNumbers": obj.get("sourceProcessingJobNumbers"),
            "sourceProcessingJobNames": obj.get("sourceProcessingJobNames"),
            "multiProcessingJob": obj.get("multiProcessingJob"),
            "expirationDate": obj.get("expirationDate"),
            "sellByDate": obj.get("sellByDate"),
            "useByDate": obj.get("useByDate"),
            "labTestResultDocumentFileId": obj.get("labTestResultDocumentFileId"),
            "isOnRetailerDelivery": obj.get("isOnRetailerDelivery"),
            "packageForProductDestruction": obj.get("packageForProductDestruction"),
            "hasPartial": obj.get("hasPartial"),
            "isPartial": obj.get("isPartial"),
            "inTransitStatus": obj.get("inTransitStatus"),
            "processingJobTypeId": obj.get("processingJobTypeId"),
            "isOnRecall": obj.get("isOnRecall"),
            "decontaminationDate": obj.get("decontaminationDate"),
            "containsDecontaminatedProduct": obj.get("containsDecontaminatedProduct"),
            "productRequiresDecontamination": obj.get("productRequiresDecontamination"),
            "productLabel": obj.get("productLabel"),
            "labTestStage": obj.get("labTestStage"),
            "externalId": obj.get("externalId"),
            "metadata": MetrcSuperpackageAllOfMetadata.from_dict(obj["metadata"]) if obj.get("metadata") is not None else None,
            "sourceHarvests": [MetrcPackageSourceHarvest.from_dict(_item) for _item in obj["sourceHarvests"]] if obj.get("sourceHarvests") is not None else None,
            "labResultBatches": [MetrcPackageLabResultBatch.from_dict(_item) for _item in obj["labResultBatches"]] if obj.get("labResultBatches") is not None else None,
            "history": [MetrcHistory.from_dict(_item) for _item in obj["history"]] if obj.get("history") is not None else None
        })
        return _obj


