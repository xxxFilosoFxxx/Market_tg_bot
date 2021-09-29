import sqlite3
from datetime import datetime


# TODO: добавить скрипт (или триггер) проверки, когда прошел месяц, поставить значение status=False
class BotDB:
    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.conn = sqlite3.connect(database)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.conn:
            result = self.cursor.execute('SELECT * FROM `users` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def get_users(self, status=True):
        """Получаем всех (не) активных подписчиков бота"""
        with self.conn:
            return self.cursor.execute('SELECT * FROM `users` WHERE `status` = ?', (status,)).fetchall()

    def get_status_user(self, user_id):
        """Получаем статус конкретного пользователя бота"""
        with self.conn:
            result = self.cursor.execute('SELECT `status` FROM `users` WHERE `user_id` = ?', (user_id,)).fetchone()
            if bool(result):
                return bool(result[0])
            return False

    def add_users(self, user_id, status=False):
        """Добавляем нового подписчика"""
        with self.conn:
            return self.cursor.execute('INSERT INTO `users` (`user_id`, `status`) VALUES(?,?)',
                                       (user_id, status))

    def update_users(self, user_id, status=True):
        """Обновляем статус подписки пользователя"""
        with self.conn:
            return self.cursor.execute('UPDATE `users` SET `status` = ?, `date` = ? WHERE `user_id` = ?',
                                       (status, datetime.utcnow(), user_id))

    def close(self):
        """Закрываем соединение с БД"""
        self.conn.close()