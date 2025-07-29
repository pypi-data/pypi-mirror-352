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

class MetrcIncomingTransfer(BaseModel):
    """
    MetrcIncomingTransfer
    """ # noqa: E501
    hostname: Optional[StrictStr] = Field(default=None, description="The hostname this object was retrieved from")
    data_model: Optional[StrictStr] = Field(default=None, description="Name of this object's data model", alias="dataModel")
    retrieved_at: Optional[datetime] = Field(default=None, description="Timestamp of when this object was pulled from Metrc", alias="retrievedAt")
    license_number: Optional[StrictStr] = Field(default=None, description="License number used to access this object", alias="licenseNumber")
    index: Optional[StrictStr] = Field(default=None, description="Describes the current state of this object at the time it was returned from the API. This cannot be used to sort or filter.")
    id: Optional[StrictInt] = Field(default=None, description="Unique identifier for the transfer")
    manifest_number: Optional[StrictStr] = Field(default=None, description="Unique manifest number associated with the transfer", alias="manifestNumber")
    shipment_license_type_name: Optional[StrictStr] = Field(default=None, description="Type of license for the shipment", alias="shipmentLicenseTypeName")
    shipper_facility_license_number: Optional[StrictStr] = Field(default=None, description="License number of the shipper's facility", alias="shipperFacilityLicenseNumber")
    shipper_facility_name: Optional[StrictStr] = Field(default=None, description="Name of the shipper's facility", alias="shipperFacilityName")
    name: Optional[StrictStr] = Field(default=None, description="Name of the transfer")
    transporter_facility_license_number: Optional[StrictStr] = Field(default=None, description="License number of the transporter facility", alias="transporterFacilityLicenseNumber")
    transporter_facility_name: Optional[StrictStr] = Field(default=None, description="Name of the transporter facility", alias="transporterFacilityName")
    driver_name: Optional[StrictStr] = Field(default=None, description="Name of the driver", alias="driverName")
    driver_occupational_license_number: Optional[StrictStr] = Field(default=None, description="Occupational license number of the driver", alias="driverOccupationalLicenseNumber")
    driver_vehicle_license_number: Optional[StrictStr] = Field(default=None, description="License number of the vehicle used by the driver", alias="driverVehicleLicenseNumber")
    vehicle_make: Optional[StrictStr] = Field(default=None, description="Make of the vehicle used for transport", alias="vehicleMake")
    vehicle_model: Optional[StrictStr] = Field(default=None, description="Model of the vehicle used for transport", alias="vehicleModel")
    vehicle_license_plate_number: Optional[StrictStr] = Field(default=None, description="License plate number of the vehicle", alias="vehicleLicensePlateNumber")
    delivery_facilities: Optional[StrictStr] = Field(default=None, description="Details of the delivery facilities", alias="deliveryFacilities")
    delivery_count: Optional[StrictInt] = Field(default=None, description="Number of deliveries in the transfer", alias="deliveryCount")
    received_delivery_count: Optional[StrictInt] = Field(default=None, description="Number of deliveries received", alias="receivedDeliveryCount")
    package_count: Optional[StrictInt] = Field(default=None, description="Total number of packages in the transfer", alias="packageCount")
    received_package_count: Optional[StrictInt] = Field(default=None, description="Number of packages received", alias="receivedPackageCount")
    contains_plant_package: Optional[StrictBool] = Field(default=None, description="Indicates if the transfer contains plant packages", alias="containsPlantPackage")
    contains_product_package: Optional[StrictBool] = Field(default=None, description="Indicates if the transfer contains product packages", alias="containsProductPackage")
    contains_trade_sample: Optional[StrictBool] = Field(default=None, description="Indicates if the transfer contains trade samples", alias="containsTradeSample")
    contains_donation: Optional[StrictBool] = Field(default=None, description="Indicates if the transfer contains donations", alias="containsDonation")
    contains_testing_sample: Optional[StrictBool] = Field(default=None, description="Indicates if the transfer contains testing samples", alias="containsTestingSample")
    contains_product_requires_remediation: Optional[StrictBool] = Field(default=None, description="Indicates if the transfer contains products that require remediation", alias="containsProductRequiresRemediation")
    contains_remediated_product_package: Optional[StrictBool] = Field(default=None, description="Indicates if the transfer contains remediated product packages", alias="containsRemediatedProductPackage")
    edit_count: Optional[StrictInt] = Field(default=None, description="Number of times the transfer record has been edited", alias="editCount")
    can_edit: Optional[StrictBool] = Field(default=None, description="Indicates if the transfer record can be edited", alias="canEdit")
    can_edit_outgoing_inactive: Optional[StrictBool] = Field(default=None, description="Indicates if the transfer record can be edited when outgoing and inactive", alias="canEditOutgoingInactive")
    is_voided: Optional[StrictBool] = Field(default=None, description="Indicates if the transfer has been voided", alias="isVoided")
    created_date_time: Optional[datetime] = Field(default=None, description="The date and time when the transfer was created", alias="createdDateTime")
    created_by_user_name: Optional[StrictStr] = Field(default=None, description="Username of the person who created the transfer record", alias="createdByUserName")
    last_modified: Optional[datetime] = Field(default=None, description="The date and time when the transfer was last modified", alias="lastModified")
    delivery_id: Optional[StrictInt] = Field(default=None, description="Unique identifier for the delivery associated with the transfer", alias="deliveryId")
    recipient_facility_id: Optional[StrictInt] = Field(default=None, description="The ID of the recipient facility.", alias="recipientFacilityId")
    recipient_facility_license_number: Optional[StrictStr] = Field(default=None, description="License number of the recipient facility", alias="recipientFacilityLicenseNumber")
    recipient_facility_name: Optional[StrictStr] = Field(default=None, description="Name of the recipient facility", alias="recipientFacilityName")
    shipment_type_name: Optional[StrictStr] = Field(default=None, description="Type of shipment", alias="shipmentTypeName")
    shipment_transaction_type_name: Optional[StrictStr] = Field(default=None, description="Type of shipment transaction", alias="shipmentTransactionTypeName")
    estimated_departure_date_time: Optional[datetime] = Field(default=None, description="Estimated date and time of departure", alias="estimatedDepartureDateTime")
    actual_departure_date_time: Optional[datetime] = Field(default=None, description="Actual date and time of departure", alias="actualDepartureDateTime")
    estimated_arrival_date_time: Optional[datetime] = Field(default=None, description="Estimated date and time of arrival", alias="estimatedArrivalDateTime")
    actual_arrival_date_time: Optional[datetime] = Field(default=None, description="Actual date and time of arrival", alias="actualArrivalDateTime")
    delivery_package_count: Optional[StrictInt] = Field(default=None, description="Number of packages in the delivery", alias="deliveryPackageCount")
    delivery_received_package_count: Optional[StrictInt] = Field(default=None, description="Number of packages received in the delivery", alias="deliveryReceivedPackageCount")
    received_by_name: Optional[StrictStr] = Field(default=None, description="Name of the person who received the delivery", alias="receivedByName")
    received_date_time: Optional[datetime] = Field(default=None, description="Date and time when the delivery was received", alias="receivedDateTime")
    estimated_return_departure_date_time: Optional[datetime] = Field(default=None, description="Estimated date and time of return departure", alias="estimatedReturnDepartureDateTime")
    actual_return_departure_date_time: Optional[datetime] = Field(default=None, description="Actual date and time of return departure", alias="actualReturnDepartureDateTime")
    estimated_return_arrival_date_time: Optional[datetime] = Field(default=None, description="Estimated date and time of return arrival", alias="estimatedReturnArrivalDateTime")
    actual_return_arrival_date_time: Optional[datetime] = Field(default=None, description="Actual date and time of return arrival", alias="actualReturnArrivalDateTime")
    rejected_packages_returned: Optional[StrictBool] = Field(default=None, description="Indicates if rejected packages were returned", alias="rejectedPackagesReturned")
    transporter_all_approval_date: Optional[datetime] = Field(default=None, description="Date and time when all transporters were approved", alias="transporterAllApprovalDate")
    destinations_all_approval_date: Optional[datetime] = Field(default=None, description="Date and time when all destinations were approved", alias="destinationsAllApprovalDate")
    transporters_automatically_approved: Optional[StrictBool] = Field(default=None, description="Indicates if transporters were automatically approved", alias="transportersAutomaticallyApproved")
    destinations_automatically_approved: Optional[StrictBool] = Field(default=None, description="Indicates if destinations were automatically approved", alias="destinationsAutomaticallyApproved")
    approval_reject_date_time: Optional[datetime] = Field(default=None, description="Date and time when the approval was rejected", alias="approvalRejectDateTime")
    approval_rejected_by_user: Optional[StrictStr] = Field(default=None, description="Username of the person who rejected the approval", alias="approvalRejectedByUser")
    approval_rejected_facility_license_number: Optional[StrictStr] = Field(default=None, description="License number of the facility where approval was rejected", alias="approvalRejectedFacilityLicenseNumber")
    approval_reject_reason_id: Optional[StrictStr] = Field(default=None, description="Reason ID for the approval rejection", alias="approvalRejectReasonId")
    tolling_agreement_file_system_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="tollingAgreementFileSystemId")
    invoice_number: Optional[StrictStr] = Field(default=None, alias="invoiceNumber")
    line_number: Optional[StrictInt] = Field(default=None, alias="lineNumber")
    __properties: ClassVar[List[str]] = ["hostname", "dataModel", "retrievedAt", "licenseNumber", "index", "id", "manifestNumber", "shipmentLicenseTypeName", "shipperFacilityLicenseNumber", "shipperFacilityName", "name", "transporterFacilityLicenseNumber", "transporterFacilityName", "driverName", "driverOccupationalLicenseNumber", "driverVehicleLicenseNumber", "vehicleMake", "vehicleModel", "vehicleLicensePlateNumber", "deliveryFacilities", "deliveryCount", "receivedDeliveryCount", "packageCount", "receivedPackageCount", "containsPlantPackage", "containsProductPackage", "containsTradeSample", "containsDonation", "containsTestingSample", "containsProductRequiresRemediation", "containsRemediatedProductPackage", "editCount", "canEdit", "canEditOutgoingInactive", "isVoided", "createdDateTime", "createdByUserName", "lastModified", "deliveryId", "recipientFacilityId", "recipientFacilityLicenseNumber", "recipientFacilityName", "shipmentTypeName", "shipmentTransactionTypeName", "estimatedDepartureDateTime", "actualDepartureDateTime", "estimatedArrivalDateTime", "actualArrivalDateTime", "deliveryPackageCount", "deliveryReceivedPackageCount", "receivedByName", "receivedDateTime", "estimatedReturnDepartureDateTime", "actualReturnDepartureDateTime", "estimatedReturnArrivalDateTime", "actualReturnArrivalDateTime", "rejectedPackagesReturned", "transporterAllApprovalDate", "destinationsAllApprovalDate", "transportersAutomaticallyApproved", "destinationsAutomaticallyApproved", "approvalRejectDateTime", "approvalRejectedByUser", "approvalRejectedFacilityLicenseNumber", "approvalRejectReasonId", "tollingAgreementFileSystemId", "invoiceNumber", "lineNumber"]

    @field_validator('index')
    def index_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['ACTIVE_INCOMING_TRANSFER', 'INACTIVE_INCOMING_TRANSFER']):
            raise ValueError("must be one of enum values ('ACTIVE_INCOMING_TRANSFER', 'INACTIVE_INCOMING_TRANSFER')")
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
        """Create an instance of MetrcIncomingTransfer from a JSON string"""
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
        # set to None if name (nullable) is None
        # and model_fields_set contains the field
        if self.name is None and "name" in self.model_fields_set:
            _dict['name'] = None

        # set to None if actual_departure_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.actual_departure_date_time is None and "actual_departure_date_time" in self.model_fields_set:
            _dict['actualDepartureDateTime'] = None

        # set to None if actual_arrival_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.actual_arrival_date_time is None and "actual_arrival_date_time" in self.model_fields_set:
            _dict['actualArrivalDateTime'] = None

        # set to None if received_by_name (nullable) is None
        # and model_fields_set contains the field
        if self.received_by_name is None and "received_by_name" in self.model_fields_set:
            _dict['receivedByName'] = None

        # set to None if received_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.received_date_time is None and "received_date_time" in self.model_fields_set:
            _dict['receivedDateTime'] = None

        # set to None if estimated_return_departure_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.estimated_return_departure_date_time is None and "estimated_return_departure_date_time" in self.model_fields_set:
            _dict['estimatedReturnDepartureDateTime'] = None

        # set to None if actual_return_departure_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.actual_return_departure_date_time is None and "actual_return_departure_date_time" in self.model_fields_set:
            _dict['actualReturnDepartureDateTime'] = None

        # set to None if estimated_return_arrival_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.estimated_return_arrival_date_time is None and "estimated_return_arrival_date_time" in self.model_fields_set:
            _dict['estimatedReturnArrivalDateTime'] = None

        # set to None if actual_return_arrival_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.actual_return_arrival_date_time is None and "actual_return_arrival_date_time" in self.model_fields_set:
            _dict['actualReturnArrivalDateTime'] = None

        # set to None if approval_reject_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.approval_reject_date_time is None and "approval_reject_date_time" in self.model_fields_set:
            _dict['approvalRejectDateTime'] = None

        # set to None if approval_rejected_facility_license_number (nullable) is None
        # and model_fields_set contains the field
        if self.approval_rejected_facility_license_number is None and "approval_rejected_facility_license_number" in self.model_fields_set:
            _dict['approvalRejectedFacilityLicenseNumber'] = None

        # set to None if approval_reject_reason_id (nullable) is None
        # and model_fields_set contains the field
        if self.approval_reject_reason_id is None and "approval_reject_reason_id" in self.model_fields_set:
            _dict['approvalRejectReasonId'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of MetrcIncomingTransfer from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "hostname": obj.get("hostname"),
            "dataModel": obj.get("dataModel"),
            "retrievedAt": obj.get("retrievedAt"),
            "licenseNumber": obj.get("licenseNumber"),
            "index": obj.get("index"),
            "id": obj.get("id"),
            "manifestNumber": obj.get("manifestNumber"),
            "shipmentLicenseTypeName": obj.get("shipmentLicenseTypeName"),
            "shipperFacilityLicenseNumber": obj.get("shipperFacilityLicenseNumber"),
            "shipperFacilityName": obj.get("shipperFacilityName"),
            "name": obj.get("name"),
            "transporterFacilityLicenseNumber": obj.get("transporterFacilityLicenseNumber"),
            "transporterFacilityName": obj.get("transporterFacilityName"),
            "driverName": obj.get("driverName"),
            "driverOccupationalLicenseNumber": obj.get("driverOccupationalLicenseNumber"),
            "driverVehicleLicenseNumber": obj.get("driverVehicleLicenseNumber"),
            "vehicleMake": obj.get("vehicleMake"),
            "vehicleModel": obj.get("vehicleModel"),
            "vehicleLicensePlateNumber": obj.get("vehicleLicensePlateNumber"),
            "deliveryFacilities": obj.get("deliveryFacilities"),
            "deliveryCount": obj.get("deliveryCount"),
            "receivedDeliveryCount": obj.get("receivedDeliveryCount"),
            "packageCount": obj.get("packageCount"),
            "receivedPackageCount": obj.get("receivedPackageCount"),
            "containsPlantPackage": obj.get("containsPlantPackage"),
            "containsProductPackage": obj.get("containsProductPackage"),
            "containsTradeSample": obj.get("containsTradeSample"),
            "containsDonation": obj.get("containsDonation"),
            "containsTestingSample": obj.get("containsTestingSample"),
            "containsProductRequiresRemediation": obj.get("containsProductRequiresRemediation"),
            "containsRemediatedProductPackage": obj.get("containsRemediatedProductPackage"),
            "editCount": obj.get("editCount"),
            "canEdit": obj.get("canEdit"),
            "canEditOutgoingInactive": obj.get("canEditOutgoingInactive"),
            "isVoided": obj.get("isVoided"),
            "createdDateTime": obj.get("createdDateTime"),
            "createdByUserName": obj.get("createdByUserName"),
            "lastModified": obj.get("lastModified"),
            "deliveryId": obj.get("deliveryId"),
            "recipientFacilityId": obj.get("recipientFacilityId"),
            "recipientFacilityLicenseNumber": obj.get("recipientFacilityLicenseNumber"),
            "recipientFacilityName": obj.get("recipientFacilityName"),
            "shipmentTypeName": obj.get("shipmentTypeName"),
            "shipmentTransactionTypeName": obj.get("shipmentTransactionTypeName"),
            "estimatedDepartureDateTime": obj.get("estimatedDepartureDateTime"),
            "actualDepartureDateTime": obj.get("actualDepartureDateTime"),
            "estimatedArrivalDateTime": obj.get("estimatedArrivalDateTime"),
            "actualArrivalDateTime": obj.get("actualArrivalDateTime"),
            "deliveryPackageCount": obj.get("deliveryPackageCount"),
            "deliveryReceivedPackageCount": obj.get("deliveryReceivedPackageCount"),
            "receivedByName": obj.get("receivedByName"),
            "receivedDateTime": obj.get("receivedDateTime"),
            "estimatedReturnDepartureDateTime": obj.get("estimatedReturnDepartureDateTime"),
            "actualReturnDepartureDateTime": obj.get("actualReturnDepartureDateTime"),
            "estimatedReturnArrivalDateTime": obj.get("estimatedReturnArrivalDateTime"),
            "actualReturnArrivalDateTime": obj.get("actualReturnArrivalDateTime"),
            "rejectedPackagesReturned": obj.get("rejectedPackagesReturned"),
            "transporterAllApprovalDate": obj.get("transporterAllApprovalDate"),
            "destinationsAllApprovalDate": obj.get("destinationsAllApprovalDate"),
            "transportersAutomaticallyApproved": obj.get("transportersAutomaticallyApproved"),
            "destinationsAutomaticallyApproved": obj.get("destinationsAutomaticallyApproved"),
            "approvalRejectDateTime": obj.get("approvalRejectDateTime"),
            "approvalRejectedByUser": obj.get("approvalRejectedByUser"),
            "approvalRejectedFacilityLicenseNumber": obj.get("approvalRejectedFacilityLicenseNumber"),
            "approvalRejectReasonId": obj.get("approvalRejectReasonId"),
            "tollingAgreementFileSystemId": obj.get("tollingAgreementFileSystemId"),
            "invoiceNumber": obj.get("invoiceNumber"),
            "lineNumber": obj.get("lineNumber")
        })
        return _obj


