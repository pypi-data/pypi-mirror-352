#  SPDX-License-Identifier: AGPL-3.0-or-later
#  Copyright (C) 2025  Dionisis Toulatos

from enum import Enum, StrEnum


# Components
class Platform(StrEnum):
    """The platform identifying each Home Assistant component supported by the MQTT integration."""

    ALARM_CONTROL_PANEL = "alarm_control_panel"
    BINARY_SENSOR = 'binary_sensor'
    BUTTON = 'button'
    CAMERA = 'camera'
    COVER = 'cover'
    DEVICE_TRACKER = 'device_tracker'
    DEVICE_TRIGGER = 'device_automation'
    EVENT = 'event'
    FAN = 'fan'
    HUMIDIFIER = 'humidifier'
    IMAGE = 'image'
    CLIMATE = 'climate'
    HVAC = 'climate'
    LAWN_MOWER = 'lawn_mower'
    LIGHT = 'light'
    LOCK = 'lock'
    NOTIFY = 'notify'
    NUMBER = 'number'
    SCENE = 'scene'
    SELECT = 'select'
    SENSOR = 'sensor'
    SIREN = 'siren'
    SWITCH = 'switch'
    UPDATE = 'update'
    TAG_SCANNER = 'tag_scanner'
    TEXT = 'text'
    VACUUM = 'vacuum'
    VALVE = 'valve'
    WATER_HEATER = 'water_heater'


class Category(Enum):
    """The category of a component inside the device."""

    NORMAL = None
    """The default category in Home Assistant when not specified.
    
    A component of this category is actively providing useful information about the functionality of the device.
    """
    CONFIG = 'config'
    """The component configures the device in some way
    
    A component of this category represents a configuration state in a device and not a measurement or action.
    """
    DIAGNOSTIC = 'diagnostic'
    """The component is only for diagnostic purposes.
    
    A component of this category represents a state or action of the underlying system in the device.
    """


# Device Classes
class BinarySensorClass(StrEnum):
    NONE = 'None'
    BATTERY = 'battery'
    BATTERY_CHARGING = 'battery_charging'
    CARBON_MONOXIDE = 'carbon_monoxide'
    COLD = 'cold'
    CONNECTIVITY = 'connectivity'
    DOOR = 'door'
    GARAGE_DOOR = 'garage_door'
    GAS = 'gas'
    HEAT = 'heat'
    LIGHT = 'light'
    LOCK = 'lock'
    MOISTURE = 'moisture'
    MOTION = 'motion'
    MOVING = 'moving'
    OCCUPANCY = 'occupancy'
    OPENING = 'opening'
    PLUG = 'plug'
    POWER = 'power'
    PRESENCE = 'presence'
    PROBLEM = 'problem'
    RUNNING = 'running'
    SAFETY = 'safety'
    SMOKE = 'smoke'
    SOUND = 'sound'
    TAMPER = 'tamper'
    UPDATE = 'update'
    VIBRATION = 'vibration'
    WINDOW = 'window'


class ButtonClass(Enum):
    NONE = None
    IDENTIFY = 'identify'
    RESTART = 'restart'
    UPDATE = 'update'


class CoverClass(Enum):
    NONE = None
    AWNING = 'awning'
    BLIND = 'blind'
    CURTAIN = 'curtain'
    DAMPER = 'damper'
    DOOR = 'door'
    GARAGE = 'garage'
    GATE = 'gate'
    SHADE = 'shade'
    SHUTTER = 'shutter'
    WINDOW = 'window'


class EventClass(StrEnum):
    NONE = 'None'
    BUTTON = 'button'
    DOORBELL = 'doorbell'
    MOTION = 'motion'


class HumidifierClass(Enum):
    NONE = None
    HUMIDIFIER = 'humidifier'
    DEHUMIDIFIER = 'dehumidifier'


