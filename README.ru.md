<div align="center">

# Freelance Assistant

[[ENGLISH](README.md)] [[RUSSIAN](README.ru.md)]


![GitHub License](https://img.shields.io/github/license/un-but/freelance-assistant?style=for-the-badge)
![Github Commit Activity](https://img.shields.io/github/commit-activity/t/un-but/freelance-assistant?style=for-the-badge)

</div>


Телеграм бот, который каждые 30 секунд проверяет сайты на наличие новых заказов в выбранных категориях. Используются библиотеки aiogram, sqlalchemy, aiosqlite, aiohttp и playwright. Поддерживает добавление новых сайтов.

На данный момент поддерживается сбор с:
* https://kwork.ru/projects/
* https://freelance.habr.com/tasks/

## Использование

Для использования бота предусмотрен контейнер Docker. Для его запуска необходимо скачать Docker и Git, после чего выполнить следующие команды:

```bash
git clone https://github.com/un-but/freelance-assistant # Клонируем репозиторий

cd freelance-assistant # Переходим в скачанный репозиторий

docker build -t freelance_assistant_image . # Создаем image в Docker

echo 'TOKEN={токен_вашего_бота}' > .env # Создаем файл с настройками и записываем туда токен бота

docker run -d --env-file .env --restart=unless-stopped --name freelance-assistant freelance_assistant_image # Запускаем контейнер в фоне с использованием файла настроек
```

## Как связаться

Для выполнения заказов заходите на [мой профиль на Kwork](https://kwork.ru/user/unbut) и обращайтесь либо по кворку, либо пишите в лс. 
Если Вам нужно написать мне по другому проводу, то все равно пишете в Kwork, других средств для связи пока нет.

## Лицензия

Этот проект не имеет лицензии, однако защищен авторским правом. Подробнее читайте на [этом сайте](https://choosealicense.com/no-permission/).