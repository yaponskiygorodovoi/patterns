import pandas as pd


# Anti join logic  ~ инвертируем условие
df1[
    ~df1["id"].isin(df2["id"])
] 


# Второй способ

def users_without_orders(users, orders):
    merged = users.merge(
        orders[["user_id"]],
        on="user_id",
        how="left",
        indicator=True
    )

    result = merged[
        merged["_merge"] == "left_only"
    ][["user_id", "name"]]

    return result  