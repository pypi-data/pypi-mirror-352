"""Simple CLI entry-point for the Telegram connector."""

import argparse
import asyncio

from mindbank_poc.connectors.telegram.client import TelegramConnectorClient
from mindbank_poc.connectors.telegram.constants import (
    CONFIG_FILE,
    BATCH_LIMIT,
    BATCH_PAGE,
    BATCH_SLEEP,
    CONFIG_CHECK_SLEEP,
    WHITE_LIST,
)

# Base API URL – no endpoint suffix here (we add it in the client).
DEFAULT_API_URL = "http://localhost:8000"


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser("telegram-connector")
    p.add_argument("--api-url", default=DEFAULT_API_URL, help="Base Ingest API url")
    p.add_argument("--batch-limit", type=int, default=BATCH_LIMIT)
    p.add_argument("--batch-page", type=int, default=BATCH_PAGE)
    p.add_argument("--batch-sleep", type=float, default=BATCH_SLEEP)
    p.add_argument("--check-sleep", type=float, default=CONFIG_CHECK_SLEEP)
    p.add_argument("--collector-id", default="telegram-connector")
    p.add_argument("--integration-key")
    return p.parse_args()


async def _main() -> None:
    args = _parse_args()
    client = TelegramConnectorClient(
        api_url=args.api_url,
        batch_limit=args.batch_limit,
        batch_page=args.batch_page,
        batch_sleep=args.batch_sleep,
        check_sleep=args.check_sleep,
        collector_id=args.collector_id,
        integration_key=args.integration_key,
    )
    await client.run()


if __name__ == "__main__":
    asyncio.run(_main())

