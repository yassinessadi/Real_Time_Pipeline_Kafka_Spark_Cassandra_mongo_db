from confluent_kafka import Producer
import requests
import json
import time

topic = "jane__essadi__topic"
kafka_config = {
    "bootstrap.servers": "localhost:9092",  # Change this to your Kafka server address
}

producer = Producer(kafka_config)

while True:
    response = requests.get("https://randomuser.me/api/")
    data = json.dumps(response.json())
    producer.produce(topic, key="randomuser", value=data)
    time.sleep(7)
    # producer.produce(topic, key="randomuser", value="yassine")
    producer.flush()