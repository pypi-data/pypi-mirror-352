Библиотека предназначенна для работы с Polymatica API.

Основным модулем бизнес-логики является файл business_scenarios.py, импортировать который можно с помощью команды ``from polymatica import business_scenarios as sc``.

Модуль предоставляет два класса для работы с Полиматикой - ``BusinessLogic`` и ``GetDataChunk``. Методы этих классов можно посмотреть при помощи стандартной функции ``dir()``.

Аргументы функций и прочую docstring-документацию модуля и функций можно посмотреть при помощи стандартной функции ``help()``.

Инициализация нового клиентского подключения: ``client = sc.BusinessLogic(login="your_login", password="your_password", url="polymatica_server_url", **args)``


как залить на pypi:
1. python3 -m pip install --upgrade twine
2. python3 -m pip install --upgrade build
3. python3 -m build
4. python3 -m twine upload dist/*
5. ввести api token
