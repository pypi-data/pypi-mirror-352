# haplohub.MemberApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_member**](MemberApi.md#delete_member) | **DELETE** /api/v1/cohort/{cohort_id}/member/{member_id}/ | Delete member
[**get_member**](MemberApi.md#get_member) | **GET** /api/v1/cohort/{cohort_id}/member/{member_id}/ | Get member
[**list_members**](MemberApi.md#list_members) | **GET** /api/v1/cohort/{cohort_id}/member/ | List members


# **delete_member**
> ResultResponse delete_member(cohort_id, member_id)

Delete member

Delete member by its ID

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
    api_instance = haplohub.MemberApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    member_id = 'member_id_example' # str | 

    try:
        # Delete member
        api_response = api_instance.delete_member(cohort_id, member_id)
        print("The response of MemberApi->delete_member:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MemberApi->delete_member: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **member_id** | **str**|  | 

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

# **get_member**
> ResultResponseMemberSchema get_member(cohort_id, member_id)

Get member

Get member by its ID

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.result_response_member_schema import ResultResponseMemberSchema
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
    api_instance = haplohub.MemberApi(api_client)
    cohort_id = 'cohort_id_example' # str | 
    member_id = 'member_id_example' # str | 

    try:
        # Get member
        api_response = api_instance.get_member(cohort_id, member_id)
        print("The response of MemberApi->get_member:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MemberApi->get_member: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 
 **member_id** | **str**|  | 

### Return type

[**ResultResponseMemberSchema**](ResultResponseMemberSchema.md)

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

# **list_members**
> PaginatedResponseMemberSchema list_members(cohort_id)

List members

List all members

### Example

* Bearer Authentication (Auth0JWTBearer):
```python
import time
import os
import haplohub
from haplohub.models.paginated_response_member_schema import PaginatedResponseMemberSchema
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
    api_instance = haplohub.MemberApi(api_client)
    cohort_id = 'cohort_id_example' # str | 

    try:
        # List members
        api_response = api_instance.list_members(cohort_id)
        print("The response of MemberApi->list_members:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MemberApi->list_members: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cohort_id** | **str**|  | 

### Return type

[**PaginatedResponseMemberSchema**](PaginatedResponseMemberSchema.md)

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

