import time
from roborock.web_api import RoborockApiClient
import asyncio
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import zlib
import socket
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import io
import json
VACUUM_SSID = ""
YOUR_SSID = ""
YOUR_SSID_PASS = ""
YOUR_RR_USER = ""
YOUR_RR_PASS = ""
YOUR_TIMEZONE = "America/New_York"
YOUR_CST = "EST5EDT,M3.2.0,M11.1.0"
YOUR_REGION = "US"
def generate_rsa_key_pair(key_size=1024):
    key = RSA.generate(key_size)

    private_key = key.export_key().decode('utf-8')
    public_key = key.publickey().export_key().decode('utf-8')
    return private_key, public_key

KEY = generate_rsa_key_pair()

def calculate_crc32(data):
    return zlib.crc32(data) & 0xffffffff

def build_bytes(data, cmd_id):
    byte_array_output_stream = io.BytesIO()

    byte_array_output_stream.write("1.0".encode('utf-8')[:3])
    byte_array_output_stream.write(bytes([0, 0, 0, 1]))
    byte_array_output_stream.write(bytes([0, cmd_id]))
    byte_array_output_stream.write(bytes([len(data) >> 8]))
    byte_array_output_stream.write(bytes([len(data) & 0xFF]))
    byte_array_output_stream.write(data)
    crc32_val = calculate_crc32(byte_array_output_stream.getvalue())
    byte_array_output_stream.write(bytes([(crc32_val >> 24) & 0xFF]))
    byte_array_output_stream.write(bytes([(crc32_val >> 16) & 0xFF]))
    byte_array_output_stream.write(bytes([(crc32_val >> 8) & 0xFF]))
    byte_array_output_stream.write(bytes([crc32_val & 0xFF]))
    return byte_array_output_stream.getvalue()


def decrypt_rsa_data(data, private_key_pem):
    key = RSA.importKey(private_key_pem.encode())
    cipher = PKCS1_v1_5.new(key)

    i8 = ((data[9] << 8) & 0xFF00) + (data[10] & 0xFF)
    i7 = 11
    block_size = key.size_in_bytes()

    decrypted_data = bytearray()
    while i8 >= block_size:
        block = data[i7:i7 + block_size]
        decrypted_block = cipher.decrypt(block,sentinel=None)
        decrypted_data.extend(decrypted_block)
        i8 -= block_size
        i7 += block_size
    return bytes(decrypted_data)

def build_first_message():
    data = {
        "id": 1,
        "method": "hello",
        "params": {
            "app_ver": 1,
            "key": KEY[1],
        }
    }
    print(data)
    key = VACUUM_SSID.encode("utf-8")[-16:]
    cipher = AES.new(key, AES.MODE_ECB)
    padded_data = pad(json.dumps(data, separators=(',', ':')).encode("utf-8"), AES.block_size)
    ciphertext = cipher.encrypt(padded_data)

    return build_bytes(ciphertext,16)

def decode_second_messagE(message):
    return decrypt_rsa_data(message, KEY[0])

def build_third_message(key, u, s, t, r ="US"):
    data = {"u":u,
                "ssid": YOUR_SSID,
                "token": {
                    "r": r,
                    "tz": YOUR_TIMEZONE,
                    "s": s,
                    "cst": YOUR_CST,
                    "t":t
                },
                "passwd": YOUR_SSID_PASS}
    print(data)
    cipher = AES.new(key.encode("utf-8"), AES.MODE_ECB)
    padded_data = pad(json.dumps(data, separators=(',', ':')).encode("utf-8"), AES.block_size)
    ciphertext = cipher.encrypt(padded_data)

    return build_bytes(ciphertext, 1)


def send_udp_message(message, ip="192.168.8.1", port=55559, buffer_size=1024, timeout=20):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        sock.sendto(message, (ip, port))
        print(f"Sent: {message}")

        data, addr = sock.recvfrom(buffer_size)
        return data




async def main():

    api = RoborockApiClient(YOUR_RR_USER)
    ud = await api.pass_login(YOUR_RR_PASS)
    prepare = await api.nc_prepare(ud, YOUR_TIMEZONE)
    input("Reset the vacuum's wifi/ Change to the vacuums ssid, then hit any key")
    hello_msg = build_first_message()
    hello_response = json.loads(decode_second_messagE(send_udp_message(hello_msg)))
    time.sleep(.5)
    wifi_msg = send_udp_message(build_third_message(hello_response['params']['key'],u=ud.rruid,s=prepare['s'], t=prepare['t'],r=YOUR_REGION))
    input("Wait for the status identifier on your vacuum for wifi go to solid blue. Then change to a real ssid, then hit any key.")
    resp =await api.add_device(ud, s=prepare['s'], t=prepare['t'])
    print(resp)




if __name__ == '__main__':
    asyncio.run(main())

