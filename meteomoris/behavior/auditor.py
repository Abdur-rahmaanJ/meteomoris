import datetime
import json
import os
from uuid import uuid4


class Auditor:
    def __init__(self, log_dir=".meteomoris_logs", session_id=None):
        self.log_dir = log_dir
        self.session_id = session_id or str(uuid4())
        self._errors = []
        self._ensure_log_dir()

    def _ensure_log_dir(self):
        if not os.path.exists(self.log_dir):
            try:
                os.makedirs(self.log_dir, exist_ok=True)
            except OSError:
                self.log_dir = None

    def record_error(self, error_record):
        self._errors.append(error_record)
        if self.log_dir:
            self._write_log(error_record)

    def _write_log(self, error_record):
        log_path = os.path.join(
            self.log_dir,
            "errors_{}.jsonl".format(datetime.date.today().isoformat()),
        )
        entry = error_record.to_dict()
        entry["session_id"] = self.session_id
        try:
            with open(log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except OSError:
            pass

    def get_errors(self, source_id=None, since=None):
        result = list(self._errors)
        if source_id:
            result = [e for e in result if e.source_id == source_id]
        if since:
            result = [e for e in result if e.timestamp >= since]
        return result

    def last_error(self):
        return self._errors[-1] if self._errors else None

    def clear(self):
        self._errors.clear()
