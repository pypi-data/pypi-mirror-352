"""
Module Name: client.py

Description:
This module contains the relevant classes for the persistmq functionality.
It provides a convinient interface for moving from pure paho-mqtt.
The Client spawns a process which runs in parallel and caches the queued data, if there are communication problems

Usage:
Import the PersistClient class and create an instance:
    from persistmq.client import PersistClient
    my_client = PersistClient(client_id="testclient", cache_path=Path("/tmp/mymqttcache"))
    my_client.connect_async(mqtt_host="localhost")
    my_persist_client.publish("dt/blah", "Test Message")
    my_persist_client.stop()

Classes:
- PersistClient: The class for convinient usage of the PersistMqWorker
- PersistMqWorker: Worker class (do not use directly)

Depends on:
- paho.mqtt

Author:
Michael Oberhofer

Date:
Nov. 7, 2024
"""

from multiprocessing import Process, Queue 
from paho.mqtt import client as mqtt
from pathlib import Path
from typing import Union
import time
import pickle
import uuid
import sqlite3
import logging
import json
import cbor2

logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)

class PersistClient(object):
    def __init__(self, client_id: str, cache_type: str = "sq3", cache_path: Path = Path("./cache"), bulk_msg_count: int = 0, bulk_topic_rewrite: str = "mixed/bulk", **kwargs):
        """Create an instance of PersistClient

        Args:
            client_id: id for underlying mqtt-client
            cache_type: method of caching ["sq3", "pickle"]. Defaults to "sq3".
            cache_path: path for cache file(s). Defaults to Path("./cache").
            bulk_msg_count: if the cache exceeds this number of messages, bulk transfer of this messages is performed (0=disabled)
            bulk_topic_rewrite: in case of bulk transfer, the topic postfix is replaced with this string
            **kwargs: additional arguments for paho-client
        """
        self._message_q = Queue()
        self._command_q = Queue()
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id, **kwargs)
        self._cache_path = cache_path
        self._bulk_msg_count = bulk_msg_count
        self._bulk_topic_rewrite = bulk_topic_rewrite

    def connect_async(self, mqtt_host: str, mqtt_port: int = 1883, **kwargs):
        """Start the worker process with connection to broker (uses paho mqtt connect_async method)

        Args:
            mqtt_host (str): hostname, ip of broker
            mqtt_port (int, optional): port of broker. Defaults to 1883.
            kwargs (optional): additional parameter for paho mqtt connect_async
        """
        self._worker = Process(target=self._mqtt_worker, daemon=True, args=(self.mqtt_client, mqtt_host, mqtt_port, self._message_q, self._command_q, self._cache_path, self._bulk_msg_count, self._bulk_topic_rewrite), kwargs=kwargs)
        self._worker.start()
        
    def publish(self, topic: str, payload: Union[str, bytes, bytearray, int, float, None], qos: int = 2):
        """Add a message to be published

        Args:
            topic (str): topic to be published
            payload (Union[str, bytes, bytearray, int, float, None]): payload to be published
            qos (int, optional): Quality of Service. Defaults to 2.
        """
        self._message_q.put({"topic": topic,
                           "payload": payload,
                           "qos": qos})
    
    def stop(self):
        """Gently stop the worker and cache remaining data from queue
        """
        self._command_q.put("STOP")
        self._worker.terminate()
        self._worker.join()

    def __del__(self):
        self.stop()

    @staticmethod
    def _mqtt_worker( mqtt_client: mqtt.Client, mqtt_host: str, mqtt_port: int, message_q: Queue, command_q: Queue, cache_path: Path, bulk_msg_count: int, bulk_topic_rewrite: str, **kwargs):
        PersistMqWorker(mqtt_client, mqtt_host, mqtt_port, message_q, command_q, cache_path, bulk_msg_count, bulk_topic_rewrite, **kwargs).run()



