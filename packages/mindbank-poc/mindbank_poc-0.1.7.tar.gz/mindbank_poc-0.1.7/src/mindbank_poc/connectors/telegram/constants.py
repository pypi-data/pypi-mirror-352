"""Constants for Telegram connector."""

from typing import List

# Configuration constants
CONFIG_FILE = "telegram_connector_config.json"
WHITE_LIST: List[str] = [  # initial channels to monitor
    # "djinni_official",
    # "testical_news"
]

# Batch‑fetch limits
RATE_LIMIT_RPS = 20
BATCH_LIMIT = 5000        # total messages per request cycle
BATCH_PAGE = 10           # messages per API call
BATCH_SLEEP = 1           # seconds between API calls

# Sleep intervals
CONFIG_CHECK_SLEEP = 3    # seconds between config file checks

# Retry settings
RETRY_ATTEMPTS = 3        # number of retry attempts
RETRY_WAIT = 4           # base wait time between retries in seconds

# Buffer settings
BUFFER_FLUSH_TIMEOUT = 120  # seconds before auto-flush
AGGREGATE_GAP_SECONDS = 120.0  # максимальный интервал между сообщениями для одного агрегата (секунды)
MAX_BUFFER_CHARS = 1000  # максимальный размер буфера в символах
AUTO_FLUSH_INTERVAL = 120.0  # интервал автоматической проверки и отправки буфера в секундах

# Bulk send size for API (number of entries per request)
BULK_API_SIZE = 10 