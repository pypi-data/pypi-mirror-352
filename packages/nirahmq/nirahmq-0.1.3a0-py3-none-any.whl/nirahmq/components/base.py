#  SPDX-License-Identifier: AGPL-3.0-or-later
#  Copyright (C) 2025  Dionisis Toulatos

import re
import typing
from functools import cached_property
from types import GenericAlias
from typing import Annotated, Any, Literal, Self, TypeAliasType

from pydantic import Field, PrivateAttr, conlist, model_validator

from nirahmq.enums import Category, Platform
from nirahmq.mqtt import MQTTClient, QoS, Topic
from nirahmq.utils import BaseModel, Optional, Required, Unset

type ComponentCallback[T] = typing.Callable[[T, str], None]

type StateTopic = Topic
type CommandTopic = Topic

ComponentDefaultCallback = Field(default=Unset, exclude=True)
"""Default component callback value."""


class ComponentBase(BaseModel):
    """Base component class.

    All the components in :py:mod:`nirahmq.components` are derived from this class.
    """

    _mqtt_client: MQTTClient = PrivateAttr()  # Make linter happy

    platform: Annotated[Platform, Required]

    # Special base topic field
    base_topic: Annotated[Optional[str], Field(serialization_alias='~')] = Unset

    ha_status_callback: Optional[ComponentCallback['ComponentBase']] = ComponentDefaultCallback

    def _abs_topic(self, topic: str) -> str:
        """Calculate the absolute topic path based on the :py:attr:`base_topic`.

        :param str topic: The relative topic path
        :returns: The absolute topic path
        :rtype: str
        """
        if self.base_topic is not Unset:
            return f"{self.base_topic}/{topic[2:]}"
        return topic

    def _is_type(self, item: Any, type_: type | TypeAliasType) -> bool:
        """Check if an item is of a specified type.

        This method crawls annotations (:py:func:`typing.Annotated`) and generic aliases
        (:py:class:`typing.GenericAlias`) to check if the item matches the specified type.

        :param typing.Any item: The item to check
        :param type type\\_: The type to check against
        :returns: True on match
        :rtype: bool
        """
        if item is type_:
            return True
        if isinstance(item, GenericAlias):
            for arg in item.__args__:
                if self._is_type(arg, type_):
                    return True
        if typing.get_origin(item) is Annotated:
            return self._is_type(item.__origin__, type_)
        return False

    def _has_type(self, item: Any, type_: type | TypeAliasType) -> bool:
        """Check if an item has a specified type.

        This method crawls annotations (:py:func:`typing.Annotated`) and generic aliases
        (:py:class:`typing.GenericAlias`) to check if the item matches or contains the specified type.

        :param typing.Any item: The item to check
        :param type type\\_: The type to check against
        :returns: True on match
        :rtype: bool
        """
        if item is type_:
            return True
        if isinstance(item, GenericAlias):
            for arg in item.__args__:
                if self._has_type(arg, type_):
                    return True
        if typing.get_origin(item) is Annotated:
            for metadata in item.__metadata__:
                if self._has_type(metadata, type_):
                    return True
        return False

    def publish(
            self,
            topic: Optional[str],
            payload: str | bytes | bytearray | int | float | None,
            qos: QoS = QoS.MOST,
            retain: bool = True
    ) -> None:
        """Publish an arbitrary payload to the specified MQTT topic.

        Publish an arbitrary payload to the specified MQTT topic.
        Optionally, set the Quality of Service (QoS) and retain flag for the message.

        Does nothing if the instance is not connected to an MQTT broker or the ``topic`` is ``Unset``.

        :param str topic: The MQTT topic to publish the payload to
        :param str | bytes | bytearray | int | float | None payload: The payload to publish
        :param QoS qos: The QoS to use
        :param bool retain: Retain flag
        """
        if topic is Unset:
            return
        self._mqtt_client.publish(self._abs_topic(topic), payload, qos, retain)

    def _on_init(self, mqtt: MQTTClient) -> None:
        """Called when a component is registered to a device.

        :param MQTTClient mqtt: The MQTT client to use for communication
        """
        self._mqtt_client = mqtt

        # Always included fields
        for name, annotation in self.__annotations__.items():
            if self._has_type(annotation, Required):
                # Basically `self.foo = self.foo` but sets it as an explicitly set field
                setattr(self, name, getattr(self, name))

    def _on_remove(self) -> None:
        """Called before a component is unregistered from its device."""
        pass


class StatefulComponent(ComponentBase):
    """A component class that has state topics to publish to.

    All components that report a state, inherit from this class.
    """

    def _on_remove(self) -> None:
        super()._on_remove()

        for topic in self._set_state_topics:
            self.publish(getattr(self, topic), None)

    @cached_property
    def _state_topics(self) -> tuple[str, ...]:
        """All class attributes that represent state topics.

        :returns: The state topic class attribute names
        :rtype: tuple[str, ...]
        """
        return tuple(name for name, annot in self.__annotations__.items() if self._is_type(annot, StateTopic))

    @cached_property
    def _set_state_topics(self) -> tuple[str, ...]:
        """All the explicitly set class attributes that represent state topics.

        :returns: The set state topic class attribute names
        :rtype: tuple[str, ...]
        """
        return tuple(topic for topic in self._state_topics if topic in self.model_fields_set)


