# В реальном ETL твоя конструкция может выглядеть так:

# source = read_orders("orders.csv")
# normalized = normalize_orders(source)
# validated = valid_orders(normalized)
# paid = paid_orders(validated)
# selected = select_fields(paid)
# batches = batch_generator(selected, batch_size=1000)

for batch in batches:
    insert_into_database(batch)

# Это можно представить так:

# Source
#  ↓
# Transform
# ↓
# Validate
#  ↓
# Filter
#  ↓
# Select
#  ↓
# Batch
#  ↓
# Sink

# Где:

# Source — читает данные;
# Transform — преобразует;
# Validate — проверяет;
# Filter — отсеивает;
# Batch — собирает в пачки;
# Sink — записывает результат.


# Основные конструкции


# ----- ФИКСИРОВАННЫЙ РАЗМЕР БАТЧА

def batch_generator(orders,batch_size):

    batch = []
    for order in orders:
        batch.append(order)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch

# pipeline = batch_generator(ОБОРАЧИВАЕМ ФУНКЦИИ)

for batch in pipeline:
    print(batch)

## ИЛИ

def batch_generator(rows, batch_size):
    if batch_size <= 0:
        raise ValueError("batch_size должен быть больше 0")

    batch = []

    for row in rows:
        batch.append(row)

        if len(batch) >= batch_size:
            yield batch
            batch = []

    if batch: 
        yield batch

 ##  Подходит для:

# batch insert в БД;
# отправки сообщений в Kafka;
# записи данных частями;
# обработки больших файлов;
# вызова API с ограничением количества объектов за запрос.
      

## ------ Генератор-источник Source generator

# Он не преобразует данные, а лениво читает их из источника.

import csv


def read_orders(filename):
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            yield row  

## Подходит для:

# CSV, JSONL и TXT-файлов;
# чтения результата SQL-запроса;
# чтения сообщений из Kafka;
# работы с логами;
# получения данных из API. 


## ------  Генератор-фильтр  Filter generator

# Пропускает дальше только подходящие строки.

def paid_orders(orders):
    for order in orders:
        if order["status"] == "paid":
            yield order

# Тут всё понятно, он нужен для фильтрации, валидации, очистки итд
# ОСНОВНАЯ ИДЕЯ - ПОЛУЧЕТ МИЛЛИОН СТРОК - В ПАМЯТИ ДЕРЖИТ ТОЛЬКО ОДНУ =)

## ----- Генератор-преобразователь Map/Transform generator

# Получает строку, изменяет её и отдаёт дальше.

def normalize_orders(orders):
    for order in orders:
        yield {
            "order_id": int(order["order_id"]),
            "status": order["status"].strip().lower(),
            "amount": int(order["amount"]),
        }

# Подходит для:

# приведения типов;
# нормализации строк;
# переименования полей;
# расчёта новых колонок;
# выбора нужных полей; 
# обогащения данных.

## ----------- Генератор с ветвлением  Router/Fan-out

# Направляет строки в разные ветки в зависимости от результата проверки.

# Сам генератор обычно отдаёт результат проверки вместе со строкой:

def validate_orders(orders):
    for order in orders:
        if order["amount"] <= 0:
            yield "error", order
        else:
            yield "clean", order

## Batch - Router

for status, order in validate_orders(orders):
    if status == "clean":
        write_clean(order)
    else:
        write_quarantine(order) 

# Подходит для:

# веток clean и quarantine;
# маршрутизации событий по event_type;
# отправки разных типов данных в разные таблицы;
# разделения успешных и ошибочных записей.

# Пример архитектуры:

 #                 → clean_orders
# source → validate
 #                 → error_orders        



 ## ------- Time batch

# Данные собираются не до определённого количества, а в течение определённого времени.

# Упрощённый пример:

import time


def time_batches(events, interval_seconds):
    batch = []
    batch_started_at = time.monotonic()

    for event in events:
        batch.append(event)

        elapsed = time.monotonic() - batch_started_at

        if elapsed >= interval_seconds:
            yield batch
            batch = []
            batch_started_at = time.monotonic()

    if batch:
        yield batch  

## ------   Hybrid Batch 

import time


def hybrid_batches(events, batch_size, interval_seconds):
    batch = []
    batch_started_at = time.monotonic()

    for event in events:
        batch.append(event)

        elapsed = time.monotonic() - batch_started_at

        if len(batch) >= batch_size or elapsed >= interval_seconds:
            yield batch
            batch = []
            batch_started_at = time.monotonic()

    if batch:
        yield batch
## Подходит для потоковых систем, где важно одновременно:

## не создавать слишком большие задержки;
## не отправлять каждый объект отдельно;
## ограничивать размер одного запроса. 

# Низкий поток:
# прошло 5 секунд → отправили 37 событий

# Высокий поток:
# накопили 1000 событий за секунду → сразу отправили

## ------ ПАГИНАЦИЯ

# API часто отдаёт данные страницами:

page=1
page=2
page=3

# Генератор скрывает работу с пагинацией:

def fetch_pages(api_client):
    page = 1

    while True:
        response = api_client.get_orders(page=page)
        rows = response["orders"]

        if not rows:
            break

        yield rows
        page += 1

# Использование:

for page in fetch_pages(api_client):
    process_batch(page)

# Или выдача отдельных строк:

def fetch_orders(api_client):
    page = 1

    while True:
        response = api_client.get_orders(page=page)
        rows = response["orders"]

        if not rows:
            break

        for row in rows:
            yield row

        page += 1

# Подходит для:

# REST API;
# облачных сервисов;
# постраничного чтения;
# API, возвращающих next_page_token;
# выгрузки данных из внешних систем.

## ------------ Скользящее окно

# Генератор создаёт пересекающиеся группы.

from collections import deque


def sliding_window(rows, window_size):
    window = deque(maxlen=window_size)

    for row in rows:
        window.append(row)

        if len(window) == window_size:
            yield list(window)

# Использование:

numbers = [1, 2, 3, 4, 5]

for window in sliding_window(numbers, 3):
    print(window)

# Результат:

[1, 2, 3]
[2, 3, 4]
[3, 4, 5]

# Отличие от батчинга:

# Обычный батч:
[1, 2, 3]
[4, 5, 6]

# Скользящее окно:
[1, 2, 3]
[2, 3, 4]
[3, 4, 5]

# Подходит для:

# анализа временных рядов;
# поиска последовательностей;
# расчёта скользящих показателей;
# сравнения текущего события с предыдущими;
# обнаружения аномалий.

## ----------- Генератор разворачивания Flatten generator

# Превращает вложенные коллекции в единый поток.

def flatten(batches):
    for batch in batches:
        for row in batch:
            yield row

# Пример:

batches = [
    [1, 2, 3],
    [4, 5],
    [6, 7],
]

for row in flatten(batches):
    print(row)

# Результат:

1
2
3
4
5
6
7

# Подходит, когда источник возвращает страницы или батчи, а последующие функции должны работать с отдельными строками.

pages = fetch_pages(api_client)
orders = flatten(pages)
paid = paid_orders(orders) 