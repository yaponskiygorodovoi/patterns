-- ПАТТЕРН ПО НАПИСАНИЮ ВИТРИНЫ В КЛИКЕ SummingMergeTree

-- 1 DDL витрины
DROP TABLE IF EXISTS dm_lesson_views_daily
ON CLUSTER clickhouse_cluster;

CREATE TABLE dm_lesson_views_daily
ON CLUSTER clickhouse_cluster
(
 lesson_id Int64,
 view_date Date,
 total_views UInt64
)
ENGINE = ReplicatedSummingMergeTree ( )
ORDER BY (lesson_id, view_date) 

-- MV связывающая витрину и источник(хранилище)
CREATE MATERIALIZED VIEW mv_lesson_views_daily
ON CLUSTER clickhouse_cluster
TO dm_lesson_views_daily
AS 
SELECT 
    lesson_id,
    toDate(view_date) AS view_date,
    count() AS total_views
FROM core_fact_lesson_views
GROUP BY lesson_id,
         view_date;

-- Ручной бэкфилл данных(для таких идиотов как я, кто сначала залил данные, а потом начал писать витрины)
INSERT INTO dm_lesson_views_daily
SELECT
    lesson_id,
    toDate(view_date) AS view_date,
    count() AS total_views 
FROM core_fact_lesson_views 
GROUP BY lesson_id,
         view_date;

-- чтение витринки
SELECT 
    lesson_id,
    view_date,
    sum(total_views) AS total_views
FROM dm_lesson_views_daily
GROUP BY lesson_id,
         view_date
ORDER BY view_date,
         lesson_id;
     



-- AggregatingMergeTree

-- DDL витрины, применение функций

CREATE TABLE dm_lesson_stats
ON CLUSTER clickhouse_cluster
(
    lesson_id Int64,

    total_views_state AggregateFunction(count),
    unique_users_state AggregateFunction(uniqExact, Int64),
    first_view_state AggregateFunction(min, DateTime64(3)),
    last_view_state AggregateFunction(max, DateTime64(3))
)
ENGINE = ReplicatedAggregatingMergeTree()
ORDER BY lesson_id;

-- Вьюшка

CREATE MATERIALIZED VIEW mv_lesson_stats
ON CLUSTER clickhouse_cluster
TO dm_lesson_stats
AS
SELECT
    lesson_id,

    countState() AS total_views_state,
    uniqExactState(user_id) AS unique_users_state,
    minState(viewed_at) AS first_view_state,
    maxState(viewed_at) AS last_view_state
FROM core_fact_lesson_views
GROUP BY lesson_id;


-- Бэкфилл

INSERT INTO dm_lesson_stats
SELECT
    lesson_id,

    countState() AS total_views_state,
    uniqExactState(user_id) AS unique_users_state,
    minState(viewed_at) AS first_view_state,
    maxState(viewed_at) AS last_view_state
FROM core_fact_lesson_views
GROUP BY lesson_id;

-- Чтение витринки

SELECT
    lesson_id,

    countMerge(total_views_state) AS total_views,
    uniqExactMerge(unique_users_state) AS unique_users,
    minMerge(first_view_state) AS first_view_at,
    maxMerge(last_view_state) AS last_view_at
FROM dm_lesson_stats
GROUP BY lesson_id
ORDER BY lesson_id


-- чуть по сложнее, из пет проекта

-- Задание 2
-- DDL витрины
DROP TABLE IF EXISTS dm_lesson_popularity_summary
ON CLUSTER clickhouse_cluster;

CREATE TABLE dm_lesson_popularity_summary
ON CLUSTER clickhouse_cluster
(
 lesson_id Int64,
 lesson_title String,
 course_id Int64,
 course_title String,
 total_views_state AggregateFunction(count),
 unique_users_state AggregateFunction(uniqExact, Int64),
 first_view_state AggregateFunction (min, DateTime64(3)),
 last_view_state AggregateFunction (max, DateTime64(3))
 )
 ENGINE = ReplicatedAggregatingMergeTree()
ORDER BY lesson_id;

-- Представление, для передачи данных из источника в витрину
CREATE MATERIALIZED VIEW mv_lesson_popularity_summary
ON CLUSTER clickhouse_cluster
TO dm_lesson_popularity_summary
AS 
SELECT 
    flv.lesson_id,
    any(dl.title) AS lesson_title,
    any(flv.course_id) AS course_id,
    any(dc.title) AS course_title,
    
    countState() AS total_views_state,
    uniqExactState(flv.user_id) AS unique_users_state,
    minState(flv.viewed_at) AS first_view_state,
    maxState(flv.viewed_at) AS last_view_state
FROM core_fact_lesson_views flv
LEFT JOIN core_dim_lesson dl
    ON flv.lesson_id = dl.lesson_id
LEFT JOIN core_dim_course dc
    ON flv.course_id = dc.course_id
GROUP BY flv.lesson_id;

