import asyncio
import time

from loguru import logger
from paho.mqtt import client as mqtt
from pydantic import BaseModel


class ReaderMessage(BaseModel):
    reader_id: str
    tag_id: str


class MQTTClientManager:
    def __init__(self, callback, mqtt_config):
        self.mqtt_broker = mqtt_config.get("host", "127.0.0.1")
        self.mqtt_port = int(mqtt_config.get("port", "1883"))
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.username_pw_set(mqtt_config.get("username", None), mqtt_config.get("password", None))
        self.topics = set()
        self.callback = callback
        self.reconnect_delay = 1
        self.loop = asyncio.get_event_loop()

    def connect(self):
        logger.debug(
            f"Connecting to MQTT broker {
                self.mqtt_broker}:{self.mqtt_port}"
        )
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

    def publish(self, topic: str, message: str | bytearray | int | float | None):
        self.mqtt_client.publish(topic, message)

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
                # Incremental backoff up to 60 seconds
                self.reconnect_delay = min(self.reconnect_delay * 2, 60)

    def add_topic(self, topic):
        if topic not in self.topics:
            self.topics.add(topic)
        self.mqtt_client.subscribe(topic)
        logger.debug(f"Subscribed to topic {topic}")

    def start(self):
        # self.loop.run_forever()
        pass

    def stop(self):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()

    def is_connected(self):
        return self.mqtt_client.is_connected()