class CallableComponent(ComponentBase):
    """A component class that has command topics to receive data from.

    All components that receive commands, inherit from this class.
    """

    def _on_init(self, mqtt: MQTTClient) -> None:
        super()._on_init(mqtt)

        def _callback_outer(callback_: ComponentCallback):
            def _callback_inner(payload: bytes | bytearray):
                callback_(self, payload.decode(self.encoding if isinstance(self, EntityBase) else 'utf-8'))

            return _callback_inner

        for topic, callback in self._command_mapping.items():
            topic = getattr(self, topic)
            callback = getattr(self, callback)
            self._mqtt_client.add_callback(self._abs_topic(topic), _callback_outer(callback))

    def _on_remove(self) -> None:
        super()._on_remove()

        for topic in self._command_mapping:
            topic = getattr(self, topic)
            self._mqtt_client.remove_callback(self._abs_topic(topic))
            self.publish(topic, None)

    @cached_property
    def _command_topics(self) -> tuple[str, ...]:
        """All class attributes that represent command topics.

        :returns: The command topic class attribute names
        :rtype: tuple[str, ...]
        """
        return tuple(name for name, annot in self.__annotations__.items() if self._is_type(annot, CommandTopic))

    @cached_property
    def _set_command_topics(self) -> tuple[str, ...]:
        """All the explicitly set class attributes that represent command topics.

        :returns: The set command topic class attribute names
        :rtype: tuple[str, ...]
        """
        return tuple(topic for topic in self._command_topics if topic in self.model_fields_set)

    @cached_property
    def _command_mapping(self) -> dict[str, str]:
        """A mapping between class attributes of command topics and callbacks.

        A map that takes a class attribute name of a command topic
        and returns the class attribute name of its corresponding callback.

        :returns: The mapping between class attributes of command topics and callbacks
        :rtype: dict[str, str]
        """
        mapping = {}
        for topic in self._set_command_topics:
            callback = re.sub(r"^(.+)_(topic)$", r"\1_callback", topic)
            if getattr(self, callback) is not Unset:
                mapping[topic] = callback
        return mapping


class AvailabilityItem(BaseModel):
    """Dataclass representing an item in the availability list of an :py:class:`Availability` class."""

    payload_available: Optional[str] = 'online'
    payload_not_available: Optional[str] = 'offline'
    topic: StateTopic
    value_template: Optional[str] = Unset


class Availability(BaseModel):
    """A dataclass representing a component that supports availability.

    All components that support availability, inherit from this class.
    """

    availability: Optional[conlist(AvailabilityItem, min_length=1)] = Unset
    availability_mode: Optional[Literal['all', 'any', 'latest']] = 'latest'
    availability_template: Optional[str] = Unset
    availability_topic: Optional[StateTopic] = Unset
    payload_available: Optional[str] = 'online'
    payload_not_available: Optional[str] = 'offline'

    @model_validator(mode='after')
    def _check_stuff(self) -> Self:
        if self.availability is not Unset and self.availability_topic is not Unset:
            raise ValueError('`availability_topic` and `availability` are mutually exclusive')
        return self

    def get_availability_topics(self) -> list[tuple[str, str, str]]:
        """Get all the available availability topics and their ``AVAILABLE`` and ``NOT AVAILABLE`` payloads.

        :returns: The available availability topics and corresponding payloads
        :rtype: list[tuple[str, str, str]]
        """
        if self.availability is not Unset:
            return [(av.topic, av.payload_available, av.payload_not_available) for av in self.availability]
        if self.availability_topic is not Unset:
            return [(self.availability_topic, self.payload_available, self.payload_not_available)]
        return []


class BareEntityBase(Availability, ComponentBase):
    """A component class that represents a bare Home Assistant entity."""

    icon: Optional[str] = Unset
    json_attributes_template: Optional[str] = Unset
    json_attributes_topic: Optional[StateTopic] = Unset
    name: Optional[str | None] = Unset
    object_id: Optional[str] = Unset
    qos: Optional[QoS] = QoS.MOST
    unique_id: Optional[str] = Unset

    def _on_init(self, mqtt: MQTTClient) -> None:
        super()._on_init(mqtt)

        if self.availability is not Unset:
            pass

    def _on_remove(self) -> None:
        super()._on_remove()

        for topic, _, _ in self.get_availability_topics():
            self.publish(topic, None)

    def set_availability(self, state: bool) -> None:
        """Set availability of the entity.

        :param bool state: Whether the entity should be available
        """
        for topic, online, offline in self.get_availability_topics():
            self.publish(topic, online if state else offline)


class EntityBase(BareEntityBase):
    """A component class that represents a Home Assistant entity."""

    enabled_by_default: Optional[bool] = True
    encoding: Optional[str] = 'utf-8'
    entity_category: Optional[Category] = Category.NORMAL
    entity_picture: Optional[str] = Unset
