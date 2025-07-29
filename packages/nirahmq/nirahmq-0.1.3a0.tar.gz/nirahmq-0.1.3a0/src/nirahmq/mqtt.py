#  SPDX-License-Identifier: AGPL-3.0-or-later
#  Copyright (C) 2025  Dionisis Toulatos

import time
from enum import IntEnum
from queue import SimpleQueue
from typing import Annotated, Any, Callable, Self

import paho.mqtt as pmq
from paho.mqtt import client as pmq_client
from paho.mqtt.subscribeoptions import SubscribeOptions
from pydantic import Field

type Topic = Annotated[str, Field(pattern=r"^(?:(?:~/)?[a-zA-Z0-9_-]+)(?:/[a-zA-Z0-9_-]+)*$")]


def _check_mqtt_error(func: Callable[[...], pmq.enums.MQTTErrorCode], *args, **kwargs) -> None:
    if (err := func(*args, **kwargs)) != pmq.enums.MQTTErrorCode.MQTT_ERR_SUCCESS:
        raise RuntimeError(f"Failed to call function {func.__name__}: {err}")


class QoS(IntEnum):
    """MQTT Quality of Service (QoS) enumeration class."""

    MOST = 0  # At most once
    """Message is delivered at most once."""
    LEAST = 1  # At least once
    """Message is delivered at least once."""
    EXACTLY = 2  # Exactly once
    """Message is delivered exactly once."""


