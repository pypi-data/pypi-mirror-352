# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2024  Dionisis Toulatos

import hashlib
import re
from functools import cached_property
from typing import Self

from pydantic import Field, SerializeAsAny, conlist, model_validator

from nirahmq.components.base import Availability, BareEntityBase, CommandTopic, ComponentBase, ComponentCallback, \
    EntityBase, StateTopic
from nirahmq.mqtt import MQTTClient, QoS
from nirahmq.utils import BaseModel, Optional, Unset, sanitize_string


class DeviceInfo(BaseModel):
    """Dataclass that stores information about a Home Assistant device."""

    configuration_url: Optional[str] = Unset
    connections: Optional[conlist(tuple[str, str], min_length=1)] = Unset
    hw_version: Optional[str] = Unset
    identifiers: Optional[str | conlist(str, min_length=1)] = Unset
    manufacturer: Optional[str] = Unset
    model: Optional[str] = Unset
    model_id: Optional[str] = Unset
    name: Optional[str] = Unset
    serial_number: Optional[str] = Unset
    suggested_area: Optional[str] = Unset
    sw_version: Optional[str] = Unset
    via_device: Optional[str] = Unset

    use_hash: bool = Field(default=False, exclude=True)

    @model_validator(mode='after')
    def _check_identifiers(self) -> Self:
        if self.identifiers is None and self.connections is None:
            raise ValueError("At least one of `identifiers` or `connections` must be set")
        return self

    @cached_property
    def unique_id(self) -> str:
        if self.use_hash:
            sha256 = hashlib.sha256()
            if self.name is not Unset:
                sha256.update(self.name.encode())  # pylint: disable=no-member
            if self.identifiers is not None:
                # Token can be whole strings or character in single string. Same result either way
                for token in self.identifiers:
                    sha256.update(token.encode())
            if self.connections is not None:
                for type_, identifier in self.connections:
                    sha256.update(type_.encode())
                    sha256.update(identifier.encode())
            return sha256.hexdigest()
        else:
            if self.name is not Unset:
                name = self.name
            elif self.identifiers is not None:
                if isinstance(self.identifiers, str):
                    name = self.identifiers
                else:
                    name = self.identifiers[0]
            else:
                name = '-'.join(self.connections[0])
            return sanitize_string(name)


class OriginInfo(BaseModel):
    """Dataclass that stores the Home Assistant device origin information."""

    name: str
    sw_version: Optional[str] = Unset
    support_url: Optional[str] = Unset


class DiscoveryInfo(Availability):
    """Dataclass that stores the discovery info used for Home Assistant device discovery."""

    device: DeviceInfo
    origin: OriginInfo
    command_topic: Optional[CommandTopic] = Unset
    state_topic: Optional[StateTopic] = Unset
    qos: Optional[QoS] = Unset
    encoding: Optional[str] = Unset
    components: dict[str, SerializeAsAny[ComponentBase]]


