import pandas as pd
# Anti join logic  ~ инвертируем условие
df1[
    ~df1["id"].isin(df2["id"])
] 