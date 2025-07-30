"""
The `.igx_api_client.IgxApiClient` class is the main entry point for interacting with the IGX API. You use
it as a context manager, and by default it wil fetch the API key from the `IGX_API_KEY` environment variable.

Different functionalities are separated by their contexts, a list of these can be found in the `.api`
module. These are all available as attributes of the `.igx_api_client.IgxApiClient` instance.

For example, to access the `collection` API to list all your collections with their metadata, you can do the following:

```python
with IgxApiClient() as igx_client:
    for collection in igx_client.collection_api.get_collections_metadata():
        print(collection)
```
"""
