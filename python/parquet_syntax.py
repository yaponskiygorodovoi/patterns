
import pyarrow as pa
import pyarrow.parquet as pq





users = [
    {
        "user_id": 1,
        "name": "Ivan",
        "age": 25,
        "country": "RU",
    },
    {
        "user_id": 2,
        "name": "Anna",
        "age": 31,
        "country": "KZ",
    },
    {
        "user_id": 3,
        "name": "Max",
        "age": 40,
        "country": "RU",
    },
]

table = pa.Table.from_pylist(users)



filtered_table = pq.read_table("users.parquet", columns=["user_id","name", "age"], filters=[
    ("age", ">=", 30)
])

print(filtered_table)
print(filtered_table.to_pylist())
print(filtered_table.num_rows)