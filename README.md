# Проект "Foodgram"

## Описание проекта
«Фудграм» — это сайт, на котором можно публиковать собственные рецепты, добавлять чужие рецепты в избранное, подписываться на других авторов и создавать список покупок для заданных блюд.

## Вот что было сделано в ходе работы над проектом:
1. создан собственный API-сервис на базе проекта Django;
2. подключено SPA к бэкенду на Django через API;
3. созданы образы и запущены контейнеры Docker;
4. создано, развёрнуто и запущено на сервере мультиконтейнерное приложение;
5. закреплены на практике основы DevOps, включая CI/CD.

## Инструкция по запуску
1. Перенесите приложение с GitHub себе на комьютер командой `git clone`.
2. Установите виртуальное окружение командой для Windows:`python -m venv venv`, для Linux/macOS:`python3 -m venv venv`. Активируйте виртуальное окружение.
3. Установите необходимые зависимости, запустив команду `pip install -r requirements.txt`.
4. Настроить запуск проекта Foodgram в контейнерах и CI/CD с помощью GitHub Actions
5. Проект Foodgram доступен по доменному имени 
`https://foodgramproect.ydns.eu/`.
6. Пуш в ветку main запускает тестирование и деплой Foodgram, а после успешного деплоя вам приходит сообщение в телеграм.

## Примеры запросов
### Пример 1: Запрос
Пользователь: https://foodgramproect.ydns.eu/api/recipes/

### Ответ:
```
Приложение:
HTTP 200 OK
Allow: GET, POST
Content-Type: application/json
Vary: Accept

{
    "count": 6,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 45,
            "tags": [
                {
                    "id": 1,
                    "name": "Завтрак",
                    "color": "#FF0000",
                    "slug": "zavtrak"
                },
                {
                    "id": 2,
                    "name": "Обед",
                    "color": "#FFA500",
                    "slug": "obed"
                },
                {
                    "id": 3,
                    "name": "Ужин",
                    "color": "#FF0000",
                    "slug": "ujin"
                }
            ],
            "author": {
                "id": 3,
                "is_subscribed": true,
                "email": "User_recipe@mail.ru",
                "username": "User_recipe",
                "first_name": "Юзер_р",
                "last_name": "Юзер_р"
            },
            "image": "/media/images/image_gkgjCAi.jpeg",
            "ingredients": [
                {
                    "id": 1,
                    "name": "абрикосовое варенье",
                    "measurement_unit": "г",
                    "amount": 1
                },
                {
                    "id": 1914,
                    "name": "фазан",
                    "measurement_unit": "г",
                    "amount": 1
                }
            ],
            "is_favorited": false,
            "is_in_shopping_cart": false,
            "name": "Очередной",
            "text": "ПРосто",
            "cooking_time": 1
        },
    ...
    ]
}
```


### Пример 2: Запрос
Пользователь: https://foodgramproect.ydns.eu/api/ingredients/


### Ответ:
```
Приложение:
HTTP 200 OK
Allow: GET, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

[
    {
        "id": 1,
        "name": "абрикосовое варенье",
        "measurement_unit": "г"
    },
    {
        "id": 2,
        "name": "абрикосовое пюре",
        "measurement_unit": "г"
    },
    {
        "id": 3,
        "name": "абрикосовый джем",
        "measurement_unit": "г"
    },
    {
        "id": 4,
        "name": "абрикосовый сок",
        "measurement_unit": "стакан"
    },
    {
        "id": 5,
        "name": "абрикосы",
        "measurement_unit": "г"
    },
    {
        "id": 6,
        "name": "абрикосы консервированные",
        "measurement_unit": "г"
    },
...
]
```

## Использованные технологии
Этот проект использует следующие технологии:
- python
- JSON
- YAML
- Django
- React
- API 
- Docker
- Nginx
- PostgreSQL
- Gunicorn
- JWT
- Postman

## Информация об авторе
Этот проект был разработан Кулаковым В.С., студентом Яндекс-практикума. Вы можете связаться со мной по адресу электронной почты VrachKulakovVS@mail.ru.

