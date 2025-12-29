# django_sprint4_Kalinich

## Установка и запуск проекта

1. Клонируйте репозиторий:
   ```
   git clone <repository-url>
   cd django_sprint4_Kalinich
   ```

2. Создайте виртуальное окружение:
   ```
   python -m venv venv
   source venv/bin/activate  # На Windows: venv\Scripts\activate
   ```

3. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```
   Возможно нужно будет перед этим вписать
   ```
   python -m pip install --upgrade pip
   ```
   для обновления pip
5. Перейдите в папку проекта:
   ```
   cd blogicum
   ```

6. Примените миграции:
   ```
   python manage.py migrate
   ```

7. Загрузите тестовые данные:
   ```
   python manage.py loaddata db
   ```

8. Запустите сервер разработки:
   ```
   python manage.py runserver
   ```

Теперь сайт доступен по адресу http://127.0.0.1:8000/ с загруженными данными.

