# xq
A distributed queue system built on top of Redis with cron-based scheduling support

XQ is a lightweight distributed task queue that allows you to:
- Schedule tasks to run at specific times using cron expressions
- Run tasks immediately or on a recurring schedule
- Poll tasks based on their scheduled execution time
- Manage queues and tasks through code or a web interface

# Install
```bash
pip3 install -r requirements.txt
```

# Use
## Producer
```python
import redis
from xq.queue import Queue

# connect to Redis
r = redis.Redis(host='localhost', port=6379)
# create queue
q = Queue(r, "test_queue")

# enqueue a task to run immediately
q.enqueue("this is a one-time message")

# enqueue a task with cron scheduling (runs every 5 minutes)
q.enqueue("this is a recurring message", cron_expression="*/5 * * * *")

# enqueue a task to run at midnight every day
q.enqueue("this runs at midnight", cron_expression="0 0 * * *")
```

## Consumer
```python
import redis
from xq.queue import Queue

# connect to Redis
r = redis.Redis(host='localhost', port=6379)
# create queue
q = Queue(r, "test_queue")

# poll for tasks that are ready to be executed
messages = q.poll()
for message in messages:
    print(f"Processing message: {message.body}")
    # For recurring tasks (with cron expressions), they will be 
    # automatically re-enqueued for their next scheduled run
```

## Use Worker
```python
import redis
from xq.queue import Queue
from xq.worker import Worker

def process_message(message):
    print(f"Worker processing: {message.body}")
    # Your task processing logic here

# connect to Redis
r = redis.Redis(host='localhost', port=6379)
# create queue
q = Queue(r, "test_queue")
# create and run worker
worker = Worker(q, process_message)
# worker will continuously poll for tasks based on their scheduled time
worker.run()
```

# Scheduling with Cron Expressions

XQ supports cron expressions for scheduling recurring tasks:

| Cron Expression | Description |
|----------------|-------------|
| `* * * * *` | Run every minute |
| `*/5 * * * *` | Run every 5 minutes |
| `0 * * * *` | Run at the start of every hour |
| `0 0 * * *` | Run once a day at midnight |
| `0 0 * * 0` | Run once a week on Sunday at midnight |
| `0 0 1 * *` | Run once a month on the 1st at midnight |

The cron format consists of five fields: `minute hour day-of-month month day-of-week`

# Web UI & API Server

XQ includes a web interface and API for managing queues and messages with built-in cron expression interpretation.

## Setup

1. Install the required dependencies:
```bash
pip install -r server/requirements.txt
```

2. Make sure Redis is running on localhost:6379

3. Start the server:
```bash
python server/api.py
```

4. Open your browser and navigate to http://localhost:8000

## Features

- View all available queues
- Create new queues
- View messages in a queue with human-readable cron interpretations
- Add new messages with optional cron scheduling
- Delete messages from a queue
- Poll messages from a queue

## API Endpoints

- `GET /api/queues` - List all available queues
- `GET /api/queues/{queue_name}/messages` - List all messages in a queue
- `POST /api/queues/{queue_name}/messages` - Add a new message to a queue
- `DELETE /api/queues/{queue_name}/messages/{message_id}` - Delete a message from a queue
- `POST /api/queues/{queue_name}/poll` - Poll messages from a queue
