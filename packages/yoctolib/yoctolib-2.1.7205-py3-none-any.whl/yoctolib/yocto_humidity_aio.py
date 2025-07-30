# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: svn_id $
#
#  Asyncio implementation of YHumidity
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
Yoctopuce library: Asyncio implementation of YHumidity
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

# --- (YHumidity class start)
if not _IS_MICROPYTHON:
    # For CPython, use strongly typed callback types
    try:
        YHumidityValueCallback = Union[Callable[['YHumidity', str], Any], None]
        YHumidityTimedReportCallback = Union[Callable[['YHumidity', YMeasure], Any], None]
    except TypeError:
        YHumidityValueCallback = Union[Callable, Awaitable]
        YHumidityTimedReportCallback = Union[Callable, Awaitable]

# noinspection PyProtectedMember
class YHumidity(YSensor):
    """
    The YHumidity class allows you to read and configure Yoctopuce humidity sensors.
    It inherits from YSensor class the core functions to read measures,
    to register callback functions, and to access the autonomous datalogger.

    """
    # --- (end of YHumidity class start)
    if not _IS_MICROPYTHON:
        # --- (YHumidity return codes)
        RELHUM_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        ABSHUM_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        # --- (end of YHumidity return codes)

    # --- (YHumidity attributes declaration)
    _relHum: float
    _absHum: float
    _valueCallback: YHumidityValueCallback
    _timedReportCallback: YHumidityTimedReportCallback
    # --- (end of YHumidity attributes declaration)


    def __init__(self, yctx: YAPIContext, func: str):
        super().__init__(yctx, func)
        self._className = 'Humidity'
        # --- (YHumidity constructor)
        self._relHum = YHumidity.RELHUM_INVALID
        self._absHum = YHumidity.ABSHUM_INVALID
        # --- (end of YHumidity constructor)

    # --- (YHumidity implementation)

    @staticmethod
    def FirstHumidity() -> Union[YHumidity, None]:
        """
        Starts the enumeration of humidity sensors currently accessible.
        Use the method YHumidity.nextHumidity() to iterate on
        next humidity sensors.

        @return a pointer to a YHumidity object, corresponding to
                the first humidity sensor currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = YAPI._yHash.getFirstHardwareId('Humidity')
        if not next_hwid:
            return None
        return YHumidity.FindHumidity(hwid2str(next_hwid))

    @staticmethod
    def FirstHumidityInContext(yctx: YAPIContext) -> Union[YHumidity, None]:
        """
        Starts the enumeration of humidity sensors currently accessible.
        Use the method YHumidity.nextHumidity() to iterate on
        next humidity sensors.

        @param yctx : a YAPI context.

        @return a pointer to a YHumidity object, corresponding to
                the first humidity sensor currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = yctx._yHash.getFirstHardwareId('Humidity')
        if not next_hwid:
            return None
        return YHumidity.FindHumidityInContext(yctx, hwid2str(next_hwid))

    def nextHumidity(self):
        """
        Continues the enumeration of humidity sensors started using yFirstHumidity().
        Caution: You can't make any assumption about the returned humidity sensors order.
        If you want to find a specific a humidity sensor, use Humidity.findHumidity()
        and a hardwareID or a logical name.

        @return a pointer to a YHumidity object, corresponding to
                a humidity sensor currently online, or a None pointer
                if there are no more humidity sensors to enumerate.
        """
        next_hwid: Union[HwId, None] = None
        try:
            hwid: HwId = self._yapi._yHash.resolveHwID(self._className, self._func)
            next_hwid = self._yapi._yHash.getNextHardwareId(self._className, hwid)
        except YAPI_Exception:
            pass
        if not next_hwid:
            return None
        return YHumidity.FindHumidityInContext(self._yapi, hwid2str(next_hwid))

    def _parseAttr(self, json_val: dict) -> None:
        if 'relHum' in json_val:
            self._relHum = round(json_val["relHum"] / 65.536) / 1000.0
        if 'absHum' in json_val:
            self._absHum = round(json_val["absHum"] / 65.536) / 1000.0
        super()._parseAttr(json_val)

    async def set_unit(self, newval: str) -> int:
        """
        Changes the primary unit for measuring humidity. That unit is a string.
        If that strings starts with the letter 'g', the primary measured value is the absolute
        humidity, in g/m3. Otherwise, the primary measured value will be the relative humidity
        (RH), in per cents.

        Remember to call the saveToFlash() method of the module if the modification
        must be kept.

        @param newval : a string corresponding to the primary unit for measuring humidity

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return await self._setAttr("unit", rest_val)

    async def get_relHum(self) -> float:
        """
        Returns the current relative humidity, in per cents.

        @return a floating point number corresponding to the current relative humidity, in per cents

        On failure, throws an exception or returns YHumidity.RELHUM_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YHumidity.RELHUM_INVALID
        res = self._relHum
        return res

    async def get_absHum(self) -> float:
        """
        Returns the current absolute humidity, in grams per cubic meter of air.

        @return a floating point number corresponding to the current absolute humidity, in grams per cubic meter of air

        On failure, throws an exception or returns YHumidity.ABSHUM_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YHumidity.ABSHUM_INVALID
        res = self._absHum
        return res

    @staticmethod
    def FindHumidity(func: str) -> YHumidity:
        """
        Retrieves a humidity sensor for a given identifier.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the humidity sensor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YHumidity.isOnline() to test if the humidity sensor is
        indeed online at a given time. In case of ambiguity when looking for
        a humidity sensor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the humidity sensor, for instance
                YCO2MK02.humidity.

        @return a YHumidity object allowing you to drive the humidity sensor.
        """
        obj: Union[YHumidity, None]
        obj = YFunction._FindFromCache("Humidity", func)
        if obj is None:
            obj = YHumidity(YAPI, func)
            YFunction._AddToCache("Humidity", func, obj)
        return obj

    @staticmethod
    def FindHumidityInContext(yctx: YAPIContext, func: str) -> YHumidity:
        """
        Retrieves a humidity sensor for a given identifier in a YAPI context.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the humidity sensor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YHumidity.isOnline() to test if the humidity sensor is
        indeed online at a given time. In case of ambiguity when looking for
        a humidity sensor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        @param yctx : a YAPI context
        @param func : a string that uniquely characterizes the humidity sensor, for instance
                YCO2MK02.humidity.

        @return a YHumidity object allowing you to drive the humidity sensor.
        """
        obj: Union[YHumidity, None]
        obj = YFunction._FindFromCacheInContext(yctx, "Humidity", func)
        if obj is None:
            obj = YHumidity(yctx, func)
            YFunction._AddToCache("Humidity", func, obj)
        return obj

    if not _IS_MICROPYTHON:
        async def registerValueCallback(self, callback: YHumidityValueCallback) -> int:
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
        async def registerTimedReportCallback(self, callback: YHumidityTimedReportCallback) -> int:
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

    # --- (end of YHumidity implementation)

