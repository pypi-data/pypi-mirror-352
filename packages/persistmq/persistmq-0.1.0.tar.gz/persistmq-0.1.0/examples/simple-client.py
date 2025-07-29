import time
import os
import sys
from pathlib import Path
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Only necessary for development
from persistmq.client import PersistClient

# Configure Logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a PersistClient instance
my_persist_client = PersistClient(client_id="testclient", cache_path=Path("/tmp/mymqttcache"), bulk_msg_count=10, bulk_topic_rewrite="bulk")
# Configure additional options like username and password
my_persist_client.mqtt_client.username_pw_set(username="michael", password="passwd") # Optionally Configure MQTT Client itself
# Establish a connection to the mqtt broker
my_persist_client.connect_async(mqtt_host="localhost", mqtt_port=1883)

# Send some messages
for i in range(20):
    my_persist_client.publish("dt/blah", f"Test Message {i:d}")
    time.sleep(1)

# Stop the client process
my_persist_client.stop()
