import asyncio
from paho.mqtt import client as mqtt


class MQTTClientManager:
    def __init__(self, callback, host=None, port=None):
        self.mqtt_broker = host or "127.0.0.1"
        self.mqtt_port = int(port or 1883)
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.topics = set()
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
        self.callback = callback

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        for topic in self.topics:
            client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")
        asyncio.run(self.callback(msg.payload.decode(), msg.topic))

    def add_topic(self, topic):
        if topic in self.topics:
            return
        self.topics.add(topic)
        self.mqtt_client.subscribe(topic)

    def start(self):
        self.mqtt_client.loop_forever()
