"""Job worker. Processes one queued job at a time."""

import asyncio
import signal
from pathlib import Path

import structlog

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.storage import LocalStorage
from app.workers.loop import run_once

log = structlog.get_logger()


async def _serve(storage: LocalStorage) -> None:
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signum in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(signum, stop.set)
    log.info("worker_started")
    while not stop.is_set():
        try:
            worked = await run_once(storage)
        except Exception:
            log.exception("worker_poll_failed")
            worked = False
            pause = 5.0
        else:
            pause = 1.0
        if worked:
            continue
        try:
            await asyncio.wait_for(stop.wait(), timeout=pause)
        except TimeoutError:
            continue
    log.info("worker_stopping")


def main() -> None:
    configure_logging()
    storage = LocalStorage(Path(get_settings().media_root))
    asyncio.run(_serve(storage))


if __name__ == "__main__":
    main()
