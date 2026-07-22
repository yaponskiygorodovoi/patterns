# 1. Reader / Transformer / Writer
#   читаем данные → преобразуем → записываем

# 2. Pipeline / Orchestrator
#   собираем отдельные шаги в единый процесс и управляем порядком выполнения

# 3. Config Object
#   выносим настройки пайплайна в отдельный объект вместо хардкода

# 4. Adapter
#   приводим разные источники или интерфейсы к единому формату работы

# 5. Factory
#    по условию выбираем и создаём нужный объект или обработчик

# 6. Strategy
#   подменяем алгоритм обработки без изменения основного кода


"""
DATA ENGINEERING DESIGN PATTERNS

1. Reader / Transformer / Writer
2. Pipeline / Orchestrator
3. Config Object
4. Adapter
5. Factory
6. Strategy
"""


# ============================================================
# 1. READER / TRANSFORMER / WRITER
# ============================================================

# Идея паттерна:
#
# Разделяем обработку данных на независимые этапы:
#
# SOURCE
#   ↓
# Reader
#   ↓
# Transformer
#   ↓
# Writer
#   ↓
# TARGET
#
# Reader      -> отвечает только за чтение данных
# Transformer -> отвечает только за преобразование
# Writer      -> отвечает только за запись
#
# Плюс:
# можно заменить источник или target,
# не переписывая всю систему.


class Reader:

    def read(self):
        # Имитация чтения данных из источника.
        return [
            {"id": 1, "amount": 100},
            {"id": 2, "amount": 200},
            {"id": 3, "amount": 300},
        ]


class Transformer:

    def transform(self, data):

        result = []

        for row in data:

            # Пример трансформации.
            new_row = {
                "id": row["id"],
                "amount": row["amount"],
                "amount_with_tax": row["amount"] * 1.2
            }

            result.append(new_row)

        return result


class Writer:

    def write(self, data):

        # В реальном проекте здесь может быть:
        # INSERT в PostgreSQL / ClickHouse / Greenplum,
        # запись в S3, файл и т.д.

        for row in data:
            print("WRITE:", row)


reader = Reader()
transformer = Transformer()
writer = Writer()

data = reader.read()

transformed_data = transformer.transform(data)

writer.write(transformed_data)


# ============================================================
# 2. PIPELINE / ORCHESTRATOR
# ============================================================

# Идея паттерна:
#
# Pipeline собирает отдельные операции
# в единый последовательный процесс.
#
# extract
#    ↓
# transform
#    ↓
# load
#
# Pipeline / Orchestrator отвечает за:
#
# - порядок выполнения шагов;
# - запуск компонентов;
# - передачу данных между этапами;
# - обработку ошибок;
# - retries;
# - логирование.
#
# Airflow DAG — хороший пример оркестрации.


class Extractor:

    def extract(self):

        print("EXTRACT")

        return [
            {"id": 1, "amount": 100},
            {"id": 2, "amount": 200},
        ]


class DataTransformer:

    def transform(self, data):

        print("TRANSFORM")

        for row in data:
            row["amount"] *= 2

        return data


class Loader:

    def load(self, data):

        print("LOAD")

        for row in data:
            print(row)


class Pipeline:

    def __init__(self, extractor, transformer, loader):

        # Pipeline не обязан знать,
        # как именно работают компоненты.
        #
        # Он просто управляет ими.

        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader

    def run(self):

        # Оркестрация процесса.

        data = self.extractor.extract()

        data = self.transformer.transform(data)

        self.loader.load(data)


pipeline = Pipeline(
    extractor=Extractor(),
    transformer=DataTransformer(),
    loader=Loader()
)

pipeline.run()


# ============================================================
# 3. CONFIG OBJECT
# ============================================================

# Идея паттерна:
#
# Настройки приложения не должны быть разбросаны
# хардкодом по всему коду.
#
# Вместо:
#
# host = "localhost"
# port = 5432
# batch_size = 5000
#
# в разных частях программы,
#
# создаём единый объект конфигурации.
#
# CODE
#   +
# CONFIG
#   =
# конкретное поведение программы
#
# Один pipeline может работать с:
#
# DEV config
# TEST config
# PROD config


class PipelineConfig:

    def __init__(
        self,
        host,
        port,
        database,
        batch_size
    ):

        self.host = host
        self.port = port
        self.database = database
        self.batch_size = batch_size


class DatabasePipeline:

    def __init__(self, config):

        self.config = config

    def run(self):

        print("Database:", self.config.database)

        print(
            "Connection:",
            self.config.host,
            self.config.port
        )

        print(
            "Batch size:",
            self.config.batch_size
        )


config = PipelineConfig(
    host="localhost",
    port=5432,
    database="dwh",
    batch_size=5000
)

pipeline = DatabasePipeline(config)

pipeline.run()


# ============================================================
# 4. ADAPTER
# ============================================================

# Идея паттерна:
#
# Разные источники могут иметь разные интерфейсы:
#
# PostgreSQL -> fetch()
# API        -> get()
# File       -> read_file()
#
# Это неудобно для Pipeline.
#
# Adapter приводит разные интерфейсы
# к ОДНОМУ стандартному интерфейсу:
#
# source.read()
#
#
# PostgreSQL
#      ↓
# PostgresAdapter
#      ↓
#     read()
#
#
# API
#      ↓
# APIAdapter
#      ↓
#     read()
#
#
# Pipeline теперь не важно,
# откуда приходят данные.


