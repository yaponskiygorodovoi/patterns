-- Древо архитектуры DWH

SOURCE
  ↓
RAW
  сырые данные как пришли
  ↓
STG
  очистка, касты, дедупликация, quarantine
  ↓
CORE / DDS
  нормальная бизнес-модель: факты, измерения, история
  ↓
DM
  витрины под аналитику / BI / отчёты




-- Паттерны

RAW
  Pattern: Append raw as-is
  Engine: heap/ao row
  Distribution: random or source key

STG
  Pattern: Clean + Quarantine
  Engine: temp/staging tables
  Distribution: by business key

CORE DIM
  Pattern: SCD1 / SCD2
  Engine: AO row or heap
  Distribution: by dimension key or replicated

CORE FACT
  Pattern: Append fact
  Engine: AO column
  Partition: by date
  Distribution: by main join key

DM
  Pattern: Full Refresh / Incremental / Partition Refresh
  Engine: AO column
  Distribution: by common filter/join key

-- Слои
RAW

↓

VALIDATE

↓

CLEAN

↓

QUARANTINE

↓

CORE

↓

DM


-- Стадия валидации 

-- 1. Один раз валидируем raw в промежуточную temp-таблицу

DROP TABLE IF EXISTS tmp_users_validated;

CREATE TEMP TABLE tmp_users_validated AS
SELECT
    user_id,
    name,
    age,
    email,
    registration_date,
    load_dttm,
    batch_id,
    source_system,

    -- вместо regex: проверяем, что строка не пустая и состоит только из цифр
    user_id IS NOT NULL
        AND user_id <> ''
        AND translate(user_id, '0123456789', '') = '' AS valid_user,

    age IS NOT NULL
        AND age <> ''
        AND translate(age, '0123456789', '') = ''
        AND age::int BETWEEN 0 AND 120 AS valid_age,

    email IS NOT NULL
        AND email <> ''
        AND position('@' IN email) > 1 AS valid_email,

    -- проверка формата даты без regex
    registration_date IS NOT NULL
        AND length(registration_date) = 10
        AND substring(registration_date, 5, 1) = '-'
        AND substring(registration_date, 8, 1) = '-'
        AND translate(replace(registration_date, '-', ''), '0123456789', '') = ''
        AND to_char(to_date(registration_date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = registration_date
        AS valid_date

FROM raw2.users_raw
DISTRIBUTED BY (batch_id);
