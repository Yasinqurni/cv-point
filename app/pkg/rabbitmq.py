import aio_pika
from config import Config, get_config


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
    return channel
