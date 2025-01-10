import asyncio
import time
from paho.mqtt import client as mqtt

import logging

from pydantic import BaseModel

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)


class ReaderMessage(BaseModel):
    reader_id: str
    rfid: str


class MQTTClientManager:
    def __init__(self, callback, host=None, port=None):
        self.mqtt_broker = host or "127.0.0.1"
        self.mqtt_port = int(port or 1883)
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.topics = set()
        self.callback = callback
        self.reconnect_delay = 1
        self.loop = asyncio.get_event_loop()

    def connect(self):
        for _ in range(3):
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port)
            if self.mqtt_client.loop_start() == mqtt.MQTT_ERR_SUCCESS:
                break
            time.sleep(0.5)

    def on_connect(self, client, userdata, flags, rc):
        logger.debug(f"Connected with result code {rc}")
        self.reconnect_delay = 1  # Reset the reconnect delay on successful connection
        for topic in self.topics:
            client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        logger.debug(
            f"Received message: {
                     msg.payload.decode()} on topic {msg.topic}"
        )
        asyncio.run(self.callback(msg.payload.decode(), msg.topic))

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            logger.debug("Unexpected disconnection.")
            self.loop.create_task(self.reconnect())

    async def reconnect(self):
        while True:
            try:
                logger.debug(
                    f"Reconnecting in {
                             self.reconnect_delay} seconds..."
                )
                await asyncio.sleep(self.reconnect_delay)
                await self.loop.run_in_executor(None, self.mqtt_client.reconnect)
                break
            except Exception as e:
                logger.debug(f"Reconnection failed: {e}")
                self.reconnect_delay = min(
                    self.reconnect_delay * 2, 60
                )  # Incremental backoff up to 60 seconds

    def add_topic(self, topic):
        if topic not in self.topics:
            self.topics.add(topic)
        self.mqtt_client.subscribe(topic)
        logger.debug(f"Subscribed to topic {topic}")

    def start(self):
        # self.loop.run_forever()
        pass
