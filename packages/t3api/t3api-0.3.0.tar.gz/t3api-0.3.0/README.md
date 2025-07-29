# t3api
## WHAT IS THIS?

This API is part of the [Track & Trace Tools](https://trackandtrace.tools) platform. The API allows you to programmatically access all your Metrc data that is available on metrc.com

It is not related to the Metrc 3rd party API, does not use Metrc API keys, and is not affiliated with Metrc.

If you're looking for where to get started, check out the [T3 Wiki API Getting Started guide](https://github.com/classvsoftware/t3-wiki/wiki/T3-API-:-Getting-Started).

The T3 API is subject to the [Track & Trace Tools Terms of Use](https://www.trackandtrace.tools/terms-of-use). 

## FREE API ACCESS (LIMITED)

The T3 API features a limited number of free endpoints available to anyone with a Metrc login.

These can be found in the [Free](#/Free) section.

## FULL API ACCESS

There are two ways to get premium access to the T3 API:

- **Subscribe to [T3+](https://trackandtrace.tools/plus)**

*OR*

- **Use a provided T3 API key (consulting clients only. [Reach out](mailto:matt@trackandtrace.tools) for more information.)**

## AUTHENTICATION

The T3 API uses JSON Web Tokens (JWT) for request authentication. To obtain a JWT, use one of the following:

- **metrc.com login credentials:**
  - **hostname**: (The website you use to login to metrc: `ca.metrc.com`, `or.metrc.com`, etc.)
  - **username**: Your Metrc username
  - **password**: Your Metrc password
  - **otp**: A one-time password used for 2-factor authentication (Only applies to Michigan users)

*OR*

- **T3 API key**

Refer to the **Authentication** endpoints below for more information.

## SECRET KEYS

Some endpoints support the use of secret key authentication. This allows you to use simple URLs to access your Metrc data.

### Usage

Pass the `secretKey` returned from the request in the query string:

`?secretKey=<yourSecretKeyGoesHere>`

### Generating Secret Keys

Refer to the [/v2/auth/secretkey](#/Authentication/post_v2_auth_secretkey) endpoint for information on generating secret keys.

[Secret Key Generation Tool](/v2/pages/secret-key)

[Sync Link Creation Tool](/v2/pages/sync-link)

## SECURITY

The T3 API interacts with Metrc in a similar manner to the [Track & Trace Tools](https://chromewebstore.google.com/detail/track-trace-tools/dfljickgkbfaoiifheibjpejloipegcb) Chrome extension. The API login process is designed with a strong emphasis on security. Your Metrc login details are never stored, and the API backend employs robust encryption methods to protect your temporary Metrc session.

### Key Security Measures:

- **Single-Use Login Credentials:** 
  - The T3 API uses your login credentials only once to authenticate with Metrc.
  - After the Metrc login process is complete, your login credentials are immediately deleted from the system.
  - You are required to enter your login credentials each time you access the T3 API, ensuring that your credentials are never stored.
  
- **Secure Temporary Session Storage:** 
  - The T3 API securely encrypts your logged-in Metrc session data. This data is only used when you make requests through the T3 API.
  - The encrypted session data is automatically deleted after 24 hours, ensuring that your session information is not retained longer than necessary.

For any questions or concerns, please contact [matt@trackandtrace.tools](mailto:matt@trackandtrace.tools).

## PRIVACY

The T3 API privacy model follows the same principles as the [Track & Trace Tools](https://chromewebstore.google.com/detail/track-trace-tools/dfljickgkbfaoiifheibjpejloipegcb) Chrome extension. The T3 API functions solely as a connector between you and Metrc, ensuring your privacy is protected.

- **No Data Collection:** 
  - The T3 API does not record, save, harvest, inspect, or analyze any of your data.
  - All data interactions are ephemeral and occur in real-time, without permanent storage.

- **Secure and Private Access:** 
  - Your data is never shared with third parties. Unauthorized access to your login information or data is strictly prohibited.
  - T3 employs industry-standard encryption protocols to safeguard all communications between the T3 API and Metrc.
  
- **User-Controlled Sessions:** 
  - Your Metrc login credentials and session are used exclusively by you. The T3 API will never initiate Metrc traffic without your explicit authorization.

- **Compliance and Best Practices:**
  - T3's privacy practices are aligned with applicable data protection regulations, including GDPR and CCPA, ensuring that your data rights are respected.

The T3 API is subject to the [Track & Trace Tools Privacy Policy](https://trackandtrace.tools/privacy-policy). For any privacy-related inquiries, please contact [matt@trackandtrace.tools](mailto:matt@trackandtrace.tools).

## PERMISSIONS

Each Metrc account has different permissions based on several factors:

- Permissions granted by your Metrc admin
- Class of license (manufacturing, cultivation, etc)
- US state the license operates in

Use the Permissions endpoints to determine which actions are available to you.

## LICENSES

View a list of all licenses available to the current user:

`GET https://api.trackandtrace.tools/v2/licenses`

Only one license can be queried per request. Specify the target license with the required `licenseNumber` query parameter:

`GET https://api.trackandtrace.tools/v2/items?licenseNumber=LIC-00001`

## RATE LIMITING

The API has a global default request rate limit of 600 requests/minute/user. Some routes have lower rate limits.

## COLLECTIONS

All data is queried as collections. There are no individual object endpoints.  For example, you cannot find an individual object using an endpoint like `/plants/{plantId}`, individual objects must be queried by filtering the collection endpoint `/plants` for the exact `plantId`. 

Collections are paginated, and can be filtered and sorted by individual object fields.

The JSON response object includes the following properties:
- `data`: An array of objects, or any empty array
- `page`: The requested page index
- `pageSize`: The requested page size
- `total`: The total number of items in this collection. Use this to determine how many pages are required to return the entire collection.

### COLLECTION PAGINATION

Metrc data collections are queried as pages. Use the `page` and `pageSize` query parameters to indicate which page should be returned.

By default, `page=1` and `pageSize=100`.

Example: Return page 3 with a page size of 500:

`GET https://api.trackandtrace.tools/v2/items?licenseNumber=LIC-00001&page=3&pageSize=500`

### COLLECTION SORTING

Metrc data collections can be sorted. Use the `sort` query parameter to indicate how the collection should be sorted.

Example: Sort items by `name` descending:

`GET https://api.trackandtrace.tools/v2/items?licenseNumber=LIC-00001&sort=name:desc`

### COLLECTION FILTERING

Metrc data collections can be filtered. Use one or more `filter` query parameters to indicate how filters should be applied.

Example: Filter items that contain \"flower\" in the `name` field:

`GET https://api.trackandtrace.tools/v2/items?licenseNumber=LIC-00001&filter:name__contains=flower`

Multiple filters can be applied, and you can specify the logical operator (defaulting to \"and\"):

Example: Filter items that contain \"flower\" in the `name` field OR \"kush\" in the `name` field:

`GET https://api.trackandtrace.tools/v2/items?licenseNumber=LIC-00001&filter=name__contains:flower&filter=name__contains:kush&filterLogic=or`

#### FILTERING STRINGS

String fields support the following filter operators:

- `contains`
- `doesnotcontain`
- `eq`
- `neq`
- `startswith`
- `endswith`

Example `?filter=name__contains:flower`

**Note: all string filters are case-insensitive**

#### FILTERING DATETIMES

Datetime fields support the following filter operators:

- `lt`
- `lte`
- `eq`
- `neq`
- `gt`
- `gte`

Example: `?filter=harvestedDate__gte:2024-07-17T20:26:07.117Z`

**Note: all datetime filters use ISO8601 datetimes**

#### FILTERING BOOLEANS

Boolean fields support the following filter operators:

- `eq`

Example: `?filter=finished__eq:true`

### LOADING FULL COLLECTIONS
`pageSize` is limited to 500 in most cases, so you may need to load multiple pages if a license has a large number of packages.

Refer to [this example](https://github.com/classvsoftware/t3-api/blob/master/load_all_active_packages.py) for how to load a full collection in a python script.

## USING THE API

The API can be used in any way you like, but writing simple scripts to accomplish common tasks is an excellent way to take advantage of it.

The full OpenAPI spec, which can be imported into Postman, can be found here: [/v2/spec/openapi.json](/v2/spec/openapi.json)

[**Lots** of example scripts that show how the use the T3 API can be found here](https://github.com/classvsoftware/t3-api)

## CONTACT

- **Responsible Organization:** Class V LLC
- **Responsible Developer:** Matt Frisbie
- **Email:** [matt@trackandtrace.tools](mailto:matt@trackandtrace.tools)
- **URL:** [https://trackandtrace.tools](https://trackandtrace.tools)
- **Terms of Use:** [https://www.trackandtrace.tools/terms-of-use](https://www.trackandtrace.tools/terms-of-use)


This Python package is automatically generated by the [OpenAPI Generator](https://openapi-generator.tech) project:

- API version: v2
- Package version: 1.0.0
- Generator version: 7.13.0
- Build package: org.openapitools.codegen.languages.PythonClientCodegen

## Requirements.

Python 3.9+

## Installation & Usage
### pip install

If the python package is hosted on a repository, you can install directly using:

```sh
pip install git+https://github.com/GIT_USER_ID/GIT_REPO_ID.git
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/GIT_USER_ID/GIT_REPO_ID.git`)

Then import the package:
```python
import t3api
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import t3api
```

### Tests

Execute `pytest` to run the tests.

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import t3api
from t3api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.trackandtrace.tools
# See configuration.py for a list of all supported configuration parameters.
configuration = t3api.Configuration(
    host = "https://api.trackandtrace.tools"
)



# Enter a context with an instance of the API client
with t3api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = t3api.AuthenticationApi(api_client)
    v2_auth_apikey_post_request = t3api.V2AuthApikeyPostRequest() # V2AuthApikeyPostRequest | JSON object containing your API key authentication details 

    try:
        # Authenticate with a T3 API key
        api_response = api_instance.v2_auth_apikey_post(v2_auth_apikey_post_request)
        print("The response of AuthenticationApi->v2_auth_apikey_post:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AuthenticationApi->v2_auth_apikey_post: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *https://api.trackandtrace.tools*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*AuthenticationApi* | [**v2_auth_apikey_post**](docs/AuthenticationApi.md#v2_auth_apikey_post) | **POST** /v2/auth/apikey | Authenticate with a T3 API key
*AuthenticationApi* | [**v2_auth_credentials_post**](docs/AuthenticationApi.md#v2_auth_credentials_post) | **POST** /v2/auth/credentials | Authenticate with Metrc credentials
*AuthenticationApi* | [**v2_auth_secretkey_post**](docs/AuthenticationApi.md#v2_auth_secretkey_post) | **POST** /v2/auth/secretkey | Generate a secret key that can be used for special T3 routes that support secrey key authentication.
*AuthenticationApi* | [**v2_auth_whoami_get**](docs/AuthenticationApi.md#v2_auth_whoami_get) | **GET** /v2/auth/whoami | Returns information about the authenticated user
*CreatePackageApi* | [**v2_packages_create_inputs_get**](docs/CreatePackageApi.md#v2_packages_create_inputs_get) | **GET** /v2/packages/create/inputs | Input data used for creating new packages
*CreatePackageApi* | [**v2_packages_create_post**](docs/CreatePackageApi.md#v2_packages_create_post) | **POST** /v2/packages/create | Create one or more packages from existing active packages
*CreatePackageApi* | [**v2_packages_create_source_items_get**](docs/CreatePackageApi.md#v2_packages_create_source_items_get) | **GET** /v2/packages/create/source-items | List of items eligible to be used in creating new packages
*CreatePackageApi* | [**v2_packages_create_source_packages_get**](docs/CreatePackageApi.md#v2_packages_create_source_packages_get) | **GET** /v2/packages/create/source-packages | List of packages eligible to be used in creating new packages
*CreateTransferApi* | [**v2_transfers_create_destinations_get**](docs/CreateTransferApi.md#v2_transfers_create_destinations_get) | **GET** /v2/transfers/create/destinations | List of destination facilities eligible to be used in creating new transfers
*CreateTransferApi* | [**v2_transfers_create_inputs_get**](docs/CreateTransferApi.md#v2_transfers_create_inputs_get) | **GET** /v2/transfers/create/inputs | Input data used for creating new transers
*CreateTransferApi* | [**v2_transfers_create_post**](docs/CreateTransferApi.md#v2_transfers_create_post) | **POST** /v2/transfers/create | Create one or more transfers
*CreateTransferApi* | [**v2_transfers_create_transporters_get**](docs/CreateTransferApi.md#v2_transfers_create_transporters_get) | **GET** /v2/transfers/create/transporters | List of transporter facilities eligible to be used in creating new transfers
*FacilitiesApi* | [**v2_transfers_create_destinations_get**](docs/FacilitiesApi.md#v2_transfers_create_destinations_get) | **GET** /v2/transfers/create/destinations | List of destination facilities eligible to be used in creating new transfers
*FacilitiesApi* | [**v2_transfers_create_transporters_get**](docs/FacilitiesApi.md#v2_transfers_create_transporters_get) | **GET** /v2/transfers/create/transporters | List of transporter facilities eligible to be used in creating new transfers
*FreeApi* | [**v2_auth_credentials_post**](docs/FreeApi.md#v2_auth_credentials_post) | **POST** /v2/auth/credentials | Authenticate with Metrc credentials
*FreeApi* | [**v2_auth_whoami_get**](docs/FreeApi.md#v2_auth_whoami_get) | **GET** /v2/auth/whoami | Returns information about the authenticated user
*FreeApi* | [**v2_files_labels_content_data_packages_active_post**](docs/FreeApi.md#v2_files_labels_content_data_packages_active_post) | **POST** /v2/files/labels/content-data/packages/active | For a given list of active packages, returns the needed ContentDataList to render the labels.
*FreeApi* | [**v2_files_labels_content_data_packages_intransit_post**](docs/FreeApi.md#v2_files_labels_content_data_packages_intransit_post) | **POST** /v2/files/labels/content-data/packages/intransit | For a given list of in transit packages, returns the needed ContentDataList to render the labels.
*FreeApi* | [**v2_files_labels_generate_post**](docs/FreeApi.md#v2_files_labels_generate_post) | **POST** /v2/files/labels/generate | Generate a PDF of labels.
*FreeApi* | [**v2_files_labels_label_content_layouts_get**](docs/FreeApi.md#v2_files_labels_label_content_layouts_get) | **GET** /v2/files/labels/label-content-layouts | Returns a list of label content layouts
*FreeApi* | [**v2_files_labels_label_template_layouts_get**](docs/FreeApi.md#v2_files_labels_label_template_layouts_get) | **GET** /v2/files/labels/label-template-layouts | Returns a list of label template layouts
*FreeApi* | [**v2_licenses_get**](docs/FreeApi.md#v2_licenses_get) | **GET** /v2/licenses | List of accessible licenses
*FreeApi* | [**v2_permissions_get**](docs/FreeApi.md#v2_permissions_get) | **GET** /v2/permissions | List of all permissions within a single view
*FreeApi* | [**v2_permissions_views_get**](docs/FreeApi.md#v2_permissions_views_get) | **GET** /v2/permissions/views | List of all available permission views
*FreeApi* | [**v2_search_get**](docs/FreeApi.md#v2_search_get) | **GET** /v2/search | Generic text search endpoint
*FreeApi* | [**v2_states_get**](docs/FreeApi.md#v2_states_get) | **GET** /v2/states | List of accessible states
*HarvestsApi* | [**v2_harvests_active_get**](docs/HarvestsApi.md#v2_harvests_active_get) | **GET** /v2/harvests/active | List of active harvests
*HarvestsApi* | [**v2_harvests_active_report_get**](docs/HarvestsApi.md#v2_harvests_active_report_get) | **GET** /v2/harvests/active/report | Generate a report of all active harvests
*HarvestsApi* | [**v2_harvests_history_get**](docs/HarvestsApi.md#v2_harvests_history_get) | **GET** /v2/harvests/history | List of history objects for a single harvest.
*HarvestsApi* | [**v2_harvests_inactive_get**](docs/HarvestsApi.md#v2_harvests_inactive_get) | **GET** /v2/harvests/inactive | List of inactive harvests
*HarvestsApi* | [**v2_harvests_inactive_report_get**](docs/HarvestsApi.md#v2_harvests_inactive_report_get) | **GET** /v2/harvests/inactive/report | Generate a report of all active harvests
*HarvestsApi* | [**v2_harvests_onhold_get**](docs/HarvestsApi.md#v2_harvests_onhold_get) | **GET** /v2/harvests/onhold | List of on hold harvests
*HarvestsApi* | [**v2_packages_source_harvests_get**](docs/HarvestsApi.md#v2_packages_source_harvests_get) | **GET** /v2/packages/source-harvests | List of package source harvest objects for a single package
*HistoryApi* | [**v2_harvests_history_get**](docs/HistoryApi.md#v2_harvests_history_get) | **GET** /v2/harvests/history | List of history objects for a single harvest.
*HistoryApi* | [**v2_items_history_get**](docs/HistoryApi.md#v2_items_history_get) | **GET** /v2/items/history | List of item history objects for a single item
*HistoryApi* | [**v2_packages_history_get**](docs/HistoryApi.md#v2_packages_history_get) | **GET** /v2/packages/history | List of package history objects for a single package
*HistoryApi* | [**v2_plantbatches_history_get**](docs/HistoryApi.md#v2_plantbatches_history_get) | **GET** /v2/plantbatches/history | List of history objects for a single plant batch
*HistoryApi* | [**v2_plants_history_get**](docs/HistoryApi.md#v2_plants_history_get) | **GET** /v2/plants/history | List of history objects for a single plant
*HistoryApi* | [**v2_transfers_history_get**](docs/HistoryApi.md#v2_transfers_history_get) | **GET** /v2/transfers/history | List of transfer history objects for a single transfer
*ItemsApi* | [**v2_items_discontinue_post**](docs/ItemsApi.md#v2_items_discontinue_post) | **POST** /v2/items/discontinue | Discontinue one item
*ItemsApi* | [**v2_items_get**](docs/ItemsApi.md#v2_items_get) | **GET** /v2/items | List of active items
*ItemsApi* | [**v2_items_history_get**](docs/ItemsApi.md#v2_items_history_get) | **GET** /v2/items/history | List of item history objects for a single item
*ItemsApi* | [**v2_items_report_get**](docs/ItemsApi.md#v2_items_report_get) | **GET** /v2/items/report | Generate a report of all active items
*LabResultsApi* | [**v2_packages_labresult_batches_get**](docs/LabResultsApi.md#v2_packages_labresult_batches_get) | **GET** /v2/packages/labresult-batches | List of package lab result batch objects for a single package
*LabResultsApi* | [**v2_packages_labresults_document_get**](docs/LabResultsApi.md#v2_packages_labresults_document_get) | **GET** /v2/packages/labresults/document | Get the COA PDF for a lab result.
*LabResultsApi* | [**v2_packages_labresults_get**](docs/LabResultsApi.md#v2_packages_labresults_get) | **GET** /v2/packages/labresults | List of package lab result objects for a single package
*LabelsApi* | [**v2_files_labels_content_data_packages_active_post**](docs/LabelsApi.md#v2_files_labels_content_data_packages_active_post) | **POST** /v2/files/labels/content-data/packages/active | For a given list of active packages, returns the needed ContentDataList to render the labels.
*LabelsApi* | [**v2_files_labels_content_data_packages_intransit_post**](docs/LabelsApi.md#v2_files_labels_content_data_packages_intransit_post) | **POST** /v2/files/labels/content-data/packages/intransit | For a given list of in transit packages, returns the needed ContentDataList to render the labels.
*LabelsApi* | [**v2_files_labels_generate_post**](docs/LabelsApi.md#v2_files_labels_generate_post) | **POST** /v2/files/labels/generate | Generate a PDF of labels.
*LabelsApi* | [**v2_files_labels_label_content_layouts_get**](docs/LabelsApi.md#v2_files_labels_label_content_layouts_get) | **GET** /v2/files/labels/label-content-layouts | Returns a list of label content layouts
*LabelsApi* | [**v2_files_labels_label_template_layouts_get**](docs/LabelsApi.md#v2_files_labels_label_template_layouts_get) | **GET** /v2/files/labels/label-template-layouts | Returns a list of label template layouts
*LicensesApi* | [**v2_licenses_get**](docs/LicensesApi.md#v2_licenses_get) | **GET** /v2/licenses | List of accessible licenses
*ManifestsApi* | [**v2_transfers_incoming_manifest_report_get**](docs/ManifestsApi.md#v2_transfers_incoming_manifest_report_get) | **GET** /v2/transfers/incoming/manifest/report | Generate a report of all incoming transfer manifests
*ManifestsApi* | [**v2_transfers_manifest_get**](docs/ManifestsApi.md#v2_transfers_manifest_get) | **GET** /v2/transfers/manifest | Get the manifest PDF for a transfer.
*ManifestsApi* | [**v2_transfers_outgoing_manifest_report_get**](docs/ManifestsApi.md#v2_transfers_outgoing_manifest_report_get) | **GET** /v2/transfers/outgoing/manifest/report | Generate a report of all outgoing transfer manifests
*ModifyItemsApi* | [**v2_items_discontinue_post**](docs/ModifyItemsApi.md#v2_items_discontinue_post) | **POST** /v2/items/discontinue | Discontinue one item
*ModifyPackagesApi* | [**v2_packages_notes_post**](docs/ModifyPackagesApi.md#v2_packages_notes_post) | **POST** /v2/packages/notes | Add notes to packages
*ModifyPackagesApi* | [**v2_packages_unfinish_post**](docs/ModifyPackagesApi.md#v2_packages_unfinish_post) | **POST** /v2/packages/unfinish | Unfinish packages
*ModifySalesReceiptsApi* | [**v2_sales_unfinalize_post**](docs/ModifySalesReceiptsApi.md#v2_sales_unfinalize_post) | **POST** /v2/sales/unfinalize | Unfinalize sales receipts
*ModifySalesReceiptsApi* | [**v2_sales_void_post**](docs/ModifySalesReceiptsApi.md#v2_sales_void_post) | **POST** /v2/sales/void | Void one sales receipt
*PDFApi* | [**v2_files_labels_generate_post**](docs/PDFApi.md#v2_files_labels_generate_post) | **POST** /v2/files/labels/generate | Generate a PDF of labels.
*PDFApi* | [**v2_files_labels_label_content_layouts_get**](docs/PDFApi.md#v2_files_labels_label_content_layouts_get) | **GET** /v2/files/labels/label-content-layouts | Returns a list of label content layouts
*PDFApi* | [**v2_files_labels_label_template_layouts_get**](docs/PDFApi.md#v2_files_labels_label_template_layouts_get) | **GET** /v2/files/labels/label-template-layouts | Returns a list of label template layouts
*PDFApi* | [**v2_packages_labresults_document_get**](docs/PDFApi.md#v2_packages_labresults_document_get) | **GET** /v2/packages/labresults/document | Get the COA PDF for a lab result.
*PDFApi* | [**v2_transfers_manifest_get**](docs/PDFApi.md#v2_transfers_manifest_get) | **GET** /v2/transfers/manifest | Get the manifest PDF for a transfer.
*PackagesApi* | [**v2_files_labels_content_data_packages_active_post**](docs/PackagesApi.md#v2_files_labels_content_data_packages_active_post) | **POST** /v2/files/labels/content-data/packages/active | For a given list of active packages, returns the needed ContentDataList to render the labels.
*PackagesApi* | [**v2_files_labels_content_data_packages_intransit_post**](docs/PackagesApi.md#v2_files_labels_content_data_packages_intransit_post) | **POST** /v2/files/labels/content-data/packages/intransit | For a given list of in transit packages, returns the needed ContentDataList to render the labels.
*PackagesApi* | [**v2_packages_active_get**](docs/PackagesApi.md#v2_packages_active_get) | **GET** /v2/packages/active | List of active packages
*PackagesApi* | [**v2_packages_active_report_get**](docs/PackagesApi.md#v2_packages_active_report_get) | **GET** /v2/packages/active/report | Generate a report of all active packages
*PackagesApi* | [**v2_packages_create_inputs_get**](docs/PackagesApi.md#v2_packages_create_inputs_get) | **GET** /v2/packages/create/inputs | Input data used for creating new packages
*PackagesApi* | [**v2_packages_create_post**](docs/PackagesApi.md#v2_packages_create_post) | **POST** /v2/packages/create | Create one or more packages from existing active packages
*PackagesApi* | [**v2_packages_create_source_items_get**](docs/PackagesApi.md#v2_packages_create_source_items_get) | **GET** /v2/packages/create/source-items | List of items eligible to be used in creating new packages
*PackagesApi* | [**v2_packages_create_source_packages_get**](docs/PackagesApi.md#v2_packages_create_source_packages_get) | **GET** /v2/packages/create/source-packages | List of packages eligible to be used in creating new packages
*PackagesApi* | [**v2_packages_history_get**](docs/PackagesApi.md#v2_packages_history_get) | **GET** /v2/packages/history | List of package history objects for a single package
*PackagesApi* | [**v2_packages_inactive_get**](docs/PackagesApi.md#v2_packages_inactive_get) | **GET** /v2/packages/inactive | List of inactive packages
*PackagesApi* | [**v2_packages_intransit_get**](docs/PackagesApi.md#v2_packages_intransit_get) | **GET** /v2/packages/intransit | List of in transit packages
*PackagesApi* | [**v2_packages_intransit_report_get**](docs/PackagesApi.md#v2_packages_intransit_report_get) | **GET** /v2/packages/intransit/report | Generate a report of all in-transit packages
*PackagesApi* | [**v2_packages_labresult_batches_get**](docs/PackagesApi.md#v2_packages_labresult_batches_get) | **GET** /v2/packages/labresult-batches | List of package lab result batch objects for a single package
*PackagesApi* | [**v2_packages_labresults_document_get**](docs/PackagesApi.md#v2_packages_labresults_document_get) | **GET** /v2/packages/labresults/document | Get the COA PDF for a lab result.
*PackagesApi* | [**v2_packages_labresults_get**](docs/PackagesApi.md#v2_packages_labresults_get) | **GET** /v2/packages/labresults | List of package lab result objects for a single package
*PackagesApi* | [**v2_packages_notes_post**](docs/PackagesApi.md#v2_packages_notes_post) | **POST** /v2/packages/notes | Add notes to packages
*PackagesApi* | [**v2_packages_onhold_get**](docs/PackagesApi.md#v2_packages_onhold_get) | **GET** /v2/packages/onhold | List of on hold packages
*PackagesApi* | [**v2_packages_source_harvests_get**](docs/PackagesApi.md#v2_packages_source_harvests_get) | **GET** /v2/packages/source-harvests | List of package source harvest objects for a single package
*PackagesApi* | [**v2_packages_transferred_get**](docs/PackagesApi.md#v2_packages_transferred_get) | **GET** /v2/packages/transferred | List of transferred packages
*PackagesApi* | [**v2_packages_transferred_report_get**](docs/PackagesApi.md#v2_packages_transferred_report_get) | **GET** /v2/packages/transferred/report | Generate a report of all transferred packages
*PackagesApi* | [**v2_packages_unfinish_post**](docs/PackagesApi.md#v2_packages_unfinish_post) | **POST** /v2/packages/unfinish | Unfinish packages
*PackagesApi* | [**v2_transfers_create_destinations_get**](docs/PackagesApi.md#v2_transfers_create_destinations_get) | **GET** /v2/transfers/create/destinations | List of destination facilities eligible to be used in creating new transfers
*PackagesApi* | [**v2_transfers_create_transporters_get**](docs/PackagesApi.md#v2_transfers_create_transporters_get) | **GET** /v2/transfers/create/transporters | List of transporter facilities eligible to be used in creating new transfers
*PermissionsApi* | [**v2_permissions_get**](docs/PermissionsApi.md#v2_permissions_get) | **GET** /v2/permissions | List of all permissions within a single view
*PermissionsApi* | [**v2_permissions_views_get**](docs/PermissionsApi.md#v2_permissions_views_get) | **GET** /v2/permissions/views | List of all available permission views
*PlantBatchesApi* | [**v2_plantbatches_active_get**](docs/PlantBatchesApi.md#v2_plantbatches_active_get) | **GET** /v2/plantbatches/active | List of active plant batches
*PlantBatchesApi* | [**v2_plantbatches_active_report_get**](docs/PlantBatchesApi.md#v2_plantbatches_active_report_get) | **GET** /v2/plantbatches/active/report | Generate a report of all active plant batches
*PlantBatchesApi* | [**v2_plantbatches_history_get**](docs/PlantBatchesApi.md#v2_plantbatches_history_get) | **GET** /v2/plantbatches/history | List of history objects for a single plant batch
*PlantBatchesApi* | [**v2_plantbatches_inactive_get**](docs/PlantBatchesApi.md#v2_plantbatches_inactive_get) | **GET** /v2/plantbatches/inactive | List of inactive plantbatches
*PlantBatchesApi* | [**v2_plantbatches_onhold_get**](docs/PlantBatchesApi.md#v2_plantbatches_onhold_get) | **GET** /v2/plantbatches/onhold | List of on hold plantbatches
*PlantsApi* | [**v2_plants_flowering_get**](docs/PlantsApi.md#v2_plants_flowering_get) | **GET** /v2/plants/flowering | List of flowering plants
*PlantsApi* | [**v2_plants_flowering_report_get**](docs/PlantsApi.md#v2_plants_flowering_report_get) | **GET** /v2/plants/flowering/report | Generate a report of all flowering plants
*PlantsApi* | [**v2_plants_history_get**](docs/PlantsApi.md#v2_plants_history_get) | **GET** /v2/plants/history | List of history objects for a single plant
*PlantsApi* | [**v2_plants_inactive_get**](docs/PlantsApi.md#v2_plants_inactive_get) | **GET** /v2/plants/inactive | List of inactive plants
*PlantsApi* | [**v2_plants_onhold_get**](docs/PlantsApi.md#v2_plants_onhold_get) | **GET** /v2/plants/onhold | List of on hold plants
*PlantsApi* | [**v2_plants_vegetative_get**](docs/PlantsApi.md#v2_plants_vegetative_get) | **GET** /v2/plants/vegetative | List of vegetative plants
*PlantsApi* | [**v2_plants_vegetative_report_get**](docs/PlantsApi.md#v2_plants_vegetative_report_get) | **GET** /v2/plants/vegetative/report | Generate a report of all vegetative plants
*ReportsApi* | [**v2_auth_secretkey_post**](docs/ReportsApi.md#v2_auth_secretkey_post) | **POST** /v2/auth/secretkey | Generate a secret key that can be used for special T3 routes that support secrey key authentication.
*ReportsApi* | [**v2_harvests_active_report_get**](docs/ReportsApi.md#v2_harvests_active_report_get) | **GET** /v2/harvests/active/report | Generate a report of all active harvests
*ReportsApi* | [**v2_harvests_inactive_report_get**](docs/ReportsApi.md#v2_harvests_inactive_report_get) | **GET** /v2/harvests/inactive/report | Generate a report of all active harvests
*ReportsApi* | [**v2_items_report_get**](docs/ReportsApi.md#v2_items_report_get) | **GET** /v2/items/report | Generate a report of all active items
*ReportsApi* | [**v2_packages_active_report_get**](docs/ReportsApi.md#v2_packages_active_report_get) | **GET** /v2/packages/active/report | Generate a report of all active packages
*ReportsApi* | [**v2_packages_intransit_report_get**](docs/ReportsApi.md#v2_packages_intransit_report_get) | **GET** /v2/packages/intransit/report | Generate a report of all in-transit packages
*ReportsApi* | [**v2_packages_transferred_report_get**](docs/ReportsApi.md#v2_packages_transferred_report_get) | **GET** /v2/packages/transferred/report | Generate a report of all transferred packages
*ReportsApi* | [**v2_plantbatches_active_report_get**](docs/ReportsApi.md#v2_plantbatches_active_report_get) | **GET** /v2/plantbatches/active/report | Generate a report of all active plant batches
*ReportsApi* | [**v2_plants_flowering_report_get**](docs/ReportsApi.md#v2_plants_flowering_report_get) | **GET** /v2/plants/flowering/report | Generate a report of all flowering plants
*ReportsApi* | [**v2_plants_vegetative_report_get**](docs/ReportsApi.md#v2_plants_vegetative_report_get) | **GET** /v2/plants/vegetative/report | Generate a report of all vegetative plants
*ReportsApi* | [**v2_sales_active_report_get**](docs/ReportsApi.md#v2_sales_active_report_get) | **GET** /v2/sales/active/report | Generate a report of all active sales
*ReportsApi* | [**v2_transfers_incoming_manifest_report_get**](docs/ReportsApi.md#v2_transfers_incoming_manifest_report_get) | **GET** /v2/transfers/incoming/manifest/report | Generate a report of all incoming transfer manifests
*ReportsApi* | [**v2_transfers_outgoing_manifest_report_get**](docs/ReportsApi.md#v2_transfers_outgoing_manifest_report_get) | **GET** /v2/transfers/outgoing/manifest/report | Generate a report of all outgoing transfer manifests
*SalesReceiptsApi* | [**v2_sales_active_get**](docs/SalesReceiptsApi.md#v2_sales_active_get) | **GET** /v2/sales/active | List of active sales
*SalesReceiptsApi* | [**v2_sales_active_report_get**](docs/SalesReceiptsApi.md#v2_sales_active_report_get) | **GET** /v2/sales/active/report | Generate a report of all active sales
*SalesReceiptsApi* | [**v2_sales_inactive_get**](docs/SalesReceiptsApi.md#v2_sales_inactive_get) | **GET** /v2/sales/inactive | List of inactive sales
*SalesReceiptsApi* | [**v2_sales_transactions_get**](docs/SalesReceiptsApi.md#v2_sales_transactions_get) | **GET** /v2/sales/transactions | List of transactions for a single sales receipt
*SalesReceiptsApi* | [**v2_sales_unfinalize_post**](docs/SalesReceiptsApi.md#v2_sales_unfinalize_post) | **POST** /v2/sales/unfinalize | Unfinalize sales receipts
*SalesReceiptsApi* | [**v2_sales_void_post**](docs/SalesReceiptsApi.md#v2_sales_void_post) | **POST** /v2/sales/void | Void one sales receipt
*SearchApi* | [**v2_search_get**](docs/SearchApi.md#v2_search_get) | **GET** /v2/search | Generic text search endpoint
*SingleHarvestApi* | [**v2_harvests_history_get**](docs/SingleHarvestApi.md#v2_harvests_history_get) | **GET** /v2/harvests/history | List of history objects for a single harvest.
*SingleItemApi* | [**v2_items_history_get**](docs/SingleItemApi.md#v2_items_history_get) | **GET** /v2/items/history | List of item history objects for a single item
*SinglePackageApi* | [**v2_packages_history_get**](docs/SinglePackageApi.md#v2_packages_history_get) | **GET** /v2/packages/history | List of package history objects for a single package
*SinglePackageApi* | [**v2_packages_labresult_batches_get**](docs/SinglePackageApi.md#v2_packages_labresult_batches_get) | **GET** /v2/packages/labresult-batches | List of package lab result batch objects for a single package
*SinglePackageApi* | [**v2_packages_labresults_document_get**](docs/SinglePackageApi.md#v2_packages_labresults_document_get) | **GET** /v2/packages/labresults/document | Get the COA PDF for a lab result.
*SinglePackageApi* | [**v2_packages_labresults_get**](docs/SinglePackageApi.md#v2_packages_labresults_get) | **GET** /v2/packages/labresults | List of package lab result objects for a single package
*SinglePackageApi* | [**v2_packages_source_harvests_get**](docs/SinglePackageApi.md#v2_packages_source_harvests_get) | **GET** /v2/packages/source-harvests | List of package source harvest objects for a single package
*SinglePlantApi* | [**v2_plants_history_get**](docs/SinglePlantApi.md#v2_plants_history_get) | **GET** /v2/plants/history | List of history objects for a single plant
*SinglePlantBatchApi* | [**v2_plantbatches_history_get**](docs/SinglePlantBatchApi.md#v2_plantbatches_history_get) | **GET** /v2/plantbatches/history | List of history objects for a single plant batch
*SingleSalesReceiptApi* | [**v2_sales_transactions_get**](docs/SingleSalesReceiptApi.md#v2_sales_transactions_get) | **GET** /v2/sales/transactions | List of transactions for a single sales receipt
*SingleTransferApi* | [**v2_transfers_deliveries_get**](docs/SingleTransferApi.md#v2_transfers_deliveries_get) | **GET** /v2/transfers/deliveries | List of deliveries for a single transfer
*SingleTransferApi* | [**v2_transfers_history_get**](docs/SingleTransferApi.md#v2_transfers_history_get) | **GET** /v2/transfers/history | List of transfer history objects for a single transfer
*SingleTransferApi* | [**v2_transfers_manifest_get**](docs/SingleTransferApi.md#v2_transfers_manifest_get) | **GET** /v2/transfers/manifest | Get the manifest PDF for a transfer.
*SingleTransferApi* | [**v2_transfers_packages_get**](docs/SingleTransferApi.md#v2_transfers_packages_get) | **GET** /v2/transfers/packages | List of packages for a single delivery
*SingleTransferApi* | [**v2_transfers_transporter_details_get**](docs/SingleTransferApi.md#v2_transfers_transporter_details_get) | **GET** /v2/transfers/transporter-details | List of transporter detailss for a single transfer
*SingleTransferApi* | [**v2_transfers_transporters_get**](docs/SingleTransferApi.md#v2_transfers_transporters_get) | **GET** /v2/transfers/transporters | List of transporters for a single delivery
*StatesApi* | [**v2_states_get**](docs/StatesApi.md#v2_states_get) | **GET** /v2/states | List of accessible states
*TransfersApi* | [**v2_transfers_create_destinations_get**](docs/TransfersApi.md#v2_transfers_create_destinations_get) | **GET** /v2/transfers/create/destinations | List of destination facilities eligible to be used in creating new transfers
*TransfersApi* | [**v2_transfers_create_inputs_get**](docs/TransfersApi.md#v2_transfers_create_inputs_get) | **GET** /v2/transfers/create/inputs | Input data used for creating new transers
*TransfersApi* | [**v2_transfers_create_post**](docs/TransfersApi.md#v2_transfers_create_post) | **POST** /v2/transfers/create | Create one or more transfers
*TransfersApi* | [**v2_transfers_create_transporters_get**](docs/TransfersApi.md#v2_transfers_create_transporters_get) | **GET** /v2/transfers/create/transporters | List of transporter facilities eligible to be used in creating new transfers
*TransfersApi* | [**v2_transfers_deliveries_get**](docs/TransfersApi.md#v2_transfers_deliveries_get) | **GET** /v2/transfers/deliveries | List of deliveries for a single transfer
*TransfersApi* | [**v2_transfers_history_get**](docs/TransfersApi.md#v2_transfers_history_get) | **GET** /v2/transfers/history | List of transfer history objects for a single transfer
*TransfersApi* | [**v2_transfers_incoming_active_get**](docs/TransfersApi.md#v2_transfers_incoming_active_get) | **GET** /v2/transfers/incoming/active | List of incoming active transfers
*TransfersApi* | [**v2_transfers_incoming_inactive_get**](docs/TransfersApi.md#v2_transfers_incoming_inactive_get) | **GET** /v2/transfers/incoming/inactive | List of incoming inactive transfers
*TransfersApi* | [**v2_transfers_incoming_manifest_report_get**](docs/TransfersApi.md#v2_transfers_incoming_manifest_report_get) | **GET** /v2/transfers/incoming/manifest/report | Generate a report of all incoming transfer manifests
*TransfersApi* | [**v2_transfers_manifest_get**](docs/TransfersApi.md#v2_transfers_manifest_get) | **GET** /v2/transfers/manifest | Get the manifest PDF for a transfer.
*TransfersApi* | [**v2_transfers_outgoing_active_get**](docs/TransfersApi.md#v2_transfers_outgoing_active_get) | **GET** /v2/transfers/outgoing/active | List of outgoing active transfers
*TransfersApi* | [**v2_transfers_outgoing_inactive_get**](docs/TransfersApi.md#v2_transfers_outgoing_inactive_get) | **GET** /v2/transfers/outgoing/inactive | List of outgoing inactive transfers
*TransfersApi* | [**v2_transfers_outgoing_manifest_report_get**](docs/TransfersApi.md#v2_transfers_outgoing_manifest_report_get) | **GET** /v2/transfers/outgoing/manifest/report | Generate a report of all outgoing transfer manifests
*TransfersApi* | [**v2_transfers_packages_get**](docs/TransfersApi.md#v2_transfers_packages_get) | **GET** /v2/transfers/packages | List of packages for a single delivery
*TransfersApi* | [**v2_transfers_rejected_get**](docs/TransfersApi.md#v2_transfers_rejected_get) | **GET** /v2/transfers/rejected | List of rejected transfers
*TransfersApi* | [**v2_transfers_transporter_details_get**](docs/TransfersApi.md#v2_transfers_transporter_details_get) | **GET** /v2/transfers/transporter-details | List of transporter detailss for a single transfer
*TransfersApi* | [**v2_transfers_transporters_get**](docs/TransfersApi.md#v2_transfers_transporters_get) | **GET** /v2/transfers/transporters | List of transporters for a single delivery


## Documentation For Models

 - [EndpointId](docs/EndpointId.md)
 - [IncomingTransferManifestReportResponse](docs/IncomingTransferManifestReportResponse.md)
 - [JWTData](docs/JWTData.md)
 - [LabTestingStates](docs/LabTestingStates.md)
 - [MetrcCreatePackageInputsResponse](docs/MetrcCreatePackageInputsResponse.md)
 - [MetrcCredentialAuthPayload](docs/MetrcCredentialAuthPayload.md)
 - [MetrcDeliveryPackage](docs/MetrcDeliveryPackage.md)
 - [MetrcDeliveryPackageListResponse](docs/MetrcDeliveryPackageListResponse.md)
 - [MetrcDiscontinueItemPayload](docs/MetrcDiscontinueItemPayload.md)
 - [MetrcDriver](docs/MetrcDriver.md)
 - [MetrcFacility](docs/MetrcFacility.md)
 - [MetrcFacilityListResponse](docs/MetrcFacilityListResponse.md)
 - [MetrcFacilityPhysicalAddress](docs/MetrcFacilityPhysicalAddress.md)
 - [MetrcHarvest](docs/MetrcHarvest.md)
 - [MetrcHarvestListResponse](docs/MetrcHarvestListResponse.md)
 - [MetrcHarvestReportResponse](docs/MetrcHarvestReportResponse.md)
 - [MetrcHistory](docs/MetrcHistory.md)
 - [MetrcHistoryListResponse](docs/MetrcHistoryListResponse.md)
 - [MetrcIncomingTransfer](docs/MetrcIncomingTransfer.md)
 - [MetrcIncomingTransferListResponse](docs/MetrcIncomingTransferListResponse.md)
 - [MetrcItem](docs/MetrcItem.md)
 - [MetrcItemListResponse](docs/MetrcItemListResponse.md)
 - [MetrcLicense](docs/MetrcLicense.md)
 - [MetrcLocation](docs/MetrcLocation.md)
 - [MetrcOutgoingTransfer](docs/MetrcOutgoingTransfer.md)
 - [MetrcOutgoingTransferListResponse](docs/MetrcOutgoingTransferListResponse.md)
 - [MetrcPackage](docs/MetrcPackage.md)
 - [MetrcPackageLabResult](docs/MetrcPackageLabResult.md)
 - [MetrcPackageLabResultBatch](docs/MetrcPackageLabResultBatch.md)
 - [MetrcPackageLabResultBatchListResponse](docs/MetrcPackageLabResultBatchListResponse.md)
 - [MetrcPackageLabResultListResponse](docs/MetrcPackageLabResultListResponse.md)
 - [MetrcPackageListResponse](docs/MetrcPackageListResponse.md)
 - [MetrcPackageReportResponse](docs/MetrcPackageReportResponse.md)
 - [MetrcPackageSourceHarvest](docs/MetrcPackageSourceHarvest.md)
 - [MetrcPackageSourceHarvestListResponse](docs/MetrcPackageSourceHarvestListResponse.md)
 - [MetrcPlant](docs/MetrcPlant.md)
 - [MetrcPlantBatch](docs/MetrcPlantBatch.md)
 - [MetrcPlantBatchListResponse](docs/MetrcPlantBatchListResponse.md)
 - [MetrcPlantBatchReportResponse](docs/MetrcPlantBatchReportResponse.md)
 - [MetrcPlantListResponse](docs/MetrcPlantListResponse.md)
 - [MetrcPlantReportResponse](docs/MetrcPlantReportResponse.md)
 - [MetrcRemediationMethod](docs/MetrcRemediationMethod.md)
 - [MetrcSalesReceipt](docs/MetrcSalesReceipt.md)
 - [MetrcSalesReceiptListResponse](docs/MetrcSalesReceiptListResponse.md)
 - [MetrcSalesReceiptReportResponse](docs/MetrcSalesReceiptReportResponse.md)
 - [MetrcState](docs/MetrcState.md)
 - [MetrcSuperpackage](docs/MetrcSuperpackage.md)
 - [MetrcSuperpackageAllOfMetadata](docs/MetrcSuperpackageAllOfMetadata.md)
 - [MetrcSuperpackageAllOfMetadataTestResults](docs/MetrcSuperpackageAllOfMetadataTestResults.md)
 - [MetrcTag](docs/MetrcTag.md)
 - [MetrcTransaction](docs/MetrcTransaction.md)
 - [MetrcTransactionListResponse](docs/MetrcTransactionListResponse.md)
 - [MetrcTransferDelivery](docs/MetrcTransferDelivery.md)
 - [MetrcTransferDeliveryListResponse](docs/MetrcTransferDeliveryListResponse.md)
 - [MetrcTransferTransporter](docs/MetrcTransferTransporter.md)
 - [MetrcTransferTransporterDetails](docs/MetrcTransferTransporterDetails.md)
 - [MetrcTransferTransporterDetailsListResponse](docs/MetrcTransferTransporterDetailsListResponse.md)
 - [MetrcTransferTransporterListResponse](docs/MetrcTransferTransporterListResponse.md)
 - [MetrcTransferredPackage](docs/MetrcTransferredPackage.md)
 - [MetrcTransferredPackageListResponse](docs/MetrcTransferredPackageListResponse.md)
 - [MetrcVehicle](docs/MetrcVehicle.md)
 - [MetrcVoidSalesReceiptPayload](docs/MetrcVoidSalesReceiptPayload.md)
 - [OutgoingTransferManifestReportResponse](docs/OutgoingTransferManifestReportResponse.md)
 - [Pagination](docs/Pagination.md)
 - [SearchResponse](docs/SearchResponse.md)
 - [T3GenerateLabelsPayload](docs/T3GenerateLabelsPayload.md)
 - [T3IncomingTransferManifest](docs/T3IncomingTransferManifest.md)
 - [T3LabelContentData](docs/T3LabelContentData.md)
 - [T3LabelContentDataListResponse](docs/T3LabelContentDataListResponse.md)
 - [T3LabelContentLayoutConfig](docs/T3LabelContentLayoutConfig.md)
 - [T3LabelContentLayoutElement](docs/T3LabelContentLayoutElement.md)
 - [T3LabelContentLayoutElementTextResizeStrategy](docs/T3LabelContentLayoutElementTextResizeStrategy.md)
 - [T3LabelContentLayoutElementType](docs/T3LabelContentLayoutElementType.md)
 - [T3LabelContentLayoutsResponse](docs/T3LabelContentLayoutsResponse.md)
 - [T3LabelTemplateLayoutsResponse](docs/T3LabelTemplateLayoutsResponse.md)
 - [T3OutgoingTransferManifest](docs/T3OutgoingTransferManifest.md)
 - [UnitOfMeasure](docs/UnitOfMeasure.md)
 - [UnitOfMeasureAbbreviation](docs/UnitOfMeasureAbbreviation.md)
 - [V2AuthApikeyPostRequest](docs/V2AuthApikeyPostRequest.md)
 - [V2AuthCredentialsPost200Response](docs/V2AuthCredentialsPost200Response.md)
 - [V2AuthCredentialsPostRequest](docs/V2AuthCredentialsPostRequest.md)
 - [V2AuthSecretkeyPost200Response](docs/V2AuthSecretkeyPost200Response.md)
 - [V2AuthSecretkeyPostRequest](docs/V2AuthSecretkeyPostRequest.md)
 - [V2AuthWhoamiGet200Response](docs/V2AuthWhoamiGet200Response.md)
 - [V2FilesLabelsContentDataPackagesActivePost200Response](docs/V2FilesLabelsContentDataPackagesActivePost200Response.md)
 - [V2FilesLabelsContentDataPackagesActivePostRequest](docs/V2FilesLabelsContentDataPackagesActivePostRequest.md)
 - [V2FilesLabelsContentDataPackagesActivePostRequestRenderingOptions](docs/V2FilesLabelsContentDataPackagesActivePostRequestRenderingOptions.md)
 - [V2FilesLabelsGeneratePostRequest](docs/V2FilesLabelsGeneratePostRequest.md)
 - [V2FilesLabelsGeneratePostRequestLabelContentDataInner](docs/V2FilesLabelsGeneratePostRequestLabelContentDataInner.md)
 - [V2FilesLabelsGeneratePostRequestRenderingOptions](docs/V2FilesLabelsGeneratePostRequestRenderingOptions.md)
 - [V2FilesLabelsLabelContentLayoutsGet200Response](docs/V2FilesLabelsLabelContentLayoutsGet200Response.md)
 - [V2FilesLabelsLabelContentLayoutsGet200ResponseData](docs/V2FilesLabelsLabelContentLayoutsGet200ResponseData.md)
 - [V2FilesLabelsLabelContentLayoutsGet200ResponseDataDataInner](docs/V2FilesLabelsLabelContentLayoutsGet200ResponseDataDataInner.md)
 - [V2FilesLabelsLabelContentLayoutsGet200ResponseDataDataInnerElementsInner](docs/V2FilesLabelsLabelContentLayoutsGet200ResponseDataDataInnerElementsInner.md)
 - [V2FilesLabelsLabelTemplateLayoutsGet200Response](docs/V2FilesLabelsLabelTemplateLayoutsGet200Response.md)
 - [V2FilesLabelsLabelTemplateLayoutsGet200ResponseData](docs/V2FilesLabelsLabelTemplateLayoutsGet200ResponseData.md)
 - [V2FilesLabelsLabelTemplateLayoutsGet200ResponseDataDataInner](docs/V2FilesLabelsLabelTemplateLayoutsGet200ResponseDataDataInner.md)
 - [V2FilesLabelsLabelTemplateLayoutsGet200ResponseDataDataInnerLabelTemplateLayoutConfig](docs/V2FilesLabelsLabelTemplateLayoutsGet200ResponseDataDataInnerLabelTemplateLayoutConfig.md)
 - [V2HarvestsActiveGet200Response](docs/V2HarvestsActiveGet200Response.md)
 - [V2HarvestsActiveReportGet200Response](docs/V2HarvestsActiveReportGet200Response.md)
 - [V2ItemsDiscontinuePost200Response](docs/V2ItemsDiscontinuePost200Response.md)
 - [V2ItemsDiscontinuePost400Response](docs/V2ItemsDiscontinuePost400Response.md)
 - [V2ItemsDiscontinuePost400ResponseError](docs/V2ItemsDiscontinuePost400ResponseError.md)
 - [V2ItemsDiscontinuePost500Response](docs/V2ItemsDiscontinuePost500Response.md)
 - [V2ItemsDiscontinuePost500ResponseError](docs/V2ItemsDiscontinuePost500ResponseError.md)
 - [V2ItemsDiscontinuePost503Response](docs/V2ItemsDiscontinuePost503Response.md)
 - [V2ItemsDiscontinuePost503ResponseError](docs/V2ItemsDiscontinuePost503ResponseError.md)
 - [V2ItemsDiscontinuePostRequest](docs/V2ItemsDiscontinuePostRequest.md)
 - [V2ItemsGet200Response](docs/V2ItemsGet200Response.md)
 - [V2ItemsHistoryGet200Response](docs/V2ItemsHistoryGet200Response.md)
 - [V2ItemsReportGet200Response](docs/V2ItemsReportGet200Response.md)
 - [V2LicensesGet200ResponseInner](docs/V2LicensesGet200ResponseInner.md)
 - [V2PackagesActiveGet200Response](docs/V2PackagesActiveGet200Response.md)
 - [V2PackagesActiveReportGet200Response](docs/V2PackagesActiveReportGet200Response.md)
 - [V2PackagesCreateInputsGet200Response](docs/V2PackagesCreateInputsGet200Response.md)
 - [V2PackagesCreatePostRequestInner](docs/V2PackagesCreatePostRequestInner.md)
 - [V2PackagesCreatePostRequestInnerIngredientsInner](docs/V2PackagesCreatePostRequestInnerIngredientsInner.md)
 - [V2PackagesLabresultBatchesGet200Response](docs/V2PackagesLabresultBatchesGet200Response.md)
 - [V2PackagesLabresultsGet200Response](docs/V2PackagesLabresultsGet200Response.md)
 - [V2PackagesNotesPostRequestInner](docs/V2PackagesNotesPostRequestInner.md)
 - [V2PackagesSourceHarvestsGet200Response](docs/V2PackagesSourceHarvestsGet200Response.md)
 - [V2PackagesTransferredGet200Response](docs/V2PackagesTransferredGet200Response.md)
 - [V2PackagesTransferredReportGet200Response](docs/V2PackagesTransferredReportGet200Response.md)
 - [V2PackagesUnfinishPostRequestInner](docs/V2PackagesUnfinishPostRequestInner.md)
 - [V2PlantbatchesActiveGet200Response](docs/V2PlantbatchesActiveGet200Response.md)
 - [V2PlantbatchesActiveReportGet200Response](docs/V2PlantbatchesActiveReportGet200Response.md)
 - [V2PlantsVegetativeGet200Response](docs/V2PlantsVegetativeGet200Response.md)
 - [V2PlantsVegetativeReportGet200Response](docs/V2PlantsVegetativeReportGet200Response.md)
 - [V2SalesActiveGet200Response](docs/V2SalesActiveGet200Response.md)
 - [V2SalesActiveReportGet200Response](docs/V2SalesActiveReportGet200Response.md)
 - [V2SalesTransactionsGet200Response](docs/V2SalesTransactionsGet200Response.md)
 - [V2SalesUnfinalizePostRequestInner](docs/V2SalesUnfinalizePostRequestInner.md)
 - [V2SearchGet200Response](docs/V2SearchGet200Response.md)
 - [V2SearchGet200ResponseDataInner](docs/V2SearchGet200ResponseDataInner.md)
 - [V2StatesGet200ResponseInner](docs/V2StatesGet200ResponseInner.md)
 - [V2TransfersCreateDestinationsGet200Response](docs/V2TransfersCreateDestinationsGet200Response.md)
 - [V2TransfersCreateInputsGet200Response](docs/V2TransfersCreateInputsGet200Response.md)
 - [V2TransfersCreateInputsGet200ResponseTransferTypesInner](docs/V2TransfersCreateInputsGet200ResponseTransferTypesInner.md)
 - [V2TransfersCreateInputsGet200ResponseTransferTypesInnerFacilityTypesInner](docs/V2TransfersCreateInputsGet200ResponseTransferTypesInnerFacilityTypesInner.md)
 - [V2TransfersCreatePostRequestInner](docs/V2TransfersCreatePostRequestInner.md)
 - [V2TransfersCreatePostRequestInnerDestinationsInner](docs/V2TransfersCreatePostRequestInnerDestinationsInner.md)
 - [V2TransfersCreatePostRequestInnerDestinationsInnerPackagesInner](docs/V2TransfersCreatePostRequestInnerDestinationsInnerPackagesInner.md)
 - [V2TransfersCreatePostRequestInnerDestinationsInnerTransportersInner](docs/V2TransfersCreatePostRequestInnerDestinationsInnerTransportersInner.md)
 - [V2TransfersCreatePostRequestInnerDestinationsInnerTransportersInnerTransporterDetailsInner](docs/V2TransfersCreatePostRequestInnerDestinationsInnerTransportersInnerTransporterDetailsInner.md)
 - [V2TransfersDeliveriesGet200Response](docs/V2TransfersDeliveriesGet200Response.md)
 - [V2TransfersIncomingActiveGet200Response](docs/V2TransfersIncomingActiveGet200Response.md)
 - [V2TransfersIncomingManifestReportGet200Response](docs/V2TransfersIncomingManifestReportGet200Response.md)
 - [V2TransfersOutgoingActiveGet200Response](docs/V2TransfersOutgoingActiveGet200Response.md)
 - [V2TransfersOutgoingManifestReportGet200Response](docs/V2TransfersOutgoingManifestReportGet200Response.md)
 - [V2TransfersTransporterDetailsGet200Response](docs/V2TransfersTransporterDetailsGet200Response.md)
 - [V2TransfersTransportersGet200Response](docs/V2TransfersTransportersGet200Response.md)


<a id="documentation-for-authorization"></a>
## Documentation For Authorization


Authentication schemes defined for the API:
<a id="BearerAuth"></a>
### BearerAuth

- **Type**: Bearer authentication (JWT)


## Author




