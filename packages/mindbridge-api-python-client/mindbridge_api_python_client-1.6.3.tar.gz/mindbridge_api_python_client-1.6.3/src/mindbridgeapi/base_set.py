#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

import contextlib
from dataclasses import dataclass
from http import HTTPStatus
import json
import logging
import shutil
from typing import TYPE_CHECKING, Any, Optional
from urllib.parse import urlencode
from urllib3.util import Retry
from mindbridgeapi.exceptions import UnexpectedServerError, ValidationError

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable
    from pathlib import Path
    from urllib3.response import BaseHTTPResponse
    from mindbridgeapi.server import Server

logger = logging.getLogger(__name__)


@dataclass
class BaseSet:
    server: "Server"

    def _get_by_id(
        self, url: str, query_parameters: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        resp = self.server.http.request("GET", url, fields=query_parameters)
        self._check_response(resp)
        return self._response_as_dict(resp)

    def _get(
        self, url: str, json: dict[str, Any]
    ) -> "Generator[dict[str, Any], None, None]":
        item_holder: list[dict[str, Any]] = []
        page_number = 0
        more_pages_to_check = True

        while item_holder or more_pages_to_check:
            if not item_holder:
                content = self._get_page(url=url, json=json, page_number=page_number)

                if not content:
                    more_pages_to_check = False
                else:
                    item_holder.extend(content)
                    page_number += 1

            if item_holder:
                yield item_holder.pop(0)

    def _get_page(
        self, url: str, json: dict[str, Any], page_number: int
    ) -> list[dict[str, Any]]:
        params = {"page": page_number}
        request_url = f"{url}?{urlencode(params)}"

        # Same as set for the PoolManager (http) in Server, but getting a page will
        # always be considered to be idempotent so we can allow repeat post requests
        method = "POST"
        retries = Retry(
            connect=3, read=3, redirect=0, other=0, allowed_methods={method}
        )

        resp = self.server.http.request(method, request_url, retries=retries, json=json)
        self._check_response(resp)
        resp_dict = self._response_as_dict(resp)

        if "content" not in resp_dict or not isinstance(resp_dict["content"], list):
            msg = f"{resp_dict}."
            raise UnexpectedServerError(msg)

        return resp_dict["content"]

    def _create(
        self,
        url: str,
        json: Optional[dict[str, Any]] = None,
        extra_ok_statuses: Optional["Iterable[int]"] = None,
    ) -> dict[str, Any]:
        if json is None:
            json = {}

        resp = self.server.http.request("POST", url, json=json)
        self._check_response(resp=resp, extra_ok_statuses=extra_ok_statuses)
        return self._response_as_dict(resp)

    def _delete(self, url: str) -> None:
        resp = self.server.http.request("DELETE", url)
        self._check_response(resp)

    def _update(self, url: str, json: dict[str, Any]) -> dict[str, Any]:
        resp = self.server.http.request("PUT", url, json=json)
        self._check_response(resp)
        return self._response_as_dict(resp)

    def _upload(self, url: str, files: dict[str, Any]) -> dict[str, Any]:
        resp = self.server.http.request("POST", url, fields=files)

        self._check_response(resp)
        return self._response_as_dict(resp)

    @staticmethod
    def _response_as_dict(resp: "BaseHTTPResponse") -> dict[str, Any]:
        """Converts the HTTP response body as a dict.

        Args:
            resp (urllib3.response.BaseHTTPResponse): The HTTP response from the server

        Returns:
            Dict[str, Any]: The dict representation of the JSON response from the server

        Raises:
            UnexpectedServerError: When the response is not JSON, or it is JSON but
                python didn't parase the data to a dict
        """
        if resp.status == HTTPStatus.NO_CONTENT:
            # No body expected, so the return value won't be used
            return {}

        try:
            resp_obj = resp.json()
        except UnicodeDecodeError as err:
            msg = "body was not UTF-8."
            raise UnexpectedServerError(msg) from err
        except json.JSONDecodeError as err:
            msg = "body was not JSON."
            raise UnexpectedServerError(msg) from err

        if not isinstance(resp_obj, dict):
            msg = "JSON was not an object."
            raise UnexpectedServerError(msg)

        return resp_obj

    def _download(self, url: str, output_path: "Path") -> "Path":
        with (
            self.server.http.request("GET", url, preload_content=False) as resp,
            output_path.open("wb") as write_file,
        ):
            shutil.copyfileobj(resp, write_file)
            self._check_response(resp)
            resp.release_conn()

        return output_path

    @staticmethod
    def _check_response(
        resp: "BaseHTTPResponse", extra_ok_statuses: Optional["Iterable[int]"] = None
    ) -> None:
        """Raises error if response status is not ok, also logs.

        Raises:
            ValidationError: If 400 response
            UnexpectedServerError: If 500 response
        """
        if extra_ok_statuses is None:
            extra_ok_statuses = iter(())

        http_code_phrase = f"{resp.status} {HTTPStatus(resp.status).phrase}"

        log_str = "HTTP response (approximately):"
        log_str += f"\n{http_code_phrase}"
        for k, v in resp.headers.items():
            log_str += f"\n{k}: {v}"

        log_str += "\n"
        try:
            log_str += f"\n{json.dumps(resp.json(), indent=4, sort_keys=True)}"
        except (UnicodeDecodeError, json.JSONDecodeError):
            if len(resp.data) > 0:
                log_str += "\n[Body that is apparently not JSON data]"

        logger.debug(log_str)

        # Raise error if not ok
        if (
            resp.status >= HTTPStatus.BAD_REQUEST
            and resp.status not in extra_ok_statuses
        ):
            http_error_msg = f"{http_code_phrase} for url: {resp.url}"
            with contextlib.suppress(UnicodeDecodeError, json.JSONDecodeError):
                http_error_msg += (
                    f"\n{json.dumps(resp.json(), indent=4, sort_keys=True)}."
                )

            if resp.status < HTTPStatus.INTERNAL_SERVER_ERROR:
                raise ValidationError(http_error_msg)

            raise UnexpectedServerError(http_error_msg)
