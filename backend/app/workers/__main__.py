"""Keep the worker process alive until the job loop lands in T-06."""

import signal
import time

import structlog

from app.core.logging import configure_logging

log = structlog.get_logger()


def main() -> None:
    configure_logging()
    stop = False

    def handle(signum: int, _frame: object) -> None:
        nonlocal stop
        stop = True
        log.info("worker_stopping", signal=signum)

    signal.signal(signal.SIGTERM, handle)
    signal.signal(signal.SIGINT, handle)
    log.info("worker_waiting")
    while not stop:
        time.sleep(1)


if __name__ == "__main__":
    main()
