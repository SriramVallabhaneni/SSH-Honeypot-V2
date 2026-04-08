from app.db.init_db import initialize_db
from app.honeypot.config import load_config
from app.honeypot.server import start_server
from app.exporter.exporter import start_exporter
import threading



def main() -> None:
    config = load_config()
    initialize_db(config)

    threading.Thread(target=start_exporter, args=(config,), daemon=True).start()

    start_server(config)


if __name__ == "__main__":
    main()