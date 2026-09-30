import asyncio

from app.seed.run import run_seed


def main() -> None:
    asyncio.run(run_seed())


if __name__ == "__main__":
    main()
