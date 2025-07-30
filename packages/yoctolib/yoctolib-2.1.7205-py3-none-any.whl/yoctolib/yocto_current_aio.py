# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: svn_id $
#
#  Asyncio implementation of YCurrent
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
Yoctopuce library: Asyncio implementation of YCurrent
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

# --- (YCurrent class start)
if not _IS_MICROPYTHON:
    # For CPython, use strongly typed callback types
    try:
        YCurrentValueCallback = Union[Callable[['YCurrent', str], Any], None]
        YCurrentTimedReportCallback = Union[Callable[['YCurrent', YMeasure], Any], None]
    except TypeError:
        YCurrentValueCallback = Union[Callable, Awaitable]
        YCurrentTimedReportCallback = Union[Callable, Awaitable]

# noinspection PyProtectedMember
class YCurrent(YSensor):
    """
    The YCurrent class allows you to read and configure Yoctopuce current sensors.
    It inherits from YSensor class the core functions to read measures,
    to register callback functions, and to access the autonomous datalogger.

    """
    # --- (end of YCurrent class start)
    if not _IS_MICROPYTHON:
        # --- (YCurrent return codes)
        ENABLED_FALSE: Final[int] = 0
        ENABLED_TRUE: Final[int] = 1
        ENABLED_INVALID: Final[int] = -1
        # --- (end of YCurrent return codes)

    # --- (YCurrent attributes declaration)
    _enabled: int
    _valueCallback: YCurrentValueCallback
    _timedReportCallback: YCurrentTimedReportCallback
    # --- (end of YCurrent attributes declaration)


    def __init__(self, yctx: YAPIContext, func: str):
        super().__init__(yctx, func)
        self._className = 'Current'
        # --- (YCurrent constructor)
        self._enabled = YCurrent.ENABLED_INVALID
        # --- (end of YCurrent constructor)

    # --- (YCurrent implementation)

    @staticmethod
    def FirstCurrent() -> Union[YCurrent, None]:
        """
        Starts the enumeration of current sensors currently accessible.
        Use the method YCurrent.nextCurrent() to iterate on
        next current sensors.

        @return a pointer to a YCurrent object, corresponding to
                the first current sensor currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = YAPI._yHash.getFirstHardwareId('Current')
        if not next_hwid:
            return None
        return YCurrent.FindCurrent(hwid2str(next_hwid))

    @staticmethod
    def FirstCurrentInContext(yctx: YAPIContext) -> Union[YCurrent, None]:
        """
        Starts the enumeration of current sensors currently accessible.
        Use the method YCurrent.nextCurrent() to iterate on
        next current sensors.

        @param yctx : a YAPI context.

        @return a pointer to a YCurrent object, corresponding to
                the first current sensor currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = yctx._yHash.getFirstHardwareId('Current')
        if not next_hwid:
            return None
        return YCurrent.FindCurrentInContext(yctx, hwid2str(next_hwid))

    def nextCurrent(self):
        """
        Continues the enumeration of current sensors started using yFirstCurrent().
        Caution: You can't make any assumption about the returned current sensors order.
        If you want to find a specific a current sensor, use Current.findCurrent()
        and a hardwareID or a logical name.

        @return a pointer to a YCurrent object, corresponding to
                a current sensor currently online, or a None pointer
                if there are no more current sensors to enumerate.
        """
        next_hwid: Union[HwId, None] = None
        try:
            hwid: HwId = self._yapi._yHash.resolveHwID(self._className, self._func)
            next_hwid = self._yapi._yHash.getNextHardwareId(self._className, hwid)
        except YAPI_Exception:
            pass
        if not next_hwid:
            return None
        return YCurrent.FindCurrentInContext(self._yapi, hwid2str(next_hwid))

    def _parseAttr(self, json_val: dict) -> None:
        if 'enabled' in json_val:
            self._enabled = json_val["enabled"] > 0
        super()._parseAttr(json_val)

    async def get_enabled(self) -> int:
        """
        Returns the activation state of this input.

        @return either YCurrent.ENABLED_FALSE or YCurrent.ENABLED_TRUE, according to the activation state of this input

        On failure, throws an exception or returns YCurrent.ENABLED_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YCurrent.ENABLED_INVALID
        res = self._enabled
        return res

    async def set_enabled(self, newval: int) -> int:
        """
        Changes the activation state of this voltage input. When AC measures are disabled,
        the device will always assume a DC signal, and vice-versa. When both AC and DC measures
        are active, the device switches between AC and DC mode based on the relative amplitude
        of variations compared to the average value.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : either YCurrent.ENABLED_FALSE or YCurrent.ENABLED_TRUE, according to the activation
        state of this voltage input

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return await self._setAttr("enabled", rest_val)

    @staticmethod
    def FindCurrent(func: str) -> YCurrent:
        """
        Retrieves a current sensor for a given identifier.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the current sensor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YCurrent.isOnline() to test if the current sensor is
        indeed online at a given time. In case of ambiguity when looking for
        a current sensor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the current sensor, for instance
                YAMPMK01.current1.

        @return a YCurrent object allowing you to drive the current sensor.
        """
        obj: Union[YCurrent, None]
        obj = YFunction._FindFromCache("Current", func)
        if obj is None:
            obj = YCurrent(YAPI, func)
            YFunction._AddToCache("Current", func, obj)
        return obj

    @staticmethod
    def FindCurrentInContext(yctx: YAPIContext, func: str) -> YCurrent:
        """
        Retrieves a current sensor for a given identifier in a YAPI context.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the current sensor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YCurrent.isOnline() to test if the current sensor is
        indeed online at a given time. In case of ambiguity when looking for
        a current sensor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        @param yctx : a YAPI context
        @param func : a string that uniquely characterizes the current sensor, for instance
                YAMPMK01.current1.

        @return a YCurrent object allowing you to drive the current sensor.
        """
        obj: Union[YCurrent, None]
        obj = YFunction._FindFromCacheInContext(yctx, "Current", func)
        if obj is None:
            obj = YCurrent(yctx, func)
            YFunction._AddToCache("Current", func, obj)
        return obj

    if not _IS_MICROPYTHON:
        async def registerValueCallback(self, callback: YCurrentValueCallback) -> int:
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
        async def registerTimedReportCallback(self, callback: YCurrentTimedReportCallback) -> int:
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

    # --- (end of YCurrent implementation)

