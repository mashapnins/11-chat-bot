import gspread
from oauth2client.service_account import ServiceAccountCredentials

# credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/natalya/Documents/rabota/masha/chat-bot/composed-hash-295912-f6cb95c472a8.json', ['https://docs.google.com/spreadsheets/d/1BVF2cLGQkEc3N58Q5JmCZKrqUupDL2ksatLiI3D-AnU/edit#gid=0'])
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1BVF2cLGQkEc3N58Q5JmCZKrqUupDL2ksatLiI3D-AnU/edit#gid=0"
gc = gspread.service_account("./composed-hash-295912-f6cb95c472a8.json")
sh = gc.open_by_url(SPREADSHEET_URL)



worksheet = sh.worksheet('Sheet1')

#Функция для получение свободных дней для записи
def check_availability():
    # Получаем дни недели из строки B1:M1
    days_of_week = worksheet.row_values(1)[1:]

    # Получаем значения из строки A2:M2
    values = worksheet.row_values(2)[1:]

    free_days = [days_of_week[i // 2] for i in range(1, min(len(days_of_week) * 2, len(values) * 2), 4) if values[i // 2] == ""]
    
    return free_days#Возвращает список свободных дней

days_columns = {'Понедельник': 'B', 'Вторник': 'D', 'Среда': 'F', 'Четверг': 'H', 'Пятница': 'J', 'Суббота': 'N'}

#Функция для записи пользвателя в таблицу
def DatatoSheet(user_data, day):
    if day.capitalize() not in days_columns:
        print("Введен некорректный день недели.")
    else:
    # Определяем колонку для введенного дня недели
        column_letter = days_columns[day.capitalize()]

    # Определяем свободную строку в найденной колонке
        next_row = len(worksheet.col_values(ord(column_letter) - 64)) + 1

        name = user_data.get("name", "")
        phone = user_data.get("phone", "")
        social = user_data.get("social", "")

        cell_value = f"Имя: {name}, Телефон: {phone}, Соц. сеть: {social}"

    # Записываем данные
        worksheet.update_cell(next_row, ord(column_letter) - 64, cell_value)


    



