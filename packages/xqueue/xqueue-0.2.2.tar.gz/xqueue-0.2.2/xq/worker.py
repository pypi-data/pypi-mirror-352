import os
import time

POLLING_INTERVAL_IN_SECOND = int(os.getenv("XQUEUE_POLLING_INTERVAL", "5"))

class Worker:
    def __init__(self, queue, func):
        self.queue = queue
        self.func = func

    def run(self):
        try:
            while True:
                msgs = self.queue.poll()
                for msg in msgs:
                    try:
                        self.func(msg.body)
                    except Exception as e:
                        print("exception from processsing message: ", e)

                time.sleep(POLLING_INTERVAL_IN_SECOND)
        except KeyboardInterrupt:
            print("Stopped by user")
