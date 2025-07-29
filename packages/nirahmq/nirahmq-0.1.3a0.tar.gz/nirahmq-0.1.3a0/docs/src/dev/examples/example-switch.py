#  SPDX-License-Identifier: AGPL-3.0-or-later
#  Copyright (C) 2025  Dionisis Toulatos

from nirahmq import *
from nirahmq.components import Switch


def callback(switch: Switch, payload: str) -> None:
    match payload:
        case switch.payload_on:
            switch.set_state(True)
            print("TURNING ON")
        case switch.payload_off:
            switch.set_state(False)
            print("TURNING OFF")
        case _:
            print(f"Invalid payload `{payload}`!")


discovery_info = DiscoveryInfo(
    device=DeviceInfo(identifiers="nirahmq-device"),
    origin=OriginInfo(name="Python example"),
    components={
        'switch': Switch(
            command_topic="~/command",
            state_topic="~/state",
            command_callback=callback
        )
    }
)

with (MQTTClient("homeassistant.lan", username="<username>", password="<password>") as client,
      Device(client, discovery_info) as device):
    input("Press enter to exit")
