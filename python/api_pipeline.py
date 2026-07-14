import requests
import json
import logging

logging.basicConfig(level=logging.INFO)

logging.info("Программа запущена")

url = "url"

params = {
    'userId' :1
}

clean_posts = []

try:
    response = requests.get(url, timeout=30, params=params)
    response.raise_for_status()

    posts = response.json()
    status_code = response.status_code

    for post in posts:
        clean_item = {
            'post_id': post["id"],
            'user_id': post["userId"],
            'title': post["title"],
        }

        clean_posts.append(clean_item)
    with open('posts_user_1.json', 'w', encoding='utf-8') as outfile:
        json.dump(clean_posts, outfile, indent=4, ensure_ascii=False)

    print(status_code)
    print(f'Записей получено: {len(posts)}')
    print(f'Записей сохранено: {len(clean_posts)}')
    print('Имя файла: posts_user_1.json')

except requests.exceptions.RequestException as error:
    logging.error(f"Ошибка при обращении к API: {error}")