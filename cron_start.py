"""
    Скрипт для запуска крон скриптов.
    Запуск конкретного скрипта осуществляется при помощи передачи аргументов через консоль
        с последующей их обработкой ниже
"""
import sys

arg = " ".join(sys.argv[1:])

if arg == "hello from cron":
    import cron.hello_from_cron

...
