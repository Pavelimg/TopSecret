from sqlite3 import connect


class DBWorker:
    def __init__(self):
        self.connection = connect("db.db")
        self.cursor = self.connection.cursor()

    def add_drug(self, user_id: int, name: str, start_time: int, repeats: int = 1, repeat_time: int = -1):
        self.connection.execute(
            f'INSERT INTO schedules VALUES(null, {user_id}, "{name}", {start_time}, {repeat_time}, {repeats})')
        self.connection.commit()
        return True

    def get_drugs_by_uuid(self, user_id):
        res = self.connection.execute(
            f'SELECT drugs_name as name, start_time, repeat_time, repeats FROM schedules WHERE user_id = {user_id}').fetchall()
        return res

    def get_schedule_by_uuid(self, user_id):
        res = self.connection.execute(
            f'SELECT drugs_name as name, start_time, repeat_time, repeats FROM schedules WHERE user_id = {user_id}').fetchall()
        return res

    def __aexit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
