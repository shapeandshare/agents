""" Abstract Command Definition """

import json
import logging
import time
from abc import abstractmethod

import requests
from pydantic import BaseModel
from requests import Response

from .......sdk.contracts.dtos.command_options import CommandOptions
from .......sdk.contracts.dtos.wrapped_request import WrappedRequest
from .......sdk.contracts.errors.exceeded_retry_count import ExceededRetryCountError
from .......sdk.contracts.errors.request_failure import RequestFailureError
from .......sdk.contracts.errors.unknown_verb import UnknownVerbError
from .......sdk.contracts.types.request_verb import RequestVerbType
from ......framework.common.config.environment import demand_env_var, demand_env_var_as_float, demand_env_var_as_int


class AbstractCommand(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    options: CommandOptions | None = None
    session: requests.Session | None = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.options is None:
            self.options: CommandOptions = CommandOptions(
                sleep_time=demand_env_var_as_float(name="CHATHISTORY_SERVICE_SLEEP_TIME"),
                retry_count=demand_env_var_as_int(name="CHATHISTORY_SERVICE_RETRY_COUNT"),
                tld=demand_env_var(name="CHATHISTORY_SERVICE_TLD"),
                scheme=demand_env_var(name="CHATHISTORY_SERVICE_SCHEME"),
                timeout=demand_env_var_as_float(name="CHATHISTORY_SERVICE_TIMEOUT"),
            )

        if self.session is None:
            self.session = requests.Session()

    @abstractmethod
    async def execute(self, *args, **kwargs) -> any:
        """Command entry point"""

    def _build_requests_params(self, request: WrappedRequest) -> dict:
        """
        Builds the `requests` call parameters.

        Parameters
        ----------
        request: WrappedRequest
            The request to make.

        Returns
        -------
        params: dict
            A dictionary suitable for splatting into the `requests` call.
        """

        params: dict = {
            "url": f"{self.options.scheme}://{self.options.tld}/{request.url}",
            "timeout": self.options.timeout,
        }
        if request.verb == RequestVerbType.POST:
            params["json"] = request.data
        if request.params is not None:
            params["params"] = request.params
        return params

    async def _api_caller(self, request: WrappedRequest, depth: int) -> dict | None:
        """
        Wrapper for calls with `requests` to external APIs.

        Parameters
        ----------
        request: WrappedRequest
            Request to make.
        depth: int
            Call depth of the recursive call (retry)

        Returns
        -------
        response: dict
            A dictionary of the response.
        """

        if depth < 1:
            raise ExceededRetryCountError(json.dumps({"request": request.model_dump(), "depth": depth}))
        depth -= 1

        params: dict = self._build_requests_params(request=request)

        # pylint: disable=broad-except
        print(params)
        try:
            if request.verb == RequestVerbType.GET:
                response: Response = self.session.get(**params)
            elif request.verb == RequestVerbType.POST:
                response: Response = self.session.post(**params)
            elif request.verb == RequestVerbType.DELETE:
                response: Response = self.session.delete(**params)
            else:
                msg = f"Unknown verb: ({request.verb})"
                raise UnknownVerbError(msg)
        except requests.exceptions.ConnectionError as error:
            logging.debug("Connection Error (%s) - Retrying.. %i", str(error), depth)
            time.sleep(self.options.sleep_time)
            return await self._api_caller(request=request, depth=depth)
        except Exception as error:
            logging.debug("Exception needed to cover: %s", str(error))
            time.sleep(self.options.sleep_time)
            return await self._api_caller(request=request, depth=depth)

        if response.status_code in request.statuses.allow:
            if response.content == b"":
                return None
            return response.json()

        if response.status_code in request.statuses.retry:
            time.sleep(self.options.sleep_time)
            return await self._api_caller(request=request, depth=depth)

        if response.status_code in request.statuses.reauth:
            return await self._api_caller(request=request, depth=depth)

        raise RequestFailureError(
            json.dumps(
                {
                    "status_code": response.status_code,
                    "request": request.model_dump(),
                    "depth": depth,
                }
            )
        )

    async def wrapped_request(self, request: WrappedRequest) -> dict | None:
        """
        High level request method.  Entry point for consumption.


        Parameters
        ----------
        request: WrappedRequest
            The request to make.

        Returns
        -------
        response: dict
            The response as a dictionary.
        """

        return await self._api_caller(request=request, depth=self.options.retry_count)
