"""
The `igx_api.l2` module contains higher level functions and utilities for comfortably interacting with the IGX API.

### Platform APIs
To interact with the IGX Platform through the SDK/API, have a look at the `igx_api.l2.client.igx_api_client.IgxApiClient`
class. You will need this class to access the various APIs available in the SDK.

### Listening to Events
To listen to events from the IGX Platform, have a look at the `igx_api.l2.events` module. This module contains functions
that enable you to listen to events on the platform.
For more information about events, and the available events, have a look at the [events documentation](/public-api/v1/public/docs/events).

### System tags
For a list of all system tags, separated by their contexts (e.g. `collection`, `sequence`, `file`, etc.), have a look at
the `igx_api.l2.tags` module. These lists do not contain your own custom-made tags. If you need the ID of a custom tag
you can use the `igx_api.l2.client.api.tag_api.TagApi.get_tag_archetype_by_name` function to find it.
"""
