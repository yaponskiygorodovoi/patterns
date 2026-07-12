import json


def json_file_read_validate(json_file):

    clean_rows = []
    error_rows = []


    with open(json_file, 'r', encoding='utf8') as file:
        users = json.load(file)

        for raw_row in users:

            try:
                user_id = int(raw_row['user_id'])
                age = int(raw_row['age'])
                name = raw_row['name']

            except ValueError:
                error_rows.append({
                    'raw_row': raw_row,
                    'error': 'invalid_numeric_value'

                })

                continue

            except KeyError:

                error_rows.append({
                    'raw_row': raw_row,
                    'error': 'missing_required_field'
                })

                continue
            else:
                clean_rows.append({
                    'user_id': user_id,
                    'age': age,
                    'name': name
                })
    return clean_rows, error_rows

def write_clean_rows(clean_rows):
    with open('users2_clean.json', 'w', encoding='utf8') as clean_file:
        json.dump(clean_rows, clean_file, indent=4, ensure_ascii=False)


def write_error_rows(error_rows):
    with open('users2_error.json', 'w', encoding='utf8') as error_file:
        json.dump(error_rows, error_file, indent=4, ensure_ascii=False)

def main():

    clean_rows, error_rows = json_file_read_validate("users2.json")

    write_clean_rows(clean_rows)
    write_error_rows(error_rows)

    print(f"Корректных строк: {len(clean_rows)}")
    print(f"Ошибочных строк: {len(error_rows)}")

if __name__ == '__main__':
    main()


