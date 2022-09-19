from res import values, stages
from datetime import datetime
import hashlib

import pymongo
from pymongo import MongoClient


class Database:

    def __init__(self, auth):
        client = MongoClient(auth)
        self.db = client['KPITctf_test']
        self.users = self.db['users']
        self.stages = self.db['stages']

        self.users.create_index([('user_id', pymongo.TEXT)], unique=True)
        self.stages.create_index([('num', pymongo.ASCENDING)], unique=True)

    def add_user(self, user_id, username):

        if self.users.find_one({'user_id': user_id}) is None:
            user = {
                'user_id': user_id,
                'username': username,
                'stage': 0,
                'advanced': 'False',
                'registration time': datetime.now().strftime('%A, %d. %B %Y %I:%M%p')
            }
            self.users.insert_one(user)
            return user_id
        else:
            return 0

    def check_flag(self, user_id, flag):
        user = self.users.find_one({'user_id': user_id})
        if user is None:
            return 0  # User not found

        if self.get_stage(user_id) == 'finished':
            return 1  # Already finished

        user_flag_hash = hashlib.md5(flag.encode()).hexdigest()
        real_flag_hash = self.stages.find_one({'num': user['stage'] + 1})['flag_hash']

        if user_flag_hash == real_flag_hash:
            self.users.update_one({'user_id': user_id}, {'$set': {'stage': user['stage'] + 1}})
        else:
            return 2  # Flag is incorrect

        # Check - is finished
        print(f"us = {user['stage']}, LS = {values.LAST_STAGE}")
        if self.get_stage(user_id) == values.LAST_STAGE and user['advanced'] == 'False':
            self.users.update_one({'user_id': user_id}, {'$set': {'stage': 'finished'}})
            return 3  # Finished simple
        elif self.get_stage(user_id) == values.LAST_STAGE_ADVANCED:
            self.users.update_one({'user_id': user_id}, {'$set': {'stage': 'finished advanced'}})
            return 4  # Finished advanced
        return 5  # flag is correct

    def get_stage_hint(self, user_id):
        if self.get_stage(user_id) not in ['finished', 'finished advanced']:
            user_stage = self.users.find_one({'user_id': user_id})['stage']
            hint = self.stages.find_one({'num': user_stage + 1})['hint']
            return hint
        elif self.get_stage(user_id) == 'finished':
            return 0
        elif self.get_stage(user_id) == 'finished advanced':
            return 1

    def set_advanced(self, user_id):
        user = self.users.find_one({'user_id': user_id})

        if user['advanced'] == 'True':
            return 0  # Already advanced
        else:
            self.users.update_one({'user_id': user_id}, {'$set': {'advanced': 'True'}})
            if self.get_stage(user_id) == 'finished':
                self.users.update_one({'user_id': user_id}, {'$set': {'stage': values.LAST_STAGE}})
            return 1  # Succesfully set advanced

    def user_exists(self, user_id):
        if self.users.find_one({'user_id': user_id}) is None:
            return False
        else:
            return True

    def get_stage(self, user_id):
        if not self.user_exists(user_id):
            return -1
        user_stage = self.users.find_one({'user_id': user_id})['stage']
        return user_stage

    def get_stage_by_username(self, username):
        user_stage = self.users.find_one({'username': username})['stage']
        return user_stage

    def add_stage(self, num, hint, flag):
        flag_hash = hashlib.md5(flag.encode()).hexdigest()
        stage = {'num': num,
                 'hint': hint,
                 'flag_hash': flag_hash}
        self.stages.insert_one(stage)

    def get_username_by_id(self, user_id):
        if not self.user_exists(user_id):
            return 0
        return self.users.find_one({'user_id': user_id})['username']

    def get_id_by_username(self, username):
        if self.users.find_one({'username': username}) is None:
            return 0
        return self.users.find_one({'username': username})['user_id']

    def restart(self):
        self.db.drop_collection('users')
        self.db.drop_collection('stages')
        for i in range(values.LAST_STAGE_ADVANCED):
            self.add_stage(i + 1, stages.hints[i], stages.flags[i])

    def get_all_users_id(self):
        users = self.users.find()
        users_id = []
        for user in users:
            users_id.append(user['user_id'])
        return users_id

    def get_all_users(self):
        users_cursor = self.users.find()
        users = []
        for user in users_cursor:
            users.append(user)
        return users

    # def is_winner(self, user_id):
    #     if self.winners.find_one({user_id}) is not None:
    #         return True
    #     else:
    #         return False
