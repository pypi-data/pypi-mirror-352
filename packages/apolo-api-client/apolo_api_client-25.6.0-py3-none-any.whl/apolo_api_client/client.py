from __future__ import annotations

import json
from collections.abc import AsyncGenerator, Iterable
from contextlib import AbstractAsyncContextManager, aclosing
from datetime import UTC, datetime
from types import TracebackType
from typing import Any

import aiohttp
from multidict import MultiDict
from yarl import URL

from .jobs import Job, JobStatus, job_from_api


class ClientError(Exception):
    pass


class IllegalArgumentError(ValueError):
    pass


class ResourceNotFoundError(ValueError):
    pass


class NDJSONError(Exception):
    pass


class ApiClient:
    _client: aiohttp.ClientSession

    def __init__(
        self,
        url: URL,
        token: str | None = None,
        timeout: aiohttp.ClientTimeout = aiohttp.client.DEFAULT_TIMEOUT,
        trace_configs: list[aiohttp.TraceConfig] | None = None,
    ):
        super().__init__()

        self._base_url = url / "api/v1"
        self._token = token
        self._timeout = timeout
        self._trace_configs = trace_configs

    async def __aenter__(self) -> ApiClient:
        self._client = self._create_http_client()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    def _create_http_client(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
            headers=self._create_default_headers(),
            timeout=self._timeout,
            trace_configs=self._trace_configs,
        )

    async def aclose(self) -> None:
        assert self._client
        await self._client.close()

    def _create_default_headers(self) -> dict[str, str]:
        result = {}
        if self._token:
            result["Authorization"] = f"Bearer {self._token}"
        return result

    async def _raise_for_status(self, response: aiohttp.ClientResponse) -> None:
        if response.ok:
            return

        text = await response.text()
        if response.status == 404:
            raise ResourceNotFoundError(text)
        if 400 <= response.status < 500:
            raise IllegalArgumentError(text)

        try:
            response.raise_for_status()
        except aiohttp.ClientResponseError as exc:
            msg = f"{str(exc)}, body={text!r}"
            raise ClientError(msg) from exc

    async def get_job(self, id_: str) -> Job:
        async with self._client.get(self._base_url / "jobs" / id_) as response:
            await self._raise_for_status(response)
            data = await response.json()
            return job_from_api(data)

    def iter_jobs(
        self, **kwargs: Any
    ) -> AbstractAsyncContextManager[AsyncGenerator[Job]]:
        return aclosing(self._iter_jobs(**kwargs))

    async def _iter_jobs(
        self,
        *,
        statuses: Iterable[JobStatus] = (),
        name: str | None = None,
        tags: Iterable[str] = (),
        owners: Iterable[str] = (),
        since: datetime | None = None,
        until: datetime | None = None,
        reverse: bool = False,
        limit: int | None = None,
        cluster_name: str | None = None,
        org_names: Iterable[str | None] = (),
        project_names: Iterable[str] = (),
        _materialized: bool | None = None,
        _being_dropped: bool | None = False,
        _logs_removed: bool | None = False,
    ) -> AsyncGenerator[Job]:
        params: MultiDict[str] = MultiDict()
        for status in statuses:
            params.add("status", status.value)
        if name:
            params.add("name", name)
        for owner in owners:
            params.add("owner", owner)
        for tag in tags:
            params.add("tag", tag)
        if since:
            if since.tzinfo is None:
                # Interpret naive datetime object as local time.
                since = since.astimezone(UTC)
            params.add("since", since.isoformat())
        if until:
            if until.tzinfo is None:
                until = until.astimezone(UTC)
            params.add("until", until.isoformat())
        if reverse:
            params.add("reverse", "1")
        if limit is not None:
            params.add("limit", str(limit))
        if _materialized is not None:
            params.add("materialized", str(_materialized))
        if _being_dropped is not None:
            params.add("being_dropped", str(_being_dropped))
        if _logs_removed is not None:
            params.add("logs_removed", str(_logs_removed))
        if cluster_name:
            params["cluster_name"] = cluster_name
        for org_name in org_names:
            params.add("org_name", org_name or "NO_ORG")
        for project_name in project_names:
            params.add("project_name", project_name)
        async with self._client.get(self._base_url / "jobs", params=params) as response:
            if response.headers.get("Content-Type", "").startswith(
                "application/x-ndjson"
            ):
                async for line in response.content:
                    payload = json.loads(line)
                    if "error" in payload:
                        raise NDJSONError(payload["error"])
                    yield job_from_api(payload)
            else:
                await self._raise_for_status(response)
                ret = await response.json()
                for j in ret["jobs"]:
                    yield job_from_api(j)
