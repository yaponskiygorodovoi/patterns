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

WITH validated  AS (
SELECT 
   user_id,
    name,
    age,
    email,
    registration_date,
    load_dttm,
    batch_id,
    source_system,
    
    user_id ~ '^[0-9]+$' AS valid_user,
    age ~ '^[0-9]+$' AS valid_age,
    email IS NOT NULL AS valid_email,
    registration_date ~ '^\d{4}-\d{2}-\d{2}$' AS valid_date
FROM raw2.users_raw
) 

-- ветка Clean

INSERT INTO stg2.users_clean

SELECT

user_id::int,

name,

age::int,

email,

registration_date::date,

load_dttm,

batch_id,

source_system

FROM validated

WHERE

valid_user

AND valid_age

AND valid_date

AND valid_email;

-- ветка Quarantine

WITH validated AS (
    SELECT
        user_id,
        name,
        age,
        email,
        registration_date,
        load_dttm,
        batch_id,
        source_system,

        user_id ~ '^[0-9]+$' AS valid_user,
        age ~ '^[0-9]+$' AS valid_age,
        email IS NOT NULL AS valid_email,
        registration_date ~ '^\d{4}-\d{2}-\d{2}$' AS valid_date
    FROM raw2.users_raw
)
INSERT INTO stg2.users_quarantine
SELECT
    user_id AS user_id_raw,
    name AS name_raw,
    age AS age_raw,
    email AS email_raw,
    registration_date AS registration_date_raw,

    CASE
        WHEN NOT valid_user THEN 'invalid user_id'
        WHEN NOT valid_age THEN 'invalid age'
        WHEN NOT valid_email THEN 'invalid email'
        WHEN NOT valid_date THEN 'invalid registration_date'
        ELSE 'unknown error'
    END AS error_reason,

    load_dttm,
    batch_id,
    source_system
FROM validated
WHERE NOT (
    valid_user
    AND valid_age
    AND valid_date
    AND valid_email
);
