import json
import pytest
import paho.mqtt.client as mqtt

TOPIC = "c2/connector-model/clock/bottom_domain/notifications/notify_next_tick"


def on_message(client, userdata, msg):
    userdata.append(json.loads(msg.payload)) 
    if len(userdata) >= 3:
        client.disconnect()


# simple way to not worry about threads when using loop_forever() 
@pytest.mark.timeout(5)
def test_clock():
    ticks = []
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata=ticks)
    client.on_message = on_message
    client.connect("localhost", 1883)
    client.subscribe(TOPIC)

    client.loop_forever()

    for index, tick in enumerate(ticks):
        assert type(tick) is int
        assert tick > 0
        assert tick == ticks[0] + index
