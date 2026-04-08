import paramiko

from app.honeypot.session import SessionRecord


class SSHServerHandler(paramiko.ServerInterface):
    def __init__(self, session_record: SessionRecord):
        self.session_record = session_record

    def check_auth_password(self, username: str, password: str) -> int:
        self.session_record.add_credential_attempt(username, password)
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username: str, key) -> int:
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username: str) -> str:
        return "password,publickey"