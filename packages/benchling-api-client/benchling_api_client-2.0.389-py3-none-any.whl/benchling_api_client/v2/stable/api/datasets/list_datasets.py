from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.datasets_paginated_list import DatasetsPaginatedList
from ...models.list_datasets_sort import ListDatasetsSort
from ...models.listing_error import ListingError
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    page_size: int = 50,
    next_token: str,
    sort: ListDatasetsSort = ListDatasetsSort.MODIFIEDAT,
    archive_reason: str,
    created_at: str,
    creator_ids: str,
    folder_id: str,
    mentioned_in: str,
    modified_at: str,
    name: str,
    name_includes: str,
    namesany_ofcase_sensitive: str,
    namesany_of: str,
    origin_ids: str,
    ids: Union[Unset, str] = UNSET,
    display_ids: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/datasets".format(client.base_url)

    headers: Dict[str, Any] = client.httpx_client.headers
    headers.update(client.get_headers())

    cookies: Dict[str, Any] = client.httpx_client.cookies
    cookies.update(client.get_cookies())

    json_sort = sort.value

    params: Dict[str, Any] = {
        "pageSize": page_size,
        "nextToken": next_token,
        "sort": json_sort,
        "archiveReason": archive_reason,
        "createdAt": created_at,
        "creatorIds": creator_ids,
        "folderId": folder_id,
        "mentionedIn": mentioned_in,
        "modifiedAt": modified_at,
        "name": name,
        "nameIncludes": name_includes,
        "names.anyOf.caseSensitive": namesany_ofcase_sensitive,
        "names.anyOf": namesany_of,
        "originIds": origin_ids,
    }
    if not isinstance(ids, Unset) and ids is not None:
        params["ids"] = ids
    if not isinstance(display_ids, Unset) and display_ids is not None:
        params["displayIds"] = display_ids
    if not isinstance(returning, Unset) and returning is not None:
        params["returning"] = returning

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[DatasetsPaginatedList, ListingError]]:
    if response.status_code == 200:
        response_200 = DatasetsPaginatedList.from_dict(response.json(), strict=False)

        return response_200
    if response.status_code == 400:
        response_400 = ListingError.from_dict(response.json(), strict=False)

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[DatasetsPaginatedList, ListingError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    page_size: int = 50,
    next_token: str,
    sort: ListDatasetsSort = ListDatasetsSort.MODIFIEDAT,
    archive_reason: str,
    created_at: str,
    creator_ids: str,
    folder_id: str,
    mentioned_in: str,
    modified_at: str,
    name: str,
    name_includes: str,
    namesany_ofcase_sensitive: str,
    namesany_of: str,
    origin_ids: str,
    ids: Union[Unset, str] = UNSET,
    display_ids: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
) -> Response[Union[DatasetsPaginatedList, ListingError]]:
    kwargs = _get_kwargs(
        client=client,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
        archive_reason=archive_reason,
        created_at=created_at,
        creator_ids=creator_ids,
        folder_id=folder_id,
        mentioned_in=mentioned_in,
        modified_at=modified_at,
        name=name,
        name_includes=name_includes,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        namesany_of=namesany_of,
        origin_ids=origin_ids,
        ids=ids,
        display_ids=display_ids,
        returning=returning,
    )

    response = client.httpx_client.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    page_size: int = 50,
    next_token: str,
    sort: ListDatasetsSort = ListDatasetsSort.MODIFIEDAT,
    archive_reason: str,
    created_at: str,
    creator_ids: str,
    folder_id: str,
    mentioned_in: str,
    modified_at: str,
    name: str,
    name_includes: str,
    namesany_ofcase_sensitive: str,
    namesany_of: str,
    origin_ids: str,
    ids: Union[Unset, str] = UNSET,
    display_ids: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
) -> Optional[Union[DatasetsPaginatedList, ListingError]]:
    """ List datasets """

    return sync_detailed(
        client=client,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
        archive_reason=archive_reason,
        created_at=created_at,
        creator_ids=creator_ids,
        folder_id=folder_id,
        mentioned_in=mentioned_in,
        modified_at=modified_at,
        name=name,
        name_includes=name_includes,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        namesany_of=namesany_of,
        origin_ids=origin_ids,
        ids=ids,
        display_ids=display_ids,
        returning=returning,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    page_size: int = 50,
    next_token: str,
    sort: ListDatasetsSort = ListDatasetsSort.MODIFIEDAT,
    archive_reason: str,
    created_at: str,
    creator_ids: str,
    folder_id: str,
    mentioned_in: str,
    modified_at: str,
    name: str,
    name_includes: str,
    namesany_ofcase_sensitive: str,
    namesany_of: str,
    origin_ids: str,
    ids: Union[Unset, str] = UNSET,
    display_ids: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
) -> Response[Union[DatasetsPaginatedList, ListingError]]:
    kwargs = _get_kwargs(
        client=client,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
        archive_reason=archive_reason,
        created_at=created_at,
        creator_ids=creator_ids,
        folder_id=folder_id,
        mentioned_in=mentioned_in,
        modified_at=modified_at,
        name=name,
        name_includes=name_includes,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        namesany_of=namesany_of,
        origin_ids=origin_ids,
        ids=ids,
        display_ids=display_ids,
        returning=returning,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    page_size: int = 50,
    next_token: str,
    sort: ListDatasetsSort = ListDatasetsSort.MODIFIEDAT,
    archive_reason: str,
    created_at: str,
    creator_ids: str,
    folder_id: str,
    mentioned_in: str,
    modified_at: str,
    name: str,
    name_includes: str,
    namesany_ofcase_sensitive: str,
    namesany_of: str,
    origin_ids: str,
    ids: Union[Unset, str] = UNSET,
    display_ids: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
) -> Optional[Union[DatasetsPaginatedList, ListingError]]:
    """ List datasets """

    return (
        await asyncio_detailed(
            client=client,
            page_size=page_size,
            next_token=next_token,
            sort=sort,
            archive_reason=archive_reason,
            created_at=created_at,
            creator_ids=creator_ids,
            folder_id=folder_id,
            mentioned_in=mentioned_in,
            modified_at=modified_at,
            name=name,
            name_includes=name_includes,
            namesany_ofcase_sensitive=namesany_ofcase_sensitive,
            namesany_of=namesany_of,
            origin_ids=origin_ids,
            ids=ids,
            display_ids=display_ids,
            returning=returning,
        )
    ).parsed
