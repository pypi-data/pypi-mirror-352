import logging
import random
import signal
import time
from threading import Thread
import sys
from paho.mqtt import client as mqtt_client
from paho.mqtt.enums import CallbackAPIVersion
from core.settings.base import MQTT_INTERNAL_SERVER, MQTT_PORT_TCP


logger = logging.getLogger(__name__)
interupt = False


def try_to_connect(client):
    while not interupt:
        logging.info(f"Reconnecting with broker {MQTT_INTERNAL_SERVER}:{MQTT_PORT_TCP} in %d seconds...", 5)
        time.sleep(5)

        if interupt:
            break

        try:
            client.reconnect()
            logging.info(f"Reconnected successfully with broker {MQTT_INTERNAL_SERVER}:{MQTT_PORT_TCP}")
            return
        except Exception as err:
            logging.error(f"%s. Reconnect with broker {MQTT_INTERNAL_SERVER}:{MQTT_PORT_TCP} failed. Retrying...", err)


def on_connect(client, userdata, flags, rc, *args):
    if rc == 0:
        logging.info(f"Connected to MQTT Broker {MQTT_INTERNAL_SERVER}:{MQTT_PORT_TCP}")
    else:
        logging.error(f"Failed to connect with broker {MQTT_INTERNAL_SERVER}:{MQTT_PORT_TCP}, return code %d\n", rc)


def on_disconnect(client, userdata, rc, *args):
    logging.error(f"Disconnected with broker {MQTT_INTERNAL_SERVER}:{MQTT_PORT_TCP} with result code: %s", rc)
    try_to_connect(client)


def on_connect_fail(client, *args):
    try_to_connect(client)


def loop(m):
    while not interupt:
        m.loop()

    if m.is_connected():
        m.disconnect()


try:
    # if sys.argv[0:1] != ["aixblock_core/manage.py"] or (sys.argv[1:2] == ["runserver"] or sys.argv[1:2] == ["runsslserver"]):
    mqtt = mqtt_client.Client(CallbackAPIVersion.VERSION2, f'python-mqtt-{random.randint(0, 1000)}')
    mqtt.on_connect = on_connect
    mqtt.on_disconnect = on_disconnect
    mqtt.on_connect_fail = on_connect_fail
    mqtt.connect(MQTT_INTERNAL_SERVER, MQTT_PORT_TCP)
    logger.info(f"Connecting to MQTT Broker {MQTT_INTERNAL_SERVER}:{MQTT_PORT_TCP}...")
    loopThread = Thread(target=loop, args=(mqtt,))
    loopThread.daemon = True
    loopThread.start()
except Exception as e:
    logging.error(f"Error in exit_mqtt: {e}")


def get_mqtt():
    global mqtt
    return mqtt


def exit_mqtt():
    try:
        global mqtt, interupt
        logger.info("Received interupt signal")
        interupt = True
        sys.exit()
    except Exception as e:
        logging.error(f"Error in exit_mqtt: {e}")


def signal_handler(_, __):
    exit_mqtt()


try:
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
except Exception:
    pass
