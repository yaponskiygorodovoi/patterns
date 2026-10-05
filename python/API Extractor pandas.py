import requests
import pandas as pd
import logging
import time


logger = logging.getLogger(__name__)


def get_orders(
    base_url: str,
    timeout: int = 10
) -> list[dict]:

    all_rows = []

    page = 1

    while True:

        logger.info(
            "Requesting page %s",
            page
        )

        response = requests.get(
            base_url,
            params={"page": page},
            timeout=timeout
        )

        response.raise_for_status()

        payload = response.json()

        rows = payload.get("data", [])

        all_rows.extend(rows)

        next_page = payload.get("next_page")

        if next_page is None:
            break

        page = next_page

    return all_rows


def prepare_orders(
    rows: list[dict]
) -> pd.DataFrame:

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    df["order_id"] = pd.to_numeric(
        df["order_id"],
        errors="coerce"
    )

    df["user_id"] = pd.to_numeric(
        df["user_id"],
        errors="coerce"
    )

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "order_id",
            "user_id",
            "amount"
        ]
    )

    df = df[
        df["amount"] > 0
    ]

    df = df.drop_duplicates(
        subset=["order_id"]
    )

    return df

def request_page(
    url: str,
    page: int,
    max_retries: int = 5
) -> dict:

    for attempt in range(max_retries):

        try:

            response = requests.get(
                url,
                params={"page": page},
                timeout=10
            )

            if response.status_code == 429:

                retry_after = response.headers.get(
                    "Retry-After"
                )

                delay = (
                    int(retry_after)
                    if retry_after
                    else 2 ** attempt
                )

                logger.warning(
                    "Rate limited. Retry in %s sec",
                    delay
                )

                time.sleep(delay)
                continue

            if 500 <= response.status_code < 600:

                delay = 2 ** attempt

                logger.warning(
                    "Server error %s. Retry in %s sec",
                    response.status_code,
                    delay
                )

                time.sleep(delay)
                continue

            response.raise_for_status()

            return response.json()

        except requests.Timeout:

            delay = 2 ** attempt

            logger.warning(
                "Timeout. Retry in %s sec",
                delay
            )

            time.sleep(delay)

    raise RuntimeError(
        f"Request failed after {max_retries} attempts"
    )

def main():

    url = "https://api.example.com/orders"

    try:

        rows = get_orders(url)

        logger.info(
            "Received %s rows",
            len(rows)
        )

        df = prepare_orders(rows)

        logger.info(
            "Valid rows: %s",
            len(df)
        )

        df.to_parquet(
            "orders.parquet",
            index=False
        )

    except requests.RequestException:
        logger.exception(
            "API request failed"
        )
        raise

    except Exception:
        logger.exception(
            "Extractor failed"
        )
        raise


if __name__ == "__main__":
    main()