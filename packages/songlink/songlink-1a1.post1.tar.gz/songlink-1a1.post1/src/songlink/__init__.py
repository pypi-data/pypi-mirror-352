from typing import Literal, Final #, Any, TypedDict, Self
from dataclasses import dataclass, asdict
import json
import requests
# from functools import lru_cache

ENDPOINT: Final = 'https://api.song.link/v1-alpha.1/links'

type Platform = Literal[
    'spotify',
    'itunes',
    'appleMusic',
    'youtube',
    'youtubeMusic',
    'google',
    'googleStore',
    'pandora',
    'deezer',
    'tidal',
    'amazonStore',
    'amazonMusic',
    'soundcloud',
    'napster',
    'yandex',
    'spinrilla',
    'audius',
    'audiomack',
    'anghami',
    'boomplay'
]

type APIProvider = Literal[
    'spotify',
    'itunes',
    'youtube',
    'google',
    'pandora',
    'deezer',
    'tidal',
    'amazon',
    'soundcloud',
    'napster',
    'yandex',
    'spinrilla',
    'audius',
    'audiomack',
    'anghami',
    'boomplay'
]

#The platforms supposedly supported for queries by songlink.
type SearchablePlatforms = Literal[
    'spotify',
    'itunes',
    'appleMusic',
    'youtube',
    'youtubeMusic',
    'google',
    'googleStore',
    'pandora',
    'deezer',
    'tidal',
    'amazonStore',
    'amazonMusic',
    'soundcloud',
    'napster',
    'yandex',
    'spinrilla',
    'audius',
    'anghami',
    'boomplay',
    'audiomack',
    'isrc',
    'upc'
]

@dataclass(frozen=True)
class QueryParameters():
    """**`url`** -- The URL of a valid song or album from any of our supported platforms.`

**`userCountry`** -- Two-letter country code. Specifies the country/location we use when searching streaming catalogs. Optional. Defaults to `US`.

**`songIfSingle`** -- Defaults to `false`. Pass in `true` if you'd like us to use/return song data for single-song albums (i.e. “singles”). We often do better matching if we use the song instead of the album/single, so this is highly recommend.

**`platform`** -- The platform of the entity you'd like to match. See above section for supported platforms. If `url` is not provided, you must provide `platform`, `type` and `id`.

**`type`** -- The type of streaming entity. We support `song` and `album`. If `url` is not provided, you must provide `platform`, `type` and `id`.

**`id`** -- The unique identifier of the streaming entity, e.g. `1443109064` which is an iTunes ID. If `url` is not provided, you must provide `platform`, `type` and `id`."""
    url: str | None = None
    userCountry: str | None = None
    songIfSingle: bool | None = None
    platform: SearchablePlatforms | None = None
    type: Literal['song', 'album'] | None = None
    id: str | None = None

    def as_dict(self) -> dict[str, str | bool | Literal['song', 'album']]:
        data = asdict(self)
        return {key: value for key, value in data.items() if value is not None}

@dataclass(frozen=True)
class LinkInfo:
    entityUniqueId: str
    url: str
    country: str | None = None #UNDOCUMENTED API BEHAVIOUR
    nativeAppUriMobile: str | None = None
    nativeAppUriDesktop: str | None = None

@dataclass(frozen=True)
class IdInfo:
    id: str

    type: Literal['song', 'album']

    apiProvider: APIProvider

    platforms: list[Platform]

    title: str | None = None
    artistName: str | None = None
    thumbnailUrl: str | None = None
    thumbnailWidth: int | None = None
    thumbnailHeight: int | None = None

@dataclass(frozen=True)
class APIResponse:
    entityUniqueId: str
    userCountry: str
    pageUrl: str

    linksByPlatform: dict[Platform, LinkInfo]

    entitiesByUniqueId: dict[str, IdInfo]

class Decoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if (
            'entityUniqueId' in obj and
            'userCountry' in obj and
            'pageUrl' in obj and
            'linksByPlatform' in obj and
            'entitiesByUniqueId' in obj
        ):
            links = {
                k: LinkInfo(**v)
                for k, v in obj['linksByPlatform'].items()
            }

            entities = {
                k: IdInfo(**v)
                for k, v in obj['entitiesByUniqueId'].items()
            }

            return APIResponse(
                entityUniqueId=obj['entityUniqueId'],
                userCountry=obj['userCountry'],
                pageUrl=obj['pageUrl'],
                linksByPlatform=links,
                entitiesByUniqueId=entities
            )
        
        return obj


class Client(requests.sessions.Session):
    def __init__(self, default_params: QueryParameters | None = None):
        super().__init__()

        self.default_params = default_params.as_dict() if default_params else {}
    
    # @lru_cache(maxsize=256) ruining method signature
    def search(self, query: QueryParameters) -> APIResponse:
        params = self.default_params | query.as_dict()

        request = self.get(ENDPOINT, params=params)

        request.raise_for_status()

        return request.json(cls=Decoder)
    