-- Бэкфилл, так как я уже вставил данные в источник, до создания витрин =)
INSERT INTO dm_lesson_popularity_summary
SELECT 
    flv.lesson_id,
    any(dl.title) AS lesson_title,
    any(flv.course_id) AS course_id,
    any(dc.title) AS course_title,
    
    countState() AS total_views_state,
    uniqExactState(flv.user_id) AS unique_users_state,
    minState(flv.viewed_at) AS first_view_state,
    maxState(flv.viewed_at) AS last_view_state
FROM core_fact_lesson_views flv
LEFT JOIN core_dim_lesson dl
    ON flv.lesson_id = dl.lesson_id
LEFT JOIN core_dim_course dc
    ON flv.course_id = dc.course_id
GROUP BY flv.lesson_id;

-- чтение витрины
SELECT  
    lesson_id,
    any(lesson_title) AS lesson_title,
    any(course_id) AS course_id,
    any(course_title) AS course_title,
    
    countMerge(total_views_state) AS total_views,
    uniqExactMerge(unique_users_state) AS unique_users,
    minMerge(first_view_state) AS first_view,
    maxMerge(last_view_state) AS last_view
FROM dm_lesson_popularity_summary
GROUP BY lesson_id
ORDER BY lesson_id;


-- Batch rebuild витрина

DROP TABLE IF EXISTS dm_inactive_users_summary
ON CLUSTER clickhouse_cluster;

CREATE TABLE dm_inactive_users_summary
ON cluster clickhouse_cluster
(
  user_id Int64,
  name String,
  email String,
  age Int32,
  registered_courses_count UInt64,
  registration_date Date
 )
 ENGINE = ReplicatedMergeTree ()
 ORDER BY user_id;

TRUNCATE TABLE inactive_users_summary
ON CLUSTER clickhouse_cluster;

INSERT INTO inactive_users_summary
SELECT 
    usr.user_id,
    any(usr.name) AS name,
    any(usr.email) AS email,
    any(usr.age) AS age,
    countDistinct(enr.course_id) AS registered_courses_count,
    any(registration_date) AS registration_date
FROM core_dim_user usr
LEFT JOIN core_enrollments enr
    ON usr.user_id = enr.user_id
LEFT ANTI JOIN core_fact_lesson_views flv
    ON usr.user_id = flv.user_id
GROUP BY usr.user_id;

SELECT *
FROM dm_inactive_users_summary
ORDER BY registered_courses_count DESC;


-- более сложный паттерн такой витрины

DROP TABLE IF EXISTS sbeinik.dm_course_completion_rate
ON CLUSTER clickhouse_cluster;

CREATE TABLE dm_course_completion_rate
ON CLUSTER clickhouse_cluster
(
 user_id Int64,
 user_name String,
 course_id Int64,
 course_title String,
 lessons_in_course UInt64,
 lessons_viewed UInt64
)
ENGINE = ReplicatedMergeTree ()
ORDER BY (course_id, user_id);

TRUNCATE TABLE sbeinik.dm_course_completion_rate
ON CLUSTER clickhouse_cluster;

INSERT INTO sbeinik.dm_course_completion_rate
WITH course_lessons AS (
SELECT
    course_id,
    uniqExact(lesson_id) AS lessons_in_course
 FROM core_dim_lesson2 
 GROUP BY course_id
),

user_course_views AS (
SELECT 
    user_id,
    course_id,
    uniqExact(lesson_id) AS lessons_viewed
FROM core_fact_lesson_views
GROUP BY 
     user_id,
     course_id
),

user_courses AS (
SELECT 
    user_id,
    course_id
FROM core_enrollments
GROUP BY 
     user_id,
     course_id
)

SELECT  
  usr.user_id,
  any(usr.name) AS user_name,
  cou.course_id, 
  any(cou.title) AS course_title,
  any(cl.lessons_in_course) AS lessons_in_course,
  coalesce(any(ucv.lessons_viewed), 0) AS lessons_viewed
FROM user_courses uc
LEFT JOIN course_lessons cl
    ON uc.course_id = cl.course_id
LEFT JOIN user_course_views ucv
    ON uc.user_id = ucv.user_id
    AND uc.course_id = ucv.course_id
JOIN core_dim_user usr
    ON uc.user_id = usr.user_id 
JOIN core_dim_course cou
    ON uc.course_id = cou.course_id
GROUP BY 
     usr.user_id,
     cou.course_id;
    
SELECT  
    user_id,
    any(user_name) AS user_name,
    course_id,
    any(course_title) AS course_title,
    any(lessons_in_course) AS lessons_in_course,
    any(lessons_viewed) AS lessons_viewed,
    round((any(lessons_viewed)) / nullIf((any(lessons_in_course)), 0), 2) AS completion_rate
FROM dm_course_completion_rate
GROUP BY user_id, course_id 
ORDER BY completion_rate;
