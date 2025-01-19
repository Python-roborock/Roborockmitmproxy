from roborock.protocol import MessageParser
import json

LOCAL_KEY = "YOUR_KEY_HERE"
def decode(message):
    parsed_message = MessageParser.parse(message, LOCAL_KEY)
    if parsed_message[0]:
        if parsed_message[0][0]:
            payload = parsed_message[0][0]
            json_payload = json.loads(payload.payload.decode())
            data_point_number, data_point = list(json_payload.get("dps").items())[0]
            data_point_response = json.loads(data_point)
            method =payload.get_method()
            params = data_point_response.get("params")
            result = data_point_response.get("result")
            if result is not None:
                result = json.dumps(result, indent=4)
            result = f"Result: \n{result}\n" if result else ""
            return (f"Protocol: {parsed_message[0][0].protocol}\n"
                    f"Method: {method}\n"
                    f"Params: {params}\n"
                    f"{result}"
                    f"DPS: {data_point_number}\n"
                    f"ID:  {data_point_response.get('id')}")
    return parsed_message



from mitmproxy import contentviews
from mitmproxy.utils import strutils
from mitmproxy.contentviews import mqtt
from mitmproxy.addonmanager import Loader
from mitmproxy.contentviews import base



class RoborockControlPacket(mqtt.MQTTControlPacket):
    def __init__(self, packet):
        super().__init__(packet)

    def pprint(self):
        s = f"[{self.Names[self.packet_type]}]"
        if self.packet_type == self.PUBLISH:
            if not self.payload:
                return f"Empty payload"
            topic_name = strutils.bytes_to_escaped_str(self.topic_name)
            payload = strutils.bytes_to_escaped_str(self.payload)
            try:
                payload = decode(self.payload)
            except Exception:
                ...
            s += (f" {payload} \n"
                  f"Topic: '{topic_name}'")
            return s
        else:
            return super().pprint()


class Roborock(mqtt.ViewMQTT):
    name = "Roborock"

    def __call__(self, data, **metadata):
        mqtt_packet = RoborockControlPacket(data)
        text = mqtt_packet.pprint()
        return "Roborock", base.format_text(text)


view = Roborock()

def load(loader: Loader):
    contentviews.add(view)


def done():
    contentviews.remove(view)