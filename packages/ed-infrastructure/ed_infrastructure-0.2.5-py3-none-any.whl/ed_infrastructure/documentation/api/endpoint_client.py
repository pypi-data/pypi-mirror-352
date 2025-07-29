from typing import Generic, TypeVar

import aiohttp
import jsons
from ed_domain.common.exceptions import ApplicationException, Exceptions
from ed_domain.common.logging import get_logger
from ed_domain.documentation.api.abc_endpoint_client import ABCEndpointClient
from ed_domain.documentation.api.definitions import (ApiResponse,
                                                     EndpointCallParams,
                                                     EndpointDescription)

TResponceType = TypeVar("TResponceType")
LOG = get_logger()


class EndpointClient(Generic[TResponceType], ABCEndpointClient[TResponceType]):
    def __init__(self, description: EndpointDescription):
        self._description = description
        self._client_session = aiohttp.ClientSession(
            json_serialize=jsons.dumps)

    async def __call__(
        self, call_params: EndpointCallParams
    ) -> ApiResponse[TResponceType]:
        self._validate_endpoint_description(call_params)

        url = self._build_url(call_params)
        method = self._description["method"]
        headers = call_params.get("headers", {})
        params = call_params.get("query_params", {})
        data = (
            call_params.get("request", {})
            if "request_model" in self._description
            else None
        )
        dumped_data = jsons.dumps(data) if data else None

        try:
            LOG.debug(
                f"Making  a {method} request to {url} with headers {headers}, params {params}, and data {dumped_data}"
            )

            async with self._client_session.request(
                method=method, url=url, headers=headers, params=params, data=dumped_data
            ) as response:
                LOG.debug(f"Response Status Code: {response.status}")
                response_text = await response.text()
                LOG.debug(f"Response Text: {response_text}")

                try:
                    json_data = await response.json()
                except aiohttp.ContentTypeError:
                    json_data = {}

                json_data["http_status_code"] = response.status
                return json_data  # type: ignore

        except aiohttp.ClientError as e:
            LOG.error(f"Request failed: {e}")
            raise ApplicationException(
                Exceptions.InternalServerException,
                "Internal server error",
                [f"Request to {url} failed with error: {e}"],
            )

    def _build_url(self, call_params: EndpointCallParams) -> str:
        path = self._description["path"]
        path_params = call_params.get("path_params", {})

        for key, value in path_params.items():
            path = path.replace(f"{{{key}}}", str(value))

        return f"{path}"

    def _validate_endpoint_description(self, call_params: EndpointCallParams):
        if request_model := self._description.get("request_model", None):
            if request := call_params.get("request", None):
                if not isinstance(request, type(request_model)):
                    ...
            else:
                raise ValueError("Request is not provided but is expected.")

        if path_params := call_params.get("path_params", None):
            for param in path_params.keys():
                if f"{{{param}}}" not in self._description["path"]:
                    raise ValueError(
                        f"Path parameter '{param}' is not present in the path."
                    )

        if placeholders := [
            part[1:-1]
            for part in self._description["path"].split("/")
            if part.startswith("{") and part.endswith("}")
        ]:
            if "path_params" not in call_params:
                raise ValueError("Path parameters are missing in path_params.")

            for placeholder in placeholders:
                if placeholder not in call_params["path_params"]:
                    raise ValueError(
                        f"Path parameter '{placeholder}' is missing in path_params."
                    )

    async def close(self):
        await self._client_session.close()
