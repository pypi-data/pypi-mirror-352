#  SPDX-License-Identifier: AGPL-3.0-or-later
#  Copyright (C) 2025  Dionisis Toulatos

import json
import re
from typing import Annotated, Any, Literal, Self

from pydantic import AnyUrl, Field, conlist, constr, field_validator, model_validator

from nirahmq import utils
from nirahmq.components.base import BareEntityBase, CallableComponent, CommandTopic, ComponentBase, ComponentCallback, \
    ComponentDefaultCallback, EntityBase, StateTopic, StatefulComponent
from nirahmq.enums import AlarmControlPanelCode, AlarmControlPanelFeature, AlarmControlPanelState, BinarySensorClass, \
    ButtonClass, CoverClass, CoverState, DeviceTrackerSource, DeviceTriggerSubtype, DeviceTriggerType, EventClass, \
    HVACAction, HVACFanMode, HVACMode, HVACPresetMode, HumidifierAction, HumidifierClass, HumidifierMode, \
    ImageEncoding, LawnMowerState, LightColorMode, LockState, NumberClass, NumberMode, Platform, Precision, \
    SensorClass, SensorStateClass, SwitchClass, TemperatureUnit, TextMode, UpdateClass, VacuumFanSpeed, VacuumFeature, \
    VacuumState, ValveClass, ValveState, WaterHeaterMode
from nirahmq.mqtt import MQTTClient, QoS
from nirahmq.utils import Optional, Regex, Required, Unset, clamp


