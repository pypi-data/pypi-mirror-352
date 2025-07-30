# ise_openapi_endpoints.EndpointsApi

All URIs are relative to *https://172.23.160.114:44330*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_bulk_end_points**](EndpointsApi.md#create_bulk_end_points) | **POST** /api/v1/endpoint/bulk | Create Endpoint in bulk
[**create_end_point**](EndpointsApi.md#create_end_point) | **POST** /api/v1/endpoint | Create Endpoint
[**create_end_point_task**](EndpointsApi.md#create_end_point_task) | **POST** /api/v1/endpointTask | Create Endpoint task
[**delete_bulk_end_points**](EndpointsApi.md#delete_bulk_end_points) | **DELETE** /api/v1/endpoint/bulk | Delete Endpoint in bulk
[**delete_endpoint**](EndpointsApi.md#delete_endpoint) | **DELETE** /api/v1/endpoint/{value} | Delete endpoint by id or mac
[**get1**](EndpointsApi.md#get1) | **GET** /api/v1/endpoint/{value} | Get endpoint by id or MAC
[**get_device_type_summary**](EndpointsApi.md#get_device_type_summary) | **GET** /api/v1/endpoint/deviceType/summary | Get aggregate of device types
[**list1**](EndpointsApi.md#list1) | **GET** /api/v1/endpoint | Get all endpoints
[**update_bulk_end_points**](EndpointsApi.md#update_bulk_end_points) | **PUT** /api/v1/endpoint/bulk | Update Endpoint in bulk
[**update_endpoint**](EndpointsApi.md#update_endpoint) | **PUT** /api/v1/endpoint/{value} | Update Endpoint by id or mac

# **create_bulk_end_points**
> TaskResponse create_bulk_end_points(body=body)

Create Endpoint in bulk

### Example
```python
from __future__ import print_function
import time
import ise_openapi_endpoints
from ise_openapi_endpoints.rest import ApiException
from pprint import pprint
# Configure HTTP basic authorization: httpBasic
configuration = ise_openapi_endpoints.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = ise_openapi_endpoints.EndpointsApi(ise_openapi_endpoints.ApiClient(configuration))
body = [ise_openapi_endpoints.OpenAPIEndpoint()] # list[OpenAPIEndpoint] |  (optional)

try:
    # Create Endpoint in bulk
    api_response = api_instance.create_bulk_end_points(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->create_bulk_end_points: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**list[OpenAPIEndpoint]**](OpenAPIEndpoint.md)|  | [optional] 

### Return type

[**TaskResponse**](TaskResponse.md)

### Authorization

[httpBasic](../README.md#httpBasic)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_end_point**
> str create_end_point(body=body)

Create Endpoint

### Example
```python
from __future__ import print_function
import time
import ise_openapi_endpoints
from ise_openapi_endpoints.rest import ApiException
from pprint import pprint
# Configure HTTP basic authorization: httpBasic
configuration = ise_openapi_endpoints.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = ise_openapi_endpoints.EndpointsApi(ise_openapi_endpoints.ApiClient(configuration))
body = ise_openapi_endpoints.OpenAPIEndpoint() # OpenAPIEndpoint |  (optional)

try:
    # Create Endpoint
    api_response = api_instance.create_end_point(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->create_end_point: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**OpenAPIEndpoint**](OpenAPIEndpoint.md)|  | [optional] 

### Return type

**str**

### Authorization

[httpBasic](../README.md#httpBasic)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_end_point_task**
> TaskResponse create_end_point_task(body=body)

Create Endpoint task

### Example
```python
from __future__ import print_function
import time
import ise_openapi_endpoints
from ise_openapi_endpoints.rest import ApiException
from pprint import pprint
# Configure HTTP basic authorization: httpBasic
configuration = ise_openapi_endpoints.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = ise_openapi_endpoints.EndpointsApi(ise_openapi_endpoints.ApiClient(configuration))
body = ise_openapi_endpoints.OpenAPIEndpoint() # OpenAPIEndpoint |  (optional)

try:
    # Create Endpoint task
    api_response = api_instance.create_end_point_task(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->create_end_point_task: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**OpenAPIEndpoint**](OpenAPIEndpoint.md)|  | [optional] 

### Return type

[**TaskResponse**](TaskResponse.md)

### Authorization

[httpBasic](../README.md#httpBasic)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_bulk_end_points**
> TaskResponse delete_bulk_end_points(body=body)

Delete Endpoint in bulk

### Example
```python
from __future__ import print_function
import time
import ise_openapi_endpoints
from ise_openapi_endpoints.rest import ApiException
from pprint import pprint
# Configure HTTP basic authorization: httpBasic
configuration = ise_openapi_endpoints.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = ise_openapi_endpoints.EndpointsApi(ise_openapi_endpoints.ApiClient(configuration))
body = ise_openapi_endpoints.BulkEndpoints() # BulkEndpoints |  (optional)

try:
    # Delete Endpoint in bulk
    api_response = api_instance.delete_bulk_end_points(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->delete_bulk_end_points: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**BulkEndpoints**](BulkEndpoints.md)|  | [optional] 

### Return type

[**TaskResponse**](TaskResponse.md)

### Authorization

[httpBasic](../README.md#httpBasic)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_endpoint**
> str delete_endpoint(value)

Delete endpoint by id or mac

### Example
```python
from __future__ import print_function
import time
import ise_openapi_endpoints
from ise_openapi_endpoints.rest import ApiException
from pprint import pprint
# Configure HTTP basic authorization: httpBasic
configuration = ise_openapi_endpoints.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = ise_openapi_endpoints.EndpointsApi(ise_openapi_endpoints.ApiClient(configuration))
value = 'value_example' # str | The id or MAC of the endpoint

try:
    # Delete endpoint by id or mac
    api_response = api_instance.delete_endpoint(value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->delete_endpoint: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **value** | **str**| The id or MAC of the endpoint | 

### Return type

**str**

### Authorization

[httpBasic](../README.md#httpBasic)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get1**
> OpenAPIEndpoint get1(value)

Get endpoint by id or MAC

### Example
```python
from __future__ import print_function
import time
import ise_openapi_endpoints
from ise_openapi_endpoints.rest import ApiException
from pprint import pprint
# Configure HTTP basic authorization: httpBasic
configuration = ise_openapi_endpoints.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = ise_openapi_endpoints.EndpointsApi(ise_openapi_endpoints.ApiClient(configuration))
value = 'value_example' # str | The id or MAC of the endpoint

try:
    # Get endpoint by id or MAC
    api_response = api_instance.get1(value)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->get1: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **value** | **str**| The id or MAC of the endpoint | 

### Return type

[**OpenAPIEndpoint**](OpenAPIEndpoint.md)

### Authorization

[httpBasic](../README.md#httpBasic)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_device_type_summary**
> list[DeviceTypeEntry] get_device_type_summary()

Get aggregate of device types

### Example
```python
from __future__ import print_function
import time
import ise_openapi_endpoints
from ise_openapi_endpoints.rest import ApiException
from pprint import pprint
# Configure HTTP basic authorization: httpBasic
configuration = ise_openapi_endpoints.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = ise_openapi_endpoints.EndpointsApi(ise_openapi_endpoints.ApiClient(configuration))

try:
    # Get aggregate of device types
    api_response = api_instance.get_device_type_summary()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->get_device_type_summary: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[DeviceTypeEntry]**](DeviceTypeEntry.md)

### Authorization

[httpBasic](../README.md#httpBasic)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list1**
> list[OpenAPIEndpoint] list1(page=page, size=size, sort=sort, sort_by=sort_by, filter=filter, filter_type=filter_type)

Get all endpoints

### Example
```python
from __future__ import print_function
import time
import ise_openapi_endpoints
from ise_openapi_endpoints.rest import ApiException
from pprint import pprint
# Configure HTTP basic authorization: httpBasic
configuration = ise_openapi_endpoints.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = ise_openapi_endpoints.EndpointsApi(ise_openapi_endpoints.ApiClient(configuration))
page = 56 # int | Page number (optional)
size = 56 # int | Number of objects returned per page (optional)
sort = 'sort_example' # str | sort type - asc or desc (optional)
sort_by = 'sort_by_example' # str | sort column by which objects needs to be sorted (optional)
filter = 'filter_example' # str | <div> <style type=\"text/css\" scoped> .apiServiceTable td, .apiServiceTable th { padding: 5px 10px !important; text-align: left; } </style> <span> <b>Simple filtering</b> should be available through the filter query string parameter. The structure of a filter is a triplet of field operator and value separated with dots. More than one filter can be sent. The logical operator common to ALL filter criteria will be by default AND, and can be changed by using the <i>\"filterType=or\"</i> query string parameter. Each resource Data model description should specify if an attribute is a filtered field. </span> <br /> <table class=\"apiServiceTable\"> <thead> <tr> <th>OPERATOR</th> <th>DESCRIPTION</th> </tr> </thead> <tbody> <tr> <td>EQ</td> <td>Equals</td> </tr> <tr> <td>NEQ</td> <td>Not Equals</td> </tr> <tr> <td>GT</td> <td>Greater Than</td> </tr> <tr> <td>LT</td> <td>Less Then</td> </tr> <tr> <td>STARTSW</td> <td>Starts With</td> </tr> <tr> <td>NSTARTSW</td> <td>Not Starts With</td> </tr> <tr> <td>ENDSW</td> <td>Ends With</td> </tr> <tr> <td>NENDSW</td> <td>Not Ends With</td> </tr> <tr> <td>CONTAINS</td> <td>Contains</td> </tr> <tr> <td>NCONTAINS</td> <td>Not Contains</td> </tr> </tbody> </table> </div> (optional)
filter_type = 'filter_type_example' # str | The logical operator common to ALL filter criteria will be by default AND, and can be changed by using the parameter (optional)

try:
    # Get all endpoints
    api_response = api_instance.list1(page=page, size=size, sort=sort, sort_by=sort_by, filter=filter, filter_type=filter_type)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->list1: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**| Page number | [optional] 
 **size** | **int**| Number of objects returned per page | [optional] 
 **sort** | **str**| sort type - asc or desc | [optional] 
 **sort_by** | **str**| sort column by which objects needs to be sorted | [optional] 
 **filter** | **str**| &lt;div&gt; &lt;style type&#x3D;\&quot;text/css\&quot; scoped&gt; .apiServiceTable td, .apiServiceTable th { padding: 5px 10px !important; text-align: left; } &lt;/style&gt; &lt;span&gt; &lt;b&gt;Simple filtering&lt;/b&gt; should be available through the filter query string parameter. The structure of a filter is a triplet of field operator and value separated with dots. More than one filter can be sent. The logical operator common to ALL filter criteria will be by default AND, and can be changed by using the &lt;i&gt;\&quot;filterType&#x3D;or\&quot;&lt;/i&gt; query string parameter. Each resource Data model description should specify if an attribute is a filtered field. &lt;/span&gt; &lt;br /&gt; &lt;table class&#x3D;\&quot;apiServiceTable\&quot;&gt; &lt;thead&gt; &lt;tr&gt; &lt;th&gt;OPERATOR&lt;/th&gt; &lt;th&gt;DESCRIPTION&lt;/th&gt; &lt;/tr&gt; &lt;/thead&gt; &lt;tbody&gt; &lt;tr&gt; &lt;td&gt;EQ&lt;/td&gt; &lt;td&gt;Equals&lt;/td&gt; &lt;/tr&gt; &lt;tr&gt; &lt;td&gt;NEQ&lt;/td&gt; &lt;td&gt;Not Equals&lt;/td&gt; &lt;/tr&gt; &lt;tr&gt; &lt;td&gt;GT&lt;/td&gt; &lt;td&gt;Greater Than&lt;/td&gt; &lt;/tr&gt; &lt;tr&gt; &lt;td&gt;LT&lt;/td&gt; &lt;td&gt;Less Then&lt;/td&gt; &lt;/tr&gt; &lt;tr&gt; &lt;td&gt;STARTSW&lt;/td&gt; &lt;td&gt;Starts With&lt;/td&gt; &lt;/tr&gt; &lt;tr&gt; &lt;td&gt;NSTARTSW&lt;/td&gt; &lt;td&gt;Not Starts With&lt;/td&gt; &lt;/tr&gt; &lt;tr&gt; &lt;td&gt;ENDSW&lt;/td&gt; &lt;td&gt;Ends With&lt;/td&gt; &lt;/tr&gt; &lt;tr&gt; &lt;td&gt;NENDSW&lt;/td&gt; &lt;td&gt;Not Ends With&lt;/td&gt; &lt;/tr&gt; &lt;tr&gt; &lt;td&gt;CONTAINS&lt;/td&gt; &lt;td&gt;Contains&lt;/td&gt; &lt;/tr&gt; &lt;tr&gt; &lt;td&gt;NCONTAINS&lt;/td&gt; &lt;td&gt;Not Contains&lt;/td&gt; &lt;/tr&gt; &lt;/tbody&gt; &lt;/table&gt; &lt;/div&gt; | [optional] 
 **filter_type** | **str**| The logical operator common to ALL filter criteria will be by default AND, and can be changed by using the parameter | [optional] 

### Return type

[**list[OpenAPIEndpoint]**](OpenAPIEndpoint.md)

### Authorization

[httpBasic](../README.md#httpBasic)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_bulk_end_points**
> TaskResponse update_bulk_end_points(body=body)

Update Endpoint in bulk

### Example
```python
from __future__ import print_function
import time
import ise_openapi_endpoints
from ise_openapi_endpoints.rest import ApiException
from pprint import pprint
# Configure HTTP basic authorization: httpBasic
configuration = ise_openapi_endpoints.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = ise_openapi_endpoints.EndpointsApi(ise_openapi_endpoints.ApiClient(configuration))
body = [ise_openapi_endpoints.OpenAPIEndpoint()] # list[OpenAPIEndpoint] |  (optional)

try:
    # Update Endpoint in bulk
    api_response = api_instance.update_bulk_end_points(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->update_bulk_end_points: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**list[OpenAPIEndpoint]**](OpenAPIEndpoint.md)|  | [optional] 

### Return type

[**TaskResponse**](TaskResponse.md)

### Authorization

[httpBasic](../README.md#httpBasic)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_endpoint**
> OpenAPIEndpoint update_endpoint(value, body=body)

Update Endpoint by id or mac

### Example
```python
from __future__ import print_function
import time
import ise_openapi_endpoints
from ise_openapi_endpoints.rest import ApiException
from pprint import pprint
# Configure HTTP basic authorization: httpBasic
configuration = ise_openapi_endpoints.Configuration()
configuration.username = 'YOUR_USERNAME'
configuration.password = 'YOUR_PASSWORD'

# create an instance of the API class
api_instance = ise_openapi_endpoints.EndpointsApi(ise_openapi_endpoints.ApiClient(configuration))
value = 'value_example' # str | The id or MAC of the endpoint
body = ise_openapi_endpoints.OpenAPIEndpoint() # OpenAPIEndpoint |  (optional)

try:
    # Update Endpoint by id or mac
    api_response = api_instance.update_endpoint(value, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling EndpointsApi->update_endpoint: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **value** | **str**| The id or MAC of the endpoint | 
 **body** | [**OpenAPIEndpoint**](OpenAPIEndpoint.md)|  | [optional] 

### Return type

[**OpenAPIEndpoint**](OpenAPIEndpoint.md)

### Authorization

[httpBasic](../README.md#httpBasic)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

