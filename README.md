# Foodgram - сайт с рецептами
Foodgram - сервис для публикации рецептов.

## Подготовка и запуск проекта
### Склонировать репозиторий на локальную машину:
```
git clone https://github.com/imersir/foodgram-project-react.git
```

## Для работы с удаленным сервером (на ubuntu):
### Выполните вход на свой удаленный сервер

### Установите docker на сервер:
```
sudo apt install docker.io 
```
### Установите docker-compose на сервер:
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
### Локально отредактируйте файл infra/nginx.conf и в строке server_name впишите свой IP
### Скопируйте файлы docker-compose.yml и nginx.conf из директории infra на сервер:
```
scp docker-compose.yml <username>@<host>:/home/<username>/
scp nginx.conf <username>@<host>:/home/<username>/
```
### На сервере создайте файл .env (nano .env) и заполните переменные окружения:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<имя базы данных postgres>
POSTGRES_USER=<имя пользователя>
POSTGRES_PASSWORD=<пароль для базы данных>
DB_HOST=db
DB_PORT=5432
SECRET_KEY=<секретный ключ проекта django>
HOSTS=<IP(публичный ключ) вашего сервера>
```
### На сервере соберите docker-compose:
```
sudo docker-compose up -d --build
```
### После успешной сборки на сервере выполните команды (только после первого деплоя):
#### Соберите статические файлы:
```
sudo docker-compose exec web python manage.py collectstatic --noinput
```
#### Применитe миграции:
```
sudo docker-compose exec web python manage.py migrate --noinput
```
#### Загрузите ингридиенты в базу данных
```
sudo docker-compose exec web python manage.py loaddata ingredients.json
```
#### Создать суперпользователя Django:
```
sudo docker-compose exec web python manage.py createsuperuser
```
### Проект будет доступен по вашему IP

## Для ревью проект будет доступен по адресу http://178.154.201.89

### Вход на сайт/в админку:
```
admin@ya.ru
admin
```
