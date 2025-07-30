# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: svn_id $
#
#  Asyncio implementation of YHubPort
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
Yoctopuce library: Asyncio implementation of YHubPort
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

# --- (YHubPort class start)
if not _IS_MICROPYTHON:
    # For CPython, use strongly typed callback types
    try:
        YHubPortValueCallback = Union[Callable[['YHubPort', str], Any], None]
    except TypeError:
        YHubPortValueCallback = Union[Callable, Awaitable]

# noinspection PyProtectedMember
class YHubPort(YFunction):
    """
    The YHubPort class provides control over the power supply for slave ports
    on a YoctoHub. It provide information about the device connected to it.
    The logical name of a YHubPort is always automatically set to the
    unique serial number of the Yoctopuce device connected to it.

    """
    # --- (end of YHubPort class start)
    if not _IS_MICROPYTHON:
        # --- (YHubPort return codes)
        BAUDRATE_INVALID: Final[int] = YAPI.INVALID_UINT
        ENABLED_FALSE: Final[int] = 0
        ENABLED_TRUE: Final[int] = 1
        ENABLED_INVALID: Final[int] = -1
        PORTSTATE_OFF: Final[int] = 0
        PORTSTATE_OVRLD: Final[int] = 1
        PORTSTATE_ON: Final[int] = 2
        PORTSTATE_RUN: Final[int] = 3
        PORTSTATE_PROG: Final[int] = 4
        PORTSTATE_INVALID: Final[int] = -1
        # --- (end of YHubPort return codes)

    # --- (YHubPort attributes declaration)
    _enabled: int
    _portState: int
    _baudRate: int
    _valueCallback: YHubPortValueCallback
    # --- (end of YHubPort attributes declaration)


    def __init__(self, yctx: YAPIContext, func: str):
        super().__init__(yctx, func)
        self._className = 'HubPort'
        # --- (YHubPort constructor)
        self._enabled = YHubPort.ENABLED_INVALID
        self._portState = YHubPort.PORTSTATE_INVALID
        self._baudRate = YHubPort.BAUDRATE_INVALID
        # --- (end of YHubPort constructor)

    # --- (YHubPort implementation)

    @staticmethod
    def FirstHubPort() -> Union[YHubPort, None]:
        """
        Starts the enumeration of YoctoHub slave ports currently accessible.
        Use the method YHubPort.nextHubPort() to iterate on
        next YoctoHub slave ports.

        @return a pointer to a YHubPort object, corresponding to
                the first YoctoHub slave port currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = YAPI._yHash.getFirstHardwareId('HubPort')
        if not next_hwid:
            return None
        return YHubPort.FindHubPort(hwid2str(next_hwid))

    @staticmethod
    def FirstHubPortInContext(yctx: YAPIContext) -> Union[YHubPort, None]:
        """
        Starts the enumeration of YoctoHub slave ports currently accessible.
        Use the method YHubPort.nextHubPort() to iterate on
        next YoctoHub slave ports.

        @param yctx : a YAPI context.

        @return a pointer to a YHubPort object, corresponding to
                the first YoctoHub slave port currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = yctx._yHash.getFirstHardwareId('HubPort')
        if not next_hwid:
            return None
        return YHubPort.FindHubPortInContext(yctx, hwid2str(next_hwid))

    def nextHubPort(self):
        """
        Continues the enumeration of YoctoHub slave ports started using yFirstHubPort().
        Caution: You can't make any assumption about the returned YoctoHub slave ports order.
        If you want to find a specific a YoctoHub slave port, use HubPort.findHubPort()
        and a hardwareID or a logical name.

        @return a pointer to a YHubPort object, corresponding to
                a YoctoHub slave port currently online, or a None pointer
                if there are no more YoctoHub slave ports to enumerate.
        """
        next_hwid: Union[HwId, None] = None
        try:
            hwid: HwId = self._yapi._yHash.resolveHwID(self._className, self._func)
            next_hwid = self._yapi._yHash.getNextHardwareId(self._className, hwid)
        except YAPI_Exception:
            pass
        if not next_hwid:
            return None
        return YHubPort.FindHubPortInContext(self._yapi, hwid2str(next_hwid))

    def _parseAttr(self, json_val: dict) -> None:
        if 'enabled' in json_val:
            self._enabled = json_val["enabled"] > 0
        if 'portState' in json_val:
            self._portState = json_val["portState"]
        if 'baudRate' in json_val:
            self._baudRate = json_val["baudRate"]
        super()._parseAttr(json_val)

    async def get_enabled(self) -> int:
        """
        Returns true if the YoctoHub port is powered, false otherwise.

        @return either YHubPort.ENABLED_FALSE or YHubPort.ENABLED_TRUE, according to true if the YoctoHub
        port is powered, false otherwise

        On failure, throws an exception or returns YHubPort.ENABLED_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YHubPort.ENABLED_INVALID
        res = self._enabled
        return res

    async def set_enabled(self, newval: int) -> int:
        """
        Changes the activation of the YoctoHub port. If the port is enabled, the
        connected module is powered. Otherwise, port power is shut down.

        @param newval : either YHubPort.ENABLED_FALSE or YHubPort.ENABLED_TRUE, according to the activation
        of the YoctoHub port

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return await self._setAttr("enabled", rest_val)

    async def get_portState(self) -> int:
        """
        Returns the current state of the YoctoHub port.

        @return a value among YHubPort.PORTSTATE_OFF, YHubPort.PORTSTATE_OVRLD, YHubPort.PORTSTATE_ON,
        YHubPort.PORTSTATE_RUN and YHubPort.PORTSTATE_PROG corresponding to the current state of the YoctoHub port

        On failure, throws an exception or returns YHubPort.PORTSTATE_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YHubPort.PORTSTATE_INVALID
        res = self._portState
        return res

    async def get_baudRate(self) -> int:
        """
        Returns the current baud rate used by this YoctoHub port, in kbps.
        The default value is 1000 kbps, but a slower rate may be used if communication
        problems are encountered.

        @return an integer corresponding to the current baud rate used by this YoctoHub port, in kbps

        On failure, throws an exception or returns YHubPort.BAUDRATE_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YHubPort.BAUDRATE_INVALID
        res = self._baudRate
        return res

    @staticmethod
    def FindHubPort(func: str) -> YHubPort:
        """
        Retrieves a YoctoHub slave port for a given identifier.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the YoctoHub slave port is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YHubPort.isOnline() to test if the YoctoHub slave port is
        indeed online at a given time. In case of ambiguity when looking for
        a YoctoHub slave port by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the YoctoHub slave port, for instance
                YHUBETH1.hubPort1.

        @return a YHubPort object allowing you to drive the YoctoHub slave port.
        """
        obj: Union[YHubPort, None]
        obj = YFunction._FindFromCache("HubPort", func)
        if obj is None:
            obj = YHubPort(YAPI, func)
            YFunction._AddToCache("HubPort", func, obj)
        return obj

    @staticmethod
    def FindHubPortInContext(yctx: YAPIContext, func: str) -> YHubPort:
        """
        Retrieves a YoctoHub slave port for a given identifier in a YAPI context.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the YoctoHub slave port is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YHubPort.isOnline() to test if the YoctoHub slave port is
        indeed online at a given time. In case of ambiguity when looking for
        a YoctoHub slave port by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        @param yctx : a YAPI context
        @param func : a string that uniquely characterizes the YoctoHub slave port, for instance
                YHUBETH1.hubPort1.

        @return a YHubPort object allowing you to drive the YoctoHub slave port.
        """
        obj: Union[YHubPort, None]
        obj = YFunction._FindFromCacheInContext(yctx, "HubPort", func)
        if obj is None:
            obj = YHubPort(yctx, func)
            YFunction._AddToCache("HubPort", func, obj)
        return obj

    if not _IS_MICROPYTHON:
        async def registerValueCallback(self, callback: YHubPortValueCallback) -> int:
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

    # --- (end of YHubPort implementation)

