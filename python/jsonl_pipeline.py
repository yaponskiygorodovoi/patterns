import json

clean_rows = []
error_rows = []

with open('users2.jsonl', 'r', encoding='utf8') as file:

    for line_number, line in enumerate(file,start=1):

        try:
            user = json.loads(line)

        except json.JSONDecodeError:

            error_rows.append({
                'line_number': line_number,
                'raw_line': line.strip(),
                'error' : 'invalid_json'
            })
            continue


        try:
            user_id = int(user["user_id"])
            age = int(user["age"])
            name = user["name"]

        except ValueError:
            error_rows.append({
                'line_number': line_number,
                'raw_line': line.strip(),
                'error' : 'invalid_numeric_value'
            })
            continue

        clean_rows.append({
            'user_id': user_id,
            'name': name,
            'age': age,
        })

with open('users2_clean.jsonl', 'w', encoding='utf8') as file:
    for row in clean_rows:
        json_line = json.dumps(row, ensure_ascii=False)
        file.write(json_line + '\n')

with open('users2_clean_error.jsonl', 'w', encoding='utf8') as file:
    for row in error_rows:
        json_error_line = json.dumps(row, ensure_ascii=False)
        file.write(json_error_line + '\n')

