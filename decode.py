from roborock.protocol import MessageParser
import json

LOCAL_KEY = "YOUR_KEY_HERE"

def decode(message):
    parsed_message = MessageParser.parse(message, LOCAL_KEY)
    if parsed_message[0]:
        if parsed_message[0][0]:
            payload = parsed_message[0][0]
            parsed_payload = payload.payload.decode("latin1")
            #print(parsed_payload)
            return f"V:{payload.version} S:{payload.seq} T:{payload.timestamp} P:{payload.protocol} D:{parsed_payload}"
    return parsed_message



from mitmproxy import contentviews
from mitmproxy.utils import strutils
from mitmproxy.contentviews import _view_mqtt
from mitmproxy.addonmanager import Loader
from mitmproxy.contentviews import base
from mitmproxy.contentviews._api import Contentview
from mitmproxy.contentviews._api import Metadata

import traceback

class RoborockControlPacket(_view_mqtt.MQTTControlPacket):
    def __init__(self, packet):
        super().__init__(packet)

    def pprint(self):
        s = f"[{self.Names[self.packet_type]}]"
        if self.packet_type == self.PUBLISH:
            print(self)
            if not self.payload:
                return f"Empty payload"
            topic_name = strutils.bytes_to_escaped_str(self.topic_name)
            payload = strutils.bytes_to_escaped_str(self.payload)
            try:
                payload = decode(self.payload)
            except Exception:
                topic_name = traceback.format_exc()
                ...
            s += (f" {payload} \n"
                  f"Topic: '{topic_name}'")
            return s
        else:
            return super().pprint()


class Roborock(Contentview):
    name = "Roborock"

    def prettify(self, data: bytes, metadata: Metadata):
        mqtt_packet = RoborockControlPacket(data)
        return mqtt_packet.pprint()


view = Roborock()

def load(loader: Loader):
    contentviews.add(view)


def done():
    contentviews.remove(view)
