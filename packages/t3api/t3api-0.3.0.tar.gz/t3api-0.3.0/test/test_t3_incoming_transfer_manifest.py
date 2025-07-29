# coding: utf-8

"""
    T3 API

    ## WHAT IS THIS?  This API is part of the [Track & Trace Tools](https://trackandtrace.tools) platform. The API allows you to programmatically access all your Metrc data that is available on metrc.com  It is not related to the Metrc 3rd party API, does not use Metrc API keys, and is not affiliated with Metrc.  If you're looking for where to get started, check out the [T3 Wiki API Getting Started guide](https://github.com/classvsoftware/t3-wiki/wiki/T3-API-:-Getting-Started).  The T3 API is subject to the [Track & Trace Tools Terms of Use](https://www.trackandtrace.tools/terms-of-use).   ## FREE API ACCESS (LIMITED)  The T3 API features a limited number of free endpoints available to anyone with a Metrc login.  These can be found in the [Free](#/Free) section.  ## FULL API ACCESS  There are two ways to get premium access to the T3 API:  - **Subscribe to [T3+](https://trackandtrace.tools/plus)**  *OR*  - **Use a provided T3 API key (consulting clients only. [Reach out](mailto:matt@trackandtrace.tools) for more information.)**  ## AUTHENTICATION  The T3 API uses JSON Web Tokens (JWT) for request authentication. To obtain a JWT, use one of the following:  - **metrc.com login credentials:**   - **hostname**: (The website you use to login to metrc: `ca.metrc.com`, `or.metrc.com`, etc.)   - **username**: Your Metrc username   - **password**: Your Metrc password   - **otp**: A one-time password used for 2-factor authentication (Only applies to Michigan users)  *OR*  - **T3 API key**  Refer to the **Authentication** endpoints below for more information.  ## SECRET KEYS  Some endpoints support the use of secret key authentication. This allows you to use simple URLs to access your Metrc data.  ### Usage  Pass the `secretKey` returned from the request in the query string:  `?secretKey=<yourSecretKeyGoesHere>`  ### Generating Secret Keys  Refer to the [/v2/auth/secretkey](#/Authentication/post_v2_auth_secretkey) endpoint for information on generating secret keys.  [Secret Key Generation Tool](/v2/pages/secret-key)  [Sync Link Creation Tool](/v2/pages/sync-link)  ## SECURITY  The T3 API interacts with Metrc in a similar manner to the [Track & Trace Tools](https://chromewebstore.google.com/detail/track-trace-tools/dfljickgkbfaoiifheibjpejloipegcb) Chrome extension. The API login process is designed with a strong emphasis on security. Your Metrc login details are never stored, and the API backend employs robust encryption methods to protect your temporary Metrc session.  ### Key Security Measures:  - **Single-Use Login Credentials:**    - The T3 API uses your login credentials only once to authenticate with Metrc.   - After the Metrc login process is complete, your login credentials are immediately deleted from the system.   - You are required to enter your login credentials each time you access the T3 API, ensuring that your credentials are never stored.    - **Secure Temporary Session Storage:**    - The T3 API securely encrypts your logged-in Metrc session data. This data is only used when you make requests through the T3 API.   - The encrypted session data is automatically deleted after 24 hours, ensuring that your session information is not retained longer than necessary.  For any questions or concerns, please contact [matt@trackandtrace.tools](mailto:matt@trackandtrace.tools).  ## PRIVACY  The T3 API privacy model follows the same principles as the [Track & Trace Tools](https://chromewebstore.google.com/detail/track-trace-tools/dfljickgkbfaoiifheibjpejloipegcb) Chrome extension. The T3 API functions solely as a connector between you and Metrc, ensuring your privacy is protected.  - **No Data Collection:**    - The T3 API does not record, save, harvest, inspect, or analyze any of your data.   - All data interactions are ephemeral and occur in real-time, without permanent storage.  - **Secure and Private Access:**    - Your data is never shared with third parties. Unauthorized access to your login information or data is strictly prohibited.   - T3 employs industry-standard encryption protocols to safeguard all communications between the T3 API and Metrc.    - **User-Controlled Sessions:**    - Your Metrc login credentials and session are used exclusively by you. The T3 API will never initiate Metrc traffic without your explicit authorization.  - **Compliance and Best Practices:**   - T3's privacy practices are aligned with applicable data protection regulations, including GDPR and CCPA, ensuring that your data rights are respected.  The T3 API is subject to the [Track & Trace Tools Privacy Policy](https://trackandtrace.tools/privacy-policy). For any privacy-related inquiries, please contact [matt@trackandtrace.tools](mailto:matt@trackandtrace.tools).  ## PERMISSIONS  Each Metrc account has different permissions based on several factors:  - Permissions granted by your Metrc admin - Class of license (manufacturing, cultivation, etc) - US state the license operates in  Use the Permissions endpoints to determine which actions are available to you.  ## LICENSES  View a list of all licenses available to the current user:  `GET https://api.trackandtrace.tools/v2/licenses`  Only one license can be queried per request. Specify the target license with the required `licenseNumber` query parameter:  `GET https://api.trackandtrace.tools/v2/items?licenseNumber=LIC-00001`  ## RATE LIMITING  The API has a global default request rate limit of 600 requests/minute/user. Some routes have lower rate limits.  ## COLLECTIONS  All data is queried as collections. There are no individual object endpoints.  For example, you cannot find an individual object using an endpoint like `/plants/{plantId}`, individual objects must be queried by filtering the collection endpoint `/plants` for the exact `plantId`.   Collections are paginated, and can be filtered and sorted by individual object fields.  The JSON response object includes the following properties: - `data`: An array of objects, or any empty array - `page`: The requested page index - `pageSize`: The requested page size - `total`: The total number of items in this collection. Use this to determine how many pages are required to return the entire collection.  ### COLLECTION PAGINATION  Metrc data collections are queried as pages. Use the `page` and `pageSize` query parameters to indicate which page should be returned.  By default, `page=1` and `pageSize=100`.  Example: Return page 3 with a page size of 500:  `GET https://api.trackandtrace.tools/v2/items?licenseNumber=LIC-00001&page=3&pageSize=500`  ### COLLECTION SORTING  Metrc data collections can be sorted. Use the `sort` query parameter to indicate how the collection should be sorted.  Example: Sort items by `name` descending:  `GET https://api.trackandtrace.tools/v2/items?licenseNumber=LIC-00001&sort=name:desc`  ### COLLECTION FILTERING  Metrc data collections can be filtered. Use one or more `filter` query parameters to indicate how filters should be applied.  Example: Filter items that contain \"flower\" in the `name` field:  `GET https://api.trackandtrace.tools/v2/items?licenseNumber=LIC-00001&filter:name__contains=flower`  Multiple filters can be applied, and you can specify the logical operator (defaulting to \"and\"):  Example: Filter items that contain \"flower\" in the `name` field OR \"kush\" in the `name` field:  `GET https://api.trackandtrace.tools/v2/items?licenseNumber=LIC-00001&filter=name__contains:flower&filter=name__contains:kush&filterLogic=or`  #### FILTERING STRINGS  String fields support the following filter operators:  - `contains` - `doesnotcontain` - `eq` - `neq` - `startswith` - `endswith`  Example `?filter=name__contains:flower`  **Note: all string filters are case-insensitive**  #### FILTERING DATETIMES  Datetime fields support the following filter operators:  - `lt` - `lte` - `eq` - `neq` - `gt` - `gte`  Example: `?filter=harvestedDate__gte:2024-07-17T20:26:07.117Z`  **Note: all datetime filters use ISO8601 datetimes**  #### FILTERING BOOLEANS  Boolean fields support the following filter operators:  - `eq`  Example: `?filter=finished__eq:true`  ### LOADING FULL COLLECTIONS `pageSize` is limited to 500 in most cases, so you may need to load multiple pages if a license has a large number of packages.  Refer to [this example](https://github.com/classvsoftware/t3-api/blob/master/load_all_active_packages.py) for how to load a full collection in a python script.  ## USING THE API  The API can be used in any way you like, but writing simple scripts to accomplish common tasks is an excellent way to take advantage of it.  The full OpenAPI spec, which can be imported into Postman, can be found here: [/v2/spec/openapi.json](/v2/spec/openapi.json)  [**Lots** of example scripts that show how the use the T3 API can be found here](https://github.com/classvsoftware/t3-api)  ## CONTACT  - **Responsible Organization:** Class V LLC - **Responsible Developer:** Matt Frisbie - **Email:** [matt@trackandtrace.tools](mailto:matt@trackandtrace.tools) - **URL:** [https://trackandtrace.tools](https://trackandtrace.tools) - **Terms of Use:** [https://www.trackandtrace.tools/terms-of-use](https://www.trackandtrace.tools/terms-of-use) 

    The version of the OpenAPI document: v2
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from t3api.models.t3_incoming_transfer_manifest import T3IncomingTransferManifest

class TestT3IncomingTransferManifest(unittest.TestCase):
    """T3IncomingTransferManifest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> T3IncomingTransferManifest:
        """Test T3IncomingTransferManifest
            include_optional is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `T3IncomingTransferManifest`
        """
        model = T3IncomingTransferManifest()
        if include_optional:
            return T3IncomingTransferManifest(
                transfer_data_model = 'MetrcPackage',
                transfer_retrieved_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                transfer_license_number = '',
                transfer_index = 'ACTIVE_INCOMING_TRANSFER',
                transfer_id = 1234567,
                transfer_manifest_number = '0001234567',
                transfer_shipment_license_type_name = 'Licensed',
                transfer_shipper_facility_license_number = 'LIC-00002',
                transfer_shipper_facility_name = 'Fire Manufacturing, Inc.',
                transfer_name = '',
                transfer_transporter_facility_license_number = '',
                transfer_transporter_facility_name = '',
                transfer_driver_name = '',
                transfer_driver_occupational_license_number = '',
                transfer_driver_vehicle_license_number = '',
                transfer_vehicle_make = '',
                transfer_vehicle_model = '',
                transfer_vehicle_license_plate_number = '',
                transfer_delivery_facilities = 'LIC-00001 (Dank Dispensary LLC)',
                transfer_delivery_count = 1,
                transfer_received_delivery_count = 0,
                transfer_package_count = 8,
                transfer_received_package_count = 0,
                transfer_contains_plant_package = False,
                transfer_contains_product_package = True,
                transfer_contains_trade_sample = False,
                transfer_contains_donation = False,
                transfer_contains_testing_sample = False,
                transfer_contains_product_requires_remediation = False,
                transfer_contains_remediated_product_package = False,
                transfer_edit_count = 1,
                transfer_can_edit = True,
                transfer_can_edit_outgoing_inactive = False,
                transfer_is_voided = False,
                transfer_created_date_time = '2024-07-25T13:00Z',
                transfer_created_by_user_name = 'Mike Smith',
                transfer_last_modified = '2024-07-25T00:00Z',
                transfer_delivery_id = 1234566,
                transfer_recipient_facility_id = 456,
                transfer_recipient_facility_license_number = 'LIC-00001',
                transfer_recipient_facility_name = 'Dank Dispensary LLC',
                transfer_shipment_type_name = 'Unaffiliated Transfer',
                transfer_shipment_transaction_type_name = 'Wholesale',
                transfer_estimated_departure_date_time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                transfer_actual_departure_date_time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                transfer_estimated_arrival_date_time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                transfer_actual_arrival_date_time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                transfer_delivery_package_count = 8,
                transfer_delivery_received_package_count = 0,
                transfer_received_by_name = '',
                transfer_received_date_time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                transfer_estimated_return_departure_date_time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                transfer_actual_return_departure_date_time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                transfer_estimated_return_arrival_date_time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                transfer_actual_return_arrival_date_time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                transfer_rejected_packages_returned = False,
                transfer_transporter_all_approval_date = '2024-07-25T13:00Z',
                transfer_destinations_all_approval_date = '2024-07-25T13:00Z',
                transfer_transporters_automatically_approved = True,
                transfer_destinations_automatically_approved = True,
                transfer_approval_reject_date_time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                transfer_approval_rejected_by_user = 'Mike Smith',
                transfer_approval_rejected_facility_license_number = '',
                transfer_approval_reject_reason_id = '',
                transfer_tolling_agreement_file_system_id = 0,
                transfer_invoice_number = '',
                transporter_data_model = 'MetrcPackage',
                transporter_retrieved_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                transporter_license_number = '',
                transporter_transporter_facility_license_number = 'LIC-00001',
                transporter_transporter_facility_name = 'Dank Dispensary LLC',
                transporter_transporter_direction_name = 'Outbound',
                transporter_transporter_approval_date = '2024-07-26T13:00Z',
                transporter_transporter_auto_approval = True,
                transporter_driver_name = 'John Doe',
                transporter_driver_occupational_license_number = 'DL123456789',
                transporter_driver_vehicle_license_number = 'ABC1234',
                transporter_driver_layover_leg = '',
                transporter_vehicle_make = 'Ford',
                transporter_vehicle_model = 'F-150',
                transporter_vehicle_license_plate_number = 'XYZ7890',
                transporter_accepted_date_time = '2024-07-26T13:00-05:00',
                transporter_is_layover = False,
                transporter_estimated_departure_date_time = '2024-07-26T14:00Z',
                transporter_actual_departure_date_time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                transporter_estimated_arrival_date_time = '2024-07-26T15:00Z',
                transporter_actual_arrival_date_time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                package_id = 1234567,
                package_data_model = 'MetrcPackage',
                package_retrieved_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                package_license_number = '',
                package_index = 'TRANSFERRED_PACKAGE',
                package_package_id = 9876543,
                package_recipient_facility_license_number = 'LIC-00001',
                package_recipient_facility_name = 'Dank Dispensary LLC',
                package_manifest_number = '0001234567',
                package_package_label = '1A4000000000000000006310',
                package_source_harvest_names = 'Sunset Sherbet',
                package_source_package_labels = '1A4000000000000000005267',
                package_product_name = 'Sunset Sherbet | 3.5g',
                package_product_category_name = 'Bud/Flower (Final Packaging)',
                package_item_strain_name = 'Sunset Sherbet',
                package_lab_testing_state_name = 'TestPassed',
                package_shipped_quantity = 1224.0,
                package_shipped_unit_of_measure_abbreviation = 'g',
                package_gross_weight = 224.0,
                package_gross_unit_of_weight_abbreviation = 'g',
                package_shipper_wholesale_price = 1.337,
                package_received_quantity = 1224.0,
                package_received_unit_of_measure_abbreviation = 'g',
                package_receiver_wholesale_price = 1.337,
                package_shipment_package_state_name = 'Accepted',
                package_actual_departure_date_time = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                package_received_date_time = '2024-07-26T00:00-05:00',
                package_processing_job_type_name = ''
            )
        else:
            return T3IncomingTransferManifest(
                package_id = 1234567,
                package_package_id = 9876543,
                package_recipient_facility_license_number = 'LIC-00001',
                package_recipient_facility_name = 'Dank Dispensary LLC',
                package_manifest_number = '0001234567',
                package_package_label = '1A4000000000000000006310',
                package_product_name = 'Sunset Sherbet | 3.5g',
                package_product_category_name = 'Bud/Flower (Final Packaging)',
                package_item_strain_name = 'Sunset Sherbet',
                package_lab_testing_state_name = 'TestPassed',
                package_shipped_quantity = 1224.0,
                package_shipped_unit_of_measure_abbreviation = 'g',
                package_gross_weight = 224.0,
                package_gross_unit_of_weight_abbreviation = 'g',
                package_received_quantity = 1224.0,
                package_received_unit_of_measure_abbreviation = 'g',
                package_shipment_package_state_name = 'Accepted',
                package_received_date_time = '2024-07-26T00:00-05:00',
        )
        """

    def testT3IncomingTransferManifest(self):
        """Test T3IncomingTransferManifest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
