SELECT
    user_id,
    transaction_date,
    amount,
    SUM(amount) OVER(
        PARTITION BY user_id ORDER BY transaction_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total
FROM transactions;     