class PersistMqWorker:
    QUEUE_CACHE_THRESHOLD = 100 # Cache messages, if queue exceeds this amount of messages

    def __init__(self, mqtt_client: mqtt.Client, mqtt_host: str, mqtt_port: int, message_q: Queue, command_q: Queue, cache_path: Path, bulk_msg_count: int = 0, bulk_topic_rewrite: str = "mixed/cbor", **kwargs):
        """Worker class for actual processing the messages

        Args:
            mqtt_client: paho-mqtt client instance to be used for actual publishing
            mqtt_host: hostname/ip of the mqtt broker to connect
            mqtt_port: port of the mqtt broker to connect
            message_q: queue for messages
            command_q: queue for worker commands
            cache_path: cache path for either files or database
            bulk_msg_count: if the cache exceeds this number of messages, bulk transfer of this messages is performed (0=disabled)
            bulk_topic_rewrite: in case of bulk transfer, the topic postfix is replaced with this string
        """
        self.mqtt_client = mqtt_client
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.message_q = message_q
        self.command_q = command_q
        self.cache_path = cache_path
        self.bulk_msg_count = bulk_msg_count
        self.bulk_topic_rewrite = bulk_topic_rewrite
        self._connect_kwargs = kwargs
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_publish = self.on_publish
        self.cache_path.mkdir(exist_ok=True)
        self.file_prefix = "persistmq_cache_"
        self.last_time_checked_cache = 0
        self._stop_loop = False
        self.cache_timeout = 10
        self._setup_cache_database()
        self._cache_type = "sq3"

    def _setup_cache_database(self):
        self.db_connection = sqlite3.connect((self.cache_path/"database.sq3").as_posix())
        self.db_cursor = self.db_connection.cursor()
        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                topic TEXT,
                payload BLOB,
                qos INTEGER
            )
            ''')
        self.db_connection.commit()

    def _get_cache_from_file(self):
        data_obj = None
        cache_file = None
        # Load Data from Cache if any
        for file in self.cache_path.glob("*.pkl"):
            try:
                file_data = file.read_bytes() # Check if file is corrupt
                cache_file = file
            except:
                logger.warning("Could not read file, will be delited:", file.name)
                file.unlink()
                continue
            break
        # Read File
        if cache_file:
            data_obj = pickle.loads(cache_file.read_bytes())
            logger.debug("Loaded data from cache file")
        return cache_file, data_obj

    def _get_cache_from_database(self, use_bulk = False):
        if use_bulk:
            payload = []
            data_id = []
            bulk_topic_parts = len(self.bulk_topic_rewrite.split("/"))
            self.db_cursor.execute(f'SELECT id, topic, payload, qos FROM messages ORDER BY id ASC LIMIT {self.bulk_msg_count:d}')
            result = self.db_cursor.fetchall()
            for entry in result:
                subtopic = "/".join(entry[1].split("/")[-bulk_topic_parts:])
                payload.append({"subtopic": subtopic, "payload": entry[2]})
                data_id.append(entry[0])
            topic_prefix = "/".join(entry[1].split("/")[:-bulk_topic_parts])
            data_obj = {"topic": topic_prefix + "/" + self.bulk_topic_rewrite,
                        "payload": cbor2.dumps(payload),
                        "qos": entry[3]}
            logger.debug("Loaded bulk message from cache database")
        # Read Database
        else:
            self.db_cursor.execute('SELECT id, topic, payload, qos FROM messages ORDER BY id ASC LIMIT 1')
            result = self.db_cursor.fetchone()
            data_obj = None
            data_id = None
            if result:
                data_obj = {"topic": result[1],
                            "payload": result[2],
                            "qos": result[3]}
                data_id = result[0]
            logger.debug("Loaded single message from cache database")
        return data_id, data_obj

    def _get_data_from_cache(self):
        if self._cache_type == "pickle":
            return self._get_cache_from_file()
        elif self._cache_type == "sq3":
            if self.bulk_msg_count and (self._count_cached_messages() >= self.bulk_msg_count):
                return self._get_cache_from_database(use_bulk=True)
            else:
                return self._get_cache_from_database(use_bulk=False)

    def _remove_cache_instance(self, cache_instance):
        if self._cache_type == "pickle":
            cache_instance.unlink()
        elif self._cache_type == "sq3":
            if isinstance(cache_instance, list):
                for id in cache_instance:
                    self.db_cursor.execute('DELETE FROM messages WHERE id = ?', (id,))        
            else:
                self.db_cursor.execute('DELETE FROM messages WHERE id = ?', (cache_instance,))
            self.db_connection.commit()

    def _put_data_to_file(self, data_obj):
        filename = self.file_prefix + str(uuid.uuid4()) + ".pkl"
        cache_file = self.cache_path/filename
        try:
            cache_file.write_bytes(pickle.dumps(data_obj))
        except: #TODO: Real Exception Handling
            pass

    def _put_data_to_database(self, data_obj):
        self.db_cursor.execute('''
            INSERT INTO messages (topic, payload, qos) VALUES (?, ?, ?)
            ''', (data_obj["topic"], data_obj["payload"], data_obj["qos"]))
        self.db_connection.commit()

    def _put_data_to_cache(self, data_obj):
        if self._cache_type == "pickle":
            self._put_data_to_file(data_obj)
        elif self._cache_type == "sq3":
            self._put_data_to_database(data_obj)

    def _count_cached_messages(self):
        if self._cache_type == "pickle":
            raise NotImplementedError
        elif self._cache_type == "sq3":
            self.db_cursor.execute(f'SELECT count(*) FROM messages')
            result = self.db_cursor.fetchone()
            return result[0]

    def run(self):
        self.mqtt_client.message_published = True
        self.mqtt_client.connect_async(self.mqtt_host, self.mqtt_port, **self._connect_kwargs)
        self.mqtt_client.loop_start()
        cache_instance = None
        data_obj = None

        while not self._stop_loop:
            self._handle_command()
            
            # Load Data from cache (if exists)
            cache_instance, data_obj = self._get_data_from_cache()
                
            # Load Data from Queue to be sent next (Cache is cleared)
            while (not self._stop_loop) and (data_obj is None):
                if not self.message_q.empty():
                    logger.debug("Wait for new message")
                    data_obj = self.message_q.get() # Block until new Item available
                    break
                else:
                    time.sleep(0.1)
                self._handle_command()

            # Break worker loop here if stop requested
            if self._stop_loop:
                break

            # Put Data into MQTT Client for Publish
            self.mqtt_client.message_published = False
            msg = self.mqtt_client.publish(data_obj["topic"],
                                data_obj["payload"],
                                qos=data_obj["qos"])
            logger.debug(f"Loaded Message from Input Queue, Actual Size: {self.message_q.qsize():d}")

            # Loop for message to be sent
            loop_start_time = time.time()
            first_msg_loop = True
            while not self.mqtt_client.message_published or first_msg_loop:
                # Check Process Command Queue
                self._handle_command()
                first_msg_loop = False
                # Cache data which stucks in MQTT Output Queue
                if (time.time() > (loop_start_time + self.cache_timeout)) or self._stop_loop or (self.message_q.qsize() > self.QUEUE_CACHE_THRESHOLD):
                    if data_obj and not cache_instance:
                        self._put_data_to_cache(data_obj)
                        data_obj = None # Reset Object
                    while not self.message_q.empty():
                        logger.info("Caching message")
                        data_obj = self.message_q.get()
                        self._put_data_to_cache(data_obj)
                        data_obj = None
                # Break while in case of stop signal
                if self._stop_loop:
                    break
                else:
                    time.sleep(min(time.time() - loop_start_time, 1))
            else: # Not Break by Stop Command
                # Data is sent via MQTT, reset data object
                data_obj = None
                if cache_instance:
                    self._remove_cache_instance(cache_instance)
        logger.info("Loop Stopped")

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            logger.info("Connection to mqtt broker established")
        else:
            logger.info(f"Connection to mqtt broker broken: return code {reason_code:d}")

    def on_publish(self, client, userdata, mid, reason_code, properties):
        logger.debug(f"Published Message with mid {mid:d}")
        self.mqtt_client.message_published = True

    def _handle_command(self):
        if not self.command_q.empty():
            cmd = self.command_q.get()
            if cmd == "STOP":
                logger.info("Worker stoping in progress")
                self.mqtt_client.disconnect()
                self._stop_loop = True
