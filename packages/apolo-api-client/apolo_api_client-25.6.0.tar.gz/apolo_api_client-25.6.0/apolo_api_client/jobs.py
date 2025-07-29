from __future__ import annotations

import enum
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import (
    Any,
    Dict,
    Set,
    overload,
)

from dateutil.parser import isoparse
from yarl import URL


@dataclass(frozen=True)
class Resources:
    memory: int
    cpu: float
    nvidia_gpu: int | None = None
    amd_gpu: int | None = None
    intel_gpu: int | None = None
    nvidia_gpu_model: str | None = None
    amd_gpu_model: str | None = None
    intel_gpu_model: str | None = None
    shm: bool = True
    tpu_type: str | None = None
    tpu_software_version: str | None = None


class JobStatus(str, enum.Enum):
    """An Enum subclass that represents job statuses.

    PENDING: a job is being created and scheduled. This includes finding (and
    possibly waiting for) sufficient amount of resources, pulling an image
    from a registry etc.
    SUSPENDED: a preemptible job is paused to allow other jobs to run.
    RUNNING: a job is being run.
    SUCCEEDED: a job terminated with the 0 exit code.
    CANCELLED: a running job was manually terminated/deleted.
    FAILED: a job terminated with a non-0 exit code.
    """

    PENDING = "pending"
    SUSPENDED = "suspended"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"  # invalid status code, a default value is status is not sent

    @property
    def is_pending(self) -> bool:
        cls = type(self)
        return self in (cls.PENDING, cls.SUSPENDED)

    @property
    def is_running(self) -> bool:
        return self == type(self).RUNNING

    @property
    def is_finished(self) -> bool:
        cls = type(self)
        return self in (cls.SUCCEEDED, cls.FAILED, cls.CANCELLED)

    @classmethod
    def items(cls) -> Set[JobStatus]:
        return {item for item in cls if item != cls.UNKNOWN}

    @classmethod
    def active_items(cls) -> Set[JobStatus]:
        return {item for item in cls.items() if not item.is_finished}

    @classmethod
    def finished_items(cls) -> Set[JobStatus]:
        return {item for item in cls.items() if item.is_finished}

    __format__ = str.__format__  # type: ignore[assignment]
    __str__ = str.__str__


@dataclass(frozen=True)
class HTTPPort:
    port: int
    requires_auth: bool = True


@dataclass(frozen=True)
class Volume:
    storage_uri: URL
    container_path: str
    read_only: bool = False


@dataclass(frozen=True)
class DiskVolume:
    disk_uri: URL
    container_path: str
    read_only: bool = False


@dataclass(frozen=True)
class SecretFile:
    secret_uri: URL
    container_path: str


@dataclass(frozen=True)
class Container:
    image: str
    resources: Resources
    entrypoint: str | None = None
    command: str | None = None
    working_dir: str | None = None
    http: HTTPPort | None = None
    env: Mapping[str, str] = field(default_factory=dict)
    volumes: Sequence[Volume] = field(default_factory=list)
    secret_env: Mapping[str, URL] = field(default_factory=dict)
    secret_files: Sequence[SecretFile] = field(default_factory=list)
    disk_volumes: Sequence[DiskVolume] = field(default_factory=list)
    tty: bool = False


@dataclass(frozen=True)
class JobStatusItem:
    status: JobStatus
    transition_time: datetime
    reason: str = ""
    description: str = ""
    exit_code: int | None = None


@dataclass(frozen=True)
class JobStatusHistory:
    status: JobStatus
    reason: str = ""
    description: str = ""
    restarts: int = 0
    created_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    run_time_seconds: float | None = None
    exit_code: int | None = None
    transitions: Sequence[JobStatusItem] = field(default_factory=list)

    @property
    def changed_at(self) -> datetime:
        if self.status == JobStatus.PENDING:
            when = self.created_at
        elif self.status == JobStatus.RUNNING or self.status == JobStatus.SUSPENDED:
            when = self.started_at
        elif self.status.is_finished:
            when = self.finished_at
        else:
            when = self.transitions[-1].transition_time
        assert when is not None
        return when


