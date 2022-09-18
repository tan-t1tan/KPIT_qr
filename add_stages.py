import db_connect
import values

if __name__ == '__main__':
    db = db_connect.Database()

    db.drop_stages()

    for i in range(4):
        db.add_stage(i + 1, values.hints[i], values.flags[i])