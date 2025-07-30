# haplohub.VariantApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_variant**](VariantApi.md#get_variant) | **POST** /api/v1/cohort/{cohort_id}/variant/ | Get Variant


# **get_variant**
> ResultListResponseVariantSchema get_variant(cohort_id, get_variant_request)

Get Variant

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.get_variant_request import GetVariantRequest
from haplohub.models.result_list_response_variant_schema import ResultListResponseVariantSchema
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
    api_instance = haplohub.VariantApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    get_variant_request = haplohub.GetVariantRequest() # GetVariantRequest | 

    try:
        # Get Variant
        api_response = api_instance.get_variant(cohort_id, get_variant_request)
        print("The response of VariantApi->get_variant:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling VariantApi->get_variant: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **get_variant_request** | [**GetVariantRequest**](GetVariantRequest.md)|  | 

### Return type

[**ResultListResponseVariantSchema**](ResultListResponseVariantSchema.md)

### Authorization

[Auth0JWTBearer](../README.md#Auth0JWTBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

