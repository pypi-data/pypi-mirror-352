from __future__ import annotations

from typing import Any, Literal, Mapping, TypedDict, Union

from httpx._types import QueryParamTypes, RequestExtensions


class Omit:
    """In certain situations you need to be able to represent a case where a default value has
    to be explicitly removed and `None` is not an appropriate substitute, for example:

    ```py
    # as the default `Content-Type` header is `application/json` that will be sent
    client.post("/upload/files", files={"file": b"my raw file content"})

    # you can't explicitly override the header as it has to be dynamically generated
    # to look something like: 'multipart/form-data; boundary=0d8382fcf5f8c3be01ca2e11002d2983'
    client.post(..., headers={"Content-Type": "multipart/form-data"})

    # instead you can remove the default `application/json` header by passing Omit
    client.post(..., headers={"Content-Type": Omit()})
    ```
    """

    def __bool__(self) -> Literal[False]:
        return False


Headers = Mapping[str, Union[str, Omit]]


class RequestOptions(TypedDict, total=False):
    json: Any | None
    headers: Headers | None
    params: QueryParamTypes | None
    extensions: RequestExtensions | None
    stream: bool | None
