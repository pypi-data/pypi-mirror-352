# haplohub.SampleApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_sample**](SampleApi.md#delete_sample) | **DELETE** /api/v1/cohort/{cohort_id}/sample/{sample_id}/ | Delete sample
[**get_sample**](SampleApi.md#get_sample) | **GET** /api/v1/cohort/{cohort_id}/sample/{sample_id}/ | Get sample
[**hgvs_dosage**](SampleApi.md#hgvs_dosage) | **GET** /api/v1/sample/ | Fetch the dosage of a given allele for a sample based on the hgvs nomenclature. For example &#39;NC_000001.11:g.11794419T&gt;G&#39;
[**list_samples**](SampleApi.md#list_samples) | **GET** /api/v1/cohort/{cohort_id}/sample/ | List samples


# **delete_sample**
> ResultResponse delete_sample(cohort_id, sample_id)

Delete sample

Delete sample by its ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.result_response import ResultResponse
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
    api_instance = haplohub.SampleApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    sample_id = 'sample_id_example' # str | 

    try:
        # Delete sample
        api_response = api_instance.delete_sample(cohort_id, sample_id)
        print("The response of SampleApi->delete_sample:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SampleApi->delete_sample: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **sample_id** | **str**|  | 

### Return type

[**ResultResponse**](ResultResponse.md)

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

# **get_sample**
> ResultResponseSampleSchema get_sample(cohort_id, sample_id)

Get sample

Get sample by its ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.result_response_sample_schema import ResultResponseSampleSchema
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
    api_instance = haplohub.SampleApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    sample_id = 'sample_id_example' # str | 

    try:
        # Get sample
        api_response = api_instance.get_sample(cohort_id, sample_id)
        print("The response of SampleApi->get_sample:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SampleApi->get_sample: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **sample_id** | **str**|  | 

### Return type

[**ResultResponseSampleSchema**](ResultResponseSampleSchema.md)

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

# **hgvs_dosage**
> GetHgvsResponse hgvs_dosage(sample_id, description)

Fetch the dosage of a given allele for a sample based on the hgvs nomenclature. For example 'NC_000001.11:g.11794419T>G'

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.get_hgvs_response import GetHgvsResponse
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
    api_instance = haplohub.SampleApi(api_client)
    sample_id = 'sample_id_example' # str | 
    description = 'description_example' # str | 

    try:
        # Fetch the dosage of a given allele for a sample based on the hgvs nomenclature. For example 'NC_000001.11:g.11794419T>G'
        api_response = api_instance.hgvs_dosage(sample_id, description)
        print("The response of SampleApi->hgvs_dosage:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SampleApi->hgvs_dosage: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sample_id** | **str**|  | 
 **description** | **str**|  | 

### Return type

[**GetHgvsResponse**](GetHgvsResponse.md)

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

# **list_samples**
> PaginatedResponseSampleSchema list_samples(cohort_id)

List samples

List all samples

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.paginated_response_sample_schema import PaginatedResponseSampleSchema
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
    api_instance = haplohub.SampleApi(api_client)
    cohort_id = 'cohort_id_example' # str | 

    try:
        # List samples
        api_response = api_instance.list_samples(cohort_id)
        print("The response of SampleApi->list_samples:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SampleApi->list_samples: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 

### Return type

[**PaginatedResponseSampleSchema**](PaginatedResponseSampleSchema.md)

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

