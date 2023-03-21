import traceback
from datetime import datetime
from typing import Union

import aiofiles
import aiomysql

from settings import host, base_user, base_pass, base_charset, product_server, log_dir


class DBClass:
    def __init__(self):
        self.connection: Union[aiomysql.Pool, None] = None

    async def mysql_connect(self, base):
        self.connection = await aiomysql.create_pool(host=host,
                                                     user=base_user,
                                                     password=base_pass,
                                                     db=base,
                                                     charset=base_charset,
                                                     autocommit=True,
                                                     pool_recycle=31536000,
                                                     maxsize=100,
                                                     )

    async def mysql_disconnect(self):
        try:
            self.connection.close()
            await self.connection.wait_closed()
        except AttributeError:
            pass

    @classmethod
    async def write_log(cls, filename, error_text, need_print=False):  # Запись лога об ошибке
        if need_print or not product_server:
            print(error_text)
        else:
            async with aiofiles.open(f'{log_dir}/{filename}.txt', 'a') as file:
                error_text = f'{str(datetime.now())}\n{error_text}'
                await file.write(error_text)
                await file.flush()

    async def execute(self, query: str, args: tuple = None,
                      fetchone: bool = False,
                      fetchall: bool = False,
                      commit: bool = False,
                      need_log: bool = True,
                      ):
        """
        :param query: sql query
        :param args: arguments for query in execute
        :param fetchone: return 1 result
        :param fetchall: return all result
        :param commit: commit changes in query
        :param need_log: need log error
        :return: result of execute. Return count if not set additional params
        """
        result = None
        try:
            async with self.connection.acquire() as con:
                con: aiomysql.Connection
                async with con.cursor(aiomysql.cursors.DictCursor) as cursor:
                    cursor: aiomysql.Cursor
                    result = await cursor.execute(query, args)
                    if fetchone:
                        result = await cursor.fetchone()
                    elif fetchall:
                        result = await cursor.fetchall()
                    elif commit:
                        result = await con.commit()
        except RuntimeError as e:
            if str(e) == 'Cannot acquire connection after closing pool':
                # В идеале, надо не игнорировать ошибку, а при ребуте бота
                # останавливать получение апдейтов, обрабатывать уже полученные запросы и выходить
                pass
            elif need_log:
                await self.write_log('db_errors', query + '\n' + str(args) + '\n' + traceback.format_exc())
        except aiomysql.Error:
            if need_log:
                await self.write_log('db_errors', query + '\n' + str(args) + '\n' + traceback.format_exc())
        return result