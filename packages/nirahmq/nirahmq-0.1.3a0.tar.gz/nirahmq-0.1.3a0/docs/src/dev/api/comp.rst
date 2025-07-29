..
    SPDX-License-Identifier: AGPL-3.0-or-later
    Copyright (C) 2025  Dionisis Toulatos

Components
##########

.. py:currentmodule:: nirahmq.components.base

.. toctree::
    :hidden:

    comp/base
    comp/components

NirahMQ components are split into two categories.
The :doc:`base <comp/base>` components and the :doc:`Home Asisstant <comp/components>` components.
Each Home Assistant component inherits one or more base components to implement specific behaviours.

.. inheritance-diagram:: EntityBase StatefulComponent CallableComponent
    :top-classes: nirahmq.utils.BaseModel
    :parts: 1
