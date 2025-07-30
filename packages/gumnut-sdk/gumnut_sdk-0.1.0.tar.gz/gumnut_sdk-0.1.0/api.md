# APIKeys

Types:

```python
from photos.types import APIKeyResponse, APIKeyCreateResponse, APIKeyListResponse
```

Methods:

- <code title="post /api-keys/">client.api_keys.<a href="./src/photos/resources/api_keys.py">create</a>() -> <a href="./src/photos/types/api_key_create_response.py">APIKeyCreateResponse</a></code>
- <code title="get /api-keys/">client.api_keys.<a href="./src/photos/resources/api_keys.py">list</a>() -> <a href="./src/photos/types/api_key_list_response.py">APIKeyListResponse</a></code>
- <code title="delete /api-keys/{key_id}">client.api_keys.<a href="./src/photos/resources/api_keys.py">delete</a>(key_id) -> None</code>

# Assets

Types:

```python
from photos.types import AssetResponse
```

Methods:

- <code title="post /api/assets">client.assets.<a href="./src/photos/resources/assets.py">create</a>(\*\*<a href="src/photos/types/asset_create_params.py">params</a>) -> <a href="./src/photos/types/asset_response.py">AssetResponse</a></code>
- <code title="get /api/assets/{asset_id}">client.assets.<a href="./src/photos/resources/assets.py">retrieve</a>(asset_id) -> <a href="./src/photos/types/asset_response.py">AssetResponse</a></code>
- <code title="get /api/assets">client.assets.<a href="./src/photos/resources/assets.py">list</a>(\*\*<a href="src/photos/types/asset_list_params.py">params</a>) -> <a href="./src/photos/types/asset_response.py">SyncCursorPage[AssetResponse]</a></code>
- <code title="delete /api/assets/{asset_id}">client.assets.<a href="./src/photos/resources/assets.py">delete</a>(asset_id) -> None</code>
- <code title="get /api/assets/{asset_id}/download">client.assets.<a href="./src/photos/resources/assets.py">download</a>(asset_id) -> BinaryAPIResponse</code>
- <code title="get /api/assets/{asset_id}/thumbnail">client.assets.<a href="./src/photos/resources/assets.py">download_thumbnail</a>(asset_id, \*\*<a href="src/photos/types/asset_download_thumbnail_params.py">params</a>) -> BinaryAPIResponse</code>

# Albums

Types:

```python
from photos.types import AlbumResponse
```

Methods:

- <code title="post /api/albums">client.albums.<a href="./src/photos/resources/albums/albums.py">create</a>(\*\*<a href="src/photos/types/album_create_params.py">params</a>) -> <a href="./src/photos/types/album_response.py">AlbumResponse</a></code>
- <code title="get /api/albums/{album_id}">client.albums.<a href="./src/photos/resources/albums/albums.py">retrieve</a>(album_id) -> <a href="./src/photos/types/album_response.py">AlbumResponse</a></code>
- <code title="patch /api/albums/{album_id}">client.albums.<a href="./src/photos/resources/albums/albums.py">update</a>(album_id, \*\*<a href="src/photos/types/album_update_params.py">params</a>) -> <a href="./src/photos/types/album_response.py">AlbumResponse</a></code>
- <code title="get /api/albums">client.albums.<a href="./src/photos/resources/albums/albums.py">list</a>(\*\*<a href="src/photos/types/album_list_params.py">params</a>) -> <a href="./src/photos/types/album_response.py">SyncCursorPage[AlbumResponse]</a></code>
- <code title="delete /api/albums/{album_id}">client.albums.<a href="./src/photos/resources/albums/albums.py">delete</a>(album_id) -> None</code>

## Assets

Types:

```python
from photos.types.albums import AlbumAssetAssociation, AssetListResponse
```

Methods:

- <code title="get /api/albums/{album_id}/assets">client.albums.assets.<a href="./src/photos/resources/albums/assets.py">list</a>(album_id) -> <a href="./src/photos/types/albums/asset_list_response.py">AssetListResponse</a></code>
- <code title="post /api/albums/{album_id}/assets">client.albums.assets.<a href="./src/photos/resources/albums/assets.py">add</a>(album_id, \*\*<a href="src/photos/types/albums/asset_add_params.py">params</a>) -> None</code>
- <code title="delete /api/albums/{album_id}/assets">client.albums.assets.<a href="./src/photos/resources/albums/assets.py">remove</a>(album_id, \*\*<a href="src/photos/types/albums/asset_remove_params.py">params</a>) -> None</code>

# Faces

Types:

```python
from photos.types import FaceResponse
```

Methods:

- <code title="get /api/faces/{face_id}">client.faces.<a href="./src/photos/resources/faces.py">retrieve</a>(face_id) -> <a href="./src/photos/types/face_response.py">FaceResponse</a></code>
- <code title="patch /api/faces/{face_id}">client.faces.<a href="./src/photos/resources/faces.py">update</a>(face_id, \*\*<a href="src/photos/types/face_update_params.py">params</a>) -> <a href="./src/photos/types/face_response.py">FaceResponse</a></code>
- <code title="get /api/faces">client.faces.<a href="./src/photos/resources/faces.py">list</a>(\*\*<a href="src/photos/types/face_list_params.py">params</a>) -> <a href="./src/photos/types/face_response.py">SyncCursorPage[FaceResponse]</a></code>
- <code title="delete /api/faces/{face_id}">client.faces.<a href="./src/photos/resources/faces.py">delete</a>(face_id) -> None</code>
- <code title="get /api/faces/{face_id}/thumbnail">client.faces.<a href="./src/photos/resources/faces.py">download_thumbnail</a>(face_id) -> BinaryAPIResponse</code>

# People

Types:

```python
from photos.types import PersonResponse
```

Methods:

- <code title="post /api/people">client.people.<a href="./src/photos/resources/people.py">create</a>(\*\*<a href="src/photos/types/person_create_params.py">params</a>) -> <a href="./src/photos/types/person_response.py">PersonResponse</a></code>
- <code title="get /api/people/{person_id}">client.people.<a href="./src/photos/resources/people.py">retrieve</a>(person_id) -> <a href="./src/photos/types/person_response.py">PersonResponse</a></code>
- <code title="patch /api/people/{person_id}">client.people.<a href="./src/photos/resources/people.py">update</a>(person_id, \*\*<a href="src/photos/types/person_update_params.py">params</a>) -> <a href="./src/photos/types/person_response.py">PersonResponse</a></code>
- <code title="get /api/people">client.people.<a href="./src/photos/resources/people.py">list</a>(\*\*<a href="src/photos/types/person_list_params.py">params</a>) -> <a href="./src/photos/types/person_response.py">SyncCursorPage[PersonResponse]</a></code>
- <code title="delete /api/people/{person_id}">client.people.<a href="./src/photos/resources/people.py">delete</a>(person_id) -> None</code>

# Search

Types:

```python
from photos.types import SearchResponse
```

Methods:

- <code title="get /api/search">client.search.<a href="./src/photos/resources/search.py">search</a>(\*\*<a href="src/photos/types/search_search_params.py">params</a>) -> <a href="./src/photos/types/search_response.py">SearchResponse</a></code>
