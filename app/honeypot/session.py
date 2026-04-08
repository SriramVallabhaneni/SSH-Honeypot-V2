from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class CredentialAttempt:
    username: str
    password: str


@dataclass
class SessionRecord:
    source_ip: str
    source_port: int
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: datetime | None = None
    client_banner: str | None = None
    country: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    credentials: list[CredentialAttempt] = field(default_factory=list)

    def add_credential_attempt(self, username: str, password: str) -> None:
        self.credentials.append(CredentialAttempt(username=username, password=password))

    def finish(self) -> None:
        self.ended_at = datetime.now(timezone.utc)

    def duration_seconds(self) -> float:
        if self.ended_at is None:
            return 0.0
        return round((self.ended_at - self.started_at).total_seconds(), 2)

    def to_connection_dict(self) -> dict:
        return {
            "timestamp": self.started_at,
            "source_ip": self.source_ip,
            "source_port": self.source_port,
            "client_banner": self.client_banner,
            "country": self.country,
            "city": self.city,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "auth_attempt_count": len(self.credentials),
            "duration_seconds": self.duration_seconds(),
        }

    def to_credentials_list(self) -> list[dict[str, str]]:
        return [
            {"username": item.username, "password": item.password}
            for item in self.credentials
        ]