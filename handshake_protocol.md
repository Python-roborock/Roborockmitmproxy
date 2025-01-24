# Roborock Vacuum Handshake Protocol

This expects you have a basic understanding of the Roborock web api.

You can use python-roborock for most of the basic tasks such as to get the UserData.

## Basic Message structure:

All messages following a similar structure:

Note all of my byte index ranges are inclusive.


Bytes: 0-2: Version - I believe this is equivalent to 'pv' in the normal api calls. So 1.0 for vacuums and A01 for others

Bytes 3-6: 0 0 0 1

Bytes 7-8: 0 [Message specific number - see individual sections]

Byte 9: Length of encrypted package >> 8

Byte 10: length of encrypted package & 255

Bytes 11 -> -4: The encrypted package.

You will then get the crc32 value of everything before this point.

Byte -4: (crc_32 value >> 24) & 255

Byte -3: (crc_32 value >> 16) & 255

Byte -2: (crc_32 value >> 8) & 255

Byte -1: crc_32 value & 255

## Step 0: Connection
The vacuum broadcast a ssid following the naming convention roborock-****, upon connecting to it, the vacuum's ip 
address is 192.168.8.1, while the app will connect on 192.168.8.7

The vacuum will start receiving udp messages on port 55559

The app will generate a public/private RSA pair.

### Get your HomeId
You need your home id, which is not contained in your userdata.

You can get it by making a GET call to https://[YOUR REGION]iot.roborock.com/api/v1/getHomeDetail

Authorization: Your UserData token
header_username: Your RRUID

you need the data['rrHomeId'] value.


### nc/prepare

You can get it by making a POST call to https://api-[YOUR REGION].roborock.com/nc/prepare
Authorization:
Hawk id=userdata.rriot.u,s=userdata.rriot.s,ts=currenttimestamp as a int,nonce=6 character long random, mac=hmac encoded bytes(see python roborck _get_hawk_authorization)

url encoded form:
hid: rrHomeId
tzid: Your timezone code i.e. America/New_York

You will need:
- r = result['r']
- s= result['s']
- t = result['t']


## Step 1: Hello
The app sends a hello message made up of the following:

Bytes 7-8: 0 16

Bytes 11 -> -4:  This is the payload of the message. It is AES/ECB/PKS5 encoded where the key is the last 16 characters 
of the vacuums ssid.
- id: 1
- method: hello
- params:
  - app_ver: 1
  - key: A public RSA key

## Step 1 response:  

Bytes 7-8: 0 17

The encrypted payload is encrypted with the public key created earlier.

Bytes 11 -> -4:
 - id: 1
 - method: hellow
 - params: 
   - sdks: 
     - roborock: 02
   - key: AES key it creates (This is important for later!)

## Step 2: wifi config

Bytes 7-8: 0 1

These are encoded with the AES key in the last step.
Bytes 11-> -4
- u: This is your roborock rruid - this is gotten during login
- ssid: The wifi network you want to connect to
- token: 
  - r: This is your region, i.e. US
  - tz: This is the getDefault().getId() of your timezone. i.e. "America/New_York"
  - s:I believe this is received during login
  - cst: I am not sure but here is an example: "EST5EDT,M3.2.0,M11.1.0"
  - t: I am also unsure of what this one is example: Gym****zpm - I redacted 4 characters.
- passwd: Your wifi password.

If this step is successful, you will hear the vacuum say "connecting to wifi"

## Step 2: Response:

I have not taken the time to try to reverse engineer this as it seems pretty consistent and not important

## Step 3: Add the device to your Roborock account


## Add Device

You can add the device by making a GET call to https://api-[YOUR REGION].roborock.com/user/devices/newadd

Authorization: The Hawk authorization

query params:
s: The s you got above
t: The t you got above