from mitmproxy import http
import json

MY_MQTT_SERVER = ""
def response(flow: http.HTTPFlow) -> None:
    target_url = "https://usiot.roborock.com/api/v3/auth/email/login"
    print(flow.request.pretty_url)
    if flow.request.pretty_url == target_url:
        try:
            resp = json.loads(flow.response.content)
            data = resp['data']

            if 'rriot' in data and 'r' in data['rriot'] and 'm' in data['rriot']['r']:
                data['rriot']['r']['m'] = f"ssl://{MY_MQTT_SERVER}:8883"
                modified_json = json.dumps(resp, indent=4)

                flow.response.content = modified_json.encode('utf-8')

            else:
                print(f"Response Content: {flow.response.content.decode()}")

        except Exception as e:
            print({e})
            if flow.response:
                print({flow.response.content.decode()})
