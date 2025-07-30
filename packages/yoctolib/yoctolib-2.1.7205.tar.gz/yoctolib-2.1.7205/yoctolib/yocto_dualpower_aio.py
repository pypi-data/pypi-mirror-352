# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: svn_id $
#
#  Asyncio implementation of YDualPower
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
Yoctopuce library: Asyncio implementation of YDualPower
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

# --- (YDualPower class start)
if not _IS_MICROPYTHON:
    # For CPython, use strongly typed callback types
    try:
        YDualPowerValueCallback = Union[Callable[['YDualPower', str], Any], None]
    except TypeError:
        YDualPowerValueCallback = Union[Callable, Awaitable]

# noinspection PyProtectedMember
class YDualPower(YFunction):
    """
    The YDualPower class allows you to control
    the power source to use for module functions that require high current.
    The module can also automatically disconnect the external power
    when a voltage drop is observed on the external power source
    (external battery running out of power).

    """
    # --- (end of YDualPower class start)
    if not _IS_MICROPYTHON:
        # --- (YDualPower return codes)
        EXTVOLTAGE_INVALID: Final[int] = YAPI.INVALID_UINT
        POWERSTATE_OFF: Final[int] = 0
        POWERSTATE_FROM_USB: Final[int] = 1
        POWERSTATE_FROM_EXT: Final[int] = 2
        POWERSTATE_INVALID: Final[int] = -1
        POWERCONTROL_AUTO: Final[int] = 0
        POWERCONTROL_FROM_USB: Final[int] = 1
        POWERCONTROL_FROM_EXT: Final[int] = 2
        POWERCONTROL_OFF: Final[int] = 3
        POWERCONTROL_INVALID: Final[int] = -1
        # --- (end of YDualPower return codes)

    # --- (YDualPower attributes declaration)
    _powerState: int
    _powerControl: int
    _extVoltage: int
    _valueCallback: YDualPowerValueCallback
    # --- (end of YDualPower attributes declaration)


    def __init__(self, yctx: YAPIContext, func: str):
        super().__init__(yctx, func)
        self._className = 'DualPower'
        # --- (YDualPower constructor)
        self._powerState = YDualPower.POWERSTATE_INVALID
        self._powerControl = YDualPower.POWERCONTROL_INVALID
        self._extVoltage = YDualPower.EXTVOLTAGE_INVALID
        # --- (end of YDualPower constructor)

    # --- (YDualPower implementation)

    @staticmethod
    def FirstDualPower() -> Union[YDualPower, None]:
        """
        Starts the enumeration of dual power switches currently accessible.
        Use the method YDualPower.nextDualPower() to iterate on
        next dual power switches.

        @return a pointer to a YDualPower object, corresponding to
                the first dual power switch currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = YAPI._yHash.getFirstHardwareId('DualPower')
        if not next_hwid:
            return None
        return YDualPower.FindDualPower(hwid2str(next_hwid))

    @staticmethod
    def FirstDualPowerInContext(yctx: YAPIContext) -> Union[YDualPower, None]:
        """
        Starts the enumeration of dual power switches currently accessible.
        Use the method YDualPower.nextDualPower() to iterate on
        next dual power switches.

        @param yctx : a YAPI context.

        @return a pointer to a YDualPower object, corresponding to
                the first dual power switch currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = yctx._yHash.getFirstHardwareId('DualPower')
        if not next_hwid:
            return None
        return YDualPower.FindDualPowerInContext(yctx, hwid2str(next_hwid))

    def nextDualPower(self):
        """
        Continues the enumeration of dual power switches started using yFirstDualPower().
        Caution: You can't make any assumption about the returned dual power switches order.
        If you want to find a specific a dual power switch, use DualPower.findDualPower()
        and a hardwareID or a logical name.

        @return a pointer to a YDualPower object, corresponding to
                a dual power switch currently online, or a None pointer
                if there are no more dual power switches to enumerate.
        """
        next_hwid: Union[HwId, None] = None
        try:
            hwid: HwId = self._yapi._yHash.resolveHwID(self._className, self._func)
            next_hwid = self._yapi._yHash.getNextHardwareId(self._className, hwid)
        except YAPI_Exception:
            pass
        if not next_hwid:
            return None
        return YDualPower.FindDualPowerInContext(self._yapi, hwid2str(next_hwid))

    def _parseAttr(self, json_val: dict) -> None:
        if 'powerState' in json_val:
            self._powerState = json_val["powerState"]
        if 'powerControl' in json_val:
            self._powerControl = json_val["powerControl"]
        if 'extVoltage' in json_val:
            self._extVoltage = json_val["extVoltage"]
        super()._parseAttr(json_val)

    async def get_powerState(self) -> int:
        """
        Returns the current power source for module functions that require lots of current.

        @return a value among YDualPower.POWERSTATE_OFF, YDualPower.POWERSTATE_FROM_USB and
        YDualPower.POWERSTATE_FROM_EXT corresponding to the current power source for module functions that
        require lots of current

        On failure, throws an exception or returns YDualPower.POWERSTATE_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YDualPower.POWERSTATE_INVALID
        res = self._powerState
        return res

    async def get_powerControl(self) -> int:
        """
        Returns the selected power source for module functions that require lots of current.

        @return a value among YDualPower.POWERCONTROL_AUTO, YDualPower.POWERCONTROL_FROM_USB,
        YDualPower.POWERCONTROL_FROM_EXT and YDualPower.POWERCONTROL_OFF corresponding to the selected
        power source for module functions that require lots of current

        On failure, throws an exception or returns YDualPower.POWERCONTROL_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YDualPower.POWERCONTROL_INVALID
        res = self._powerControl
        return res

    async def set_powerControl(self, newval: int) -> int:
        """
        Changes the selected power source for module functions that require lots of current.
        Remember to call the saveToFlash() method of the module if the modification must be kept.

        @param newval : a value among YDualPower.POWERCONTROL_AUTO, YDualPower.POWERCONTROL_FROM_USB,
        YDualPower.POWERCONTROL_FROM_EXT and YDualPower.POWERCONTROL_OFF corresponding to the selected
        power source for module functions that require lots of current

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("powerControl", rest_val)

    async def get_extVoltage(self) -> int:
        """
        Returns the measured voltage on the external power source, in millivolts.

        @return an integer corresponding to the measured voltage on the external power source, in millivolts

        On failure, throws an exception or returns YDualPower.EXTVOLTAGE_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YDualPower.EXTVOLTAGE_INVALID
        res = self._extVoltage
        return res

    @staticmethod
    def FindDualPower(func: str) -> YDualPower:
        """
        Retrieves a dual power switch for a given identifier.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the dual power switch is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YDualPower.isOnline() to test if the dual power switch is
        indeed online at a given time. In case of ambiguity when looking for
        a dual power switch by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the dual power switch, for instance
                SERVORC1.dualPower.

        @return a YDualPower object allowing you to drive the dual power switch.
        """
        obj: Union[YDualPower, None]
        obj = YFunction._FindFromCache("DualPower", func)
        if obj is None:
            obj = YDualPower(YAPI, func)
            YFunction._AddToCache("DualPower", func, obj)
        return obj

    @staticmethod
    def FindDualPowerInContext(yctx: YAPIContext, func: str) -> YDualPower:
        """
        Retrieves a dual power switch for a given identifier in a YAPI context.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the dual power switch is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YDualPower.isOnline() to test if the dual power switch is
        indeed online at a given time. In case of ambiguity when looking for
        a dual power switch by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        @param yctx : a YAPI context
        @param func : a string that uniquely characterizes the dual power switch, for instance
                SERVORC1.dualPower.

        @return a YDualPower object allowing you to drive the dual power switch.
        """
        obj: Union[YDualPower, None]
        obj = YFunction._FindFromCacheInContext(yctx, "DualPower", func)
        if obj is None:
            obj = YDualPower(yctx, func)
            YFunction._AddToCache("DualPower", func, obj)
        return obj

    if not _IS_MICROPYTHON:
        async def registerValueCallback(self, callback: YDualPowerValueCallback) -> int:
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

    # --- (end of YDualPower implementation)

