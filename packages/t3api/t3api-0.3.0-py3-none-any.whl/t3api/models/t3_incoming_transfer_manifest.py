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

class T3IncomingTransferManifest(BaseModel):
    """
    T3IncomingTransferManifest
    """ # noqa: E501
    transfer_data_model: Optional[StrictStr] = Field(default=None, description="Name of this object's data model", alias="transfer.dataModel")
    transfer_retrieved_at: Optional[datetime] = Field(default=None, description="Timestamp of when this object was pulled from Metrc", alias="transfer.retrievedAt")
    transfer_license_number: Optional[StrictStr] = Field(default=None, description="License number used to access this object", alias="transfer.licenseNumber")
    transfer_index: Optional[StrictStr] = Field(default=None, description="Describes the current state of this object at the time it was returned from the API. This cannot be used to sort or filter.", alias="transfer.index")
    transfer_id: Optional[StrictInt] = Field(default=None, description="Unique identifier for the transfer", alias="transfer.id")
    transfer_manifest_number: Optional[StrictStr] = Field(default=None, description="Unique manifest number associated with the transfer", alias="transfer.manifestNumber")
    transfer_shipment_license_type_name: Optional[StrictStr] = Field(default=None, description="Type of license for the shipment", alias="transfer.shipmentLicenseTypeName")
    transfer_shipper_facility_license_number: Optional[StrictStr] = Field(default=None, description="License number of the shipper's facility", alias="transfer.shipperFacilityLicenseNumber")
    transfer_shipper_facility_name: Optional[StrictStr] = Field(default=None, description="Name of the shipper's facility", alias="transfer.shipperFacilityName")
    transfer_name: Optional[StrictStr] = Field(default=None, description="Name of the transfer", alias="transfer.name")
    transfer_transporter_facility_license_number: Optional[StrictStr] = Field(default=None, description="License number of the transporter facility", alias="transfer.transporterFacilityLicenseNumber")
    transfer_transporter_facility_name: Optional[StrictStr] = Field(default=None, description="Name of the transporter facility", alias="transfer.transporterFacilityName")
    transfer_driver_name: Optional[StrictStr] = Field(default=None, description="Name of the driver", alias="transfer.driverName")
    transfer_driver_occupational_license_number: Optional[StrictStr] = Field(default=None, description="Occupational license number of the driver", alias="transfer.driverOccupationalLicenseNumber")
    transfer_driver_vehicle_license_number: Optional[StrictStr] = Field(default=None, description="License number of the vehicle used by the driver", alias="transfer.driverVehicleLicenseNumber")
    transfer_vehicle_make: Optional[StrictStr] = Field(default=None, description="Make of the vehicle used for transport", alias="transfer.vehicleMake")
    transfer_vehicle_model: Optional[StrictStr] = Field(default=None, description="Model of the vehicle used for transport", alias="transfer.vehicleModel")
    transfer_vehicle_license_plate_number: Optional[StrictStr] = Field(default=None, description="License plate number of the vehicle", alias="transfer.vehicleLicensePlateNumber")
    transfer_delivery_facilities: Optional[StrictStr] = Field(default=None, description="Details of the delivery facilities", alias="transfer.deliveryFacilities")
    transfer_delivery_count: Optional[StrictInt] = Field(default=None, description="Number of deliveries in the transfer", alias="transfer.deliveryCount")
    transfer_received_delivery_count: Optional[StrictInt] = Field(default=None, description="Number of deliveries received", alias="transfer.receivedDeliveryCount")
    transfer_package_count: Optional[StrictInt] = Field(default=None, description="Total number of packages in the transfer", alias="transfer.packageCount")
    transfer_received_package_count: Optional[StrictInt] = Field(default=None, description="Number of packages received", alias="transfer.receivedPackageCount")
    transfer_contains_plant_package: Optional[StrictBool] = Field(default=None, description="Indicates if the transfer contains plant packages", alias="transfer.containsPlantPackage")
    transfer_contains_product_package: Optional[StrictBool] = Field(default=None, description="Indicates if the transfer contains product packages", alias="transfer.containsProductPackage")
    transfer_contains_trade_sample: Optional[StrictBool] = Field(default=None, description="Indicates if the transfer contains trade samples", alias="transfer.containsTradeSample")
    transfer_contains_donation: Optional[StrictBool] = Field(default=None, description="Indicates if the transfer contains donations", alias="transfer.containsDonation")
    transfer_contains_testing_sample: Optional[StrictBool] = Field(default=None, description="Indicates if the transfer contains testing samples", alias="transfer.containsTestingSample")
    transfer_contains_product_requires_remediation: Optional[StrictBool] = Field(default=None, description="Indicates if the transfer contains products that require remediation", alias="transfer.containsProductRequiresRemediation")
    transfer_contains_remediated_product_package: Optional[StrictBool] = Field(default=None, description="Indicates if the transfer contains remediated product packages", alias="transfer.containsRemediatedProductPackage")
    transfer_edit_count: Optional[StrictInt] = Field(default=None, description="Number of times the transfer record has been edited", alias="transfer.editCount")
    transfer_can_edit: Optional[StrictBool] = Field(default=None, description="Indicates if the transfer record can be edited", alias="transfer.canEdit")
    transfer_can_edit_outgoing_inactive: Optional[StrictBool] = Field(default=None, description="Indicates if the transfer record can be edited when outgoing and inactive", alias="transfer.canEditOutgoingInactive")
    transfer_is_voided: Optional[StrictBool] = Field(default=None, description="Indicates if the transfer has been voided", alias="transfer.isVoided")
    transfer_created_date_time: Optional[datetime] = Field(default=None, description="The date and time when the transfer was created", alias="transfer.createdDateTime")
    transfer_created_by_user_name: Optional[StrictStr] = Field(default=None, description="Username of the person who created the transfer record", alias="transfer.createdByUserName")
    transfer_last_modified: Optional[datetime] = Field(default=None, description="The date and time when the transfer was last modified", alias="transfer.lastModified")
    transfer_delivery_id: Optional[StrictInt] = Field(default=None, description="Unique identifier for the delivery associated with the transfer", alias="transfer.deliveryId")
    transfer_recipient_facility_id: Optional[StrictInt] = Field(default=None, description="The ID of the recipient facility.", alias="transfer.recipientFacilityId")
    transfer_recipient_facility_license_number: Optional[StrictStr] = Field(default=None, description="License number of the recipient facility", alias="transfer.recipientFacilityLicenseNumber")
    transfer_recipient_facility_name: Optional[StrictStr] = Field(default=None, description="Name of the recipient facility", alias="transfer.recipientFacilityName")
    transfer_shipment_type_name: Optional[StrictStr] = Field(default=None, description="Type of shipment", alias="transfer.shipmentTypeName")
    transfer_shipment_transaction_type_name: Optional[StrictStr] = Field(default=None, description="Type of shipment transaction", alias="transfer.shipmentTransactionTypeName")
    transfer_estimated_departure_date_time: Optional[datetime] = Field(default=None, description="Estimated date and time of departure", alias="transfer.estimatedDepartureDateTime")
    transfer_actual_departure_date_time: Optional[datetime] = Field(default=None, description="Actual date and time of departure", alias="transfer.actualDepartureDateTime")
    transfer_estimated_arrival_date_time: Optional[datetime] = Field(default=None, description="Estimated date and time of arrival", alias="transfer.estimatedArrivalDateTime")
    transfer_actual_arrival_date_time: Optional[datetime] = Field(default=None, description="Actual date and time of arrival", alias="transfer.actualArrivalDateTime")
    transfer_delivery_package_count: Optional[StrictInt] = Field(default=None, description="Number of packages in the delivery", alias="transfer.deliveryPackageCount")
    transfer_delivery_received_package_count: Optional[StrictInt] = Field(default=None, description="Number of packages received in the delivery", alias="transfer.deliveryReceivedPackageCount")
    transfer_received_by_name: Optional[StrictStr] = Field(default=None, description="Name of the person who received the delivery", alias="transfer.receivedByName")
    transfer_received_date_time: Optional[datetime] = Field(default=None, description="Date and time when the delivery was received", alias="transfer.receivedDateTime")
    transfer_estimated_return_departure_date_time: Optional[datetime] = Field(default=None, description="Estimated date and time of return departure", alias="transfer.estimatedReturnDepartureDateTime")
    transfer_actual_return_departure_date_time: Optional[datetime] = Field(default=None, description="Actual date and time of return departure", alias="transfer.actualReturnDepartureDateTime")
    transfer_estimated_return_arrival_date_time: Optional[datetime] = Field(default=None, description="Estimated date and time of return arrival", alias="transfer.estimatedReturnArrivalDateTime")
    transfer_actual_return_arrival_date_time: Optional[datetime] = Field(default=None, description="Actual date and time of return arrival", alias="transfer.actualReturnArrivalDateTime")
    transfer_rejected_packages_returned: Optional[StrictBool] = Field(default=None, description="Indicates if rejected packages were returned", alias="transfer.rejectedPackagesReturned")
    transfer_transporter_all_approval_date: Optional[datetime] = Field(default=None, description="Date and time when all transporters were approved", alias="transfer.transporterAllApprovalDate")
    transfer_destinations_all_approval_date: Optional[datetime] = Field(default=None, description="Date and time when all destinations were approved", alias="transfer.destinationsAllApprovalDate")
    transfer_transporters_automatically_approved: Optional[StrictBool] = Field(default=None, description="Indicates if transporters were automatically approved", alias="transfer.transportersAutomaticallyApproved")
    transfer_destinations_automatically_approved: Optional[StrictBool] = Field(default=None, description="Indicates if destinations were automatically approved", alias="transfer.destinationsAutomaticallyApproved")
    transfer_approval_reject_date_time: Optional[datetime] = Field(default=None, description="Date and time when the approval was rejected", alias="transfer.approvalRejectDateTime")
    transfer_approval_rejected_by_user: Optional[StrictStr] = Field(default=None, description="Username of the person who rejected the approval", alias="transfer.approvalRejectedByUser")
    transfer_approval_rejected_facility_license_number: Optional[StrictStr] = Field(default=None, description="License number of the facility where approval was rejected", alias="transfer.approvalRejectedFacilityLicenseNumber")
    transfer_approval_reject_reason_id: Optional[StrictStr] = Field(default=None, description="Reason ID for the approval rejection", alias="transfer.approvalRejectReasonId")
    transfer_tolling_agreement_file_system_id: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="transfer.tollingAgreementFileSystemId")
    transfer_invoice_number: Optional[StrictStr] = Field(default=None, alias="transfer.invoiceNumber")
    transporter_data_model: Optional[StrictStr] = Field(default=None, description="Name of this object's data model", alias="transporter.dataModel")
    transporter_retrieved_at: Optional[datetime] = Field(default=None, description="Timestamp of when this object was pulled from Metrc", alias="transporter.retrievedAt")
    transporter_license_number: Optional[StrictStr] = Field(default=None, description="License number used to access this object", alias="transporter.licenseNumber")
    transporter_transporter_facility_license_number: Optional[StrictStr] = Field(default=None, description="The license number of the transporter's facility.", alias="transporter.transporterFacilityLicenseNumber")
    transporter_transporter_facility_name: Optional[StrictStr] = Field(default=None, description="The name of the transporter's facility.", alias="transporter.transporterFacilityName")
    transporter_transporter_direction_name: Optional[StrictStr] = Field(default=None, description="The direction of the transporter.", alias="transporter.transporterDirectionName")
    transporter_transporter_approval_date: Optional[datetime] = Field(default=None, description="The date and time when the transporter was approved.", alias="transporter.transporterApprovalDate")
    transporter_transporter_auto_approval: Optional[StrictBool] = Field(default=None, description="Indicates if the transporter was automatically approved.", alias="transporter.transporterAutoApproval")
    transporter_driver_name: Optional[StrictStr] = Field(default=None, description="The name of the driver.", alias="transporter.driverName")
    transporter_driver_occupational_license_number: Optional[StrictStr] = Field(default=None, description="The occupational license number of the driver.", alias="transporter.driverOccupationalLicenseNumber")
    transporter_driver_vehicle_license_number: Optional[StrictStr] = Field(default=None, description="The vehicle license number of the driver.", alias="transporter.driverVehicleLicenseNumber")
    transporter_driver_layover_leg: Optional[StrictStr] = Field(default=None, description="Information about the driver's layover leg.", alias="transporter.driverLayoverLeg")
    transporter_vehicle_make: Optional[StrictStr] = Field(default=None, description="The make of the vehicle.", alias="transporter.vehicleMake")
    transporter_vehicle_model: Optional[StrictStr] = Field(default=None, description="The model of the vehicle.", alias="transporter.vehicleModel")
    transporter_vehicle_license_plate_number: Optional[StrictStr] = Field(default=None, description="The license plate number of the vehicle.", alias="transporter.vehicleLicensePlateNumber")
    transporter_accepted_date_time: Optional[datetime] = Field(default=None, description="The date and time when the transporter was accepted.", alias="transporter.acceptedDateTime")
    transporter_is_layover: Optional[StrictBool] = Field(default=None, description="Indicates if the transport includes a layover.", alias="transporter.isLayover")
    transporter_estimated_departure_date_time: Optional[datetime] = Field(default=None, description="The estimated date and time of departure.", alias="transporter.estimatedDepartureDateTime")
    transporter_actual_departure_date_time: Optional[datetime] = Field(default=None, description="The actual date and time of departure.", alias="transporter.actualDepartureDateTime")
    transporter_estimated_arrival_date_time: Optional[datetime] = Field(default=None, description="The estimated date and time of arrival.", alias="transporter.estimatedArrivalDateTime")
    transporter_actual_arrival_date_time: Optional[datetime] = Field(default=None, description="The actual date and time of arrival.", alias="transporter.actualArrivalDateTime")
    package_id: StrictInt = Field(description="Unique identifier for the item", alias="package.id")
    package_data_model: Optional[StrictStr] = Field(default=None, description="Name of this object's data model", alias="package.dataModel")
    package_retrieved_at: Optional[datetime] = Field(default=None, description="Timestamp of when this object was pulled from Metrc", alias="package.retrievedAt")
    package_license_number: Optional[StrictStr] = Field(default=None, description="License number used to access this object", alias="package.licenseNumber")
    package_index: Optional[StrictStr] = Field(default=None, description="Describes the current state of this object at the time it was returned from the API. This cannot be used to sort or filter.", alias="package.index")
    package_package_id: StrictInt = Field(description="Identifier for the package", alias="package.packageId")
    package_recipient_facility_license_number: StrictStr = Field(description="License number of the recipient facility", alias="package.recipientFacilityLicenseNumber")
    package_recipient_facility_name: StrictStr = Field(description="Name of the recipient facility", alias="package.recipientFacilityName")
    package_manifest_number: StrictStr = Field(description="Manifest number associated with the shipment", alias="package.manifestNumber")
    package_package_label: StrictStr = Field(description="Label of the package", alias="package.packageLabel")
    package_source_harvest_names: Optional[StrictStr] = Field(default=None, description="Names of the source harvests", alias="package.sourceHarvestNames")
    package_source_package_labels: Optional[StrictStr] = Field(default=None, description="Labels of the source packages", alias="package.sourcePackageLabels")
    package_product_name: StrictStr = Field(description="Name of the product", alias="package.productName")
    package_product_category_name: StrictStr = Field(description="Category name of the product", alias="package.productCategoryName")
    package_item_strain_name: StrictStr = Field(description="Strain name of the item", alias="package.itemStrainName")
    package_lab_testing_state_name: StrictStr = Field(description="Lab testing status of the item", alias="package.labTestingStateName")
    package_shipped_quantity: Union[StrictFloat, StrictInt] = Field(description="Quantity shipped", alias="package.shippedQuantity")
    package_shipped_unit_of_measure_abbreviation: StrictStr = Field(description="Unit of measure for the shipped quantity", alias="package.shippedUnitOfMeasureAbbreviation")
    package_gross_weight: Union[StrictFloat, StrictInt] = Field(description="Gross weight of the package", alias="package.grossWeight")
    package_gross_unit_of_weight_abbreviation: StrictStr = Field(description="Unit of measure for the gross weight", alias="package.grossUnitOfWeightAbbreviation")
    package_shipper_wholesale_price: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Wholesale price from the shipper", alias="package.shipperWholesalePrice")
    package_received_quantity: Union[StrictFloat, StrictInt] = Field(description="Quantity received", alias="package.receivedQuantity")
    package_received_unit_of_measure_abbreviation: StrictStr = Field(description="Unit of measure for the received quantity", alias="package.receivedUnitOfMeasureAbbreviation")
    package_receiver_wholesale_price: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Wholesale price to the receiver", alias="package.receiverWholesalePrice")
    package_shipment_package_state_name: StrictStr = Field(description="State of the shipment package", alias="package.shipmentPackageStateName")
    package_actual_departure_date_time: Optional[datetime] = Field(default=None, description="Actual departure date and time", alias="package.actualDepartureDateTime")
    package_received_date_time: datetime = Field(description="Date and time when the package was received", alias="package.receivedDateTime")
    package_processing_job_type_name: Optional[StrictStr] = Field(default=None, alias="package.processingJobTypeName")
    __properties: ClassVar[List[str]] = ["transfer.dataModel", "transfer.retrievedAt", "transfer.licenseNumber", "transfer.index", "transfer.id", "transfer.manifestNumber", "transfer.shipmentLicenseTypeName", "transfer.shipperFacilityLicenseNumber", "transfer.shipperFacilityName", "transfer.name", "transfer.transporterFacilityLicenseNumber", "transfer.transporterFacilityName", "transfer.driverName", "transfer.driverOccupationalLicenseNumber", "transfer.driverVehicleLicenseNumber", "transfer.vehicleMake", "transfer.vehicleModel", "transfer.vehicleLicensePlateNumber", "transfer.deliveryFacilities", "transfer.deliveryCount", "transfer.receivedDeliveryCount", "transfer.packageCount", "transfer.receivedPackageCount", "transfer.containsPlantPackage", "transfer.containsProductPackage", "transfer.containsTradeSample", "transfer.containsDonation", "transfer.containsTestingSample", "transfer.containsProductRequiresRemediation", "transfer.containsRemediatedProductPackage", "transfer.editCount", "transfer.canEdit", "transfer.canEditOutgoingInactive", "transfer.isVoided", "transfer.createdDateTime", "transfer.createdByUserName", "transfer.lastModified", "transfer.deliveryId", "transfer.recipientFacilityId", "transfer.recipientFacilityLicenseNumber", "transfer.recipientFacilityName", "transfer.shipmentTypeName", "transfer.shipmentTransactionTypeName", "transfer.estimatedDepartureDateTime", "transfer.actualDepartureDateTime", "transfer.estimatedArrivalDateTime", "transfer.actualArrivalDateTime", "transfer.deliveryPackageCount", "transfer.deliveryReceivedPackageCount", "transfer.receivedByName", "transfer.receivedDateTime", "transfer.estimatedReturnDepartureDateTime", "transfer.actualReturnDepartureDateTime", "transfer.estimatedReturnArrivalDateTime", "transfer.actualReturnArrivalDateTime", "transfer.rejectedPackagesReturned", "transfer.transporterAllApprovalDate", "transfer.destinationsAllApprovalDate", "transfer.transportersAutomaticallyApproved", "transfer.destinationsAutomaticallyApproved", "transfer.approvalRejectDateTime", "transfer.approvalRejectedByUser", "transfer.approvalRejectedFacilityLicenseNumber", "transfer.approvalRejectReasonId", "transfer.tollingAgreementFileSystemId", "transfer.invoiceNumber", "transporter.dataModel", "transporter.retrievedAt", "transporter.licenseNumber", "transporter.transporterFacilityLicenseNumber", "transporter.transporterFacilityName", "transporter.transporterDirectionName", "transporter.transporterApprovalDate", "transporter.transporterAutoApproval", "transporter.driverName", "transporter.driverOccupationalLicenseNumber", "transporter.driverVehicleLicenseNumber", "transporter.driverLayoverLeg", "transporter.vehicleMake", "transporter.vehicleModel", "transporter.vehicleLicensePlateNumber", "transporter.acceptedDateTime", "transporter.isLayover", "transporter.estimatedDepartureDateTime", "transporter.actualDepartureDateTime", "transporter.estimatedArrivalDateTime", "transporter.actualArrivalDateTime", "package.id", "package.dataModel", "package.retrievedAt", "package.licenseNumber", "package.index", "package.packageId", "package.recipientFacilityLicenseNumber", "package.recipientFacilityName", "package.manifestNumber", "package.packageLabel", "package.sourceHarvestNames", "package.sourcePackageLabels", "package.productName", "package.productCategoryName", "package.itemStrainName", "package.labTestingStateName", "package.shippedQuantity", "package.shippedUnitOfMeasureAbbreviation", "package.grossWeight", "package.grossUnitOfWeightAbbreviation", "package.shipperWholesalePrice", "package.receivedQuantity", "package.receivedUnitOfMeasureAbbreviation", "package.receiverWholesalePrice", "package.shipmentPackageStateName", "package.actualDepartureDateTime", "package.receivedDateTime", "package.processingJobTypeName"]

    @field_validator('transfer_index')
    def transfer_index_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['ACTIVE_INCOMING_TRANSFER', 'INACTIVE_INCOMING_TRANSFER']):
            raise ValueError("must be one of enum values ('ACTIVE_INCOMING_TRANSFER', 'INACTIVE_INCOMING_TRANSFER')")
        return value

    @field_validator('transporter_transporter_direction_name')
    def transporter_transporter_direction_name_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['Outbound']):
            raise ValueError("must be one of enum values ('Outbound')")
        return value

    @field_validator('package_index')
    def package_index_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['TRANSFERRED_PACKAGE']):
            raise ValueError("must be one of enum values ('TRANSFERRED_PACKAGE')")
        return value

    @field_validator('package_lab_testing_state_name')
    def package_lab_testing_state_name_validate_enum(cls, value):
        """Validates the enum"""
        if value not in set(['TestPassed', 'TestFailed', 'Pending']):
            raise ValueError("must be one of enum values ('TestPassed', 'TestFailed', 'Pending')")
        return value

    @field_validator('package_shipment_package_state_name')
    def package_shipment_package_state_name_validate_enum(cls, value):
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
        """Create an instance of T3IncomingTransferManifest from a JSON string"""
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
        # set to None if transfer_name (nullable) is None
        # and model_fields_set contains the field
        if self.transfer_name is None and "transfer_name" in self.model_fields_set:
            _dict['transfer.name'] = None

        # set to None if transfer_actual_departure_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.transfer_actual_departure_date_time is None and "transfer_actual_departure_date_time" in self.model_fields_set:
            _dict['transfer.actualDepartureDateTime'] = None

        # set to None if transfer_actual_arrival_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.transfer_actual_arrival_date_time is None and "transfer_actual_arrival_date_time" in self.model_fields_set:
            _dict['transfer.actualArrivalDateTime'] = None

        # set to None if transfer_received_by_name (nullable) is None
        # and model_fields_set contains the field
        if self.transfer_received_by_name is None and "transfer_received_by_name" in self.model_fields_set:
            _dict['transfer.receivedByName'] = None

        # set to None if transfer_received_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.transfer_received_date_time is None and "transfer_received_date_time" in self.model_fields_set:
            _dict['transfer.receivedDateTime'] = None

        # set to None if transfer_estimated_return_departure_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.transfer_estimated_return_departure_date_time is None and "transfer_estimated_return_departure_date_time" in self.model_fields_set:
            _dict['transfer.estimatedReturnDepartureDateTime'] = None

        # set to None if transfer_actual_return_departure_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.transfer_actual_return_departure_date_time is None and "transfer_actual_return_departure_date_time" in self.model_fields_set:
            _dict['transfer.actualReturnDepartureDateTime'] = None

        # set to None if transfer_estimated_return_arrival_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.transfer_estimated_return_arrival_date_time is None and "transfer_estimated_return_arrival_date_time" in self.model_fields_set:
            _dict['transfer.estimatedReturnArrivalDateTime'] = None

        # set to None if transfer_actual_return_arrival_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.transfer_actual_return_arrival_date_time is None and "transfer_actual_return_arrival_date_time" in self.model_fields_set:
            _dict['transfer.actualReturnArrivalDateTime'] = None

        # set to None if transfer_approval_reject_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.transfer_approval_reject_date_time is None and "transfer_approval_reject_date_time" in self.model_fields_set:
            _dict['transfer.approvalRejectDateTime'] = None

        # set to None if transfer_approval_rejected_facility_license_number (nullable) is None
        # and model_fields_set contains the field
        if self.transfer_approval_rejected_facility_license_number is None and "transfer_approval_rejected_facility_license_number" in self.model_fields_set:
            _dict['transfer.approvalRejectedFacilityLicenseNumber'] = None

        # set to None if transfer_approval_reject_reason_id (nullable) is None
        # and model_fields_set contains the field
        if self.transfer_approval_reject_reason_id is None and "transfer_approval_reject_reason_id" in self.model_fields_set:
            _dict['transfer.approvalRejectReasonId'] = None

        # set to None if transporter_driver_layover_leg (nullable) is None
        # and model_fields_set contains the field
        if self.transporter_driver_layover_leg is None and "transporter_driver_layover_leg" in self.model_fields_set:
            _dict['transporter.driverLayoverLeg'] = None

        # set to None if transporter_accepted_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.transporter_accepted_date_time is None and "transporter_accepted_date_time" in self.model_fields_set:
            _dict['transporter.acceptedDateTime'] = None

        # set to None if transporter_estimated_departure_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.transporter_estimated_departure_date_time is None and "transporter_estimated_departure_date_time" in self.model_fields_set:
            _dict['transporter.estimatedDepartureDateTime'] = None

        # set to None if transporter_actual_departure_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.transporter_actual_departure_date_time is None and "transporter_actual_departure_date_time" in self.model_fields_set:
            _dict['transporter.actualDepartureDateTime'] = None

        # set to None if transporter_estimated_arrival_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.transporter_estimated_arrival_date_time is None and "transporter_estimated_arrival_date_time" in self.model_fields_set:
            _dict['transporter.estimatedArrivalDateTime'] = None

        # set to None if transporter_actual_arrival_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.transporter_actual_arrival_date_time is None and "transporter_actual_arrival_date_time" in self.model_fields_set:
            _dict['transporter.actualArrivalDateTime'] = None

        # set to None if package_source_harvest_names (nullable) is None
        # and model_fields_set contains the field
        if self.package_source_harvest_names is None and "package_source_harvest_names" in self.model_fields_set:
            _dict['package.sourceHarvestNames'] = None

        # set to None if package_source_package_labels (nullable) is None
        # and model_fields_set contains the field
        if self.package_source_package_labels is None and "package_source_package_labels" in self.model_fields_set:
            _dict['package.sourcePackageLabels'] = None

        # set to None if package_shipper_wholesale_price (nullable) is None
        # and model_fields_set contains the field
        if self.package_shipper_wholesale_price is None and "package_shipper_wholesale_price" in self.model_fields_set:
            _dict['package.shipperWholesalePrice'] = None

        # set to None if package_receiver_wholesale_price (nullable) is None
        # and model_fields_set contains the field
        if self.package_receiver_wholesale_price is None and "package_receiver_wholesale_price" in self.model_fields_set:
            _dict['package.receiverWholesalePrice'] = None

        # set to None if package_actual_departure_date_time (nullable) is None
        # and model_fields_set contains the field
        if self.package_actual_departure_date_time is None and "package_actual_departure_date_time" in self.model_fields_set:
            _dict['package.actualDepartureDateTime'] = None

        # set to None if package_processing_job_type_name (nullable) is None
        # and model_fields_set contains the field
        if self.package_processing_job_type_name is None and "package_processing_job_type_name" in self.model_fields_set:
            _dict['package.processingJobTypeName'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of T3IncomingTransferManifest from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "transfer.dataModel": obj.get("transfer.dataModel"),
            "transfer.retrievedAt": obj.get("transfer.retrievedAt"),
            "transfer.licenseNumber": obj.get("transfer.licenseNumber"),
            "transfer.index": obj.get("transfer.index"),
            "transfer.id": obj.get("transfer.id"),
            "transfer.manifestNumber": obj.get("transfer.manifestNumber"),
            "transfer.shipmentLicenseTypeName": obj.get("transfer.shipmentLicenseTypeName"),
            "transfer.shipperFacilityLicenseNumber": obj.get("transfer.shipperFacilityLicenseNumber"),
            "transfer.shipperFacilityName": obj.get("transfer.shipperFacilityName"),
            "transfer.name": obj.get("transfer.name"),
            "transfer.transporterFacilityLicenseNumber": obj.get("transfer.transporterFacilityLicenseNumber"),
            "transfer.transporterFacilityName": obj.get("transfer.transporterFacilityName"),
            "transfer.driverName": obj.get("transfer.driverName"),
            "transfer.driverOccupationalLicenseNumber": obj.get("transfer.driverOccupationalLicenseNumber"),
            "transfer.driverVehicleLicenseNumber": obj.get("transfer.driverVehicleLicenseNumber"),
            "transfer.vehicleMake": obj.get("transfer.vehicleMake"),
            "transfer.vehicleModel": obj.get("transfer.vehicleModel"),
            "transfer.vehicleLicensePlateNumber": obj.get("transfer.vehicleLicensePlateNumber"),
            "transfer.deliveryFacilities": obj.get("transfer.deliveryFacilities"),
            "transfer.deliveryCount": obj.get("transfer.deliveryCount"),
            "transfer.receivedDeliveryCount": obj.get("transfer.receivedDeliveryCount"),
            "transfer.packageCount": obj.get("transfer.packageCount"),
            "transfer.receivedPackageCount": obj.get("transfer.receivedPackageCount"),
            "transfer.containsPlantPackage": obj.get("transfer.containsPlantPackage"),
            "transfer.containsProductPackage": obj.get("transfer.containsProductPackage"),
            "transfer.containsTradeSample": obj.get("transfer.containsTradeSample"),
            "transfer.containsDonation": obj.get("transfer.containsDonation"),
            "transfer.containsTestingSample": obj.get("transfer.containsTestingSample"),
            "transfer.containsProductRequiresRemediation": obj.get("transfer.containsProductRequiresRemediation"),
            "transfer.containsRemediatedProductPackage": obj.get("transfer.containsRemediatedProductPackage"),
            "transfer.editCount": obj.get("transfer.editCount"),
            "transfer.canEdit": obj.get("transfer.canEdit"),
            "transfer.canEditOutgoingInactive": obj.get("transfer.canEditOutgoingInactive"),
            "transfer.isVoided": obj.get("transfer.isVoided"),
            "transfer.createdDateTime": obj.get("transfer.createdDateTime"),
            "transfer.createdByUserName": obj.get("transfer.createdByUserName"),
            "transfer.lastModified": obj.get("transfer.lastModified"),
            "transfer.deliveryId": obj.get("transfer.deliveryId"),
            "transfer.recipientFacilityId": obj.get("transfer.recipientFacilityId"),
            "transfer.recipientFacilityLicenseNumber": obj.get("transfer.recipientFacilityLicenseNumber"),
            "transfer.recipientFacilityName": obj.get("transfer.recipientFacilityName"),
            "transfer.shipmentTypeName": obj.get("transfer.shipmentTypeName"),
            "transfer.shipmentTransactionTypeName": obj.get("transfer.shipmentTransactionTypeName"),
            "transfer.estimatedDepartureDateTime": obj.get("transfer.estimatedDepartureDateTime"),
            "transfer.actualDepartureDateTime": obj.get("transfer.actualDepartureDateTime"),
            "transfer.estimatedArrivalDateTime": obj.get("transfer.estimatedArrivalDateTime"),
            "transfer.actualArrivalDateTime": obj.get("transfer.actualArrivalDateTime"),
            "transfer.deliveryPackageCount": obj.get("transfer.deliveryPackageCount"),
            "transfer.deliveryReceivedPackageCount": obj.get("transfer.deliveryReceivedPackageCount"),
            "transfer.receivedByName": obj.get("transfer.receivedByName"),
            "transfer.receivedDateTime": obj.get("transfer.receivedDateTime"),
            "transfer.estimatedReturnDepartureDateTime": obj.get("transfer.estimatedReturnDepartureDateTime"),
            "transfer.actualReturnDepartureDateTime": obj.get("transfer.actualReturnDepartureDateTime"),
            "transfer.estimatedReturnArrivalDateTime": obj.get("transfer.estimatedReturnArrivalDateTime"),
            "transfer.actualReturnArrivalDateTime": obj.get("transfer.actualReturnArrivalDateTime"),
            "transfer.rejectedPackagesReturned": obj.get("transfer.rejectedPackagesReturned"),
            "transfer.transporterAllApprovalDate": obj.get("transfer.transporterAllApprovalDate"),
            "transfer.destinationsAllApprovalDate": obj.get("transfer.destinationsAllApprovalDate"),
            "transfer.transportersAutomaticallyApproved": obj.get("transfer.transportersAutomaticallyApproved"),
            "transfer.destinationsAutomaticallyApproved": obj.get("transfer.destinationsAutomaticallyApproved"),
            "transfer.approvalRejectDateTime": obj.get("transfer.approvalRejectDateTime"),
            "transfer.approvalRejectedByUser": obj.get("transfer.approvalRejectedByUser"),
            "transfer.approvalRejectedFacilityLicenseNumber": obj.get("transfer.approvalRejectedFacilityLicenseNumber"),
            "transfer.approvalRejectReasonId": obj.get("transfer.approvalRejectReasonId"),
            "transfer.tollingAgreementFileSystemId": obj.get("transfer.tollingAgreementFileSystemId"),
            "transfer.invoiceNumber": obj.get("transfer.invoiceNumber"),
            "transporter.dataModel": obj.get("transporter.dataModel"),
            "transporter.retrievedAt": obj.get("transporter.retrievedAt"),
            "transporter.licenseNumber": obj.get("transporter.licenseNumber"),
            "transporter.transporterFacilityLicenseNumber": obj.get("transporter.transporterFacilityLicenseNumber"),
            "transporter.transporterFacilityName": obj.get("transporter.transporterFacilityName"),
            "transporter.transporterDirectionName": obj.get("transporter.transporterDirectionName"),
            "transporter.transporterApprovalDate": obj.get("transporter.transporterApprovalDate"),
            "transporter.transporterAutoApproval": obj.get("transporter.transporterAutoApproval"),
            "transporter.driverName": obj.get("transporter.driverName"),
            "transporter.driverOccupationalLicenseNumber": obj.get("transporter.driverOccupationalLicenseNumber"),
            "transporter.driverVehicleLicenseNumber": obj.get("transporter.driverVehicleLicenseNumber"),
            "transporter.driverLayoverLeg": obj.get("transporter.driverLayoverLeg"),
            "transporter.vehicleMake": obj.get("transporter.vehicleMake"),
            "transporter.vehicleModel": obj.get("transporter.vehicleModel"),
            "transporter.vehicleLicensePlateNumber": obj.get("transporter.vehicleLicensePlateNumber"),
            "transporter.acceptedDateTime": obj.get("transporter.acceptedDateTime"),
            "transporter.isLayover": obj.get("transporter.isLayover"),
            "transporter.estimatedDepartureDateTime": obj.get("transporter.estimatedDepartureDateTime"),
            "transporter.actualDepartureDateTime": obj.get("transporter.actualDepartureDateTime"),
            "transporter.estimatedArrivalDateTime": obj.get("transporter.estimatedArrivalDateTime"),
            "transporter.actualArrivalDateTime": obj.get("transporter.actualArrivalDateTime"),
            "package.id": obj.get("package.id"),
            "package.dataModel": obj.get("package.dataModel"),
            "package.retrievedAt": obj.get("package.retrievedAt"),
            "package.licenseNumber": obj.get("package.licenseNumber"),
            "package.index": obj.get("package.index"),
            "package.packageId": obj.get("package.packageId"),
            "package.recipientFacilityLicenseNumber": obj.get("package.recipientFacilityLicenseNumber"),
            "package.recipientFacilityName": obj.get("package.recipientFacilityName"),
            "package.manifestNumber": obj.get("package.manifestNumber"),
            "package.packageLabel": obj.get("package.packageLabel"),
            "package.sourceHarvestNames": obj.get("package.sourceHarvestNames"),
            "package.sourcePackageLabels": obj.get("package.sourcePackageLabels"),
            "package.productName": obj.get("package.productName"),
            "package.productCategoryName": obj.get("package.productCategoryName"),
            "package.itemStrainName": obj.get("package.itemStrainName"),
            "package.labTestingStateName": obj.get("package.labTestingStateName"),
            "package.shippedQuantity": obj.get("package.shippedQuantity"),
            "package.shippedUnitOfMeasureAbbreviation": obj.get("package.shippedUnitOfMeasureAbbreviation"),
            "package.grossWeight": obj.get("package.grossWeight"),
            "package.grossUnitOfWeightAbbreviation": obj.get("package.grossUnitOfWeightAbbreviation"),
            "package.shipperWholesalePrice": obj.get("package.shipperWholesalePrice"),
            "package.receivedQuantity": obj.get("package.receivedQuantity"),
            "package.receivedUnitOfMeasureAbbreviation": obj.get("package.receivedUnitOfMeasureAbbreviation"),
            "package.receiverWholesalePrice": obj.get("package.receiverWholesalePrice"),
            "package.shipmentPackageStateName": obj.get("package.shipmentPackageStateName"),
            "package.actualDepartureDateTime": obj.get("package.actualDepartureDateTime"),
            "package.receivedDateTime": obj.get("package.receivedDateTime"),
            "package.processingJobTypeName": obj.get("package.processingJobTypeName")
        })
        return _obj


