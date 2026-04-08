from app.honeypot.session import SessionRecord


def test_add_credential_attempt_updates_session() -> None:
    session = SessionRecord(source_ip="127.0.0.1", source_port=12345)

    session.add_credential_attempt("admin", "password123")

    credentials = session.to_credentials_list()
    assert len(credentials) == 1
    assert credentials[0]["username"] == "admin"
    assert credentials[0]["password"] == "password123"


def test_finish_sets_nonzero_duration() -> None:
    session = SessionRecord(source_ip="127.0.0.1", source_port=12345)

    session.finish()

    assert session.ended_at is not None
    assert session.duration_seconds() >= 0.0