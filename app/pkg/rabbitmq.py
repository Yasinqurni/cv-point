import aio_pika
from .config import Config, get_config
from enum import Enum

class ExchangeName(str, Enum):
    JOB = "job_exchange"
    UPLOAD = "candidate_exchange"

class QueueName(str, Enum):
    UPLOAD_JOB = "upload_job_queue"
    UPLOAD_CANDIDATE = "upload_candidate_queue"



configs = get_config()

def build_rabbitmq_url(config: Config) -> str:
    return (
        f"amqp://{config.rabbitmq_user}:{config.rabbitmq_password}"
        f"@{config.rabbitmq_host}:{config.rabbitmq_port}/"
    )


async def get_rabbitmq_connection() -> aio_pika.RobustConnection:
    rabbitmq_url = build_rabbitmq_url(configs)
    connection = await aio_pika.connect_robust(rabbitmq_url)
    return connection


async def get_channel():
    connection = await get_rabbitmq_connection()
    channel = await connection.channel()

    # Declare exchanges
    job_exchange = await channel.declare_exchange(
        ExchangeName.JOB.value,
        aio_pika.ExchangeType.DIRECT,
        durable=True,
    )
    upload_exchange = await channel.declare_exchange(
        ExchangeName.UPLOAD.value,
        aio_pika.ExchangeType.DIRECT,
        durable=True,
    )

    # Declare queues
    upload_candidate_queue = await channel.declare_queue(
        QueueName.UPLOAD_CANDIDATE.value,
        durable=True,
    )
    upload_job_queue = await channel.declare_queue(
        QueueName.UPLOAD_JOB.value,
        durable=True,
    )

    # Bind queues to exchanges
    await upload_candidate_queue.bind(upload_exchange, routing_key=QueueName.UPLOAD_CANDIDATE.value)
    await upload_job_queue.bind(job_exchange, routing_key=QueueName.UPLOAD_JOB.value)

    return channel



async def publish_message(exchange_name: ExchangeName, routing_key: str, message: bytes):
    channel = await get_channel()
    exchange = await channel.get_exchange(exchange_name.value)

    await exchange.publish(
        aio_pika.Message(body=message),
        routing_key=routing_key,
    )
    await channel.close()


async def consume_queue(queue_name: QueueName, callback):
    channel = await get_channel()
    queue = await channel.get_queue(queue_name.value, ensure=True)

    async with queue.iterator() as queue_iter:
        print(f"Consuming messages from {queue_name.value} data: {queue_iter}")
        async for message in queue_iter:
            async with message.process():
                await callback(message)