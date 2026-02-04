import sys
from pathlib import Path

import uvicorn

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from core.settings import APP_LISTEN_ADDR, APP_LISTEN_PORT, LOG_CONFIG

# TODO set dev flag

if __name__ == "__main__":
    uvicorn.run(
        app="app:app",
        host=APP_LISTEN_ADDR,
        port=int(APP_LISTEN_PORT),
        log_config=LOG_CONFIG,
        # access_log=True,
        reload=True,
        loop="uvloop",
        reload_dirs=["src/"],
        reload_delay=1.0,
    )
