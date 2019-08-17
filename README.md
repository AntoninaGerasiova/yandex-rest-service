# GIFTR

## Описание
REST-API сервис, который позволяет:
* сохранять переданные ему наборы данных с информацией о жителях 
* просматривать переданные ему наборы данных
* редактировать информацию об отдельных жителях
* анализировать возраста жителей по городам для указанного набора данных
* анализировать спрос на подарки в разных месяцах для указанного набора данных

Приложение выполнено с использованием фрэймворка Flask. 
Доступ к базе данных осуществляется с использованием API SQLAlchemy (Flask-SQLAlchemy). 
В качестве базы данных рекомендуется использовать SQLite для разработки или Postgres 
для высоконагруженного применения.

## Используемые инструменты (рекомендуемые версии)
* Python3 3.6, 3.7
* Flask 1.1.1
* Flask-SQLAlchemy 2.4.0
* SQLAlchemy 1.3.6
* numpy 1.17.0
* jsonschema 3.0.2
* python-dateutil 2.8.0

Для выполнения автотестов потребуется дополнительно: 
* requests  2.22.0
* pytest    5.0.1

## Инструкция по установке
Установку и настройку необходимых модулей рекомендуется осуществлять в виртуальном окружении python 
[virtualenv](https://virtualenv.pypa.io/en/latest/userguide/#usage)

Установите зависимости перечисленные выше:

`pip install Flask Flask-SQLAlchemy numpy jsonschema python-dateutil requests pytest`

Склонируйте репозиторий командой:

`git clone https://github.com/AntoninaGerasiova/yandex-rest-service.git`

Создайте конфигурационный файл:

В корневой папке проекта создайте папку `instance`. В папке `instance` создайте файл `config.cfg`. 
В файле укажите:

```
TESTING = True
SQLALCHEMY_DATABASE_URI = <uri базы данных>
```

`TESTING = True` для включения тестового API (реинициализация базы данных)

`SQLALCHEMY_DATABASE_URI` - uri в [формате принимаемом SQLAlchemy](https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls)

Пример uri для SQLite:

`SQLALCHEMY_DATABASE_URI = 'sqlite:///../instance/gifts.sqlite'`

Запуск для тестирования или отладки:

В корневой папке проекта задайте переменные окружения:

`export FLASK_APP=giftr`

`export FLASK_ENV=development`

Запустите сервер командой:

`GIFTS_SETTINGS=config.cfg flask run`

Запуск тестов:

Перейдите в папку `tests`

Запустите тесты командой:
`pytest ./test.py`
