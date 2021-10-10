from homeassistant.components.climate.const import (
    HVAC_MODE_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_FAN_MODE,
    SUPPORT_SWING_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    SWING_OFF,
    SWING_VERTICAL,
)
from homeassistant.const import STATE_UNAVAILABLE, TEMP_CELSIUS, TEMP_FAHRENHEIT

from ..const import FERSK_VIND2_PAYLOAD
from ..helpers import assert_device_properties_set
from .base_device_tests import TuyaDeviceTestCase

POWER_DPS = "1"
TEMPERATURE_DPS = "2"
CURRENTTEMP_DPS = "3"
HVACMODE_DPS = "4"
FAN_DPS = "5"
UNIT_DPS = "19"
UNKNOWN101_DPS = "101"
UNKNOWN102_DPS = "102"
TIMER_DPS = "103"
SWING_DPS = "104"
COUNTDOWN_DPS = "105"
UNKNOWN106_DPS = "106"
UNKNOWN109_DPS = "109"
UNKNOWN110_DPS = "110"


class TestFerskVind2Climate(TuyaDeviceTestCase):
    __test__ = True

    def setUp(self):
        self.setUpForConfig("fersk_vind_2_climate.yaml", FERSK_VIND2_PAYLOAD)
        self.subject = self.entities.get("climate")

    def test_supported_features(self):
        self.assertEqual(
            self.subject.supported_features,
            SUPPORT_TARGET_TEMPERATURE | SUPPORT_FAN_MODE | SUPPORT_SWING_MODE,
        )

    def test_icon(self):
        self.dps[POWER_DPS] = True
        self.dps[HVACMODE_DPS] = "COOL"
        self.assertEqual(self.subject.icon, "mdi:snowflake")
        self.dps[HVACMODE_DPS] = "FAN"
        self.assertEqual(self.subject.icon, "mdi:fan")
        self.dps[HVACMODE_DPS] = "DRY"
        self.assertEqual(self.subject.icon, "mdi:water")
        self.dps[HVACMODE_DPS] = "HEAT"
        self.assertEqual(self.subject.icon, "mdi:fire")
        self.dps[POWER_DPS] = False
        self.assertEqual(self.subject.icon, "mdi:hvac-off")

    def test_temperature_unit(self):
        self.dps[UNIT_DPS] = "C"
        self.assertEqual(self.subject.temperature_unit, TEMP_CELSIUS)
        self.dps[UNIT_DPS] = "F"
        self.assertEqual(self.subject.temperature_unit, TEMP_FAHRENHEIT)

    def test_target_temperature(self):
        self.dps[TEMPERATURE_DPS] = 25
        self.assertEqual(self.subject.target_temperature, 25)

    def test_target_temperature_step(self):
        self.assertEqual(self.subject.target_temperature_step, 1)

    def test_minimum_target_temperature(self):
        self.dps[UNIT_DPS] = "C"
        self.assertEqual(self.subject.min_temp, 16)
        self.dps[UNIT_DPS] = "F"
        self.assertEqual(self.subject.min_temp, 60)

    def test_maximum_target_temperature(self):
        self.dps[UNIT_DPS] = "C"
        self.assertEqual(self.subject.max_temp, 32)
        self.dps[UNIT_DPS] = "F"
        self.assertEqual(self.subject.max_temp, 90)

    async def test_legacy_set_temperature_with_temperature(self):
        self.dps[UNIT_DPS] = "C"
        async with assert_device_properties_set(
            self.subject._device, {TEMPERATURE_DPS: 24}
        ):
            await self.subject.async_set_temperature(temperature=24)

    async def test_set_target_temperature_succeeds_within_valid_range(self):
        self.dps[UNIT_DPS] = "C"
        async with assert_device_properties_set(
            self.subject._device, {TEMPERATURE_DPS: 24}
        ):
            await self.subject.async_set_target_temperature(24)
        self.dps[UNIT_DPS] = "F"
        async with assert_device_properties_set(
            self.subject._device, {TEMPERATURE_DPS: 80}
        ):
            await self.subject.async_set_target_temperature(80)

    async def test_set_target_temperature_fails_outside_valid_range(self):
        self.dps[UNIT_DPS] = "C"
        with self.assertRaisesRegex(
            ValueError, "temperature \\(15\\) must be between 16 and 32"
        ):
            await self.subject.async_set_target_temperature(15)

        with self.assertRaisesRegex(
            ValueError, "temperature \\(33\\) must be between 16 and 32"
        ):
            await self.subject.async_set_target_temperature(33)

        self.dps[UNIT_DPS] = "F"
        with self.assertRaisesRegex(
            ValueError, "temperature \\(59\\) must be between 60 and 90"
        ):
            await self.subject.async_set_target_temperature(59)

        with self.assertRaisesRegex(
            ValueError, "temperature \\(91\\) must be between 60 and 90"
        ):
            await self.subject.async_set_target_temperature(91)

    def test_current_temperature(self):
        self.dps[CURRENTTEMP_DPS] = 25
        self.assertEqual(self.subject.current_temperature, 25)

    def test_hvac_mode(self):
        self.dps[POWER_DPS] = True
        self.dps[HVACMODE_DPS] = "COOL"
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_COOL)
        self.dps[HVACMODE_DPS] = "FAN"
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_FAN_ONLY)
        self.dps[HVACMODE_DPS] = "DRY"
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_DRY)
        self.dps[HVACMODE_DPS] = "HEAT"
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_HEAT)
        self.dps[POWER_DPS] = False
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_OFF)

    def test_hvac_modes(self):
        self.assertCountEqual(
            self.subject.hvac_modes,
            [
                HVAC_MODE_COOL,
                HVAC_MODE_DRY,
                HVAC_MODE_FAN_ONLY,
                HVAC_MODE_HEAT,
                HVAC_MODE_OFF,
            ],
        )

    async def test_set_hvac_mode_off(self):
        async with assert_device_properties_set(
            self.subject._device, {POWER_DPS: False}
        ):
            await self.subject.async_set_hvac_mode(HVAC_MODE_OFF)

    async def test_set_hvac_mode_cool(self):
        async with assert_device_properties_set(
            self.subject._device, {POWER_DPS: True, HVACMODE_DPS: "COOL"}
        ):
            await self.subject.async_set_hvac_mode(HVAC_MODE_COOL)

    async def test_set_hvac_mode_dry(self):
        async with assert_device_properties_set(
            self.subject._device, {POWER_DPS: True, HVACMODE_DPS: "DRY"}
        ):
            await self.subject.async_set_hvac_mode(HVAC_MODE_DRY)

    async def test_set_hvac_mode_fan(self):
        async with assert_device_properties_set(
            self.subject._device, {POWER_DPS: True, HVACMODE_DPS: "FAN"}
        ):
            await self.subject.async_set_hvac_mode(HVAC_MODE_FAN_ONLY)

    async def test_set_hvac_mode_heat(self):
        async with assert_device_properties_set(
            self.subject._device, {POWER_DPS: True, HVACMODE_DPS: "HEAT"}
        ):
            await self.subject.async_set_hvac_mode(HVAC_MODE_HEAT)

    def test_fan_mode(self):
        self.dps[FAN_DPS] = 1
        self.assertEqual(self.subject.fan_mode, "low")
        self.dps[FAN_DPS] = 2
        self.assertEqual(self.subject.fan_mode, "medium")
        self.dps[FAN_DPS] = 3
        self.assertEqual(self.subject.fan_mode, "high")

    def test_fan_modes(self):
        self.assertCountEqual(
            self.subject.fan_modes,
            ["low", "medium", "high"],
        )

    async def test_set_fan_mode_to_low(self):
        async with assert_device_properties_set(
            self.subject._device,
            {FAN_DPS: 1},
        ):
            await self.subject.async_set_fan_mode("low")

    async def test_set_fan_mode_to_medium(self):
        async with assert_device_properties_set(
            self.subject._device,
            {FAN_DPS: 2},
        ):
            await self.subject.async_set_fan_mode("medium")

    async def test_set_fan_mode_to_high(self):
        async with assert_device_properties_set(
            self.subject._device,
            {FAN_DPS: 3},
        ):
            await self.subject.async_set_fan_mode("high")

    def test_swing_modes(self):
        self.assertCountEqual(
            self.subject.swing_modes,
            [SWING_OFF, SWING_VERTICAL],
        )

    def test_swing_mode(self):
        self.dps[SWING_DPS] = False
        self.assertEqual(self.subject.swing_mode, SWING_OFF)
        self.dps[SWING_DPS] = True
        self.assertEqual(self.subject.swing_mode, SWING_VERTICAL)

    async def test_set_swing_mode_to_vertical(self):
        async with assert_device_properties_set(
            self.subject._device,
            {SWING_DPS: True},
        ):
            await self.subject.async_set_swing_mode(SWING_VERTICAL)

    async def test_set_swing_mode_to_off(self):
        async with assert_device_properties_set(
            self.subject._device,
            {SWING_DPS: False},
        ):
            await self.subject.async_set_swing_mode(SWING_OFF)

    def test_device_state_attribures(self):
        self.dps[UNKNOWN101_DPS] = True
        self.dps[UNKNOWN102_DPS] = False
        self.dps[TIMER_DPS] = 103
        self.dps[COUNTDOWN_DPS] = 105
        self.dps[UNKNOWN106_DPS] = 106
        self.dps[UNKNOWN109_DPS] = True
        self.dps[UNKNOWN110_DPS] = 110
        self.assertDictEqual(
            self.subject.device_state_attributes,
            {
                "unknown_101": True,
                "unknown_102": False,
                "timer": 103,
                "countdown": 105,
                "unknown_106": 106,
                "unknown_109": True,
                "unknown_110": 110,
            },
        )
