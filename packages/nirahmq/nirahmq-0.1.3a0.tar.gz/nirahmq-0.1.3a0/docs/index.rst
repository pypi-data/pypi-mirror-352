..
    SPDX-License-Identifier: AGPL-3.0-or-later
    Copyright (C) 2025  Dionisis Toulatos

.. toctree::
    :hidden:

    src/install
    src/quickstart

.. toctree::
    :caption: Development
    :hidden:

    src/dev/api
    src/dev/examples
    src/dev/license

NirahMQ
#######

A complete Home Assistant MQTT Python library with ease of use in mind.

.. warning::

    This library is currently in ALPHA! Expect things to change or break!

✨ Features
===========

* Supports all Home Assistant MQTT components and all their features
* Use of device-based discovery instead of component-based for simpler organization
* Support for automatic cleanup of topics on exit
* Device wide and per component availability support
* MQTT birth and last will support for both device and Home Assistant
* Ease of use by simple static definitions, while allowing runtime modifications
* Full Python type hint support
* Validation of definitions and user inputs on load thanks to `pydantic <https://github.com/pydantic/pydantic>`_
* Extensible API through simple class inheritance