class MQTTClient:
    """NirahMQ MQTT client class

    This class is responsible for establishing a connection to the MQTT broker, handles authentication, callback
    registration and subscription, as well as publishing arbitrary payloads to any MQTT topic.
    """

    _mqtt_client: pmq_client.Client
    _mqtt_queue: SimpleQueue

    _hostname: str
    _port: int
    _client_id: str

    _subscriptions: SimpleQueue[str]

    def __init__(
            self,
            hostname: str,
            port: int = 1883,
            username: str | None = None,
            password: str | None = None,
            client_id: str = "nirahmq"
    ):
        """Initialize the MQTT client.

        .. caution::
            Currently there is no TLS support! Authentication details and messages are sent on plaintext!

        :param str hostname: The MQTT broker hostname
        :param int port: The MQTT broker port
        :param str username: The MQTT broker username
        :param str password: The MQTT broker password
        :param str client_id: The MQTT broker client ID
        """
        self._hostname = hostname
        self._port = port
        self._client_id = client_id

        self._mqtt_client = pmq_client.Client(
            pmq.enums.CallbackAPIVersion.VERSION2,
            client_id,
            protocol=pmq_client.MQTTv5
        )

        if username is not None:
            self._mqtt_client.username_pw_set(username, password)

        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.on_connect_fail = self._on_connect_fail
        self._mqtt_client.on_disconnect = self._on_disconnect

        self._mqtt_queue = SimpleQueue()

        self._subscriptions = SimpleQueue()

    def __enter__(self) -> Self:
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.disconnect()

    @property
    def hostname(self) -> str:
        """The configured MQTT broker hostname (read-only).

        :return: The configured hostname
        :rtype: str
        """
        return self._hostname

    @property
    def port(self) -> int:
        """The configured MQTT broker port (read-only).

        :return: The configured port
        :rtype: int
        """
        return self._port

    @property
    def client_id(self) -> str:
        """The configured MQTT client ID (read-only).

        :return: The configured client ID
        :rtype: str
        """
        return self._client_id

    def _on_connect(
            self,
            client: pmq_client.Client,
            userdata: Any,
            flags: dict[str, Any],
            reason: pmq.reasoncodes.ReasonCode,
            properties: pmq.properties.Properties | None
    ) -> None:
        if reason.value != 0:
            self._mqtt_client.disconnect()
            self._mqtt_queue.put(False)
            return

        if not self._subscriptions.empty():
            opts = SubscribeOptions()
            topics = []
            while not self._subscriptions.empty():
                topics.append((self._subscriptions.get(), opts))
            self._mqtt_client.subscribe(topics)
        self._mqtt_queue.put(True)

    def _on_connect_fail(
            self,
            client: pmq_client.Client,
            userdata: Any
    ) -> None:
        self._mqtt_queue.put(False)

    def _on_disconnect(
            self,
            client: pmq_client.Client,
            userdata: Any,
            flags: pmq_client.DisconnectFlags,
            reason: pmq.reasoncodes.ReasonCode,
            properties: pmq.properties.Properties | None
    ) -> None:
        pass  # TODO: Handle gracefully

    # TODO: This thing acts weird. Needs more investigating
    def set_will(self, topic: str, payload: str) -> None:  # NOTE: Must be called before `connect`
        """Set the MQTT Last Will and Testament (LWT) payload and topic.

        Set the MQTT topic and payload that the MQTT broker will publish to when the client disconnects unexpectedly.

        .. note::
            Must be called before connection.
            Does nothing otherwise.

        :param str topic: The LWT topic
        :param str payload: The LWT payload
        """
        self._mqtt_client.will_set(topic, payload)

    def add_callback(self, topic: str, callback: Callable[[bytes | bytearray], None]) -> None:
        """Register a callback to an MQTT topic.

        Subscribes to the specified MQTT topic and registers a user supplied callback to it.
        See :py:meth:`remove_callback` for how to remove a callback.

        :param str topic: The MQTT topic to register the callback to
        :param Callable[[bytes | bytearray], None] callback: The callback to register
        """
        self._mqtt_client.message_callback_add(topic, lambda c, u, m: callback(m.payload))
        if self._mqtt_client.is_connected():
            self._mqtt_client.subscribe((topic, SubscribeOptions()))
        else:
            self._subscriptions.put(topic)

    def remove_callback(self, topic: str) -> None:
        """Unregister a callback to an MQTT topic.

        Removes a previously registered callback with :py:meth:`add_callback`
        and unsubscribes from the associated MQTT topic.
        See :py:meth:`add_callback` for how to add a callback.

        .. note::
            The instance must be connected to take effect.
            Does nothing otherwise.

        :param str topic: The topic to remove the callback from
        """
        if self._mqtt_client.is_connected():
            # TODO: Needs more testing. Is it safe immediately return after `message_callback_remove`
            self._mqtt_client.message_callback_remove(topic)
            self._mqtt_client.unsubscribe(topic)

    def connect(self) -> bool:
        """Connect to the MQTT broker.

        Attempt to connect to the MQTT broker with the configured settings.
        If the connection was successful, returns True.
        If the connection failed or the instance is already connected, returns False.

        :return: True if the connection was successful
        :rtype: bool

        :raises RuntimeError: If the connection was not successful
        """
        if not self._mqtt_client.is_connected():
            _check_mqtt_error(self._mqtt_client.connect, self._hostname, self._port)
            self._mqtt_client.loop_start()
            return self._mqtt_queue.get()
        return False

    def disconnect(self) -> None:
        """Disconnect from the MQTT broker.

        Disconnect from the connected MQTT broker.
        Does nothing if the instance is already disconnected.

        :raises RuntimeError: If the connection was not successfully terminated
        """
        if self._mqtt_client.is_connected():
            while self._mqtt_client.want_write():
                time.sleep(0.01)
            _check_mqtt_error(self._mqtt_client.disconnect)

    def publish(
            self,
            topic: str,
            payload: str | bytes | bytearray | int | float | None,
            qos: QoS = QoS.MOST,
            retain: bool = True
    ) -> None:
        """Publish an arbitrary payload to the specified MQTT topic.

        Publish an arbitrary payload to the specified MQTT topic.
        Optionally, set the Quality of Service (QoS) and retain flag for the message.

        Does nothing if the instance is not connected to an MQTT broker.

        :param str topic: The MQTT topic to publish the payload to
        :param str | bytes | bytearray | int | float | None payload: The payload to publish
        :param QoS qos: The QoS to use
        :param bool retain: Retain flag
        """
        if self._mqtt_client.is_connected():
            self._mqtt_client.publish(topic, payload, int(qos), retain)
