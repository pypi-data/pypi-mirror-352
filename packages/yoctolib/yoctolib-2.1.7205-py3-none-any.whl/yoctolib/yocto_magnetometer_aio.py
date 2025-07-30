# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: svn_id $
#
#  Asyncio implementation of YMagnetometer
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
Yoctopuce library: Asyncio implementation of YMagnetometer
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
    YAPIContext, YAPI, YAPI_Exception, HwId, hwid2str, YFunction, YSensor, YMeasure
)

# --- (YMagnetometer class start)
if not _IS_MICROPYTHON:
    # For CPython, use strongly typed callback types
    try:
        YMagnetometerValueCallback = Union[Callable[['YMagnetometer', str], Any], None]
        YMagnetometerTimedReportCallback = Union[Callable[['YMagnetometer', YMeasure], Any], None]
    except TypeError:
        YMagnetometerValueCallback = Union[Callable, Awaitable]
        YMagnetometerTimedReportCallback = Union[Callable, Awaitable]

# noinspection PyProtectedMember
class YMagnetometer(YSensor):
    """
    The YSensor class is the parent class for all Yoctopuce sensor types. It can be
    used to read the current value and unit of any sensor, read the min/max
    value, configure autonomous recording frequency and access recorded data.
    It also provides a function to register a callback invoked each time the
    observed value changes, or at a predefined interval. Using this class rather
    than a specific subclass makes it possible to create generic applications
    that work with any Yoctopuce sensor, even those that do not yet exist.
    Note: The YAnButton class is the only analog input which does not inherit
    from YSensor.

    """
    # --- (end of YMagnetometer class start)
    if not _IS_MICROPYTHON:
        # --- (YMagnetometer return codes)
        BANDWIDTH_INVALID: Final[int] = YAPI.INVALID_UINT
        XVALUE_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        YVALUE_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        ZVALUE_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        # --- (end of YMagnetometer return codes)

    # --- (YMagnetometer attributes declaration)
    _bandwidth: int
    _xValue: float
    _yValue: float
    _zValue: float
    _valueCallback: YMagnetometerValueCallback
    _timedReportCallback: YMagnetometerTimedReportCallback
    # --- (end of YMagnetometer attributes declaration)


    def __init__(self, yctx: YAPIContext, func: str):
        super().__init__(yctx, func)
        self._className = 'Magnetometer'
        # --- (YMagnetometer constructor)
        self._bandwidth = YMagnetometer.BANDWIDTH_INVALID
        self._xValue = YMagnetometer.XVALUE_INVALID
        self._yValue = YMagnetometer.YVALUE_INVALID
        self._zValue = YMagnetometer.ZVALUE_INVALID
        # --- (end of YMagnetometer constructor)

    # --- (YMagnetometer implementation)

    @staticmethod
    def FirstMagnetometer() -> Union[YMagnetometer, None]:
        """
        Starts the enumeration of magnetometers currently accessible.
        Use the method YMagnetometer.nextMagnetometer() to iterate on
        next magnetometers.

        @return a pointer to a YMagnetometer object, corresponding to
                the first magnetometer currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = YAPI._yHash.getFirstHardwareId('Magnetometer')
        if not next_hwid:
            return None
        return YMagnetometer.FindMagnetometer(hwid2str(next_hwid))

    @staticmethod
    def FirstMagnetometerInContext(yctx: YAPIContext) -> Union[YMagnetometer, None]:
        """
        Starts the enumeration of magnetometers currently accessible.
        Use the method YMagnetometer.nextMagnetometer() to iterate on
        next magnetometers.

        @param yctx : a YAPI context.

        @return a pointer to a YMagnetometer object, corresponding to
                the first magnetometer currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = yctx._yHash.getFirstHardwareId('Magnetometer')
        if not next_hwid:
            return None
        return YMagnetometer.FindMagnetometerInContext(yctx, hwid2str(next_hwid))

    def nextMagnetometer(self):
        """
        Continues the enumeration of magnetometers started using yFirstMagnetometer().
        Caution: You can't make any assumption about the returned magnetometers order.
        If you want to find a specific a magnetometer, use Magnetometer.findMagnetometer()
        and a hardwareID or a logical name.

        @return a pointer to a YMagnetometer object, corresponding to
                a magnetometer currently online, or a None pointer
                if there are no more magnetometers to enumerate.
        """
        next_hwid: Union[HwId, None] = None
        try:
            hwid: HwId = self._yapi._yHash.resolveHwID(self._className, self._func)
            next_hwid = self._yapi._yHash.getNextHardwareId(self._className, hwid)
        except YAPI_Exception:
            pass
        if not next_hwid:
            return None
        return YMagnetometer.FindMagnetometerInContext(self._yapi, hwid2str(next_hwid))

    def _parseAttr(self, json_val: dict) -> None:
        if 'bandwidth' in json_val:
            self._bandwidth = json_val["bandwidth"]
        if 'xValue' in json_val:
            self._xValue = round(json_val["xValue"] / 65.536) / 1000.0
        if 'yValue' in json_val:
            self._yValue = round(json_val["yValue"] / 65.536) / 1000.0
        if 'zValue' in json_val:
            self._zValue = round(json_val["zValue"] / 65.536) / 1000.0
        super()._parseAttr(json_val)

    async def get_bandwidth(self) -> int:
        """
        Returns the measure update frequency, measured in Hz.

        @return an integer corresponding to the measure update frequency, measured in Hz

        On failure, throws an exception or returns YMagnetometer.BANDWIDTH_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMagnetometer.BANDWIDTH_INVALID
        res = self._bandwidth
        return res

    async def set_bandwidth(self, newval: int) -> int:
        """
        Changes the measure update frequency, measured in Hz. When the
        frequency is lower, the device performs averaging.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : an integer corresponding to the measure update frequency, measured in Hz

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("bandwidth", rest_val)

    async def get_xValue(self) -> float:
        """
        Returns the X component of the magnetic field, as a floating point number.

        @return a floating point number corresponding to the X component of the magnetic field, as a
        floating point number

        On failure, throws an exception or returns YMagnetometer.XVALUE_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMagnetometer.XVALUE_INVALID
        res = self._xValue
        return res

    async def get_yValue(self) -> float:
        """
        Returns the Y component of the magnetic field, as a floating point number.

        @return a floating point number corresponding to the Y component of the magnetic field, as a
        floating point number

        On failure, throws an exception or returns YMagnetometer.YVALUE_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMagnetometer.YVALUE_INVALID
        res = self._yValue
        return res

    async def get_zValue(self) -> float:
        """
        Returns the Z component of the magnetic field, as a floating point number.

        @return a floating point number corresponding to the Z component of the magnetic field, as a
        floating point number

        On failure, throws an exception or returns YMagnetometer.ZVALUE_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMagnetometer.ZVALUE_INVALID
        res = self._zValue
        return res

    @staticmethod
    def FindMagnetometer(func: str) -> YMagnetometer:
        """
        Retrieves a magnetometer for a given identifier.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the magnetometer is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YMagnetometer.isOnline() to test if the magnetometer is
        indeed online at a given time. In case of ambiguity when looking for
        a magnetometer by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the magnetometer, for instance
                Y3DMK002.magnetometer.

        @return a YMagnetometer object allowing you to drive the magnetometer.
        """
        obj: Union[YMagnetometer, None]
        obj = YFunction._FindFromCache("Magnetometer", func)
        if obj is None:
            obj = YMagnetometer(YAPI, func)
            YFunction._AddToCache("Magnetometer", func, obj)
        return obj

    @staticmethod
    def FindMagnetometerInContext(yctx: YAPIContext, func: str) -> YMagnetometer:
        """
        Retrieves a magnetometer for a given identifier in a YAPI context.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the magnetometer is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YMagnetometer.isOnline() to test if the magnetometer is
        indeed online at a given time. In case of ambiguity when looking for
        a magnetometer by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        @param yctx : a YAPI context
        @param func : a string that uniquely characterizes the magnetometer, for instance
                Y3DMK002.magnetometer.

        @return a YMagnetometer object allowing you to drive the magnetometer.
        """
        obj: Union[YMagnetometer, None]
        obj = YFunction._FindFromCacheInContext(yctx, "Magnetometer", func)
        if obj is None:
            obj = YMagnetometer(yctx, func)
            YFunction._AddToCache("Magnetometer", func, obj)
        return obj

    if not _IS_MICROPYTHON:
        async def registerValueCallback(self, callback: YMagnetometerValueCallback) -> int:
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

    if not _IS_MICROPYTHON:
        async def registerTimedReportCallback(self, callback: YMagnetometerTimedReportCallback) -> int:
            """
            Registers the callback function that is invoked on every periodic timed notification.
            The callback is invoked only during the execution of ySleep or yHandleEvents.
            This provides control over the time when the callback is triggered. For good responsiveness, remember to call
            one of these two functions periodically. To unregister a callback, pass a None pointer as argument.

            @param callback : the callback function to call, or a None pointer. The callback function should take two
                    arguments: the function object of which the value has changed, and an YMeasure object describing
                    the new advertised value.
            @noreturn
            """
            return await super().registerTimedReportCallback(callback)

    # --- (end of YMagnetometer implementation)

