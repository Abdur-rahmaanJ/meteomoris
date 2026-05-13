import os
import json


CACHE_PATH = os.path.join(".", "meteomoris_cache.json")
TODAY = None


def _get_today():
    global TODAY
    if TODAY is None:
        import datetime
        TODAY = str(datetime.date.today())
    return TODAY


class Cache:
    def __init__(self, cache_path=CACHE_PATH):
        self.cache_path = cache_path
        self.enabled = True
        self._verify_cache_exists()

    def _verify_cache_exists(self):
        if not os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "w+") as f:
                    json.dump({}, f)
                self.enabled = True
            except PermissionError:
                self.enabled = False

    def _get_cache_data(self):
        self._verify_cache_exists()
        data = None
        try:
            with open(self.cache_path) as f:
                data = json.load(f)
            self.enabled = True
        except (FileNotFoundError, json.JSONDecodeError):
            self.enabled = False
        except ValueError:
            self._recover_corrupted_cache()
            self.enabled = False
            data = {}
        return data

    def _recover_corrupted_cache(self):
        import shutil
        backup = self.cache_path + ".corrupted"
        try:
            shutil.copy2(self.cache_path, backup)
            with open(self.cache_path, "w+") as f:
                json.dump({}, f)
        except OSError:
            pass
        self.enabled = True

    def get(self, key):
        if not self.enabled:
            return None
        cache_data = self._get_cache_data()
        if cache_data is None:
            return None
        today = _get_today()
        if today not in cache_data:
            cache_data[today] = {}
            try:
                with open(self.cache_path, "w+") as f:
                    json.dump(cache_data, f)
                self.enabled = True
            except PermissionError:
                self.enabled = False
            return None
        if key not in cache_data.get(today, {}):
            return None
        return cache_data[today][key]

    def get_stale(self, key):
        if not self.enabled:
            return None
        cache_data = self._get_cache_data()
        if cache_data is None:
            return None
        today = _get_today()
        for day_key, day_data in cache_data.items():
            if day_key != today and key in day_data:
                return day_data[key]
        return None

    def set(self, key, data):
        if not self.enabled:
            return
        try:
            cache_data = self._get_cache_data()
            if cache_data is None:
                cache_data = {}
            today = _get_today()
            if today not in cache_data:
                cache_data[today] = {}
            cache_data[today][key] = data
            with open(self.cache_path, "w+") as f:
                json.dump(cache_data, f)
            self.enabled = True
        except (TypeError, PermissionError, FileNotFoundError):
            self.enabled = False
