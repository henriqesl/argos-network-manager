from datetime import datetime
from enum import Enum
from ipaddress import ip_address

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    field_validator,
)


class RouterStatus(str, Enum):
    """Possible monitoring states for a router."""

    UNKNOWN = "unknown"
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"


class RouterCreate(BaseModel):
    """Data required to register a new router."""

    name: str = Field(
        min_length=1,
        max_length=100,
        examples=["Matriz"],
    )

    ip: str = Field(
        examples=["192.168.88.1"],
    )

    api_port: int = Field(
        default=8728,
        ge=1,
        le=65535,
    )

    username: str = Field(
        min_length=1,
        max_length=100,
        examples=["argos-api"],
    )

    password: SecretStr

    use_ssl: bool = False

    @field_validator("name", "username")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        """Remove surrounding whitespace from required text fields."""

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("Value cannot be empty.")

        return normalized_value

    @field_validator("ip")
    @classmethod
    def validate_ip_address(cls, value: str) -> str:
        """Validate and normalize an IPv4 or IPv6 address."""

        normalized_value = value.strip()

        try:
            return str(ip_address(normalized_value))
        except ValueError as exc:
            raise ValueError(
                "A valid IPv4 or IPv6 address is required."
            ) from exc


class RouterResponse(BaseModel):
    """Public representation of a registered router."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    name: str
    ip: str
    api_port: int
    use_ssl: bool
    is_active: bool

    model: str | None
    identity: str | None
    routeros_version: str | None

    status: RouterStatus

    cpu_usage_percent: float | None
    memory_usage_percent: float | None
    uptime_seconds: int | None

    last_checked_at: datetime | None
    last_seen_at: datetime | None
    last_error: str | None

    created_at: datetime
    updated_at: datetime