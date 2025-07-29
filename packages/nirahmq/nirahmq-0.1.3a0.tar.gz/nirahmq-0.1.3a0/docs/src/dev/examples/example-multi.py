#  SPDX-License-Identifier: AGPL-3.0-or-later
#  Copyright (C) 2025  Dionisis Toulatos

import random

from nirahmq import *
from nirahmq.components import Sensor
from nirahmq.enums import SensorClass

discovery_info = DiscoveryInfo(
    device=DeviceInfo(name="Multi device", identifiers="nirahmq-device"),
    origin=OriginInfo(name="Python example"),
    components={
        'temp': Sensor(
            device_class=SensorClass.TEMPERATURE,
            suggested_display_precision=1,
            state_topic="~/state"
        ),
        'humid': Sensor(
            device_class=SensorClass.HUMIDITY,
            suggested_display_precision=1,
            state_topic="~/state"
        )
    }
)

with (MQTTClient("homeassistant.lan", username="<username>", password="<password>") as client,
      Device(client, discovery_info) as device):
    device['temp'].set_value(random.uniform(20, 30))
    device['humid'].set_value(random.uniform(40, 60))

    input("Press enter to exit")
