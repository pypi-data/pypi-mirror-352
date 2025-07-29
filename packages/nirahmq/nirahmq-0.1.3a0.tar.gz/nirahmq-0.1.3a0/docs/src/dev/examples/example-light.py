#  SPDX-License-Identifier: AGPL-3.0-or-later
#  Copyright (C) 2025  Dionisis Toulatos

import json

from nirahmq import *
from nirahmq.components import Light
from nirahmq.enums import LightColorMode


def callback(light: Light, payload: str) -> None:
    try:
        cmd = json.loads(payload)
        if cmd['state'] == 'ON':
            if not callback.prev_state:
                print("Turning light ON")

            if brightness := cmd.get('brightness'):
                print(f"Setting brightness to {brightness / 2.55:.0f}%")

            if temp := cmd.get('color_temp'):
                print(f"Setting color temperature to {temp}K")

            callback.prev_state = True
        elif cmd['state'] == 'OFF':
            print("Turning light OFF")

            callback.prev_state = False
    except json.decoder.JSONDecodeError:
        pass


callback.prev_state = False  # Function static variable

discovery_info = DiscoveryInfo(
    device=DeviceInfo(identifiers="nirahmq-device"),
    origin=OriginInfo(name="Python example"),
    components={
        'light': Light(
            command_topic="~/command",
            supported_color_modes=[LightColorMode.COLOR_TEMP],
            color_temp_kelvin=True,
            command_callback=callback
        )
    }
)

with (MQTTClient("homeassistant.lan", username="<username>", password="<password>") as client,
      Device(client, discovery_info) as device):
    input("Press enter to exit")