class JobRestartPolicy(str, enum.Enum):
    NEVER = "never"
    ON_FAILURE = "on-failure"
    ALWAYS = "always"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return repr(self.value)


class JobPriority(enum.IntEnum):
    LOW = enum.auto()
    NORMAL = enum.auto()
    HIGH = enum.auto()


@dataclass(frozen=True)
class Job:
    id: str
    owner: str
    cluster_name: str
    org_name: str | None
    project_name: str
    status: JobStatus
    history: JobStatusHistory
    container: Container
    scheduler_enabled: bool
    pass_config: bool
    uri: URL
    total_price_credits: Decimal
    price_credits_per_hour: Decimal
    name: str | None = None
    tags: Sequence[str] = ()
    description: str | None = None
    http_url: URL = URL()
    internal_hostname: str | None = None
    internal_hostname_named: str | None = None
    restart_policy: JobRestartPolicy = JobRestartPolicy.NEVER
    life_span: float | None = None
    schedule_timeout: float | None = None
    preset_name: str | None = None
    preemptible_node: bool = False
    privileged: bool = False
    priority: JobPriority = JobPriority.NORMAL
    energy_schedule_name: str | None = None
    materialized: bool = False
    being_dropped: bool = False
    logs_removed: bool = False
    namespace: str = ""


def _resources_from_api(data: Dict[str, Any]) -> Resources:
    tpu_type = tpu_software_version = None
    if "tpu" in data:
        tpu = data["tpu"]
        tpu_type = tpu["type"]
        tpu_software_version = tpu["software_version"]
    return Resources(
        memory=data["memory"],
        cpu=data["cpu"],
        shm=data.get("shm", True),
        nvidia_gpu=data.get("nvidia_gpu", None),
        amd_gpu=data.get("amd_gpu", None),
        intel_gpu=data.get("intel_gpu", None),
        nvidia_gpu_model=data.get("nvidia_gpu_model", None),
        amd_gpu_model=data.get("amd_gpu_model", None),
        intel_gpu_model=data.get("intel_gpu_model", None),
        tpu_type=tpu_type,
        tpu_software_version=tpu_software_version,
    )


def _http_port_from_api(data: Dict[str, Any]) -> HTTPPort:
    return HTTPPort(
        port=data.get("port", -1), requires_auth=data.get("requires_auth", False)
    )


def _container_from_api(data: Dict[str, Any]) -> Container:
    return Container(
        image=data["image"],
        resources=_resources_from_api(data["resources"]),
        entrypoint=data.get("entrypoint", None),
        command=data.get("command", None),
        working_dir=data.get("working_dir"),
        http=_http_port_from_api(data["http"]) if "http" in data else None,
        env=data.get("env", {}),
        volumes=[_volume_from_api(v) for v in data.get("volumes", [])],
        secret_env={name: URL(val) for name, val in data.get("secret_env", {}).items()},
        secret_files=[_secret_file_from_api(v) for v in data.get("secret_volumes", [])],
        disk_volumes=[_disk_volume_from_api(v) for v in data.get("disk_volumes", [])],
        tty=data.get("tty", False),
    )


def _calc_status(stat: str) -> JobStatus:
    # Forward-compatible support for CANCELLED status
    try:
        return JobStatus(stat)
    except ValueError:
        return JobStatus.UNKNOWN


def _job_status_item_from_api(data: Dict[str, Any]) -> JobStatusItem:
    return JobStatusItem(
        status=_calc_status(data.get("status", "unknown")),
        transition_time=_parse_datetime(data["transition_time"]),
        reason=data.get("reason", ""),
        description=data.get("description", ""),
        exit_code=data.get("exit_code"),
    )


