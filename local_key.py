"""A script to get the local key."""

import asyncio
import argparse

from roborock.web_api import RoborockApiClient


async def main():
    """A script to get the local key."""

    parser = argparse.ArgumentParser(
        prog='get_local_key',
        description='Retrieve the local key for a Roborock device.',
        epilog='Example usage: python local_key.py -e your_email@example.com -p your_password'
    )
    parser.add_argument("-e", "--email", required=True, help="Your Roborock account email")
    parser.add_argument("-p", "--password", required=True, help="Your Roborock account password")

    args = parser.parse_args()

    web_api = RoborockApiClient(username=args.email)
    try:
        user_data = await web_api.pass_login(args.password)
    except Exception as e:
        print(f"Login failed: {e}")
        return
    # Or you can login with a code using web_api.code_login() and .request_code()
    # Login via your password
    try:
        home_data = await web_api.get_home_data_v2(user_data)
    except Exception as e:
        print(f"Failed to get device data: {e}")
        return

    for device in home_data.devices:
        local_key = device.local_key
        print(f"Device ID: {device.duid}")
        print(f"Device Model: {device.name}")
        print(f"Local Key: {local_key}")
        print()



if __name__ == "__main__":
    asyncio.run(main())
