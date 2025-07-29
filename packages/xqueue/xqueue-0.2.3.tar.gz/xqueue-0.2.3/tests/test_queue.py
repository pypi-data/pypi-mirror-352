import unittest
from xq.message import Message
from xq.queue import Queue
from datetime import datetime, timedelta
from unittest.mock import patch

BODY = "body"

class FakeRedis:
    def __init__(self):
        self.q = {}

    def zadd(self, queue, payload):
        self.q.setdefault(queue, [])
        for k in payload:
            self.q[queue].append((k, payload[k]))

    def zrange(self, queue_name, start, poll_count, withscores=True):
        if queue_name not in self.q:
            return []
        return self.q[queue_name] 

    def zrem(self, queue_name, data):
        # Find the item by its first element (the message string)
        for i, item in enumerate(self.q[queue_name]):
            if item[0] == data:
                del self.q[queue_name][i]
                return
        # If we get here, the item wasn't found
        raise ValueError(f"Item {data} not in list")


class TestQueue(unittest.TestCase):

    def test_enqueue_deque_no_time(self):
        redis = FakeRedis()
        q = Queue(redis)
        q.enqueue(BODY)
        out = q.poll()
        self.assertEqual(1, len(out))
        self.assertEqual(BODY, out[0].body)
        out = q.poll()
        self.assertEqual(0, len(out))
    
    @patch('xq.queue.croniter')
    def test_cron_expression(self, mock_croniter):
        redis = FakeRedis()
        q = Queue(redis)
        cron_expr = "*/5 * * * *"  # Every 5 minutes
        
        # Set up the mock to return a timestamp in the past for the first call
        # and a future timestamp for the second call
        now = datetime.now()
        past_time = now - timedelta(minutes=5)
        future_time = now + timedelta(minutes=5)
        
        mock_croniter_instance = mock_croniter.return_value
        mock_croniter_instance.get_next.side_effect = [past_time, future_time]
        
        q.enqueue(BODY, cron_expression=cron_expr)
        
        # First poll should execute immediately
        out = q.poll()
        self.assertEqual(1, len(out))
        self.assertEqual(BODY, out[0].body)
        self.assertEqual(cron_expr, out[0].cron_expression)

        # Verify the task was re-enqueued with correct cron expression
        messages = redis.q[q.queue_name]
        self.assertEqual(1, len(messages))
        msg = Message.from_json(messages[0][0])
        self.assertEqual(BODY, msg.body)
        self.assertEqual(cron_expr, msg.cron_expression)

if __name__ == '__main__':
    unittest.main()
