import unittest
from xq.message import Message
from datetime import datetime

BODY = "body"

class TestMessage(unittest.TestCase):

    def test_serialization(self):
        msg = Message(BODY, 12, cron_expression="*/5 * * * *")
        j = msg.to_json()
        new_msg = Message.from_json(j)
        self.assertEqual(msg.id, new_msg.id)
        self.assertEqual(msg.body, new_msg.body)
        self.assertEqual(msg.timestamp, new_msg.timestamp)
        self.assertEqual(msg.cron_expression, new_msg.cron_expression)
