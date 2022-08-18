spisok = {
    'id': 305281, 
    'status': 'rejected', 
    'homework_name': 'DKDemerchyan__homework_bot.zip', 
    'reviewer_comment': 'Еще 1 замечание ', 
    'date_updated': '2022-05-02T03:49:20Z', 
    'lesson_name': 'Проект спринта: деплой бота'
}

if 'status' in spisok.keys():
    print('Key found')
else:
    raise KeyError