class NumberClass(StrEnum):
    NONE = 'None'
    APPARENT_POWER = 'apparent_power'
    AQI = 'aqi'
    AREA = 'area'
    ATMOSPHERIC_PRESSURE = 'atmospheric_pressure'
    BATTERY = 'battery'
    BLOOD_GLUCOSE_CONCENTRATION = 'blood_glucose_concentration'
    CARBON_DIOXIDE = 'carbon_dioxide'
    CARBON_MONOXIDE = 'carbon_monoxide'
    CURRENT = 'current'
    DATA_RATE = 'data_rate'
    DATA_SIZE = 'data_size'
    DISTANCE = 'distance'
    DURATION = 'duration'
    ENERGY = 'energy'
    ENERGY_DISTANCE = 'energy_distance'
    ENERGY_STORAGE = 'energy_storage'
    FREQUENCY = 'frequency'
    GAS = 'gas'
    HUMIDITY = 'humidity'
    ILLUMINANCE = 'illuminance'
    IRRADIANCE = 'irradiance'
    MOISTURE = 'moisture'
    MONETARY = 'monetary'
    NITROGEN_DIOXIDE = 'nitrogen_dioxide'
    NITROGEN_MONOXIDE = 'nitrogen_monoxide'
    NITROUS_OXIDE = 'nitrous_oxide'
    OZONE = 'ozone'
    PH = 'ph'
    PM1 = 'pm1'
    PM25 = 'pm25'
    PM10 = 'pm10'
    POWER_FACTOR = 'power_factor'
    POWER = 'power'
    PRECIPITATION = 'precipitation'
    PRECIPITATION_INTENSITY = 'precipitation_intensity'
    PRESSURE = 'pressure'
    REACTIVE_POWER = 'reactive_power'
    SIGNAL_STRENGTH = 'signal_strength'
    SOUND_PRESSURE = 'sound_pressure'
    SPEED = 'speed'
    SULPHUR_DIOXIDE = 'sulphur_dioxide'
    TEMPERATURE = 'temperature'
    VOLATILE_ORGANIC_COMPOUNDS = 'volatile_organic_compounds'
    VOLATILE_ORGANIC_COMPOUNDS_PARTS = 'volatile_organic_compounds_parts'
    VOLTAGE = 'voltage'
    VOLUME = 'volume'
    VOLUME_FLOW_RATE = 'volume_flow_rate'
    VOLUME_STORAGE = 'volume_storage'
    WATER = 'water'
    WEIGHT = 'weight'
    WIND_DIRECTION = 'wind_direction'
    WIND_SPEED = 'wind_speed'


class SensorClass(StrEnum):
    NONE = 'None'
    APPARENT_POWER = 'apparent_power'
    AQI = 'aqi'
    AREA = 'area'
    ATMOSPHERIC_PRESSURE = 'atmospheric_pressure'
    BATTERY = 'battery'
    BLOOD_GLUCOSE_CONCENTRATION = 'blood_glucose_concentration'
    CARBON_DIOXIDE = 'carbon_dioxide'
    CARBON_MONOXIDE = 'carbon_monoxide'
    CURRENT = 'current'
    DATA_RATE = 'data_rate'
    DATA_SIZE = 'data_size'
    DATE = 'date'
    DISTANCE = 'distance'
    DURATION = 'duration'
    ENERGY = 'energy'
    ENERGY_DISTANCE = 'energy_distance'
    ENERGY_STORAGE = 'energy_storage'
    ENUM = 'enums'
    FREQUENCY = 'frequency'
    GAS = 'gas'
    HUMIDITY = 'humidity'
    ILLUMINANCE = 'illuminance'
    IRRADIANCE = 'irradiance'
    MOISTURE = 'moisture'
    MONETARY = 'monetary'
    NITROGEN_DIOXIDE = 'nitrous_oxide'
    NITROGEN_MONOXIDE = 'nitrous_monoxide'
    NITROUS_OXIDE = 'nitrous_oxide'
    OZONE = 'ozone'
    PH = 'ph'
    PM1 = 'pm1'
    PM25 = 'pm25'
    PM10 = 'pm10'
    POWER_FACTOR = 'power_factor'
    POWER = 'power'
    PRECIPITATION = 'precipitation'
    PRECIPITATION_INTENSITY = 'precipitation_intensity'
    PRESSURE = 'pressure'
    REACTIVE_POWER = 'reactive_power'
    SIGNAL_STRENGTH = 'signal_strength'
    SOUND_PRESSURE = 'sound_pressure'
    SPEED = 'speed'
    SULPHUR_DIOXIDE = 'sulphur_dioxide'
    TEMPERATURE = 'temperature'
    TIMESTAMP = 'timestamp'
    VOLATILE_ORGANIC_COMPOUNDS = 'volatile_organic_compounds'
    VOLATILE_ORGANIC_COMPOUNDS_PARTS = 'volatile_organic_compounds_parts'
    VOLTAGE = 'voltage'
    VOLUME = 'volume'
    VOLUME_FLOW_RATE = 'volume_flow_rate'
    VOLUME_STORAGE = 'volume_storage'
    WATER = 'water'
    WEIGHT = 'weight'
    WIND_DIRECTION = 'wind_direction'
    WIND_SPEED = 'wind_speed'


