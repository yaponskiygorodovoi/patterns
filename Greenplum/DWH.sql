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

  