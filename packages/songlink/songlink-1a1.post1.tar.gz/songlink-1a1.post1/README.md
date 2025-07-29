# Songlink.py is an unofficial helper libray for querying the [Songlink](https://odesli.co/) API

The library builds atop of the stdlib requests and json libraries with the `Client`, `Decoder` and, `QueryParamaters` classes. The`Client.search()` method gives a simple way to query the api. The library is modular so there is nothing stopping you from making the requests yourself and just using the JSON decoder for the structured data.

## Example Request

```python
params = QueryParameters(songIfSingle=True)

with Client(default_params=params) as songlink:
    response = songlink.search(QueryParameters(url="https://music.apple.com/au/album/its-not-up-to-you/1726654492?i=1726654496"))

    entity_id = response.entityUniqueId

    print(response.entitiesByUniqueId[entity_id].thumbnailUrl)
```
