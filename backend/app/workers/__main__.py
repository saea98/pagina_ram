"""Keep the worker process alive until the job loop lands in T-06."""

import logging
import signal
import time

log = logging.getLogger("cherry.worker")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    stop = False

    def handle(signum: int, _frame: object) -> None:
        nonlocal stop
        stop = True
        log.info("worker_stopping signal=%s", signum)

    signal.signal(signal.SIGTERM, handle)
    signal.signal(signal.SIGINT, handle)
    log.info("worker_waiting")
    while not stop:
        time.sleep(1)


if __name__ == "__main__":
    main()
