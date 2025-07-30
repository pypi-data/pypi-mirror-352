# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: svn_id $
#
#  Asyncio implementation of YColorSensor
#
#  - - - - - - - - - License information: - - - - - - - - -
#
#  Copyright (C) 2011 and beyond by Yoctopuce Sarl, Switzerland.
#
#  Yoctopuce Sarl (hereafter Licensor) grants to you a perpetual
#  non-exclusive license to use, modify, copy and integrate this
#  file into your software for the sole purpose of interfacing
#  with Yoctopuce products.
#
#  You may reproduce and distribute copies of this file in
#  source or object form, as long as the sole purpose of this
#  code is to interface with Yoctopuce products. You must retain
#  this notice in the distributed source file.
#
#  You should refer to Yoctopuce General Terms and Conditions
#  for additional information regarding your rights and
#  obligations.
#
#  THE SOFTWARE AND DOCUMENTATION ARE PROVIDED 'AS IS' WITHOUT
#  WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING
#  WITHOUT LIMITATION, ANY WARRANTY OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO
#  EVENT SHALL LICENSOR BE LIABLE FOR ANY INCIDENTAL, SPECIAL,
#  INDIRECT OR CONSEQUENTIAL DAMAGES, LOST PROFITS OR LOST DATA,
#  COST OF PROCUREMENT OF SUBSTITUTE GOODS, TECHNOLOGY OR
#  SERVICES, ANY CLAIMS BY THIRD PARTIES (INCLUDING BUT NOT
#  LIMITED TO ANY DEFENSE THEREOF), ANY CLAIMS FOR INDEMNITY OR
#  CONTRIBUTION, OR OTHER SIMILAR COSTS, WHETHER ASSERTED ON THE
#  BASIS OF CONTRACT, TORT (INCLUDING NEGLIGENCE), BREACH OF
#  WARRANTY, OR OTHERWISE.
#
# *********************************************************************
"""
Yoctopuce library: Asyncio implementation of YColorSensor
version: PATCH_WITH_VERSION
requires: yocto_api_aio
"""
from __future__ import annotations

import sys

# On MicroPython, code below will be wiped out at compile time
if sys.implementation.name != "micropython":
    # In CPython, enable edit-time type checking, including Final declaration
    from typing import Any, Union, Final
    from collections.abc import Callable, Awaitable
    const = lambda obj: obj
    _IS_MICROPYTHON = False
else:
    # In our micropython VM, common generic types are global built-ins
    # Others such as TypeVar should be avoided when using micropython,
    # as they produce overhead in runtime code
    # Final is translated into const() expressions before compilation
    _IS_MICROPYTHON: Final[bool] = True # noqa

from .yocto_api_aio import (
    YAPIContext, YAPI, YAPI_Exception, HwId, hwid2str, YFunction
)

# --- (YColorSensor class start)
if not _IS_MICROPYTHON:
    # For CPython, use strongly typed callback types
    try:
        YColorSensorValueCallback = Union[Callable[['YColorSensor', str], Any], None]
    except TypeError:
        YColorSensorValueCallback = Union[Callable, Awaitable]

