# haplohub.MetadataApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**accession**](MetadataApi.md#accession) | **GET** /api/v1/metadata/ | Each accession is a string of DNA that is used as a reference. These are defined by https://www.ncbi.nlm.nih.gov/grc/human/data?asm&#x3D;GRCh38


# **accession**
> PaginatedResponseAccessionSchema accession()

Each accession is a string of DNA that is used as a reference. These are defined by https://www.ncbi.nlm.nih.gov/grc/human/data?asm=GRCh38

Genetic variants are typically defined as a differenece from a reference. Each accession is a contiguous reference string. There is one accession per chromosome.

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.paginated_response_accession_schema import PaginatedResponseAccessionSchema
from haplohub.rest import ApiException
from pprint import pprint

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: 
configuration = haplohub.Configuration(
    access_token=os.environ["API_KEY"]
)

# Enter a context with an instance of the API client
with haplohub.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = haplohub.MetadataApi(api_client)

    try:
        # Each accession is a string of DNA that is used as a reference. These are defined by https://www.ncbi.nlm.nih.gov/grc/human/data?asm=GRCh38
        api_response = api_instance.accession()
        print("The response of MetadataApi->accession:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MetadataApi->accession: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**PaginatedResponseAccessionSchema**](PaginatedResponseAccessionSchema.md)

### Authorization

[Auth0JWTBearer](../README.md#Auth0JWTBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

