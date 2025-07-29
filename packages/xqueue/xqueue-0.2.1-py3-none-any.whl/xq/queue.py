import logging
from datetime import datetime, timedelta
from croniter import croniter
from xq.message import Message

XQ_STORAGE_PREFIX = "xq_prefix_"
BATCH_POLL_COUNT = 5

logger = logging.getLogger(__name__)

class Queue:
    def __init__(self, redis, queue_name="default"):
        self.redis = redis
        self.queue_name = XQ_STORAGE_PREFIX + queue_name
        self.next_run_timestamp = None

    def enqueue(self, body, cron_expression=None):
        if not isinstance(body, str) and not isinstance(body, bytes):
            raise TypeError("invalid body type, please use str type")
        now_timestamp = datetime.now().timestamp()
        timestamp = 0
        
        if cron_expression:
            # Use croniter to calculate the next run time
            cron = croniter(cron_expression, datetime.now())
            next_run = cron.get_next(datetime)
            timestamp = next_run.timestamp()
        else: # run immediately and only once
            pass

        msg = Message(body, timestamp, cron_expression=cron_expression)
        self.redis.zadd(self.queue_name, {msg.to_json(): timestamp})

    def poll(self):
        now_timestamp = datetime.now().timestamp()
        keep_poll = True
        messages_to_process = []
        while keep_poll:
            messages = self.redis.zrange(self.queue_name, 0, BATCH_POLL_COUNT, withscores=True)
            logger.debug(f"polled {len(messages)} messages")
            if len(messages) == 0:
                break
            for message in messages:
                msg_str, timestamp = message
                msg = Message.from_json(msg_str)
                if msg.timestamp > now_timestamp: # not ready to process
                    keep_poll = False
                else:
                    self.redis.zrem(self.queue_name, msg_str)
                    messages_to_process.append(msg)

        self._re_enqueue(messages_to_process)
        return messages_to_process

    def _re_enqueue(self, msgs):
        msgs_to_enqueue = []
        for msg in msgs:
            if msg.cron_expression:
                # Use croniter to calculate the next run time
                cron = croniter(msg.cron_expression, datetime.now())
                next_run = cron.get_next(datetime)
                msg.timestamp = next_run.timestamp()
                msgs_to_enqueue.append(msg)
        for msg in msgs_to_enqueue:
            self.redis.zadd(self.queue_name, {msg.to_json(): msg.timestamp})


