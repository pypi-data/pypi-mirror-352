import uuid
import pickle
import base64
from datetime import date, datetime, timedelta

class Message:
    def __init__(self, body: str, timestamp: float, id:str=None, cron_expression: str = None):
        self.body = body
        # timestamp when it can be processed, now if not set
        self.timestamp = datetime.now().timestamp() if timestamp is None else timestamp
        self.cron_expression = cron_expression
        self.id = id if id else str(uuid.uuid4())
        

    def to_json(self):
        byte_stream = pickle.dumps(self)
        return base64.b64encode(byte_stream).decode('utf-8')

    @staticmethod
    def from_json(json_str):
        byte_stream = base64.b64decode(json_str)
        deserialized_instance = pickle.loads(byte_stream)
        return deserialized_instance
        return Message(msg["body"], msg["timestamp"], msg["run_every"], msg["run_whenever_at"], msg["id"])

    def __str__(self):
        return self.to_json()


def default_json(t):
    return f'{t}'
