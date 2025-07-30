# tests/test_logger.py

from api.logger import AuditLogger, LogEntry
from datetime import datetime

def test_log_action():
    logger = AuditLogger("test_db.json")
    entry = LogEntry(user="test_user", action="test_action", timestamp=datetime.now().isoformat())
    result = logger.log_action(entry)
    assert result == entry
