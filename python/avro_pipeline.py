from fastavro import parse_schema, writer, reader


user_schema = {
    "type": "record",
    "name": "User",
    "namespace": "training",
    "fields": [
        {
            "name": "user_id",
            "type": "long",
        },
        {
            "name": "name",
            "type": "string",
        },
        {
            "name": "age",
            "type": "int",
        },
{
    "name": "email",
    "type": ["null", "string"],
    "default": None,
}
    ],
}

users = [
    {
        "user_id": 1,
        "name": "Ivan",
        "age": 25,
    },
    {
        "user_id": 2,
        "name": "Anna",
        "age": 31,
    },
    {
        "user_id": 3,
        "name": "Max",
        "age": 40,
    },
{
    "user_id": 4,
    "name": "Petr",
    "age": "unknown",
},
{
    "user_id": 1,
    "name": "Ivan",
    "age": 25,
    "email": "ivan@example.com",
},
{
    "user_id": 2,
    "name": "Anna",
    "age": 31,
    "email": None,
}

]

parsed_schema = parse_schema(user_schema)

clean_users = []
error_users = []


for row in users:

    try:
        user_id = int(row['user_id'])
        age = int(row['age'])
        name = row['name']
        email = row.get('email')

    except ValueError:
        error_users.append( {
            'raw_row' : row,
            'error' : 'invalid_numeric_values'

        })
        continue

    except TypeError:
        error_users.append( {
            'raw_row' : row,
            'error' : 'invalid_type'
        })
        continue

    except KeyError:
        error_users.append( {
            'raw_row' : row,
            'error' : 'invalid_key'
        })
        continue

    clean_users.append({
        'user_id': user_id,
        'name': name,
        'age': age,
        'email': email
    })



with open('users2.avro','wb') as file:
    writer(file,parsed_schema, clean_users)

with open('users2.avro','rb') as file:
    avro_reader = reader(file)

    fields =  avro_reader.writer_schema['fields']

    for field in fields:
        field_name = field['name']
        field_type = field['type']

        print(f"Поле: {field_name}, тип: {field_type}")

    for row in avro_reader:
       print(f'CLEAN: {row}')


for error_row in error_users:
    print(f'ERROR: {error_row}')
