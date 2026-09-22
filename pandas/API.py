import pandas as pd
import requests
from datetime import date, timedelta


def get_rates():
    # 1. Определяем диапазон дат
    end_date = date.today()
    start_date = end_date - timedelta(days=14)

    # 2. Формируем URL
    url = f"https://api.frankfurter.app/{start_date}..{end_date}"

    # 3. Параметры запроса
    params = {
        "from": "USD",
        "to": "EUR,GBP,CAD"
    }

    # 4. Отправляем HTTP-запрос
    response = requests.get(url, params=params)

    # 5. Проверяем, что API не вернул ошибку
    response.raise_for_status()

    # 6. Преобразуем JSON-ответ в Python-словарь
    data = response.json()

    # 7. Здесь будем собирать строки будущего DataFrame
    rows = []

    # data["rates"] имеет примерно такую структуру:
    #
    # {
    #     "2026-09-10": {
    #         "EUR": 0.85,
    #         "GBP": 0.74,
    #         "CAD": 1.37
    #     }
    # }

    # 8. Перебираем даты
    for date_value, currencies in data["rates"].items():

        # 9. Перебираем валюты внутри каждой даты
        for currency, rate in currencies.items():

            # 10. Каждую валюту превращаем в отдельную строку
            rows.append({
                "date": date_value,
                "currency": currency,
                "rate": rate
            })

    # 11. Список словарей превращаем в DataFrame
    df = pd.DataFrame(rows)

    # 12. Преобразуем date из строки в datetime
    df["date"] = pd.to_datetime(df["date"])

    # 13. Сортируем для удобства
    df = df.sort_values(
        ["date", "currency"]
    ).reset_index(drop=True)

    return df


rates_df = get_rates()

print(rates_df)