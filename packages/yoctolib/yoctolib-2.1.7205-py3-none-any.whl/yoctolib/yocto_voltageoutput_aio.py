# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: svn_id $
#
#  Asyncio implementation of YVoltageOutput
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
Yoctopuce library: Asyncio implementation of YVoltageOutput
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

# --- (YVoltageOutput class start)
if not _IS_MICROPYTHON:
    # For CPython, use strongly typed callback types
    try:
        YVoltageOutputValueCallback = Union[Callable[['YVoltageOutput', str], Any], None]
    except TypeError:
        YVoltageOutputValueCallback = Union[Callable, Awaitable]

# noinspection PyProtectedMember
class YVoltageOutput(YFunction):
    """
    The YVoltageOutput class allows you to drive a voltage output.

    """
    # --- (end of YVoltageOutput class start)
    if not _IS_MICROPYTHON:
        # --- (YVoltageOutput return codes)
        CURRENTVOLTAGE_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        VOLTAGETRANSITION_INVALID: Final[str] = YAPI.INVALID_STRING
        VOLTAGEATSTARTUP_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        # --- (end of YVoltageOutput return codes)

    # --- (YVoltageOutput attributes declaration)
    _currentVoltage: float
    _voltageTransition: str
    _voltageAtStartUp: float
    _valueCallback: YVoltageOutputValueCallback
    # --- (end of YVoltageOutput attributes declaration)


    def __init__(self, yctx: YAPIContext, func: str):
        super().__init__(yctx, func)
        self._className = 'VoltageOutput'
        # --- (YVoltageOutput constructor)
        self._currentVoltage = YVoltageOutput.CURRENTVOLTAGE_INVALID
        self._voltageTransition = YVoltageOutput.VOLTAGETRANSITION_INVALID
        self._voltageAtStartUp = YVoltageOutput.VOLTAGEATSTARTUP_INVALID
        # --- (end of YVoltageOutput constructor)

    # --- (YVoltageOutput implementation)

    @staticmethod
    def FirstVoltageOutput() -> Union[YVoltageOutput, None]:
        """
        Starts the enumeration of voltage outputs currently accessible.
        Use the method YVoltageOutput.nextVoltageOutput() to iterate on
        next voltage outputs.

        @return a pointer to a YVoltageOutput object, corresponding to
                the first voltage output currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = YAPI._yHash.getFirstHardwareId('VoltageOutput')
        if not next_hwid:
            return None
        return YVoltageOutput.FindVoltageOutput(hwid2str(next_hwid))

    @staticmethod
    def FirstVoltageOutputInContext(yctx: YAPIContext) -> Union[YVoltageOutput, None]:
        """
        Starts the enumeration of voltage outputs currently accessible.
        Use the method YVoltageOutput.nextVoltageOutput() to iterate on
        next voltage outputs.

        @param yctx : a YAPI context.

        @return a pointer to a YVoltageOutput object, corresponding to
                the first voltage output currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = yctx._yHash.getFirstHardwareId('VoltageOutput')
        if not next_hwid:
            return None
        return YVoltageOutput.FindVoltageOutputInContext(yctx, hwid2str(next_hwid))

    def nextVoltageOutput(self):
        """
        Continues the enumeration of voltage outputs started using yFirstVoltageOutput().
        Caution: You can't make any assumption about the returned voltage outputs order.
        If you want to find a specific a voltage output, use VoltageOutput.findVoltageOutput()
        and a hardwareID or a logical name.

        @return a pointer to a YVoltageOutput object, corresponding to
                a voltage output currently online, or a None pointer
                if there are no more voltage outputs to enumerate.
        """
        next_hwid: Union[HwId, None] = None
        try:
            hwid: HwId = self._yapi._yHash.resolveHwID(self._className, self._func)
            next_hwid = self._yapi._yHash.getNextHardwareId(self._className, hwid)
        except YAPI_Exception:
            pass
        if not next_hwid:
            return None
        return YVoltageOutput.FindVoltageOutputInContext(self._yapi, hwid2str(next_hwid))

    def _parseAttr(self, json_val: dict) -> None:
        if 'currentVoltage' in json_val:
            self._currentVoltage = round(json_val["currentVoltage"] / 65.536) / 1000.0
        if 'voltageTransition' in json_val:
            self._voltageTransition = json_val["voltageTransition"]
        if 'voltageAtStartUp' in json_val:
            self._voltageAtStartUp = round(json_val["voltageAtStartUp"] / 65.536) / 1000.0
        super()._parseAttr(json_val)

    async def set_currentVoltage(self, newval: float) -> int:
        """
        Changes the output voltage, in V. Valid range is from 0 to 10V.

        @param newval : a floating point number corresponding to the output voltage, in V

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return await self._setAttr("currentVoltage", rest_val)

    async def get_currentVoltage(self) -> float:
        """
        Returns the output voltage set point, in V.

        @return a floating point number corresponding to the output voltage set point, in V

        On failure, throws an exception or returns YVoltageOutput.CURRENTVOLTAGE_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YVoltageOutput.CURRENTVOLTAGE_INVALID
        res = self._currentVoltage
        return res

    async def get_voltageTransition(self) -> str:
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YVoltageOutput.VOLTAGETRANSITION_INVALID
        res = self._voltageTransition
        return res

    async def set_voltageTransition(self, newval: str) -> int:
        rest_val = newval
        return await self._setAttr("voltageTransition", rest_val)

    async def set_voltageAtStartUp(self, newval: float) -> int:
        """
        Changes the output voltage at device start up. Remember to call the matching
        module saveToFlash() method, otherwise this call has no effect.

        @param newval : a floating point number corresponding to the output voltage at device start up

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return await self._setAttr("voltageAtStartUp", rest_val)

    async def get_voltageAtStartUp(self) -> float:
        """
        Returns the selected voltage output at device startup, in V.

        @return a floating point number corresponding to the selected voltage output at device startup, in V

        On failure, throws an exception or returns YVoltageOutput.VOLTAGEATSTARTUP_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YVoltageOutput.VOLTAGEATSTARTUP_INVALID
        res = self._voltageAtStartUp
        return res

    @staticmethod
    def FindVoltageOutput(func: str) -> YVoltageOutput:
        """
        Retrieves a voltage output for a given identifier.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the voltage output is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YVoltageOutput.isOnline() to test if the voltage output is
        indeed online at a given time. In case of ambiguity when looking for
        a voltage output by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the voltage output, for instance
                TX010V01.voltageOutput1.

        @return a YVoltageOutput object allowing you to drive the voltage output.
        """
        obj: Union[YVoltageOutput, None]
        obj = YFunction._FindFromCache("VoltageOutput", func)
        if obj is None:
            obj = YVoltageOutput(YAPI, func)
            YFunction._AddToCache("VoltageOutput", func, obj)
        return obj

    @staticmethod
    def FindVoltageOutputInContext(yctx: YAPIContext, func: str) -> YVoltageOutput:
        """
        Retrieves a voltage output for a given identifier in a YAPI context.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the voltage output is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YVoltageOutput.isOnline() to test if the voltage output is
        indeed online at a given time. In case of ambiguity when looking for
        a voltage output by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        @param yctx : a YAPI context
        @param func : a string that uniquely characterizes the voltage output, for instance
                TX010V01.voltageOutput1.

        @return a YVoltageOutput object allowing you to drive the voltage output.
        """
        obj: Union[YVoltageOutput, None]
        obj = YFunction._FindFromCacheInContext(yctx, "VoltageOutput", func)
        if obj is None:
            obj = YVoltageOutput(yctx, func)
            YFunction._AddToCache("VoltageOutput", func, obj)
        return obj

    if not _IS_MICROPYTHON:
        async def registerValueCallback(self, callback: YVoltageOutputValueCallback) -> int:
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

    async def voltageMove(self, V_target: float, ms_duration: int) -> int:
        """
        Performs a smooth transition of output voltage. Any explicit voltage
        change cancels any ongoing transition process.

        @param V_target   : new output voltage value at the end of the transition
                (floating-point number, representing the end voltage in V)
        @param ms_duration : total duration of the transition, in milliseconds

        @return YAPI.SUCCESS when the call succeeds.
        """
        newval: str
        if V_target < 0.0:
            V_target  = 0.0
        if V_target > 10.0:
            V_target = 10.0
        newval = "%d:%d" % (int(round(V_target*65536)), ms_duration)

        return await self.set_voltageTransition(newval)

    # --- (end of YVoltageOutput implementation)

