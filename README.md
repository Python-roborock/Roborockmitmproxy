# Roborock MITM Proxy Addon

This is a quick and dirty addon that you can add to your mitm instance to get auto decoding of Roborock MQTT payloads.

![example_mitm.png](images/example_mitm.png)

## Installation
Copy `decode.py` to your computer, modify the local key attribute to be equal to your device's localkey.

Install python-roborock. The version I tested this with was 2.9.0
`pip install python-roborock>=2.9.0`

You can get that by doing the following:
```python
import asyncio

from roborock.web_api import RoborockApiClient

import pickle
async def main():
    web_api = RoborockApiClient(username="yourEmailHere")
    user_data = await web_api.pass_login("YourPassHere")
    # Or you can login with a code using web_api.code_login() and .request_code()
    # Login via your password
    home_data = await web_api.get_home_data_v2(user_data)
    device = home_data.devices[0]
    local_key = device.local_key

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())


```


Run mitm in the same location as the script.

I run with wireguard - I believe to get this working on Android - you have to bypass certificate pinning. 
I do not need to do that on ios. 

The command that works well with my ios device is

`mitmweb --mode wireguard -s decode.py`

Then I setup mitmprxoy like normal on my phone.