class SensorStateClass(StrEnum):
    MEASUREMENT = 'measurement'
    MEASUREMENT_ANGLE = 'measurement_angle'
    TOTAL = 'total'
    TOTAL_INCREASING = 'total_increasing'


class SwitchClass(StrEnum):
    NONE = 'None'
    OUTLET = 'outlet'
    SWITCH = 'switch'


class UpdateClass(StrEnum):
    NONE = 'None'
    FIRMWARE = 'firmware'


class ValveClass(StrEnum):
    NONE = 'None'
    WATER = 'water'
    GAS = 'gas'


# Misc
class TemperatureUnit(StrEnum):
    CELSIUS = 'C'
    FAHRENHEIT = 'F'


class Precision(Enum):
    """The precision to use for this component."""

    HIGH = 0.1
    """Values are multiple of ``0.1``"""
    MEDIUM = 0.5
    """Values are multiple of ``0.5``"""
    LOW = 1.0
    """Values are multiple of ``1``"""


# Enums
class AlarmControlPanelCode(StrEnum):
    NUMERIC = 'REMOTE_CODE'
    TEXTUAL = 'REMOTE_CODE_TEXT'


class AlarmControlPanelFeature(StrEnum):
    HOME = 'arm_home'
    AWAY = 'arm_away'
    NIGHT = 'arm_night'
    VACATION = 'arm_vacation'
    BYPASS = 'arm_custom_bypass'
    TRIGGER = 'trigger'


class AlarmControlPanelState(StrEnum):
    ARMED_AWAY = 'armed_away'
    ARMED_BYPASS = 'armed_custom_bypass'
    ARMED_HOME = 'armed_home'
    ARMED_NIGHT = 'armed_night'
    ARMED_VACATION = 'armed_vacation'
    ARMING = 'arming'
    DISARMED = 'disarmed'
    DISARMING = 'disarming'
    PENDING = 'pending'
    TRIGGERED = 'triggered'


class ImageEncoding(StrEnum):
    BINARY = 'bin'
    BASE64 = 'b64'


class CoverState(StrEnum):
    OPEN = 'open'
    OPENING = 'opening'
    CLOSED = 'closed'
    CLOSING = 'closing'
    STOPPED = 'stopped'


class DeviceTrackerSource(StrEnum):
    GPS = 'gps'
    ROUTER = 'router'
    BT = 'bluetooth'
    BLE = 'bluetooth_le'


class DeviceTriggerType(StrEnum):
    BUTTON_SHORT_PRESS = 'button_short_press'
    BUTTON_SHORT_RELEASE = 'button_short_release'
    BUTTON_LONG_PRESS = 'button_long_press'
    BUTTON_LONG_RELEASE = 'button_long_release'
    BUTTON_DOUBLE_PRESS = 'button_double_press'
    BUTTON_TRIPLE_PRESS = 'button_triple_press'
    BUTTON_QUADRUPLE_PRESS = 'button_quadruple_press'
    BUTTON_QUINTUPLE_PRESS = 'button_quintuple_press'