class AlarmControlPanel(StatefulComponent, CallableComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.ALARM_CONTROL_PANEL

    code: Optional[str | AlarmControlPanelCode] = Unset
    core_armed_required: Optional[bool] = True
    code_disarm_required: Optional[bool] = True
    core_trigger_required: Optional[bool] = True
    command_template: Optional[str] = 'action'
    command_topic: CommandTopic
    payload_arm_away: Optional[str] = 'ARM_AWAY'
    payload_arm_home: Optional[str] = 'ARM_HOME'
    payload_arm_night: Optional[str] = 'ARM_NIGHT'
    payload_arm_vacation: Optional[str] = 'ARM_VACATION'
    payload_arm_custom_bypass: Optional[str] = 'ARM_CUSTOM_BYPASS'
    payload_disarm: Optional[str] = 'DISARM'
    payload_trigger: Optional[str] = 'TRIGGER'
    retain: Optional[bool] = False
    state_topic: StateTopic
    supported_features: Optional[list[AlarmControlPanelFeature]] = [
        AlarmControlPanelFeature.HOME, AlarmControlPanelFeature.AWAY, AlarmControlPanelFeature.NIGHT,
        AlarmControlPanelFeature.VACATION, AlarmControlPanelFeature.BYPASS, AlarmControlPanelFeature.TRIGGER
    ]
    value_template: Optional[str] = Unset

    command_callback: Optional[ComponentCallback['AlarmControlPanel']] = ComponentDefaultCallback

    def set_state(self, value: Optional[AlarmControlPanelState]) -> None:
        self.publish(self.state_topic, 'None' if value is Unset else str(value))


class BinarySensor(StatefulComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.BINARY_SENSOR

    device_class: Optional[BinarySensorClass | None] = Unset
    expire_after: Optional[int] = Unset
    force_update: Optional[bool] = False
    off_delay: Optional[int] = Unset
    payload_off: Optional[str] = 'OFF'
    payload_on: Optional[str] = 'ON'
    state_topic: StateTopic
    value_template: Optional[str] = Unset

    def set_state(self, state: Optional[bool]) -> None:
        self.publish(self.state_topic, 'None' if state is Unset else (self.payload_on if state else self.payload_off))


class Button(CallableComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.BUTTON

    command_template: Optional[str] = Unset
    command_topic: CommandTopic
    device_class: Optional[ButtonClass | None] = Unset
    payload_press: Optional[str] = 'PRESS'
    retain: Optional[bool] = False

    command_callback: Optional[ComponentCallback['Button']] = ComponentDefaultCallback


class Camera(StatefulComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.CAMERA

    image_encoding: Optional[ImageEncoding] = ImageEncoding.BINARY
    topic: StateTopic

    def _on_init(self, mqtt: MQTTClient) -> None:
        super()._on_init(mqtt)

        if self.image_encoding == ImageEncoding.BINARY and 'image_encoding' in self.model_fields_set:
            self.__pydantic_fields_set__.remove('image_encoding')

    def set_image(self, data: str | bytes | bytearray) -> None:
        self.publish(self.topic, data)


class Cover(StatefulComponent, CallableComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.COVER

    command_topic: Optional[CommandTopic] = Unset
    device_class: Optional[CoverClass | None] = Unset
    payload_close: Optional[str] = 'CLOSE'
    payload_open: Optional[str] = 'OPEN'
    payload_stop: Optional[str] = 'STOP'
    payload_stop_tilt: Optional[str] = 'stop'
    position_closed: Optional[int] = 0
    position_open: Optional[int] = 100
    position_template: Optional[str] = Unset
    position_topic: Optional[StateTopic] = Unset
    retain: Optional[bool] = False
    set_position_template: Optional[str] = Unset
    set_position_topic: Optional[CommandTopic] = Unset
    state_closed: Optional[str] = 'closed'
    state_closing: Optional[str] = 'closing'
    state_open: Optional[str] = 'open'
    state_opening: Optional[str] = 'opening'
    state_stopped: Optional[str] = 'stopped'
    state_topic: Optional[StateTopic] = Unset
    tilt_closed_value: Optional[int] = 0
    tilt_command_template: Optional[str] = Unset
    tilt_command_topic: Optional[CommandTopic] = Unset
    tilt_max: Optional[int] = 100
    tilt_min: Optional[int] = 0
    tilt_opened_value: Optional[int] = 100
    tilt_status_template: Optional[str] = Unset
    tilt_status_topic: Optional[StateTopic] = Unset
    value_template: Optional[str] = Unset

    # Keep after other fields due to `data` only containing already validated fields
    optimistic: Optional[bool] = Field(default_factory=lambda data: (data['state_topic'] is Unset and
                                                                     data['position_topic'] is Unset))
    tilt_optimistic: Optional[bool] = Field(default_factory=lambda data: data['tilt_status_topic'] is Unset)

    command_callback: Optional[ComponentCallback['Cover']] = ComponentDefaultCallback
    set_position_callback: Optional[ComponentCallback['Cover']] = ComponentDefaultCallback
    tilt_command_callback: Optional[ComponentCallback['Cover']] = ComponentDefaultCallback

    @model_validator(mode='after')
    def _check_position_topic(self) -> Self:
        if 'set_position_topic' in self.model_fields_set and 'position_topic' not in self.model_fields_set:
            raise ValueError('`position_topic` must be set to use `set_position_topic`')
        return self

    def set_state(self, state: Optional[CoverState]) -> None:
        match state:
            case utils.Unset:  # Weird Python `match` wizardry
                self.publish(self.state_topic, 'None')
            case CoverState.CLOSED:
                self.publish(self.state_topic, self.state_closed)
            case CoverState.CLOSING:
                self.publish(self.state_topic, self.state_closing)
            case CoverState.OPEN:
                self.publish(self.state_topic, self.state_open)
            case CoverState.OPENING:
                self.publish(self.state_topic, self.state_opening)
            case CoverState.STOPPED:
                self.publish(self.state_topic, self.state_stopped)

    def set_position(self, position: int) -> None:
        self.publish(self.position_topic, clamp(position, self.position_closed, self.position_open))

    def set_tilt(self, tilt: int) -> None:
        self.publish(self.tilt_status_topic, clamp(tilt, self.tilt_min, self.tilt_max))


class DeviceTracker(StatefulComponent, BareEntityBase):
    platform: Annotated[Platform, Required] = Platform.DEVICE_TRACKER

    payload_home: Optional[str] = 'home'
    payload_not_home: Optional[str] = 'not_home'
    payload_reset: Optional[str] = 'None'
    source_type: Optional[DeviceTrackerSource] = Unset
    state_topic: Optional[StateTopic] = Unset
    value_template: Optional[str] = Unset

    def set_state(self, state: Optional[bool]) -> None:
        self.publish(
            self.state_topic,
            self.payload_reset if state is Unset else (self.payload_home if state else self.payload_not_home)
        )


class DeviceTrigger(StatefulComponent, ComponentBase):
    platform: Annotated[Platform, Required] = Platform.DEVICE_TRIGGER

    automation_type: Annotated[str, Required] = 'trigger'
    payload: Optional[str] = Unset
    qos: Optional[QoS] = QoS.MOST
    topic: StateTopic
    type: DeviceTriggerType | str
    subtype: DeviceTriggerSubtype | str
    value_template: Optional[str] = Unset

    def trigger(self, payload: str) -> None:
        self.publish(self.topic, payload)


class Event(StatefulComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.EVENT

    device_class: Optional[EventClass] = Unset
    event_types: list[str]
    state_topic: StateTopic
    value_template: Optional[str] = Unset

    def trigger(self, type_: str, attr: dict[str, Any] | None = None) -> None:
        if type_ in self.event_types:
            data = {'event_type': type_}
            if attr is not None:
                data.update(attr)
            self.publish(self.state_topic, json.dumps(data))


class Fan(StatefulComponent, CallableComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.FAN

    command_template: Optional[str] = Unset
    command_topic: CommandTopic
    direction_command_template: Optional[str] = Unset
    direction_command_topic: Optional[CommandTopic] = Unset
    direction_state_topic: Optional[StateTopic] = Unset
    direction_value_template: Optional[str] = Unset
    oscillation_command_template: Optional[str] = Unset
    oscillation_command_topic: Optional[CommandTopic] = Unset
    oscillation_state_topic: Optional[StateTopic] = Unset
    oscillation_value_template: Optional[str] = Unset
    payload_off: Optional[str] = 'OFF'
    payload_on: Optional[str] = 'ON'
    payload_oscillation_off: Optional[str] = 'oscillate_off'
    payload_oscillation_on: Optional[str] = 'oscillate_on'
    payload_reset_percentage: Optional[str] = 'None'
    payload_reset_preset_mode: Optional[str] = 'None'
    percentage_command_template: Optional[str] = Unset
    percentage_command_topic: Optional[CommandTopic] = Unset
    percentage_state_topic: Optional[StateTopic] = Unset
    percentage_value_template: Optional[str] = Unset
    preset_mode_command_template: Optional[str] = Unset
    preset_mode_command_topic: Optional[CommandTopic] = Unset
    preset_mode_state_topic: Optional[StateTopic] = Unset
    preset_mode_value_template: Optional[str] = Unset
    preset_modes: Optional[list[str]] = []
    retain: Optional[bool] = True
    speed_range_max: Optional[int] = 100
    speed_range_min: Optional[int] = 1
    state_topic: Optional[StateTopic] = Unset
    state_value_template: Optional[str] = Unset

    # Keep after other fields due to `data` only containing already validated fields
    optimistic: Optional[bool] = Field(default_factory=lambda data: data['state_topic'] is Unset)

    command_callback: Optional[ComponentCallback['Fan']] = ComponentDefaultCallback
    direction_command_callback: Optional[ComponentCallback['Fan']] = ComponentDefaultCallback
    oscillation_command_callback: Optional[ComponentCallback['Fan']] = ComponentDefaultCallback
    percentage_command_callback: Optional[ComponentCallback['Fan']] = ComponentDefaultCallback
    preset_mode_command_callback: Optional[ComponentCallback['Fan']] = ComponentDefaultCallback

    @model_validator(mode='after')
    def _check_preset_modes(self) -> Self:
        if ('preset_modes' in self.model_fields_set) != ('preset_mode_command_topic' in self.model_fields_set):
            raise ValueError('`preset_mode_command_topic` and `preset_modes` must both be set')
        return self

    def set_state(self, state: Optional[bool]) -> None:
        self.publish(self.state_topic, 'None' if state is Unset else (self.payload_on if state else self.payload_off))

    def set_direction(self, direction: bool) -> None:
        self.publish(self.direction_state_topic, 'forward' if direction else 'reverse')

    def set_oscillation(self, oscillation: bool) -> None:
        self.publish(
            self.oscillation_state_topic,
            self.payload_oscillation_on if oscillation else self.payload_oscillation_off
        )

    def set_percentage(self, percentage: Optional[int]) -> None:
        if percentage is Unset:
            self.publish(self.percentage_state_topic, self.payload_reset_percentage)
        else:
            self.publish(self.percentage_state_topic, clamp(percentage, self.speed_range_min, self.speed_range_max))

    def set_mode(self, mode: Optional[str]) -> None:
        if mode is Unset:
            self.publish(self.preset_mode_state_topic, self.payload_reset_preset_mode)
        else:
            self.publish(self.preset_mode_state_topic, mode)


class Humidifier(StatefulComponent, CallableComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.HUMIDIFIER

    action_template: Optional[str] = Unset
    action_topic: Optional[StateTopic] = Unset
    current_humidity_template: Optional[str] = Unset
    current_humidity_topic: Optional[StateTopic] = Unset
    command_template: Optional[str] = Unset
    command_topic: CommandTopic
    device_class: Optional[HumidifierClass | None] = HumidifierClass.HUMIDIFIER
    max_humidity: Optional[float] = 100.0
    min_humidity: Optional[float] = 0.0
    payload_off: Optional[str] = 'OFF'
    payload_on: Optional[str] = 'ON'
    payload_reset_humidity: Optional[str] = 'None'
    payload_reset_mode: Optional[str] = 'None'
    target_humidity_command_template: Optional[str] = Unset
    target_humidity_command_topic: CommandTopic
    target_humidity_state_topic: Optional[StateTopic] = Unset
    target_humidity_state_template: Optional[str] = Unset
    mode_command_template: Optional[str] = Unset
    mode_command_topic: Optional[CommandTopic] = Unset
    mode_state_topic: Optional[StateTopic] = Unset
    mode_state_template: Optional[str] = Unset
    modes: Optional[list[HumidifierMode | str]] = []
    retain: Optional[bool] = True
    state_topic: Optional[StateTopic] = Unset
    state_value_template: Optional[str] = Unset

    # Keep after other fields due to `data` only containing already validated fields
    optimistic: Optional[bool] = Field(default_factory=lambda data: data['state_topic'] is Unset)

    command_callback: Optional[ComponentCallback['Humidifier']] = ComponentDefaultCallback
    target_humidity_command_callback: Optional[ComponentCallback['Humidifier']] = ComponentDefaultCallback
    mode_command_callback: Optional[ComponentCallback['Humidifier']] = ComponentDefaultCallback

    @model_validator(mode='after')
    def _check_modes(self) -> Self:
        if ('modes' in self.model_fields_set) == (self.mode_command_topic is Unset):
            raise ValueError('`mode_command_topic` and `modes` must both be set')
        return self

    def set_state(self, state: Optional[bool]) -> None:
        self.publish(self.state_topic, 'None' if state is Unset else (self.payload_on if state else self.payload_off))

    def set_action(self, action: HumidifierAction) -> None:
        self.publish(self.action_topic, str(action))

    def set_current_humidity(self, humidity: Optional[float]) -> None:
        if humidity is Unset:
            self.publish(self.target_humidity_state_topic, self.payload_reset_humidity)
        else:
            # Clamp to valid humidity values
            self.publish(self.current_humidity_topic, clamp(humidity, 0.0, 100.0))

    def set_target_humidity(self, humidity: Optional[float]) -> None:
        if humidity is Unset:
            self.publish(self.target_humidity_state_topic, self.payload_reset_humidity)
        else:
            self.publish(self.target_humidity_state_topic, clamp(humidity, self.min_humidity, self.max_humidity))

    def set_mode(self, mode: Optional[HumidifierMode | str]) -> None:
        if mode is Unset:
            self.publish(self.target_humidity_state_topic, self.payload_reset_mode)
        else:
            self.publish(self.mode_state_topic, str(mode))


class Image(StatefulComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.IMAGE

    content_type: Optional[str] = 'image/jpeg'
    image_encoding: Optional[ImageEncoding] = ImageEncoding.BINARY
    image_topic: Optional[StateTopic] = Unset
    url_template: Optional[str] = Unset
    url_topic: Optional[StateTopic] = Unset

    @model_validator(mode='after')
    def _check_content_type_mutex(self) -> Self:
        if 'image_topic' in self.model_fields_set and 'url_topic' in self.model_fields_set:
            raise ValueError('`image_topic` and `url_topic` are mutually exclusive')
        if 'image_topic' not in self.model_fields_set and 'url_topic' not in self.model_fields_set:
            raise ValueError('One of `image_topic` or `url_topic` must be set')
        return self

    def _on_init(self, mqtt: MQTTClient) -> None:
        super()._on_init(mqtt)

        if self.image_encoding == ImageEncoding.BINARY and 'image_encoding' in self.model_fields_set:
            self.__pydantic_fields_set__.remove('image_encoding')

    def set_image(self, data: str | bytes | bytearray) -> None:
        self.publish(self.image_topic, data)

    def set_url(self, url: AnyUrl) -> None:
        self.publish(self.url_topic, str(url))


class HVAC(StatefulComponent, CallableComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.HVAC

    action_template: Optional[str] = Unset
    action_topic: Optional[StateTopic] = Unset
    current_humidity_template: Optional[str] = Unset
    current_humidity_topic: Optional[StateTopic] = Unset
    current_temperature_template: Optional[str] = Unset
    current_temperature_topic: Optional[StateTopic] = Unset
    fan_mode_command_template: Optional[str] = Unset
    fan_mode_command_topic: Optional[CommandTopic] = Unset
    fan_mode_state_template: Optional[str] = Unset
    fan_mode_state_topic: Optional[StateTopic] = Unset
    fan_modes: Optional[list[HVACFanMode | str]] = [
        HVACFanMode.AUTO, HVACFanMode.LOW, HVACFanMode.MEDIUM, HVACFanMode.HIGH
    ]
    max_humidity: Optional[float] = 99
    min_humidity: Optional[float] = 30
    mode_command_template: Optional[str] = Unset
    mode_command_topic: Optional[CommandTopic] = Unset
    mode_state_template: Optional[str] = Unset
    mode_state_topic: Optional[StateTopic] = Unset
    modes: Optional[list[HVACMode]] = [
        HVACMode.AUTO, HVACMode.OFF, HVACMode.COOL, HVACMode.HEAT, HVACMode.DRY, HVACMode.FAN_ONLY
    ]
    optimistic: Optional[bool] = False
    payload_off: Optional[str] = 'OFF'
    payload_on: Optional[str] = 'ON'
    power_command_template: Optional[str] = Unset
    power_command_topic: Optional[CommandTopic] = Unset
    preset_mode_command_template: Optional[str] = Unset
    preset_mode_command_topic: Optional[CommandTopic] = Unset
    preset_mode_state_topic: Optional[StateTopic] = Unset
    preset_mode_value_template: Optional[str] = Unset
    preset_modes: Optional[list[HVACPresetMode | str]] = []
    retain: Optional[bool] = False
    swing_horizontal_mode_command_template: Optional[str] = Unset
    swing_horizontal_mode_command_topic: Optional[CommandTopic] = Unset
    swing_horizontal_mode_state_template: Optional[str] = Unset
    swing_horizontal_mode_state_topic: Optional[StateTopic] = Unset
    swing_horizontal_modes: Optional[list[str]] = ['on', 'off']
    swing_mode_command_template: Optional[str] = Unset
    swing_mode_command_topic: Optional[CommandTopic] = Unset
    swing_mode_state_template: Optional[str] = Unset
    swing_mode_state_topic: Optional[StateTopic] = Unset
    swing_modes: Optional[list[str]] = ['on', 'off']
    target_humidity_command_template: Optional[str] = Unset
    target_humidity_command_topic: Optional[CommandTopic] = Unset
    target_humidity_state_topic: Optional[StateTopic] = Unset
    target_humidity_state_template: Optional[str] = Unset
    temperature_command_template: Optional[str] = Unset
    temperature_command_topic: Optional[CommandTopic] = Unset
    temperature_high_command_template: Optional[str] = Unset
    temperature_high_command_topic: Optional[CommandTopic] = Unset
    temperature_high_state_template: Optional[str] = Unset
    temperature_high_state_topic: Optional[StateTopic] = Unset
    temperature_low_command_template: Optional[str] = Unset
    temperature_low_command_topic: Optional[CommandTopic] = Unset
    temperature_low_state_template: Optional[str] = Unset
    temperature_low_state_topic: Optional[StateTopic] = Unset
    temperature_state_template: Optional[str] = Unset
    temperature_state_topic: Optional[StateTopic] = Unset
    temperature_unit: Optional[TemperatureUnit] = Unset  # TODO: Unset is system unit. How will we set default then?
    temp_step: Optional[float] = 1.0
    value_template: Optional[str] = Unset

    # Keep after other fields due to `data` only containing already validated fields
    initial: Optional[float] = Field(
        default_factory=lambda data: 21.0 if data['temperature_unit'] == TemperatureUnit.CELSIUS else 69.8)
    max_temp: Optional[float] = Field(
        default_factory=lambda data: 35.0 if data['temperature_unit'] == TemperatureUnit.CELSIUS else 95.0)
    min_temp: Optional[float] = Field(
        default_factory=lambda data: 7.0 if data['temperature_unit'] == TemperatureUnit.CELSIUS else 44.6)
    precision: Optional[Precision] = Field(
        default_factory=lambda data: Precision.HIGH if data['temperature_unit'] == TemperatureUnit.CELSIUS
        else Precision.LOW)

    fan_mode_command_callback: Optional[ComponentCallback['HVAC']] = ComponentDefaultCallback
    mode_command_callback: Optional[ComponentCallback['HVAC']] = ComponentDefaultCallback
    power_command_callback: Optional[ComponentCallback['HVAC']] = ComponentDefaultCallback
    preset_mode_command_callback: Optional[ComponentCallback['HVAC']] = ComponentDefaultCallback
    swing_horizontal_mode_command_callback: Optional[ComponentCallback['HVAC']] = ComponentDefaultCallback
    swing_mode_command_callback: Optional[ComponentCallback['HVAC']] = ComponentDefaultCallback
    target_humidity_command_callback: Optional[ComponentCallback['HVAC']] = ComponentDefaultCallback
    temperature_command_callback: Optional[ComponentCallback['HVAC']] = ComponentDefaultCallback
    temperature_high_command_callback: Optional[ComponentCallback['HVAC']] = ComponentDefaultCallback
    temperature_low_command_callback: Optional[ComponentCallback['HVAC']] = ComponentDefaultCallback

    @model_validator(mode='after')
    def _check_preset_modes(self) -> Self:
        if ('preset_modes' in self.model_fields_set) != ('preset_mode_command_topic' in self.model_fields_set):
            raise ValueError('`preset_mode_command_topic` and `preset_modes` must both be set')
        return self

    def set_action(self, action: HVACAction) -> None:
        self.publish(self.action_topic, str(action))

    def set_current_humidity(self, humidity: Optional[float]) -> None:
        self.publish(self.current_humidity_topic, 'None' if humidity is Unset else clamp(humidity, 0.0, 100.0))

    def set_current_temperature(self, temperature: Optional[float]) -> None:
        self.publish(self.current_temperature_topic, 'None' if temperature is Unset else temperature)

    def set_fan_mode(self, mode: Optional[HVACFanMode | str]) -> None:
        self.publish(self.fan_mode_state_topic, 'None' if mode is Unset else str(mode))

    # This must be called after a `power_command_topic` update because it is not optimistic
    def set_mode(self, mode: Optional[HVACMode]) -> None:
        self.publish(self.mode_state_topic, 'None' if mode is Unset else str(mode))

    def set_preset_mode(self, mode: Optional[HVACPresetMode | str]) -> None:
        self.publish(self.preset_mode_state_topic, 'None' if mode is Unset else str(mode))

    def set_swing_horizontal_mode(self, mode: str) -> None:
        self.publish(self.swing_horizontal_mode_state_topic, mode)

    def set_swing_mode(self, mode: str) -> None:
        self.publish(self.swing_mode_state_topic, mode)

    def set_target_humidity(self, humidity: Optional[float]) -> None:
        self.publish(
            self.target_humidity_state_topic,
            'None' if humidity is Unset else clamp(humidity, self.min_humidity, self.max_humidity)
        )

    def set_high_temperature(self, temperature: float) -> None:
        self.publish(self.temperature_high_state_topic, temperature)

    def set_low_temperature(self, temperature: float) -> None:
        self.publish(self.temperature_low_state_topic, temperature)

    def set_target_temperature(self, temperature: Optional[float]) -> None:
        self.publish(self.temperature_state_topic, 'None' if temperature is Unset else temperature)


class LawnMower(StatefulComponent, CallableComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.LAWN_MOWER

    activity_state_topic: Optional[StateTopic] = Unset
    activity_value_template: Optional[str] = Unset
    dock_command_template: Optional[str] = Unset
    dock_command_topic: Optional[CommandTopic] = Unset
    pause_command_template: Optional[str] = Unset
    pause_command_topic: Optional[CommandTopic] = Unset
    start_mowing_template: Optional[str] = Unset
    start_mowing_command_topic: Optional[CommandTopic] = Unset
    retain: Optional[bool] = False

    # Keep after other fields due to `data` only containing already validated fields
    optimistic: Optional[bool] = Field(default_factory=lambda data: data['activity_state_topic'] is Unset)

    dock_command_callback: Optional[ComponentCallback['LawnMower']] = ComponentDefaultCallback
    pause_command_callback: Optional[ComponentCallback['LawnMower']] = ComponentDefaultCallback
    start_mowing_command_callback: Optional[ComponentCallback['LawnMower']] = ComponentDefaultCallback

    def set_state(self, state: Optional[LawnMowerState]) -> None:
        # TODO: Docs say `none` not `None`
        self.publish(self.activity_state_topic, 'None' if state is Unset else str(state))


class Light(StatefulComponent, CallableComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.LIGHT

    brightness: Optional[bool] = False  # TODO: It's supposed to scale RGB, RGBW and RGBWW lights????
    brightness_scale: Optional[int] = 255
    color_temp_kelvin: Optional[bool] = False
    command_topic: CommandTopic
    effect: Optional[bool] = False
    effect_list: Optional[list[str] | str] = Unset
    flash_time_long: Optional[int] = 10
    flash_time_short: Optional[int] = 2
    max_kelvin: Optional[int] = 6535
    max_mireds: Optional[int] = Unset
    min_kelvin: Optional[int] = 2000
    min_mireds: Optional[int] = Unset
    retain: Optional[bool] = False
    schema_: Annotated[str, Field(serialization_alias='schema'), Required] = 'json'
    state_topic: Optional[StateTopic] = Unset
    supported_color_modes: list[LightColorMode]
    white_scale: Optional[int] = 255

    # Keep after other fields due to `data` only containing already validated fields
    optimistic: Optional[bool] = Field(default_factory=lambda data: data['state_topic'] is Unset)

    command_callback: Optional[ComponentCallback['Light']] = ComponentDefaultCallback

    @field_validator('supported_color_modes', mode='after')
    @classmethod
    def _check_supported_color_modes(cls, value: list[LightColorMode]) -> list[LightColorMode]:
        if LightColorMode.ONOFF in value and len(value) > 1:
            raise ValueError(f"Supported color mode {LightColorMode.ONOFF} is exclusive")
        if LightColorMode.BRIGHTNESS in value and len(value) > 1:
            raise ValueError(f"Supported color mode {LightColorMode.BRIGHTNESS} is exclusive")
        return value

    def set_state(
            self, state: Optional[bool],
            color_mode: LightColorMode | None = None,
            color: tuple[int | float, ...] | None = None,
            brightness: int | None = None,
            color_temp: int | None = None,
            effect: str | None = None
    ) -> None:
        data: dict[str, Any] = {'state': None if state is Unset else ('ON' if state else 'OFF')}  # Make linter happy
        if color_mode is not None:
            data['color_mode'] = str(color_mode)
            if color is not None:
                match color_mode:
                    case LightColorMode.HS:
                        data['color'] = {
                            'h': clamp(color[0], 0.0, 360.0),
                            's': clamp(color[1], 0.0, 100.0)
                        }
                    case LightColorMode.XY:
                        data['color'] = {
                            'x': clamp(color[0], 0.0, 0.8),
                            'y': clamp(color[1], 0.0, 0.9)
                        }
                    case LightColorMode.RGB:
                        data['color'] = {
                            'r': clamp(color[0], 0, 255),
                            'g': clamp(color[1], 0, 255),
                            'b': clamp(color[2], 0, 255)
                        }
                    case LightColorMode.RGBW:
                        data['color'] = {
                            'r': clamp(color[0], 0, 255),
                            'g': clamp(color[1], 0, 255),
                            'b': clamp(color[2], 0, 255),
                            'w': clamp(color[3], 0, 255)
                        }
                    case LightColorMode.RGBWW:
                        data['color'] = {
                            'r': clamp(color[0], 0, 255),
                            'g': clamp(color[1], 0, 255),
                            'b': clamp(color[2], 0, 255),
                            'c': clamp(color[3], 0, 255),
                            'w': clamp(color[4], 0, 255)
                        }
        if brightness is not None:
            data['brightness'] = clamp(brightness, 0, self.brightness_scale)
        if color_temp is not None:
            if self.color_temp_kelvin:
                data['color_temp'] = clamp(color_temp, self.min_kelvin, self.max_kelvin)
            else:
                if self.min_mireds is not Unset:
                    color_temp = max(color_temp, self.min_kelvin)
                if self.max_mireds is not Unset:
                    color_temp = min(color_temp, self.max_kelvin)
                data['color_temp'] = color_temp
        if effect is not None:
            data['effect'] = effect
        self.publish(self.state_topic, json.dumps(data))


class Lock(StatefulComponent, CallableComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.LOCK

    code_format: Optional[str] = Unset
    command_template: Optional[str] = Unset
    command_topic: CommandTopic
    payload_lock: Optional[str] = 'LOCK'
    payload_unlock: Optional[str] = 'UNLOCK'
    payload_open: Optional[str] = Unset
    payload_reset: Optional[str] = 'None'
    retain: Optional[bool] = False
    state_jammed: Optional[str] = 'JAMMED'
    state_locked: Optional[str] = 'LOCKED'
    state_locking: Optional[str] = 'LOCKING'
    state_topic: Optional[StateTopic] = Unset
    state_unlocked: Optional[str] = 'UNLOCKED'
    state_unlocking: Optional[str] = 'UNLOCKING'
    value_template: Optional[str] = Unset

    optimistic: Optional[bool] = Field(default_factory=lambda data: data['state_topic'] is Unset)

    command_callback: Optional[ComponentCallback['Lock']] = ComponentDefaultCallback

    def set_state(self, state: Optional[LockState]) -> None:
        match state:
            case utils.Unset:  # Weird Python `match` wizardry
                self.publish(self.state_topic, 'None')
            case LockState.JAMMED:
                self.publish(self.state_topic, self.state_jammed)
            case LockState.LOCKED:
                self.publish(self.state_topic, self.state_locked)
            case LockState.LOCKING:
                self.publish(self.state_topic, self.state_locking)
            case LockState.UNLOCKED:
                self.publish(self.state_topic, self.state_unlocked)
            case LockState.UNLOCKING:
                self.publish(self.state_topic, self.state_unlocking)


class Notify(CallableComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.NOTIFY

    command_template: Optional[str] = Unset
    command_topic: Optional[CommandTopic] = Unset
    retain: Optional[bool] = False

    command_callback: Optional[ComponentCallback['Notify']] = ComponentDefaultCallback


class Number(StatefulComponent, CallableComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.NUMBER

    command_template: Optional[str] = Unset
    command_topic: CommandTopic
    device_class: Optional[NumberClass | None] = Unset
    min: Optional[float] = 1.0
    max: Optional[float] = 100.0
    mode: Optional[NumberMode] = NumberMode.AUTO
    payload_reset: Optional[str] = 'None'
    retain: Optional[bool] = False
    state_topic: Optional[StateTopic] = Unset
    step: Optional[float] = Field(default=1.0, ge=0.001)
    unit_of_measurement: Optional[str | None] = Unset
    value_template: Optional[str] = Unset

    # Keep after other fields due to `data` only containing already validated fields
    optimistic: Optional[bool] = Field(default_factory=lambda data: data['state_topic'] is Unset)

    command_callback: Optional[ComponentCallback['Number']] = ComponentDefaultCallback

    def set_number(self, value: float | int) -> None:
        self.publish(self.state_topic, clamp(value, self.min, self.max))


class Scene(CallableComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.SCENE

    command_topic: Optional[CommandTopic] = Unset
    payload_on: Optional[str] = 'ON'
    retain: Optional[bool] = False

    command_callback: Optional[ComponentCallback['Scene']] = ComponentDefaultCallback


class Select(StatefulComponent, CallableComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.SELECT

    command_template: Optional[str] = Unset
    command_topic: CommandTopic
    options: list[str]
    retain: Optional[bool] = False
    state_topic: Optional[StateTopic] = Unset
    value_template: Optional[str] = Unset

    command_callback: Optional[ComponentCallback['Select']] = ComponentDefaultCallback

    # Keep after other fields due to `data` only containing already validated fields
    optimistic: Optional[bool] = Field(default_factory=lambda data: data['state_topic'] is Unset)

    def set_option(self, value: str) -> None:
        if value in self.options:
            self.publish(self.state_topic, value)

    def set_index(self, index: int) -> None:
        if 0 <= index < len(self.options):
            self.publish(self.state_topic, self.options[index])


class Sensor(StatefulComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.SENSOR

    device_class: Optional[SensorClass | None] = Unset
    expire_after: Optional[int] = 0
    force_update: Optional[bool] = False
    last_reset_value_template: Optional[str] = Unset
    options: Optional[conlist(str, min_length=1)] = Unset
    suggested_display_precision: Optional[int] = Unset
    state_class: Optional[SensorStateClass] = Unset
    state_topic: StateTopic
    unit_of_measurement: Optional[str | None] = Unset
    value_template: Optional[str] = Unset

    @model_validator(mode='after')
    def _check_stuff(self) -> Self:
        if self.last_reset_value_template is not Unset and self.device_class != SensorStateClass.TOTAL:
            raise ValueError('State class must be `total` when `last_reset_value_template` is set')
        if self.options is not Unset:
            if self.device_class != SensorClass.ENUM:
                raise ValueError('Device class must be `enum` when `options` is set')
            if self.state_class is not Unset:
                raise ValueError('`state_class` and `options` are mutually exclusive')
            if self.unit_of_measurement is not Unset:
                raise ValueError('`unit_of_measurement` and `options` are mutually exclusive')
        return self

    def set_value(self, value: Optional[float | int | str]) -> None:
        self.publish(self.state_topic, 'None' if value is Unset else value)


class Siren(StatefulComponent, CallableComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.SIREN

    available_tones: Optional[list[str]] = Unset
    command_template: Optional[str] = Unset
    command_off_template: Optional[str] = Unset
    command_topic: CommandTopic
    payload_off: Optional[str] = 'OFF'
    payload_on: Optional[str] = 'ON'
    retain: Optional[bool] = False
    state_topic: Optional[StateTopic] = Unset
    state_value_template: Optional[str] = Unset
    support_duration: Optional[bool] = True
    support_volume_set: Optional[bool] = True

    # Keep after other fields due to `data` only containing already validated fields
    optimistic: Optional[bool] = Field(default_factory=lambda data: data['state_topic'] is Unset)
    state_off: Optional[str] = Field(
        default_factory=lambda data: 'OFF' if data['payload_off'] is Unset else data['payload_off'])
    state_on: Optional[str] = Field(
        default_factory=lambda data: 'ON' if data['payload_on'] is Unset else data['payload_on'])

    command_callback: Optional[ComponentCallback['Siren']] = ComponentDefaultCallback

    def set_state(
            self,
            state: Optional[bool],
            tone: str | None = None,
            duration: int | None = None,
            volume: float | None = None
    ) -> None:
        data = {'state': None if state is Unset else state}
        if tone is not None and self.available_tones is not Unset and tone in self.available_tones:
            data['tone'] = tone
        if duration is not None and self.support_duration:
            data['duration'] = max(duration, 0)
        if volume is not None and self.support_volume_set:
            data['volume_level'] = clamp(volume, 0.0, 1.0)
        self.publish(self.state_topic, json.dumps(data))


class Switch(StatefulComponent, CallableComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.SWITCH

    command_template: Optional[str] = Unset
    command_topic: CommandTopic
    device_class: Optional[SwitchClass | None] = Unset
    payload_off: Optional[str] = 'OFF'
    payload_on: Optional[str] = 'ON'
    retain: Optional[bool] = False
    state_topic: Optional[StateTopic] = Unset
    value_template: Optional[str] = Unset

    # Keep after other fields due to `data` only containing already validated fields
    optimistic: Optional[bool] = Field(default_factory=lambda data: data['state_topic'] is Unset)
    state_off: Optional[str] = Field(
        default_factory=lambda data: 'OFF' if data['payload_off'] is Unset else data['payload_off'])
    state_on: Optional[str] = Field(
        default_factory=lambda data: 'ON' if data['payload_on'] is Unset else data['payload_on'])

    command_callback: Optional[ComponentCallback['Switch']] = ComponentDefaultCallback

    def set_state(self, state: Optional[bool]) -> None:
        self.publish(self.state_topic, 'None' if state is Unset else (self.payload_on if state else self.payload_off))


class Update(StatefulComponent, CallableComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.UPDATE

    command_topic: Optional[CommandTopic] = Unset
    device_class: Optional[UpdateClass | None] = Unset
    display_precision: Optional[int] = 0
    latest_version_template: Optional[str] = Unset
    latest_version_topic: Optional[StateTopic] = Unset
    payload_install: Optional[str] = Unset
    release_summary: Optional[constr(max_length=255)] = Unset
    release_url: Optional[AnyUrl] = Unset
    retain: Optional[bool] = False
    state_topic: StateTopic
    title: Optional[str] = Unset
    value_template: Optional[str] = Unset

    command_callback: Optional[ComponentCallback['Update']] = ComponentDefaultCallback

    def set_state(
            self,
            installed: str,
            latest: str | None = None,
            title: str | None = None,
            summary: str | None = None,
            url: AnyUrl | None = None,
            picture: AnyUrl | None = None,
            in_progress: bool | None = None,
            percentage: float | None = None
    ) -> None:
        data: dict[str, Any] = {'installed_version': installed}  # Make linter happy
        if latest is not None:
            data['latest_version'] = latest
        if title is not None:
            data['title'] = title
        if summary is not None:
            data['release_summary'] = summary[:255]  # Assume same limit exists here?
        if url is not None:
            data['release_url'] = url
        if picture is not None:
            data['entity_picture'] = picture
        if in_progress is not None:
            data['in_progress'] = in_progress
        if percentage is not None:
            data['update_percentage'] = clamp(percentage, 0.0, 100.0)
        self.publish(self.state_topic, json.dumps(data))


class TagScanner(StatefulComponent, ComponentBase):
    platform: Annotated[Platform, Required] = Platform.TAG_SCANNER

    topic: StateTopic
    value_template: Optional[str] = Unset

    # TODO: NFC stuff is outside the scope of this library. Maybe some helper method will be implemented in the future.
    def set_state(self, data: str) -> None:
        self.publish(self.topic, data)


class Text(StatefulComponent, CallableComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.TEXT

    command_template: Optional[str] = Unset
    command_topic: CommandTopic
    max: Optional[int] = Field(default=255, gt=0)
    min: Optional[int] = Field(default=0, ge=0)
    mode: Optional[TextMode] = TextMode.TEXT
    pattern: Optional[Regex] = Unset
    retain: Optional[bool] = False
    state_topic: Optional[StateTopic] = Unset
    value_template: Optional[str] = Unset

    command_callback: Optional[ComponentCallback['Text']] = ComponentDefaultCallback

    @model_validator(mode='after')
    def _check_min_max(self) -> Self:
        if self.max <= self.min:
            raise ValueError('`max` must be larger than `min`')
        return self

    def set_text(self, text: str) -> None:
        if self.min <= len(text) <= self.max:
            if self.pattern is not Unset and not re.match(self.pattern, text):
                return
            self.publish(self.state_topic, text)


class Vacuum(StatefulComponent, CallableComponent, BareEntityBase):
    platform: Annotated[Platform, Required] = Platform.VACUUM

    command_topic: Optional[CommandTopic] = Unset
    encoding: Optional[str] = 'utf-8'
    fan_speed_list: Optional[list[str] | str] = Unset
    payload_clean_spot: Optional[str] = 'clean_spot'
    payload_locate: Optional[str] = 'locate'
    payload_pause: Optional[str] = 'pause'
    payload_return_to_base: Optional[str] = 'return_to_base'
    payload_start: Optional[str] = 'start'
    payload_stop: Optional[str] = 'stop'
    retain: Optional[bool] = False
    send_command_topic: Optional[CommandTopic] = Unset
    set_fan_speed_topic: Optional[CommandTopic] = Unset
    state_topic: Optional[StateTopic] = Unset
    supported_features: Optional[list[VacuumFeature] | VacuumFeature] = [
        VacuumFeature.START, VacuumFeature.STOP, VacuumFeature.RETURN_HOME,
        VacuumFeature.STATUS, VacuumFeature.BATTERY, VacuumFeature.CLEAN_SPOT
    ]

    command_callback: Optional[ComponentCallback['Vacuum']] = ComponentDefaultCallback
    send_command_callback: Optional[ComponentCallback['Vacuum']] = ComponentDefaultCallback
    set_fan_speed_callback: Optional[ComponentCallback['Vacuum']] = ComponentDefaultCallback

    def set_state(
            self,
            state: Optional[VacuumState],
            battery_level: int | None = None,
            fan_speed: VacuumFanSpeed | None = None
    ) -> None:
        data: dict[str, Any] = {'state': None if state is Unset else str(state)}  # Make linter happy
        if battery_level is not None and VacuumFeature.BATTERY in self.supported_features:
            data['battery_level'] = clamp(battery_level, 0, 100)
        if fan_speed is not None and VacuumFeature.FAN_SPEED in self.supported_features:
            data['fan_speed'] = str(fan_speed)
        self.publish(self.state_topic, json.dumps(data))


class Valve(StatefulComponent, CallableComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.VALVE

    command_template: Optional[str] = Unset
    command_topic: Optional[CommandTopic] = Unset
    device_class: Optional[ValveClass | None] = Unset
    payload_stop: Optional[str] = Unset
    position_closed: Optional[int] = Field(default=0, ge=0)
    position_open: Optional[int] = Field(default=100, ge=0)
    reports_position: Optional[bool] = False
    retain: Optional[bool] = False
    state_closing: Optional[str] = 'closing'
    state_opening: Optional[str] = 'opening'
    state_topic: Optional[StateTopic] = Unset
    value_template: Optional[str] = Unset

    # Keep after other fields due to `data` only containing already validated fields
    optimistic: Optional[bool] = Field(
        default_factory=lambda data: data['state_topic'] is Unset)  # There is no position topic. Docs are wrong
    payload_close: Optional[str | None] = Field(
        default_factory=lambda data: Unset if data['reports_position'] else 'CLOSE')
    payload_open: Optional[str | None] = Field(
        default_factory=lambda data: Unset if data['reports_position'] else 'OPEN')
    state_closed: Optional[str] = Field(
        default_factory=lambda data: Unset if data['reports_position'] else 'closed')
    state_open: Optional[str] = Field(
        default_factory=lambda data: Unset if data['reports_position'] else 'open')

    command_callback: Optional[ComponentCallback['Valve']] = ComponentDefaultCallback

    @model_validator(mode='after')
    def _check_stuff(self) -> Self:
        if self.reports_position:
            if self.payload_close is not Unset:
                raise ValueError('`payload_close` and `reports_position` are mutually exclusive')
            if self.payload_open is not Unset:
                raise ValueError('`payload_open` and `reports_position` are mutually exclusive')
            if self.state_closed is not Unset:
                raise ValueError('`state_closed` and `reports_position` are mutually exclusive')
            if self.state_open is not Unset:
                raise ValueError('`state_open` and `reports_position` are mutually exclusive')
        return self

    def set_position(
            self,
            position: Optional[int],
            state: Literal[ValveState.OPENING, ValveState.CLOSING] | None = None
    ) -> None:
        if self.reports_position:
            if position is Unset:
                self.publish(self.state_topic, 'None')
            else:
                data = {'position': clamp(position, self.position_closed, self.position_open)}
                match state:
                    case ValveState.OPENING:
                        data['state'] = self.state_opening
                    case ValveState.CLOSING:
                        data['state'] = self.state_closing
                self.publish(self.state_topic, json.dumps(data))

    def set_state(self, state: Optional[ValveState]) -> None:
        match state:
            case utils.Unset:
                self.publish(self.state_topic, 'None')
            case ValveState.OPEN:
                self.publish(self.state_topic, self.state_open)
            case ValveState.OPENING:
                self.publish(self.state_topic, self.state_opening)
            case ValveState.CLOSED:
                self.publish(self.state_topic, self.state_closed)
            case ValveState.CLOSING:
                self.publish(self.state_topic, self.state_closing)


class WaterHeater(StatefulComponent, CallableComponent, EntityBase):
    platform: Annotated[Platform, Required] = Platform.WATER_HEATER

    current_temperature_template: Optional[str] = Unset
    current_temperature_topic: Optional[StateTopic] = Unset
    # Default values are floats and depend on temperature units. The user can only set an integer temperature
    # It would be auto-generated if it didn't complicate typing.
    initial: Optional[int] = Unset
    mode_command_template: Optional[str] = Unset
    mode_command_topic: Optional[CommandTopic] = Unset
    mode_state_template: Optional[str] = Unset
    mode_state_topic: Optional[StateTopic] = Unset
    modes: Optional[list[WaterHeaterMode]] = [
        WaterHeaterMode.OFF, WaterHeaterMode.ECO, WaterHeaterMode.ELECTRIC, WaterHeaterMode.GAS,
        WaterHeaterMode.HEAT_PUMP, WaterHeaterMode.HIGH_DEMAND, WaterHeaterMode.PERFORMANCE
    ]
    optimistic: Optional[bool] = False
    payload_off: Optional[str] = 'OFF'
    payload_on: Optional[str] = 'ON'
    power_command_template: Optional[str] = Unset
    power_command_topic: Optional[CommandTopic] = Unset
    retain: Optional[bool] = False
    temperature_command_template: Optional[str] = Unset
    temperature_command_topic: Optional[CommandTopic] = Unset
    temperature_state_template: Optional[str] = Unset
    temperature_state_topic: Optional[StateTopic] = Unset
    temperature_unit: Optional[TemperatureUnit] = Unset
    value_template: Optional[str] = Unset

    # Keep after other fields due to `data` only containing already validated fields
    max_temp: Optional[float] = Field(
        default_factory=lambda data: 60.0 if data['temperature_unit'] == TemperatureUnit.CELSIUS else 140.0)
    min_temp: Optional[float] = Field(
        default_factory=lambda data: 43.3 if data['temperature_unit'] == TemperatureUnit.CELSIUS else 110.0)
    precision: Optional[Precision] = Field(
        default_factory=lambda data: Precision.HIGH if data['temperature_unit'] == TemperatureUnit.CELSIUS
        else Precision.LOW)

    mode_command_callback: Optional[ComponentCallback['WaterHeater']] = ComponentDefaultCallback
    power_command_callback: Optional[ComponentCallback['WaterHeater']] = ComponentDefaultCallback
    temperature_command_callback: Optional[ComponentCallback['WaterHeater']] = ComponentDefaultCallback

    def set_current_temperature(self, temperature: Optional[float]) -> None:
        self.publish(self.current_temperature_topic, 'None' if temperature is Unset else temperature)

    def set_mode(self, mode: Optional[WaterHeaterMode]) -> None:
        if mode is Unset:
            self.publish(self.mode_command_topic, 'None')
        elif mode in self.modes:
            self.publish(self.mode_command_topic, str(mode))

    def set_target_temperature(self, temperature: Optional[float]) -> None:
        self.publish(self.temperature_state_topic, 'None' if temperature is Unset else temperature)