def job_from_api(data: Dict[str, Any]) -> Job:
    cluster_name = data["cluster_name"]
    container = _container_from_api(data["container"])
    owner = data["owner"]
    name = data.get("name")
    tags = data.get("tags", ())
    description = data.get("description")
    history = JobStatusHistory(
        # Forward-compatible support for CANCELLED status
        status=_calc_status(data["history"].get("status", "unknown")),
        reason=data["history"].get("reason", ""),
        restarts=data["history"].get("restarts", 0),
        description=data["history"].get("description", ""),
        created_at=_parse_datetime(data["history"].get("created_at")),
        started_at=_parse_datetime(data["history"].get("started_at")),
        finished_at=_parse_datetime(data["history"].get("finished_at")),
        run_time_seconds=data["history"].get("run_time_seconds"),
        exit_code=data["history"].get("exit_code"),
        transitions=[
            _job_status_item_from_api(item_raw) for item_raw in data.get("statuses", [])
        ],
    )
    http_url = URL(data.get("http_url", ""))
    http_url_named = URL(data.get("http_url_named", ""))
    internal_hostname = data.get("internal_hostname", None)
    internal_hostname_named = data.get("internal_hostname_named", None)
    restart_policy = JobRestartPolicy(
        data.get("restart_policy", JobRestartPolicy.NEVER)
    )
    max_run_time_minutes = data.get("max_run_time_minutes")
    life_span = (
        max_run_time_minutes * 60.0 if max_run_time_minutes is not None else None
    )
    total_price_credits = Decimal(data["total_price_credits"])
    price_credits_per_hour = Decimal(data["price_credits_per_hour"])
    priority = JobPriority[data.get("priority", JobPriority.NORMAL.name).upper()]
    return Job(
        status=_calc_status(data["status"]),
        id=data["id"],
        owner=owner,
        cluster_name=cluster_name,
        org_name=data.get("org_name"),
        history=history,
        container=container,
        scheduler_enabled=data["scheduler_enabled"],
        preemptible_node=data.get("preemptible_node", False),
        pass_config=data["pass_config"],
        name=name,
        tags=tags,
        description=description,
        http_url=http_url_named or http_url,
        internal_hostname=internal_hostname,
        internal_hostname_named=internal_hostname_named,
        uri=URL(data["uri"]),
        restart_policy=restart_policy,
        life_span=life_span,
        schedule_timeout=data.get("schedule_timeout", None),
        preset_name=data.get("preset_name"),
        total_price_credits=total_price_credits,
        price_credits_per_hour=price_credits_per_hour,
        priority=priority,
        energy_schedule_name=data.get("energy_schedule_name"),
        project_name=data.get("project_name", owner),
        materialized=data.get("materialized", False),
        being_dropped=data.get("being_dropped", False),
        logs_removed=data.get("logs_removed", False),
        namespace=data.get("namespace", Job.namespace),
    )


def _volume_from_api(data: Dict[str, Any]) -> Volume:
    storage_uri = URL(data["src_storage_uri"])
    container_path = data["dst_path"]
    read_only = data.get("read_only", True)
    return Volume(
        storage_uri=storage_uri, container_path=container_path, read_only=read_only
    )


def _secret_file_from_api(data: Dict[str, Any]) -> SecretFile:
    secret_uri = URL(data["src_secret_uri"])
    container_path = data["dst_path"]
    return SecretFile(secret_uri, container_path)


def _disk_volume_from_api(data: Dict[str, Any]) -> DiskVolume:
    disk_uri = URL(data["src_disk_uri"])
    container_path = data["dst_path"]
    read_only = data.get("read_only", True)
    return DiskVolume(disk_uri, container_path, read_only)


@overload
def _parse_datetime(dt: str) -> datetime: ...


@overload
def _parse_datetime(dt: str | None) -> datetime | None: ...


def _parse_datetime(dt: str | None) -> datetime | None:
    if dt is None:
        return None
    return isoparse(dt)
