# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: svn_id $
#
#  Asyncio implementation of YPowerSupply
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
Yoctopuce library: Asyncio implementation of YPowerSupply
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

# --- (YPowerSupply class start)
if not _IS_MICROPYTHON:
    # For CPython, use strongly typed callback types
    try:
        YPowerSupplyValueCallback = Union[Callable[['YPowerSupply', str], Any], None]
    except TypeError:
        YPowerSupplyValueCallback = Union[Callable, Awaitable]

# noinspection PyProtectedMember
class YPowerSupply(YFunction):
    """
    The YPowerSupply class allows you to drive a Yoctopuce power supply.
    It can be use to change the voltage and current limits, and to enable/disable
    the output.

    """
    # --- (end of YPowerSupply class start)
    if not _IS_MICROPYTHON:
        # --- (YPowerSupply return codes)
        VOLTAGELIMIT_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        CURRENTLIMIT_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        MEASUREDVOLTAGE_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        MEASUREDCURRENT_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        INPUTVOLTAGE_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        VOLTAGETRANSITION_INVALID: Final[str] = YAPI.INVALID_STRING
        VOLTAGELIMITATSTARTUP_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        CURRENTLIMITATSTARTUP_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        COMMAND_INVALID: Final[str] = YAPI.INVALID_STRING
        POWEROUTPUT_OFF: Final[int] = 0
        POWEROUTPUT_ON: Final[int] = 1
        POWEROUTPUT_INVALID: Final[int] = -1
        POWEROUTPUTATSTARTUP_OFF: Final[int] = 0
        POWEROUTPUTATSTARTUP_ON: Final[int] = 1
        POWEROUTPUTATSTARTUP_INVALID: Final[int] = -1
        # --- (end of YPowerSupply return codes)

    # --- (YPowerSupply attributes declaration)
    _voltageLimit: float
    _currentLimit: float
    _powerOutput: int
    _measuredVoltage: float
    _measuredCurrent: float
    _inputVoltage: float
    _voltageTransition: str
    _voltageLimitAtStartUp: float
    _currentLimitAtStartUp: float
    _powerOutputAtStartUp: int
    _command: str
    _valueCallback: YPowerSupplyValueCallback
    # --- (end of YPowerSupply attributes declaration)


    def __init__(self, yctx: YAPIContext, func: str):
        super().__init__(yctx, func)
        self._className = 'PowerSupply'
        # --- (YPowerSupply constructor)
        self._voltageLimit = YPowerSupply.VOLTAGELIMIT_INVALID
        self._currentLimit = YPowerSupply.CURRENTLIMIT_INVALID
        self._powerOutput = YPowerSupply.POWEROUTPUT_INVALID
        self._measuredVoltage = YPowerSupply.MEASUREDVOLTAGE_INVALID
        self._measuredCurrent = YPowerSupply.MEASUREDCURRENT_INVALID
        self._inputVoltage = YPowerSupply.INPUTVOLTAGE_INVALID
        self._voltageTransition = YPowerSupply.VOLTAGETRANSITION_INVALID
        self._voltageLimitAtStartUp = YPowerSupply.VOLTAGELIMITATSTARTUP_INVALID
        self._currentLimitAtStartUp = YPowerSupply.CURRENTLIMITATSTARTUP_INVALID
        self._powerOutputAtStartUp = YPowerSupply.POWEROUTPUTATSTARTUP_INVALID
        self._command = YPowerSupply.COMMAND_INVALID
        # --- (end of YPowerSupply constructor)

    # --- (YPowerSupply implementation)

    @staticmethod
    def FirstPowerSupply() -> Union[YPowerSupply, None]:
        """
        Starts the enumeration of regulated power supplies currently accessible.
        Use the method YPowerSupply.nextPowerSupply() to iterate on
        next regulated power supplies.

        @return a pointer to a YPowerSupply object, corresponding to
                the first regulated power supply currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = YAPI._yHash.getFirstHardwareId('PowerSupply')
        if not next_hwid:
            return None
        return YPowerSupply.FindPowerSupply(hwid2str(next_hwid))

    @staticmethod
    def FirstPowerSupplyInContext(yctx: YAPIContext) -> Union[YPowerSupply, None]:
        """
        Starts the enumeration of regulated power supplies currently accessible.
        Use the method YPowerSupply.nextPowerSupply() to iterate on
        next regulated power supplies.

        @param yctx : a YAPI context.

        @return a pointer to a YPowerSupply object, corresponding to
                the first regulated power supply currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = yctx._yHash.getFirstHardwareId('PowerSupply')
        if not next_hwid:
            return None
        return YPowerSupply.FindPowerSupplyInContext(yctx, hwid2str(next_hwid))

    def nextPowerSupply(self):
        """
        Continues the enumeration of regulated power supplies started using yFirstPowerSupply().
        Caution: You can't make any assumption about the returned regulated power supplies order.
        If you want to find a specific a regulated power supply, use PowerSupply.findPowerSupply()
        and a hardwareID or a logical name.

        @return a pointer to a YPowerSupply object, corresponding to
                a regulated power supply currently online, or a None pointer
                if there are no more regulated power supplies to enumerate.
        """
        next_hwid: Union[HwId, None] = None
        try:
            hwid: HwId = self._yapi._yHash.resolveHwID(self._className, self._func)
            next_hwid = self._yapi._yHash.getNextHardwareId(self._className, hwid)
        except YAPI_Exception:
            pass
        if not next_hwid:
            return None
        return YPowerSupply.FindPowerSupplyInContext(self._yapi, hwid2str(next_hwid))

    def _parseAttr(self, json_val: dict) -> None:
        if 'voltageLimit' in json_val:
            self._voltageLimit = round(json_val["voltageLimit"] / 65.536) / 1000.0
        if 'currentLimit' in json_val:
            self._currentLimit = round(json_val["currentLimit"] / 65.536) / 1000.0
        if 'powerOutput' in json_val:
            self._powerOutput = json_val["powerOutput"] > 0
        if 'measuredVoltage' in json_val:
            self._measuredVoltage = round(json_val["measuredVoltage"] / 65.536) / 1000.0
        if 'measuredCurrent' in json_val:
            self._measuredCurrent = round(json_val["measuredCurrent"] / 65.536) / 1000.0
        if 'inputVoltage' in json_val:
            self._inputVoltage = round(json_val["inputVoltage"] / 65.536) / 1000.0
        if 'voltageTransition' in json_val:
            self._voltageTransition = json_val["voltageTransition"]
        if 'voltageLimitAtStartUp' in json_val:
            self._voltageLimitAtStartUp = round(json_val["voltageLimitAtStartUp"] / 65.536) / 1000.0
        if 'currentLimitAtStartUp' in json_val:
            self._currentLimitAtStartUp = round(json_val["currentLimitAtStartUp"] / 65.536) / 1000.0
        if 'powerOutputAtStartUp' in json_val:
            self._powerOutputAtStartUp = json_val["powerOutputAtStartUp"] > 0
        if 'command' in json_val:
            self._command = json_val["command"]
        super()._parseAttr(json_val)

    async def set_voltageLimit(self, newval: float) -> int:
        """
        Changes the voltage limit, in V.

        @param newval : a floating point number corresponding to the voltage limit, in V

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return await self._setAttr("voltageLimit", rest_val)

    async def get_voltageLimit(self) -> float:
        """
        Returns the voltage limit, in V.

        @return a floating point number corresponding to the voltage limit, in V

        On failure, throws an exception or returns YPowerSupply.VOLTAGELIMIT_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YPowerSupply.VOLTAGELIMIT_INVALID
        res = self._voltageLimit
        return res

    async def set_currentLimit(self, newval: float) -> int:
        """
        Changes the current limit, in mA.

        @param newval : a floating point number corresponding to the current limit, in mA

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return await self._setAttr("currentLimit", rest_val)

    async def get_currentLimit(self) -> float:
        """
        Returns the current limit, in mA.

        @return a floating point number corresponding to the current limit, in mA

        On failure, throws an exception or returns YPowerSupply.CURRENTLIMIT_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YPowerSupply.CURRENTLIMIT_INVALID
        res = self._currentLimit
        return res

    async def get_powerOutput(self) -> int:
        """
        Returns the power supply output switch state.

        @return either YPowerSupply.POWEROUTPUT_OFF or YPowerSupply.POWEROUTPUT_ON, according to the power
        supply output switch state

        On failure, throws an exception or returns YPowerSupply.POWEROUTPUT_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YPowerSupply.POWEROUTPUT_INVALID
        res = self._powerOutput
        return res

    async def set_powerOutput(self, newval: int) -> int:
        """
        Changes the power supply output switch state.

        @param newval : either YPowerSupply.POWEROUTPUT_OFF or YPowerSupply.POWEROUTPUT_ON, according to
        the power supply output switch state

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return await self._setAttr("powerOutput", rest_val)

    async def get_measuredVoltage(self) -> float:
        """
        Returns the measured output voltage, in V.

        @return a floating point number corresponding to the measured output voltage, in V

        On failure, throws an exception or returns YPowerSupply.MEASUREDVOLTAGE_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YPowerSupply.MEASUREDVOLTAGE_INVALID
        res = self._measuredVoltage
        return res

    async def get_measuredCurrent(self) -> float:
        """
        Returns the measured output current, in mA.

        @return a floating point number corresponding to the measured output current, in mA

        On failure, throws an exception or returns YPowerSupply.MEASUREDCURRENT_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YPowerSupply.MEASUREDCURRENT_INVALID
        res = self._measuredCurrent
        return res

    async def get_inputVoltage(self) -> float:
        """
        Returns the measured input voltage, in V.

        @return a floating point number corresponding to the measured input voltage, in V

        On failure, throws an exception or returns YPowerSupply.INPUTVOLTAGE_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YPowerSupply.INPUTVOLTAGE_INVALID
        res = self._inputVoltage
        return res

    async def get_voltageTransition(self) -> str:
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YPowerSupply.VOLTAGETRANSITION_INVALID
        res = self._voltageTransition
        return res

    async def set_voltageTransition(self, newval: str) -> int:
        rest_val = newval
        return await self._setAttr("voltageTransition", rest_val)

    async def set_voltageLimitAtStartUp(self, newval: float) -> int:
        """
        Changes the voltage set point at device start up. Remember to call the matching
        module saveToFlash() method, otherwise this call has no effect.

        @param newval : a floating point number corresponding to the voltage set point at device start up

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return await self._setAttr("voltageLimitAtStartUp", rest_val)

    async def get_voltageLimitAtStartUp(self) -> float:
        """
        Returns the selected voltage limit at device startup, in V.

        @return a floating point number corresponding to the selected voltage limit at device startup, in V

        On failure, throws an exception or returns YPowerSupply.VOLTAGELIMITATSTARTUP_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YPowerSupply.VOLTAGELIMITATSTARTUP_INVALID
        res = self._voltageLimitAtStartUp
        return res

    async def set_currentLimitAtStartUp(self, newval: float) -> int:
        """
        Changes the current limit at device start up. Remember to call the matching
        module saveToFlash() method, otherwise this call has no effect.

        @param newval : a floating point number corresponding to the current limit at device start up

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return await self._setAttr("currentLimitAtStartUp", rest_val)

    async def get_currentLimitAtStartUp(self) -> float:
        """
        Returns the selected current limit at device startup, in mA.

        @return a floating point number corresponding to the selected current limit at device startup, in mA

        On failure, throws an exception or returns YPowerSupply.CURRENTLIMITATSTARTUP_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YPowerSupply.CURRENTLIMITATSTARTUP_INVALID
        res = self._currentLimitAtStartUp
        return res

    async def get_powerOutputAtStartUp(self) -> int:
        """
        Returns the power supply output switch state.

        @return either YPowerSupply.POWEROUTPUTATSTARTUP_OFF or YPowerSupply.POWEROUTPUTATSTARTUP_ON,
        according to the power supply output switch state

        On failure, throws an exception or returns YPowerSupply.POWEROUTPUTATSTARTUP_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YPowerSupply.POWEROUTPUTATSTARTUP_INVALID
        res = self._powerOutputAtStartUp
        return res

    async def set_powerOutputAtStartUp(self, newval: int) -> int:
        """
        Changes the power supply output switch state at device start up. Remember to call the matching
        module saveToFlash() method, otherwise this call has no effect.

        @param newval : either YPowerSupply.POWEROUTPUTATSTARTUP_OFF or
        YPowerSupply.POWEROUTPUTATSTARTUP_ON, according to the power supply output switch state at device start up

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return await self._setAttr("powerOutputAtStartUp", rest_val)

    async def get_command(self) -> str:
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YPowerSupply.COMMAND_INVALID
        res = self._command
        return res

    async def set_command(self, newval: str) -> int:
        rest_val = newval
        return await self._setAttr("command", rest_val)

    @staticmethod
    def FindPowerSupply(func: str) -> YPowerSupply:
        """
        Retrieves a regulated power supply for a given identifier.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the regulated power supply is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YPowerSupply.isOnline() to test if the regulated power supply is
        indeed online at a given time. In case of ambiguity when looking for
        a regulated power supply by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the regulated power supply, for instance
                MyDevice.powerSupply.

        @return a YPowerSupply object allowing you to drive the regulated power supply.
        """
        obj: Union[YPowerSupply, None]
        obj = YFunction._FindFromCache("PowerSupply", func)
        if obj is None:
            obj = YPowerSupply(YAPI, func)
            YFunction._AddToCache("PowerSupply", func, obj)
        return obj

    @staticmethod
    def FindPowerSupplyInContext(yctx: YAPIContext, func: str) -> YPowerSupply:
        """
        Retrieves a regulated power supply for a given identifier in a YAPI context.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the regulated power supply is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YPowerSupply.isOnline() to test if the regulated power supply is
        indeed online at a given time. In case of ambiguity when looking for
        a regulated power supply by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        @param yctx : a YAPI context
        @param func : a string that uniquely characterizes the regulated power supply, for instance
                MyDevice.powerSupply.

        @return a YPowerSupply object allowing you to drive the regulated power supply.
        """
        obj: Union[YPowerSupply, None]
        obj = YFunction._FindFromCacheInContext(yctx, "PowerSupply", func)
        if obj is None:
            obj = YPowerSupply(yctx, func)
            YFunction._AddToCache("PowerSupply", func, obj)
        return obj

    if not _IS_MICROPYTHON:
        async def registerValueCallback(self, callback: YPowerSupplyValueCallback) -> int:
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
        newval = "%d:%d" % (int(round(V_target*65536)), ms_duration)

        return await self.set_voltageTransition(newval)

    # --- (end of YPowerSupply implementation)