class DeviceTriggerSubtype(StrEnum):
    TURN_ON = 'turn_on'
    TURN_OFF = 'turn_off'
    BUTTON_1 = 'button_1'
    BUTTON_2 = 'button_2'
    BUTTON_3 = 'button_3'
    BUTTON_4 = 'button_4'
    BUTTON_5 = 'button_5'
    BUTTON_6 = 'button_6'


class HumidifierMode(StrEnum):
    NORMAL = 'normal'
    ECO = 'eco'
    AWAY = 'away'
    BOOST = 'boost'
    COMFORT = 'comfort'
    HOME = 'home'
    SLEEP = 'sleep'
    AUTO = 'auto'
    BABY = 'baby'


class HumidifierAction(StrEnum):
    OFF = 'off'
    HUMIDIFYING = 'humidifying'
    DRYING = 'drying'
    IDLE = 'idle'


class HVACAction(StrEnum):
    OFF = 'off'
    HEATING = 'heating'
    COOLING = 'cooling'
    DRYING = 'drying'
    IDLE = 'idle'
    FAN = 'fan'


class HVACFanMode(StrEnum):
    AUTO = 'auto'
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'


class HVACMode(StrEnum):
    AUTO = 'auto'
    OFF = 'off'
    COOL = 'cool'
    HEAT = 'heat'
    DRY = 'dry'
    FAN_ONLY = 'fan_only'


class HVACPresetMode(StrEnum):
    ECO = 'eco'
    AWAY = 'away'
    BOOST = 'boost'
    COMFORT = 'comfort'
    HOME = 'home'
    SLEEP = 'sleep'
    ACTIVITY = 'activity'


class LawnMowerState(StrEnum):
    MOWING = 'mowing'
    PAUSED = 'paused'
    DOCKED = 'docked'
    ERROR = 'error'


class LightColorMode(StrEnum):
    ONOFF = 'onoff'
    BRIGHTNESS = 'brightness'
    COLOR_TEMP = 'color_temp'
    HS = 'hs'
    XY = 'xy'
    RGB = 'rgb'
    RGBW = 'rgbw'
    RGBWW = 'rgbww'
    WHITE = 'white'


class LockState(StrEnum):
    JAMMED = 'jammed'
    LOCKED = 'locked'
    LOCKING = 'locking'
    UNLOCKED = 'unlocked'
    UNLOCKING = 'unlocking'


class NumberMode(StrEnum):
    AUTO = 'auto'
    BOX = 'box'
    SLIDER = 'slider'


class TextMode(StrEnum):
    TEXT = 'text'
    PASSWORD = 'password'


class VacuumFeature(StrEnum):
    START = 'start'
    STOP = 'stop'
    PAUSE = 'pause'
    RETURN_HOME = 'return_home'
    BATTERY = 'battery'
    STATUS = 'status'
    LOCATE = 'locate'
    CLEAN_SPOT = 'clean_spot'
    FAN_SPEED = 'fan_speed'
    SEND_COMMAND = 'send_command'


class VacuumState(StrEnum):
    CLEANING = 'cleaning'
    DOCKED = 'docked'
    PAUSED = 'paused'
    IDLE = 'idle'
    RETURNING = 'returning'
    ERROR = 'error'


class VacuumFanSpeed(StrEnum):
    MIN = 'min'
    MEDIUM = 'medium'
    HIGH = 'high'
    MAX = 'max'


class ValveState(StrEnum):
    OPEN = 'open'
    OPENING = 'opening'
    CLOSED = 'closed'
    CLOSING = 'closing'


class WaterHeaterMode(StrEnum):
    OFF = 'off'
    ECO = 'eco'
    ELECTRIC = 'electric'
    GAS = 'gas'
    HEAT_PUMP = 'heat_pump'
    HIGH_DEMAND = 'high_demand'
    PERFORMANCE = 'performance'
