# NirahMQ

![PyPI - Version](https://img.shields.io/pypi/v/nirahmq?label=PyPI)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/dionisis2014/nirahmq/ci.yaml?logo=github&label=CI)

A complete Home Assistant MQTT Python library with ease of use in mind

> [!WARNING]
> This library is currently in ALPHA! Expect things to change or break!

## ✨ Features

- Supports all Home Assistant MQTT components and all their features
- Use of device-based discovery instead of component-based for simpler organization
- Support for automatic cleanup of topics on exit
- Device wide and per component availability support
- MQTT birth and last will support for both device and Home Assistant
- Ease of use by simple static definitions, while allowing runtime modifications
- Full Python type hint support
- Validation of definitions and user inputs on load thanks to [pydantic](https://github.com/pydantic/pydantic)
- Extensible API through simple class inheritance

## 📦 Installation

NirahMQ requires Python 3.12 or later and can be installed simply with `pip install nirahmq`.

## 🚀 Simple example

Below is an example of a simple Text component that prints its contents on update:

<details>
<summary>Example code</summary>

```python
from nirahmq.components import Text
from nirahmq.device import Device, DeviceInfo, DiscoveryInfo, OriginInfo
from nirahmq.mqtt import MQTTClient


def callback(text: Text, payload: str) -> None:
    print(f"Got new text: `{payload}`")
    text.set_text(payload)


dinfo = DiscoveryInfo(
    device=DeviceInfo(
        name="NirahMQ Test Device",
        identifiers="NirahMQ-Test-Device"
    ),
    origin=OriginInfo(
        name="Python Program"
    ),
    components={
        'component1': Text(command_topic="~/cmd", state_topic="~/state", command_callback=callback)
    }
)

with (MQTTClient("homeassistant.lan", 1883, "user", r"password") as client,
      Device(client, dinfo, "node_id") as device):
    input("Press enter to continue...\n")
```
</details>

## 📝 License
Copyright © 2025 [Dionisis Toulatos](https://github.com/dionisis2014)

NirahMQ uses the [AGPL-3.0+](LICENSE) license
