
CREATE SCHEMA IF NOT EXISTS raw2;
CREATE SCHEMA IF NOT EXISTS stg2;
CREATE SCHEMA IF NOT EXISTS core2;
CREATE SCHEMA IF NOT EXISTS dm2;

DROP TABLE IF EXISTS raw2.users_raw;
CREATE TABLE raw2.users_raw
(
    user_id text,
    name text,
    age text,
    email text,
    registration_date text,
    load_dttm timestamp,
    batch_id int,
    source_system text
)
DISTRIBUTED RANDOMLY;

DROP TABLE IF EXISTS stg2.users_clean;
CREATE TABLE stg2.users_clean
(
    user_id int,
    name text,
    age int,
    email text,
    registration_date date,
    load_dttm timestamp,
    batch_id int,
    source_system text
)
DISTRIBUTED BY (user_id);

DROP TABLE IF EXISTS stg2.users_quarantine;
CREATE TABLE stg2.users_quarantine
(
    user_id_raw text,
    name_raw text,
    age_raw text,
    email_raw text,
    registration_date_raw text,
    error_reason text,
    load_dttm timestamp,
    batch_id int,
    source_system text
)
DISTRIBUTED RANDOMLY;