class Device:
    """A wrapper class for a Home Assistant device.

    The class stores an instance of an :py:class:`nirahmq.mqtt.MQTTClient` and :py:class:`DiscoveryInfo`.
    At initialization, they are configured, command topics are subscribed to and callbacks are registered.
    At runtime, availability and dynamic component addition and removal are managed automatically.

    .. tip::
        The class can be used as a dictionary proxy to the provided :py:attr:`DiscoveryInfo.components` attribute.
    """

    _mqtt_client: MQTTClient
    _discovery_info: DiscoveryInfo

    _node_id: str | None
    _discovery_topic: str
    _state_topic_base: str

    _use_status: bool

    _flag_remove: bool

    _status_callback: ComponentCallback['Device'] | None

    def __init__(
            self,
            mqtt_client: MQTTClient,
            discovery_info: DiscoveryInfo,
            node_id: str | None = None,
            discovery_prefix: str = "homeassistant",
            state_prefix: str = "nirahmq",
            use_status: bool = False,
            remove_on_exit: bool = False,
            status_callback: ComponentCallback['Device'] | None = None
    ) -> None:
        """Initialize the Home Assistant device wrapper.

        :param MQTTClient mqtt_client: The MQTT client instance to use
        :param DiscoveryInfo discovery_info: The Home Assistant device discovery information
        :param str | None node_id: The `node_id` to use in MQTT topics
        :param str discovery_prefix: The MQTT topic prefix Home Assistant uses for discovery
        :param str state_prefix: The MQTT topic prefix to use for state and command topics
        :param bool use_status: Use availability
        :param bool remove_on_exit: Remove device on disconnect
        :param ComponentCallback['Device'] | None status_callback: The callback to call when Home Assistant
            publishes and availability message

        .. tip::
            Set the ``node_id`` when using multiple devices to group them together for better organization.
        """
        self._mqtt_client = mqtt_client
        self._discovery_info = discovery_info
        self._node_id = sanitize_string(node_id) if node_id is not None else None

        self._state_topic_base = f"{state_prefix}/"
        if self._node_id is not None:
            self._state_topic_base += f"{self._node_id}/"
        self._state_topic_base += self._discovery_info.device.unique_id

        self._discovery_topic = f"{discovery_prefix}/device/"
        if node_id is not None:
            self._discovery_topic += f"{self._node_id}/"
        self._discovery_topic += f"{self._discovery_info.device.unique_id}/config"

        self._use_status = use_status

        for key_id, component in self._discovery_info.components.items():
            self._component_init(key_id, component)

        # Handle availability `~/` prefix
        if self._discovery_info.availability_topic is not Unset:
            self._discovery_info.availability_topic = re.sub(
                r"^~/(.+)$",
                rf"{self._state_topic_base}/\1",
                self._discovery_info.availability_topic
            )
            will_topic = self._discovery_info.availability_topic
            payload_lwt = self._discovery_info.payload_not_available
        elif self._discovery_info.availability is not Unset:
            for availability in self._discovery_info.availability:
                availability.topic = re.sub(
                    r"^~/(.+)$",
                    rf"{self._state_topic_base}/\1",
                    availability.topic
                )
            will_topic = self._discovery_info.availability[0].topic
            payload_lwt = self._discovery_info.availability[0].payload_not_available
        else:
            will_topic = self._state_topic_base
            payload_lwt = self._discovery_info.payload_not_available
            # Make field set so it serializes
            self._discovery_info.availability_topic = self._state_topic_base
            self._discovery_info.__pydantic_fields_set__.remove('availability_topic')
        if self._use_status:
            self._mqtt_client.set_will(will_topic, payload_lwt)
            # Home Assistant birth and will
            self._mqtt_client.add_callback(
                f"{discovery_prefix}/status",
                self._ha_status_callback
            )

        self._flag_remove = remove_on_exit
        self._status_callback = status_callback

    def __getitem__(self, key: str) -> ComponentBase:
        return self._discovery_info.components[key]

    def __contains__(self, key: str) -> bool:
        return key in self._discovery_info.components

    def __enter__(self) -> Self:
        self.set_availability(True)
        self.announce()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.set_availability(False)
        if self._flag_remove:
            self.remove()

    def _ha_status_callback(self, payload: bytes | bytearray) -> None:
        if self._status_callback is not None:
            if self._discovery_info.encoding is Unset:
                self._status_callback(self, payload.decode('utf-8'))
            else:
                self._status_callback(self, payload.decode(self._discovery_info.encoding))
        for component in self._discovery_info.components.values():
            if component.ha_status_callback is not Unset:
                if self._discovery_info.encoding is not Unset:
                    payload = payload.decode(self._discovery_info.encoding)
                elif isinstance(component, EntityBase):
                    payload = payload.decode(component.encoding)
                else:
                    payload = payload.decode('utf-8')
                component.ha_status_callback(component, payload)

    def _component_init(self, key_id: str, component: ComponentBase) -> None:
        # Handle shared QoS and encoding
        if ('qos' in self._discovery_info.model_fields_set
                and 'qos' not in component.model_fields_set):
            component.qos = self._discovery_info.qos
            component.__pydantic_fields_set__.remove('qos')
        if ('encoding' in self._discovery_info.model_fields_set
                and 'encoding' not in component.model_fields_set):
            component.encoding = self._discovery_info.encoding
            component.__pydantic_fields_set__.remove('encoding')

        # Handle base topic if unset
        if component.base_topic is Unset:
            # Only set `base_topic` if user has entered any relative topic paths
            topics = filter(
                lambda f: f.endswith('_topic') or f == 'topic',
                component.model_fields_set
            )
            for topic in topics:
                topic = getattr(component, topic)
                if topic.startswith('~') or topic.endswith('~'):
                    component.base_topic = f"{self._state_topic_base}/{key_id}"
                    break

        component._on_init(self._mqtt_client)

        # Set `unique_id` after fields are at correct values
        if isinstance(component, BareEntityBase) and component.unique_id is Unset:
            sha256 = hashlib.sha256(
                component.model_dump_json(
                    exclude_unset=True,
                    by_alias=True
                ).encode('utf-8')
            )
            sha256.update(self._discovery_info.device.unique_id.encode('utf-8'))
            component.unique_id = sha256.hexdigest()

    def announce(self) -> None:
        """Send the Home Assistant discovery message."""
        self._mqtt_client.publish(
            self._discovery_topic,
            self._discovery_info.model_dump_json(exclude_unset=True, by_alias=True),
            retain=True
        )

    def component_register(
            self,
            name: str,
            component: ComponentBase,
            announce: bool = True
    ) -> None:
        """Register a new component with Home Assistant.

        :param str name: The internal name of the component to use
        :param ComponentBase component: The component to register
        :param bool announce: Whether to announce the registration

        :raises ValueError: If the component with the specified name is already registered
        """
        if name in self._discovery_info.components:
            raise ValueError(f"Component '{name}' is already registered")
        self._discovery_info.components[name] = component
        self._component_init(name, component)
        if announce:
            self.announce()

    def remove_component(self, name: str, announce: bool = True) -> None:
        """Unregister a component from Home Assistant.

        :param str name: The internal name of the component
        :param bool announce: Whether to announce the deregistration

        :raises ValueError: If the component with the specified name isn't registered
        """
        try:
            if announce:
                # Send an empty entity with `platform` key only to remove component
                self._discovery_info.components[name] = ComponentBase(
                    platform=self._discovery_info.components[name].platform
                )
                self.announce()
            del self._discovery_info.components[name]
            if announce:
                self.announce()
        except ValueError:
            raise ValueError(f"Component '{name}' is not registered")

    def remove(self) -> None:
        """Remove the device from Home Assistant and cleanup leftover topics."""
        for component in self._discovery_info.components.values():
            component._on_remove()
        if self._use_status:
            for topic, _, _ in self._discovery_info.get_availability_topics():
                self._mqtt_client.publish(topic, None)
        self._mqtt_client.publish(
            self._discovery_topic,
            '',
            self._discovery_info.qos if self._discovery_info.qos is not Unset else QoS.MOST,
            retain=True  # Docs say retained. Works without, IDK
        )

    def set_availability(self, state: bool) -> None:
        """Set device availability state.

        Only works if ``use_status`` was set to ``True`` in :py:class:`Device` constructor.

        :param bool state: The availability state
        """
        if self._use_status:
            for topic, online, offline in self._discovery_info.get_availability_topics():
                self._mqtt_client.publish(topic, online if state else offline)
