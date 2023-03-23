# Миграции, выполняющиеся при запуске бота. Нужно для изменения базы данных (структуры и данных)
from bot.classes.DBClass import DBClass

"""
    !!!!!!!!!!!!!!!!!!!!!!       ВАЖНО       !!!!!!!!!!!!!!!!!!!!!!
         перед первым запуском бота, необходимо создать таблицу:
            
            CREATE TABLE `config` (
              `name` varchar(256) NOT NULL,
              `value` varchar(256) DEFAULT NULL,
              PRIMARY KEY (`name`)
            );
"""


async def check_migrations(db: DBClass):
    # список миграций, от первой к последней (очерёдность критична)

    async def first_start():
        await db.execute("""
            CREATE TABLE `chat` (
              `chat_id` bigint(20) NOT NULL,
              `delete_message` int(11) DEFAULT -1 COMMENT '-1 - не удаляем. > 0 - число минут через сколько удаляем',
              `start_date` datetime NOT NULL DEFAULT current_timestamp(),
              `thread_id` int(11) DEFAULT NULL,
              PRIMARY KEY (`chat_id`)
            )
        """, commit=True)

    migrations = [
        first_start
    ]

    # Определяем последнюю применённую миграцию
    last_migration = await db.execute("SELECT value FROM config WHERE name = 'last_update'", fetchone=True)
    last_migration_index = 0
    if last_migration:
        last_migration = last_migration['value']
        migration_index = 0
        for migration in migrations:
            migration_index += 1
            if migration.__name__ == last_migration:
                last_migration_index = migration_index
    else:
        await db.execute("INSERT INTO config (name, value) VALUES ('last_update', NULL)", commit=True)

    # собираем только нужные миграции и выполняем их по порядку расположения в migrations
    need_migrations = migrations[last_migration_index::]
    for migration in need_migrations:
        await migration()
        last_migration = migration.__name__

    # Обновляем последнюю миграцию
    if last_migration:
        await db.execute("UPDATE config SET value = %s WHERE name = 'last_update'",
                         (last_migration,), commit=True)