# noinspection PyProtectedMember
class YColorSensor(YFunction):
    """
    The YColorSensor class allows you to read and configure Yoctopuce color sensors.

    """
    # --- (end of YColorSensor class start)
    if not _IS_MICROPYTHON:
        # --- (YColorSensor return codes)
        LEDCURRENT_INVALID: Final[int] = YAPI.INVALID_UINT
        LEDCALIBRATION_INVALID: Final[int] = YAPI.INVALID_UINT
        INTEGRATIONTIME_INVALID: Final[int] = YAPI.INVALID_UINT
        GAIN_INVALID: Final[int] = YAPI.INVALID_UINT
        SATURATION_INVALID: Final[int] = YAPI.INVALID_UINT
        ESTIMATEDRGB_INVALID: Final[int] = YAPI.INVALID_UINT
        ESTIMATEDHSL_INVALID: Final[int] = YAPI.INVALID_UINT
        ESTIMATEDXYZ_INVALID: Final[str] = YAPI.INVALID_STRING
        ESTIMATEDOKLAB_INVALID: Final[str] = YAPI.INVALID_STRING
        NEARRAL1_INVALID: Final[str] = YAPI.INVALID_STRING
        NEARRAL2_INVALID: Final[str] = YAPI.INVALID_STRING
        NEARRAL3_INVALID: Final[str] = YAPI.INVALID_STRING
        NEARHTMLCOLOR_INVALID: Final[str] = YAPI.INVALID_STRING
        NEARSIMPLECOLOR_INVALID: Final[str] = YAPI.INVALID_STRING
        ESTIMATIONMODEL_REFLECTION: Final[int] = 0
        ESTIMATIONMODEL_EMISSION: Final[int] = 1
        ESTIMATIONMODEL_INVALID: Final[int] = -1
        WORKINGMODE_AUTO: Final[int] = 0
        WORKINGMODE_EXPERT: Final[int] = 1
        WORKINGMODE_INVALID: Final[int] = -1
        NEARSIMPLECOLORINDEX_BROWN: Final[int] = 0
        NEARSIMPLECOLORINDEX_RED: Final[int] = 1
        NEARSIMPLECOLORINDEX_ORANGE: Final[int] = 2
        NEARSIMPLECOLORINDEX_YELLOW: Final[int] = 3
        NEARSIMPLECOLORINDEX_WHITE: Final[int] = 4
        NEARSIMPLECOLORINDEX_GRAY: Final[int] = 5
        NEARSIMPLECOLORINDEX_BLACK: Final[int] = 6
        NEARSIMPLECOLORINDEX_GREEN: Final[int] = 7
        NEARSIMPLECOLORINDEX_BLUE: Final[int] = 8
        NEARSIMPLECOLORINDEX_PURPLE: Final[int] = 9
        NEARSIMPLECOLORINDEX_PINK: Final[int] = 10
        NEARSIMPLECOLORINDEX_INVALID: Final[int] = -1
        # --- (end of YColorSensor return codes)

    # --- (YColorSensor attributes declaration)
    _estimationModel: int
    _workingMode: int
    _ledCurrent: int
    _ledCalibration: int
    _integrationTime: int
    _gain: int
    _saturation: int
    _estimatedRGB: int
    _estimatedHSL: int
    _estimatedXYZ: str
    _estimatedOkLab: str
    _nearRAL1: str
    _nearRAL2: str
    _nearRAL3: str
    _nearHTMLColor: str
    _nearSimpleColorIndex: int
    _nearSimpleColor: str
    _valueCallback: YColorSensorValueCallback
    # --- (end of YColorSensor attributes declaration)


    def __init__(self, yctx: YAPIContext, func: str):
        super().__init__(yctx, func)
        self._className = 'ColorSensor'
        # --- (YColorSensor constructor)
        self._estimationModel = YColorSensor.ESTIMATIONMODEL_INVALID
        self._workingMode = YColorSensor.WORKINGMODE_INVALID
        self._ledCurrent = YColorSensor.LEDCURRENT_INVALID
        self._ledCalibration = YColorSensor.LEDCALIBRATION_INVALID
        self._integrationTime = YColorSensor.INTEGRATIONTIME_INVALID
        self._gain = YColorSensor.GAIN_INVALID
        self._saturation = YColorSensor.SATURATION_INVALID
        self._estimatedRGB = YColorSensor.ESTIMATEDRGB_INVALID
        self._estimatedHSL = YColorSensor.ESTIMATEDHSL_INVALID
        self._estimatedXYZ = YColorSensor.ESTIMATEDXYZ_INVALID
        self._estimatedOkLab = YColorSensor.ESTIMATEDOKLAB_INVALID
        self._nearRAL1 = YColorSensor.NEARRAL1_INVALID
        self._nearRAL2 = YColorSensor.NEARRAL2_INVALID
        self._nearRAL3 = YColorSensor.NEARRAL3_INVALID
        self._nearHTMLColor = YColorSensor.NEARHTMLCOLOR_INVALID
        self._nearSimpleColorIndex = YColorSensor.NEARSIMPLECOLORINDEX_INVALID
        self._nearSimpleColor = YColorSensor.NEARSIMPLECOLOR_INVALID
        # --- (end of YColorSensor constructor)

    # --- (YColorSensor implementation)

    @staticmethod
    def FirstColorSensor() -> Union[YColorSensor, None]:
        """
        Starts the enumeration of color sensors currently accessible.
        Use the method YColorSensor.nextColorSensor() to iterate on
        next color sensors.

        @return a pointer to a YColorSensor object, corresponding to
                the first color sensor currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = YAPI._yHash.getFirstHardwareId('ColorSensor')
        if not next_hwid:
            return None
        return YColorSensor.FindColorSensor(hwid2str(next_hwid))

    @staticmethod
    def FirstColorSensorInContext(yctx: YAPIContext) -> Union[YColorSensor, None]:
        """
        Starts the enumeration of color sensors currently accessible.
        Use the method YColorSensor.nextColorSensor() to iterate on
        next color sensors.

        @param yctx : a YAPI context.

        @return a pointer to a YColorSensor object, corresponding to
                the first color sensor currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = yctx._yHash.getFirstHardwareId('ColorSensor')
        if not next_hwid:
            return None
        return YColorSensor.FindColorSensorInContext(yctx, hwid2str(next_hwid))

    def nextColorSensor(self):
        """
        Continues the enumeration of color sensors started using yFirstColorSensor().
        Caution: You can't make any assumption about the returned color sensors order.
        If you want to find a specific a color sensor, use ColorSensor.findColorSensor()
        and a hardwareID or a logical name.

        @return a pointer to a YColorSensor object, corresponding to
                a color sensor currently online, or a None pointer
                if there are no more color sensors to enumerate.
        """
        next_hwid: Union[HwId, None] = None
        try:
            hwid: HwId = self._yapi._yHash.resolveHwID(self._className, self._func)
            next_hwid = self._yapi._yHash.getNextHardwareId(self._className, hwid)
        except YAPI_Exception:
            pass
        if not next_hwid:
            return None
        return YColorSensor.FindColorSensorInContext(self._yapi, hwid2str(next_hwid))

    def _parseAttr(self, json_val: dict) -> None:
        if 'estimationModel' in json_val:
            self._estimationModel = json_val["estimationModel"]
        if 'workingMode' in json_val:
            self._workingMode = json_val["workingMode"]
        if 'ledCurrent' in json_val:
            self._ledCurrent = json_val["ledCurrent"]
        if 'ledCalibration' in json_val:
            self._ledCalibration = json_val["ledCalibration"]
        if 'integrationTime' in json_val:
            self._integrationTime = json_val["integrationTime"]
        if 'gain' in json_val:
            self._gain = json_val["gain"]
        if 'saturation' in json_val:
            self._saturation = json_val["saturation"]
        if 'estimatedRGB' in json_val:
            self._estimatedRGB = json_val["estimatedRGB"]
        if 'estimatedHSL' in json_val:
            self._estimatedHSL = json_val["estimatedHSL"]
        if 'estimatedXYZ' in json_val:
            self._estimatedXYZ = json_val["estimatedXYZ"]
        if 'estimatedOkLab' in json_val:
            self._estimatedOkLab = json_val["estimatedOkLab"]
        if 'nearRAL1' in json_val:
            self._nearRAL1 = json_val["nearRAL1"]
        if 'nearRAL2' in json_val:
            self._nearRAL2 = json_val["nearRAL2"]
        if 'nearRAL3' in json_val:
            self._nearRAL3 = json_val["nearRAL3"]
        if 'nearHTMLColor' in json_val:
            self._nearHTMLColor = json_val["nearHTMLColor"]
        if 'nearSimpleColorIndex' in json_val:
            self._nearSimpleColorIndex = json_val["nearSimpleColorIndex"]
        if 'nearSimpleColor' in json_val:
            self._nearSimpleColor = json_val["nearSimpleColor"]
        super()._parseAttr(json_val)

    async def get_estimationModel(self) -> int:
        """
        Returns the predictive model used for color estimation (reflective or emissive).

        @return either YColorSensor.ESTIMATIONMODEL_REFLECTION or YColorSensor.ESTIMATIONMODEL_EMISSION,
        according to the predictive model used for color estimation (reflective or emissive)

        On failure, throws an exception or returns YColorSensor.ESTIMATIONMODEL_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorSensor.ESTIMATIONMODEL_INVALID
        res = self._estimationModel
        return res

    async def set_estimationModel(self, newval: int) -> int:
        """
        Changes the predictive model to be used for color estimation (reflective or emissive).
        Remember to call the saveToFlash() method of the module if the modification must be kept.

        @param newval : either YColorSensor.ESTIMATIONMODEL_REFLECTION or
        YColorSensor.ESTIMATIONMODEL_EMISSION, according to the predictive model to be used for color
        estimation (reflective or emissive)

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("estimationModel", rest_val)

    async def get_workingMode(self) -> int:
        """
        Returns the sensor working mode.
        In Auto mode, sensor parameters are automatically set based on the selected estimation model.
        In Expert mode, sensor parameters such as gain and integration time are configured manually.

        @return either YColorSensor.WORKINGMODE_AUTO or YColorSensor.WORKINGMODE_EXPERT, according to the
        sensor working mode

        On failure, throws an exception or returns YColorSensor.WORKINGMODE_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorSensor.WORKINGMODE_INVALID
        res = self._workingMode
        return res

    async def set_workingMode(self, newval: int) -> int:
        """
        Changes the sensor working mode.
        In Auto mode, sensor parameters are automatically set based on the selected estimation model.
        In Expert mode, sensor parameters such as gain and integration time are configured manually.
        Remember to call the saveToFlash() method of the module if the modification must be kept.

        @param newval : either YColorSensor.WORKINGMODE_AUTO or YColorSensor.WORKINGMODE_EXPERT, according
        to the sensor working mode

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("workingMode", rest_val)

    async def get_ledCurrent(self) -> int:
        """
        Returns the amount of current sent to the illumination LEDs, for reflection measures.
        The value is an integer ranging from 0 (LEDs off) to 254 (LEDs at maximum intensity).

        @return an integer corresponding to the amount of current sent to the illumination LEDs, for reflection measures

        On failure, throws an exception or returns YColorSensor.LEDCURRENT_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorSensor.LEDCURRENT_INVALID
        res = self._ledCurrent
        return res

    async def set_ledCurrent(self, newval: int) -> int:
        """
        Changes the amount of current sent to the illumination LEDs, for reflection measures.
        The value is an integer ranging from 0 (LEDs off) to 254 (LEDs at maximum intensity).

        @param newval : an integer corresponding to the amount of current sent to the illumination LEDs,
        for reflection measures

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("ledCurrent", rest_val)

    async def get_ledCalibration(self) -> int:
        """
        Returns the current sent to the illumination LEDs during the latest calibration.

        @return an integer corresponding to the current sent to the illumination LEDs during the latest calibration

        On failure, throws an exception or returns YColorSensor.LEDCALIBRATION_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorSensor.LEDCALIBRATION_INVALID
        res = self._ledCalibration
        return res

    async def set_ledCalibration(self, newval: int) -> int:
        """
        Remember the LED current sent to the illumination LEDs during a calibration.
        Thanks to this, the device is able to use the same current when taking measures.
        Remember to call the saveToFlash() method of the module if the modification must be kept.

        @param newval : an integer

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("ledCalibration", rest_val)

    async def get_integrationTime(self) -> int:
        """
        Returns the current integration time for spectral measure, in milliseconds.
        A longer integration time increase the sensitivity for low light conditions,
        but reduces the measure taking rate and may lead to saturation for lighter colors.

        @return an integer corresponding to the current integration time for spectral measure, in milliseconds

        On failure, throws an exception or returns YColorSensor.INTEGRATIONTIME_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorSensor.INTEGRATIONTIME_INVALID
        res = self._integrationTime
        return res

    async def set_integrationTime(self, newval: int) -> int:
        """
        Changes the integration time for spectral measure, in milliseconds.
        A longer integration time increase the sensitivity for low light conditions,
        but reduces the measure taking rate and may lead to saturation for lighter colors.
        This method can only be used when the sensor is configured in expert mode;
        when running in auto mode, the change is ignored.
        Remember to call the saveToFlash() method of the module if the modification must be kept.

        @param newval : an integer corresponding to the integration time for spectral measure, in milliseconds

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("integrationTime", rest_val)

    async def get_gain(self) -> int:
        """
        Returns the current spectral channel detector gain exponent.
        For a value n ranging from 0 to 12, the applied gain is 2^(n-1).
        0 corresponds to a gain of 0.5, and 12 corresponds to a gain of 2048.

        @return an integer corresponding to the current spectral channel detector gain exponent

        On failure, throws an exception or returns YColorSensor.GAIN_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorSensor.GAIN_INVALID
        res = self._gain
        return res

    async def set_gain(self, newval: int) -> int:
        """
        Changes the spectral channel detector gain exponent.
        For a value n ranging from 0 to 12, the applied gain is 2^(n-1).
        0 corresponds to a gain of 0.5, and 12 corresponds to a gain of 2048.
        This method can only be used when the sensor is configured in expert mode;
        when running in auto mode, the change is ignored.
        Remember to call the saveToFlash() method of the module if the modification must be kept.

        @param newval : an integer corresponding to the spectral channel detector gain exponent

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("gain", rest_val)

    async def get_saturation(self) -> int:
        """
        Returns the current saturation state of the sensor, as an integer.
        Bit 0 indicates saturation of the analog sensor, which can only
        be corrected by reducing the gain parameters or the luminosity.
        Bit 1 indicates saturation of the digital interface, which can
        be corrected by reducing the integration time or the gain.

        @return an integer corresponding to the current saturation state of the sensor, as an integer

        On failure, throws an exception or returns YColorSensor.SATURATION_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorSensor.SATURATION_INVALID
        res = self._saturation
        return res

    async def get_estimatedRGB(self) -> int:
        """
        Returns the estimated color in RGB color model (0xRRGGBB).
        The RGB color model describes each color using a combination of 3 components:
        - Red (R): the intensity of red, in the 0...255 range
        - Green (G): the intensity of green, in the 0...255 range
        - Blue (B): the intensity of blue, in the 0...255 range

        @return an integer corresponding to the estimated color in RGB color model (0xRRGGBB)

        On failure, throws an exception or returns YColorSensor.ESTIMATEDRGB_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorSensor.ESTIMATEDRGB_INVALID
        res = self._estimatedRGB
        return res

    async def get_estimatedHSL(self) -> int:
        """
        Returns the estimated color in HSL color model (0xHHSSLL).
        The HSL color model describes each color using a combination of 3 components:
        - Hue (H): the angle on the color wheel (0-360 degrees), mapped to 0...255
        - Saturation (S): the intensity of the color (0-100%), mapped to 0...255
        - Lightness (L): the brightness of the color (0-100%), mapped to 0...255

        @return an integer corresponding to the estimated color in HSL color model (0xHHSSLL)

        On failure, throws an exception or returns YColorSensor.ESTIMATEDHSL_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorSensor.ESTIMATEDHSL_INVALID
        res = self._estimatedHSL
        return res

    async def get_estimatedXYZ(self) -> str:
        """
        Returns the estimated color according to the CIE XYZ color model.
        This color model is based on human vision and light perception, with three components
        represented by real numbers between 0 and 1:
        - X: corresponds to a component mixing sensitivity to red and green
        - Y: represents luminance (perceived brightness)
        - Z: corresponds to sensitivity to blue

        @return a string corresponding to the estimated color according to the CIE XYZ color model

        On failure, throws an exception or returns YColorSensor.ESTIMATEDXYZ_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorSensor.ESTIMATEDXYZ_INVALID
        res = self._estimatedXYZ
        return res

    async def get_estimatedOkLab(self) -> str:
        """
        Returns the estimated color according to the OkLab color model.
        OkLab is a perceptual color model that aims to align human color perception with numerical
        values, so that colors that are visually near are also numerically near. Colors are represented
        using three components:
        - L: lightness, a real number between 0 and 1
        - a: color variations between green and red, between -0.5 and 0.5
        - b: color variations between blue and yellow, between -0.5 and 0.5.

        @return a string corresponding to the estimated color according to the OkLab color model

        On failure, throws an exception or returns YColorSensor.ESTIMATEDOKLAB_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorSensor.ESTIMATEDOKLAB_INVALID
        res = self._estimatedOkLab
        return res

    async def get_nearRAL1(self) -> str:
        """
        Returns the RAL Classic color closest to the estimated color, with a similarity ratio.

        @return a string corresponding to the RAL Classic color closest to the estimated color, with a similarity ratio

        On failure, throws an exception or returns YColorSensor.NEARRAL1_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorSensor.NEARRAL1_INVALID
        res = self._nearRAL1
        return res

    async def get_nearRAL2(self) -> str:
        """
        Returns the second closest RAL Classic color to the estimated color, with a similarity ratio.

        @return a string corresponding to the second closest RAL Classic color to the estimated color, with
        a similarity ratio

        On failure, throws an exception or returns YColorSensor.NEARRAL2_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorSensor.NEARRAL2_INVALID
        res = self._nearRAL2
        return res

    async def get_nearRAL3(self) -> str:
        """
        Returns the third closest RAL Classic color to the estimated color, with a similarity ratio.

        @return a string corresponding to the third closest RAL Classic color to the estimated color, with
        a similarity ratio

        On failure, throws an exception or returns YColorSensor.NEARRAL3_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorSensor.NEARRAL3_INVALID
        res = self._nearRAL3
        return res

    async def get_nearHTMLColor(self) -> str:
        """
        Returns the name of the HTML color closest to the estimated color.

        @return a string corresponding to the name of the HTML color closest to the estimated color

        On failure, throws an exception or returns YColorSensor.NEARHTMLCOLOR_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorSensor.NEARHTMLCOLOR_INVALID
        res = self._nearHTMLColor
        return res

    async def get_nearSimpleColorIndex(self) -> int:
        """
        Returns the index of the basic color typically used to refer to the estimated color (enumerated value).
        The list of basic colors recognized is:
        - 0 - Brown
        - 1 - Red
        - 2 - Orange
        - 3 - Yellow
        - 4 - White
        - 5 - Gray
        - 6 - Black
        - 7 - Green
        - 8 - Blue
        - 9 - Purple
        - 10 - Pink

        @return a value among YColorSensor.NEARSIMPLECOLORINDEX_BROWN,
        YColorSensor.NEARSIMPLECOLORINDEX_RED, YColorSensor.NEARSIMPLECOLORINDEX_ORANGE,
        YColorSensor.NEARSIMPLECOLORINDEX_YELLOW, YColorSensor.NEARSIMPLECOLORINDEX_WHITE,
        YColorSensor.NEARSIMPLECOLORINDEX_GRAY, YColorSensor.NEARSIMPLECOLORINDEX_BLACK,
        YColorSensor.NEARSIMPLECOLORINDEX_GREEN, YColorSensor.NEARSIMPLECOLORINDEX_BLUE,
        YColorSensor.NEARSIMPLECOLORINDEX_PURPLE and YColorSensor.NEARSIMPLECOLORINDEX_PINK corresponding
        to the index of the basic color typically used to refer to the estimated color (enumerated value)

        On failure, throws an exception or returns YColorSensor.NEARSIMPLECOLORINDEX_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorSensor.NEARSIMPLECOLORINDEX_INVALID
        res = self._nearSimpleColorIndex
        return res

    async def get_nearSimpleColor(self) -> str:
        """
        Returns the name of the basic color typically used to refer to the estimated color.

        @return a string corresponding to the name of the basic color typically used to refer to the estimated color

        On failure, throws an exception or returns YColorSensor.NEARSIMPLECOLOR_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorSensor.NEARSIMPLECOLOR_INVALID
        res = self._nearSimpleColor
        return res

    @staticmethod
    def FindColorSensor(func: str) -> YColorSensor:
        """
        Retrieves a color sensor for a given identifier.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the color sensor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YColorSensor.isOnline() to test if the color sensor is
        indeed online at a given time. In case of ambiguity when looking for
        a color sensor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the color sensor, for instance
                MyDevice.colorSensor.

        @return a YColorSensor object allowing you to drive the color sensor.
        """
        obj: Union[YColorSensor, None]
        obj = YFunction._FindFromCache("ColorSensor", func)
        if obj is None:
            obj = YColorSensor(YAPI, func)
            YFunction._AddToCache("ColorSensor", func, obj)
        return obj

    @staticmethod
    def FindColorSensorInContext(yctx: YAPIContext, func: str) -> YColorSensor:
        """
        Retrieves a color sensor for a given identifier in a YAPI context.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the color sensor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YColorSensor.isOnline() to test if the color sensor is
        indeed online at a given time. In case of ambiguity when looking for
        a color sensor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        @param yctx : a YAPI context
        @param func : a string that uniquely characterizes the color sensor, for instance
                MyDevice.colorSensor.

        @return a YColorSensor object allowing you to drive the color sensor.
        """
        obj: Union[YColorSensor, None]
        obj = YFunction._FindFromCacheInContext(yctx, "ColorSensor", func)
        if obj is None:
            obj = YColorSensor(yctx, func)
            YFunction._AddToCache("ColorSensor", func, obj)
        return obj

    if not _IS_MICROPYTHON:
        async def registerValueCallback(self, callback: YColorSensorValueCallback) -> int:
            """
            Registers the callback function that is invoked on every change of advertised value.
            The callback is invoked only during the execution of ySleep or yHandleEvents.
            This provides control over the time when the callback is triggered. For good responsiveness, remember to call
            one of these two functions periodically. To unregister a callback, pass a None pointer as argument.

            @param callback : the callback function to call, or a None pointer. The callback function should take two
                    arguments: the function object of which the value has changed, and the character string describing
                    the new advertised value.
            @noreturn
            """
            return await super().registerValueCallback(callback)

    async def turnLedOn(self) -> int:
        """
        Turns on the built-in illumination LEDs using the same current as used during the latest calibration.
        On failure, throws an exception or returns a negative error code.
        """
        return await self.set_ledCurrent(await self.get_ledCalibration())

    async def turnLedOff(self) -> int:
        """
        Turns off the built-in illumination LEDs.
        On failure, throws an exception or returns a negative error code.
        """
        return await self.set_ledCurrent(0)

    # --- (end of YColorSensor implementation)