class PostgresSource:

    def fetch(self):

        return [
            {"id": 1, "source": "postgres"}
        ]


class APISource:

    def get(self):

        return [
            {"id": 2, "source": "api"}
        ]


class PostgresAdapter:

    def __init__(self, postgres):

        self.postgres = postgres

    def read(self):

        # Переводим интерфейс:
        #
        # fetch()
        #    ↓
        # read()

        return self.postgres.fetch()


class APIAdapter:

    def __init__(self, api):

        self.api = api

    def read(self):

        # Переводим интерфейс:
        #
        # get()
        #   ↓
        # read()

        return self.api.get()


def process_source(source):

    # Функции больше не важно,
    # PostgreSQL это, API или другой источник.
    #
    # Все источники имеют единый интерфейс read().

    data = source.read()

    print(data)


postgres = PostgresAdapter(
    PostgresSource()
)

api = APIAdapter(
    APISource()
)

process_source(postgres)

process_source(api)


# ============================================================
# 5. FACTORY
# ============================================================

# Идея паттерна:
#
# Factory отвечает за создание нужного объекта.
#
# Например:
#
# "csv"
#    ↓
# CSVReader
#
# "postgres"
#    ↓
# PostgresReader
#
# "api"
#    ↓
# APIReader
#
#
# Основному коду не нужно знать:
#
# какой класс создавать;
# как именно его создавать.
#
# Он просто говорит:
#
# ReaderFactory.create("csv")


class CSVReader:

    def read(self):

        return "Reading CSV"


class PostgresReader:

    def read(self):

        return "Reading PostgreSQL"


class APIReader:

    def read(self):

        return "Reading API"


class ReaderFactory:

    @staticmethod
    def create(source_type):

        # Вся логика выбора объекта
        # находится в одном месте.

        if source_type == "csv":

            return CSVReader()

        elif source_type == "postgres":

            return PostgresReader()

        elif source_type == "api":

            return APIReader()

        else:

            raise ValueError(
                f"Unknown source type: {source_type}"
            )


reader = ReaderFactory.create(
    "postgres"
)

print(
    reader.read()
)


# ============================================================
# 6. STRATEGY
# ============================================================

# Идея паттерна:
#
# Strategy позволяет менять АЛГОРИТМ,
# не меняя основной Pipeline.
#
#
#              ┌── FullLoadStrategy
# Pipeline ────┼── IncrementalStrategy
#              └── CDCStrategy
#
#
# Pipeline остаётся одинаковым.
#
# Меняется только стратегия обработки.
#
#
# Например:
#
# FULL LOAD
# truncate target
# load all data
#
#
# INCREMENTAL
# load only new rows
#
#
# CDC
# process inserts / updates / deletes


class FullLoadStrategy:

    def load(self, data):

        print("FULL LOAD")

        print("Truncate target")

        for row in data:
            print("INSERT:", row)


class IncrementalLoadStrategy:

    def load(self, data):

        print("INCREMENTAL LOAD")

        for row in data:
            print("UPSERT:", row)


class CDCLoadStrategy:

    def load(self, data):

        print("CDC LOAD")

        for row in data:
            print("PROCESS EVENT:", row)


class LoadPipeline:

    def __init__(self, strategy):

        # Pipeline получает стратегию извне.
        #
        # Поэтому алгоритм загрузки
        # можно заменить без изменения Pipeline.

        self.strategy = strategy

    def run(self, data):

        self.strategy.load(data)


data = [
    {"id": 1},
    {"id": 2},
]


# FULL LOAD

pipeline = LoadPipeline(
    FullLoadStrategy()
)

pipeline.run(data)


# INCREMENTAL LOAD

pipeline = LoadPipeline(
    IncrementalLoadStrategy()
)

pipeline.run(data)


# CDC

pipeline = LoadPipeline(
    CDCLoadStrategy()
)

pipeline.run(data)


# ============================================================
# КРАТКАЯ ШПАРГАЛКА
# ============================================================

# 1. READER / TRANSFORMER / WRITER
#
# Читаем -> преобразуем -> записываем.
#
# Разделяем ответственность компонентов.


# 2. PIPELINE / ORCHESTRATOR
#
# Управляет последовательностью выполнения:
#
# extract -> transform -> load
#
# Определяет, ЧТО и КОГДА запускать.


# 3. CONFIG OBJECT
#
# Хранит настройки отдельно от бизнес-логики.
#
# Один код + разные configs
# =
# DEV / TEST / PROD.


# 4. ADAPTER
#
# Разные интерфейсы
# ->
# единый интерфейс.
#
# fetch()
# get()
# read_file()
#
# превращаем в:
#
# read()


# 5. FACTORY
#
# Выбирает и создаёт нужный объект.
#
# source_type
# ->
# нужный Reader.


# 6. STRATEGY
#
# Позволяет менять алгоритм,
# не меняя основной код.
#
# Full Load
# Incremental Load
# CDC
#
# один Pipeline
# +
# разные стратегии