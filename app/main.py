from app.db.init_db import initialize_db
from app.honeypot.config import load_config
from app.honeypot.server import start_server


def main() -> None:
    config = load_config()
    initialize_db(config)
    start_server(config)


if __name__ == "__main__":
    main()