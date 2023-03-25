from naruno.apps.remote_app import Integration

import time
import fire
import pickle
import contextlib

class aps:
    def __init__(self, password, timeout=180, cache_time=120, trusted_users=[], port=8000):
        self.trusted_users = trusted_users
        self.integration = Integration("APS", password=password, port=port)
        self.timeout = timeout
        self.cache_time = cache_time
        self.last_ping_time = 0

        self.load_cache()

    def last_ping_time_save(self):
        with open("last_ping_time.txt", "wb") as f:
            pickle.dump(self.last_ping_time, f)
    def last_ping_time_load(self):
        with open("last_ping_time.txt", "rb") as f:
            self.last_ping_time = pickle.load(f)

    def save_cache(self):

        self.last_ping_time_save()

    def load_cache(self):
        with contextlib.suppress(Exception):
            self.last_ping_time_load()    

    
    def ping(self, user):
        if time.time() - self.last_ping_time < self.cache_time:
            return True

        self.integration.send("message", "hi", user)
        start_time = time.time()
        while True:
            if time.time() - start_time > self.timeout:
                return False
            data = self.integration.get()
            if data != []:
                for each in data:
                    if each["fromUser"] == user:
                        if time.time() - each["transaction_time"] < self.timeout:
                            self.last_ping_time = time.time()
                            self.save_cache()
                            return True
            time.sleep(5)


    
    def add_user(self, user):
        self.trusted_users.append(user)

    def run(self):
        while True:
            data = self.integration.get()
            if data != []:
                for each in data:
                    if each["fromUser"] in self.trusted_users:
                        self.integration.send("reply", "hello", each["fromUser"])
            time.sleep(5)

    def close(self):
        self.integration.close()

def main():
    fire.Fire(aps)