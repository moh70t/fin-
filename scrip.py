import json
from django.core.management import call_command

with open('db.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

with open('db_utf8.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

call_command('loaddata', 'db_utf8.json')
