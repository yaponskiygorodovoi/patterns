import csv

def read_and_validate_csv(file_path):
    with open(file_path, 'r', encoding='utf-8', newline='') as file:
        reader = csv.DictReader(file)
        clean_rows = []
        error_rows = []

        for raw_row in reader:

            try:
                user_id = int(raw_row['user_id'])
                age = int(raw_row['age'])
                name = raw_row['name']

            except ValueError:
                error_row = {
                    'raw_row': raw_row,
                    'error_row': 'invalid_numeric_value'
                }

                error_rows.append(error_row)
                continue

            clean_row = {
                'user_id': user_id,
                'name': name,
                'age': age
            }
            clean_rows.append(clean_row)

        print(clean_rows)
        print(f'Корректных строк: {len(clean_rows)}')

        print(error_rows)
        print(f'Ошибочных строк: {len(error_rows)}')
    return clean_rows, error_rows





def write_clean_rows(clean_rows):
    fieldnames = ['user_id', 'name', 'age']
    with open('users2_clean.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clean_rows)


def write_error_rows(error_rows):
    error_fieldnames = ["user_id", "name", "age", "error"]

    flat_error_rows = []

    for error_row in error_rows:
        raw_row = error_row["raw_row"]

        flat_error_row = {
            "user_id": raw_row["user_id"],
            "name": raw_row["name"],
            "age": raw_row["age"],
            "error": error_row["error_row"],
        }

        flat_error_rows.append(flat_error_row)

    with open(
            "users2_error.csv",
            "w",
            encoding="utf-8",
            newline="",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=error_fieldnames)

        writer.writeheader()
        writer.writerows(flat_error_rows)


clean_rows, error_rows = read_and_validate_csv("users2.csv")

write_clean_rows(clean_rows)
write_error_rows(error_rows)

print(f"Корректных строк: {len(clean_rows)}")
print(f"Ошибочных строк: {len(error_rows)}")