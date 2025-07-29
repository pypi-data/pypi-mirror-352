..
    SPDX-License-Identifier: AGPL-3.0-or-later
    Copyright (C) 2025  Dionisis Toulatos

Usage examples
##############

Simple switch
=============

A simple single switch example. It prints the state of the switch on change.

Import modules
--------------

First import all the necessary modules:

.. literalinclude:: examples/example-switch.py
    :lineno-start: 1
    :lines: 4-5

Declare the switch callback
---------------------------

The switch command callback is called each time a payload is sent from Home Assistant to the switch.
The expected payloads are :py:attr:`Switch.payload_on <nirahmq.components.Switch.payload_on>` for activating
and :py:attr:`Switch.payload_off <nirahmq.components.Switch.payload_off>` for deactivating the switch.

.. literalinclude:: examples/example-switch.py
    :lineno-start: 5
    :lines: 8-17

.. note::
    Notice that the switch component is sending its new state back to Home Assistant.
    Is :py:attr:`Switch.optimistic <nirahmq.components.Switch.optimistic>` was set to ``True`` manually or by not
    defining :py:attr:`Switch.state_topic <nirahmq.components.Switch.state_topic>`, this would not be required.

Declare the discovery info
--------------------------

Declare a bare bones device with a single switch component.

.. literalinclude:: examples/example-switch.py
    :lineno-start: 17
    :lines: 20-30

Main program
------------

The preferred way to use the :py:class:`~nirahmq.device.Device` and :py:class:`~nirahmq.mqtt.MQTTClient` classes is
inside a context manager.

.. literalinclude:: examples/example-switch.py
    :lineno-start: 29
    :lines: 32-

Full code sample
----------------

.. admonition:: Full code sample
    :collapsible: closed

    .. literalinclude:: examples/example-switch.py
        :caption: Switch example
        :lines: 4-
        :linenos:

Temperature light
=================

A single light with color temperature support in Kelvin.

Import modules
--------------

First import all the necessary modules:

.. literalinclude:: examples/example-light.py
    :lineno-start: 1
    :lines: 4-8

Declare the light callback
---------------------------

The light command callback is called each time a payload is sent from Home Assistant to the light.
The expected payloads are JSON encoded.

.. important::
    Currently only the JSON schema is supported with the :py:class:`~nirahmq.components.Light` component.

.. literalinclude:: examples/example-light.py
    :lineno-start: 8
    :lines: 11-33

.. note::
    Here, the light is working in optimistic mode, as no
    :py:attr:`Light.state_topic <nirahmq.components.Light.state_topic>` is defined.

Declare the discovery info
--------------------------

Declare a bare bones device with a single light component.

.. literalinclude:: examples/example-light.py
    :lineno-start: 32
    :lines: 35-46

Main program
------------

.. literalinclude:: examples/example-light.py
    :lineno-start: 45
    :lines: 48-

Full code sample
----------------

.. admonition:: Full code sample
    :collapsible: closed

    .. literalinclude:: examples/example-light.py
        :caption: Light example
        :lines: 4-
        :linenos:

Multi-sensor device
===================

A device containing multiple sensor components.

Import modules
--------------

First import all the necessary modules:

.. literalinclude:: examples/example-multi.py
    :lineno-start: 1
    :lines: 4-8

Declare the discovery info
--------------------------

Declare a bare bones device with one temperature and one humidity sensor.

.. literalinclude:: examples/example-multi.py
    :lineno-start: 7
    :lines: 10-25

Main program
------------

Inside the context, the values for the temperature and humidity sensor is set to random values.

.. literalinclude:: examples/example-multi.py
    :lineno-start: 24
    :lines: 27-

Full code sample
----------------

.. admonition:: Full code sample
    :collapsible: closed

    .. literalinclude:: examples/example-multi.py
        :caption: Light example
        :lines: 4-
        :linenos:
