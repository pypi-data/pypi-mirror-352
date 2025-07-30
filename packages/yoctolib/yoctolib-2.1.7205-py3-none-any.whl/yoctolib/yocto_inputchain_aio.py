# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: svn_id $
#
#  Asyncio implementation of YInputChain
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
Yoctopuce library: Asyncio implementation of YInputChain
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
    YAPIContext, YAPI, YAPI_Exception, HwId, hwid2str, YFunction, xarray
)

async def yInternalEventCallback(obj: YInputChain, value: str):
    await obj._internalEventHandler(value)

# --- (YInputChain class start)
if not _IS_MICROPYTHON:
    # For CPython, use strongly typed callback types
    try:
        YInputChainValueCallback = Union[Callable[['YInputChain', str], Any], None]
        YStateChangeCallback = Union[Callable[['YInputChain',int , str, str, str], Any], None]
    except TypeError:
        YInputChainValueCallback = Union[Callable, Awaitable]
        YStateChangeCallback = Union[Callable, Awaitable]

# noinspection PyProtectedMember
class YInputChain(YFunction):
    """
    The YInputChain class provides access to separate
    digital inputs connected in a chain.

    """
    # --- (end of YInputChain class start)
    if not _IS_MICROPYTHON:
        # --- (YInputChain return codes)
        EXPECTEDNODES_INVALID: Final[int] = YAPI.INVALID_UINT
        DETECTEDNODES_INVALID: Final[int] = YAPI.INVALID_UINT
        REFRESHRATE_INVALID: Final[int] = YAPI.INVALID_UINT
        BITCHAIN1_INVALID: Final[str] = YAPI.INVALID_STRING
        BITCHAIN2_INVALID: Final[str] = YAPI.INVALID_STRING
        BITCHAIN3_INVALID: Final[str] = YAPI.INVALID_STRING
        BITCHAIN4_INVALID: Final[str] = YAPI.INVALID_STRING
        BITCHAIN5_INVALID: Final[str] = YAPI.INVALID_STRING
        BITCHAIN6_INVALID: Final[str] = YAPI.INVALID_STRING
        BITCHAIN7_INVALID: Final[str] = YAPI.INVALID_STRING
        WATCHDOGPERIOD_INVALID: Final[int] = YAPI.INVALID_UINT
        CHAINDIAGS_INVALID: Final[int] = YAPI.INVALID_UINT
        LOOPBACKTEST_OFF: Final[int] = 0
        LOOPBACKTEST_ON: Final[int] = 1
        LOOPBACKTEST_INVALID: Final[int] = -1
        # --- (end of YInputChain return codes)

    # --- (YInputChain attributes declaration)
    _expectedNodes: int
    _detectedNodes: int
    _loopbackTest: int
    _refreshRate: int
    _bitChain1: str
    _bitChain2: str
    _bitChain3: str
    _bitChain4: str
    _bitChain5: str
    _bitChain6: str
    _bitChain7: str
    _watchdogPeriod: int
    _chainDiags: int
    _valueCallback: YInputChainValueCallback
    _stateChangeCallback: YStateChangeCallback
    _prevPos: int
    _eventPos: int
    _eventStamp: int
    _eventChains: list[str]
    # --- (end of YInputChain attributes declaration)


    def __init__(self, yctx: YAPIContext, func: str):
        super().__init__(yctx, func)
        self._className = 'InputChain'
        # --- (YInputChain constructor)
        self._expectedNodes = YInputChain.EXPECTEDNODES_INVALID
        self._detectedNodes = YInputChain.DETECTEDNODES_INVALID
        self._loopbackTest = YInputChain.LOOPBACKTEST_INVALID
        self._refreshRate = YInputChain.REFRESHRATE_INVALID
        self._bitChain1 = YInputChain.BITCHAIN1_INVALID
        self._bitChain2 = YInputChain.BITCHAIN2_INVALID
        self._bitChain3 = YInputChain.BITCHAIN3_INVALID
        self._bitChain4 = YInputChain.BITCHAIN4_INVALID
        self._bitChain5 = YInputChain.BITCHAIN5_INVALID
        self._bitChain6 = YInputChain.BITCHAIN6_INVALID
        self._bitChain7 = YInputChain.BITCHAIN7_INVALID
        self._watchdogPeriod = YInputChain.WATCHDOGPERIOD_INVALID
        self._chainDiags = YInputChain.CHAINDIAGS_INVALID
        self._prevPos = 0
        self._eventPos = 0
        self._eventStamp = 0
        self._eventChains = []
        # --- (end of YInputChain constructor)

    # --- (YInputChain implementation)

    @staticmethod
    def FirstInputChain() -> Union[YInputChain, None]:
        """
        Starts the enumeration of digital input chains currently accessible.
        Use the method YInputChain.nextInputChain() to iterate on
        next digital input chains.

        @return a pointer to a YInputChain object, corresponding to
                the first digital input chain currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = YAPI._yHash.getFirstHardwareId('InputChain')
        if not next_hwid:
            return None
        return YInputChain.FindInputChain(hwid2str(next_hwid))

    @staticmethod
    def FirstInputChainInContext(yctx: YAPIContext) -> Union[YInputChain, None]:
        """
        Starts the enumeration of digital input chains currently accessible.
        Use the method YInputChain.nextInputChain() to iterate on
        next digital input chains.

        @param yctx : a YAPI context.

        @return a pointer to a YInputChain object, corresponding to
                the first digital input chain currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = yctx._yHash.getFirstHardwareId('InputChain')
        if not next_hwid:
            return None
        return YInputChain.FindInputChainInContext(yctx, hwid2str(next_hwid))

    def nextInputChain(self):
        """
        Continues the enumeration of digital input chains started using yFirstInputChain().
        Caution: You can't make any assumption about the returned digital input chains order.
        If you want to find a specific a digital input chain, use InputChain.findInputChain()
        and a hardwareID or a logical name.

        @return a pointer to a YInputChain object, corresponding to
                a digital input chain currently online, or a None pointer
                if there are no more digital input chains to enumerate.
        """
        next_hwid: Union[HwId, None] = None
        try:
            hwid: HwId = self._yapi._yHash.resolveHwID(self._className, self._func)
            next_hwid = self._yapi._yHash.getNextHardwareId(self._className, hwid)
        except YAPI_Exception:
            pass
        if not next_hwid:
            return None
        return YInputChain.FindInputChainInContext(self._yapi, hwid2str(next_hwid))

    def _parseAttr(self, json_val: dict) -> None:
        if 'expectedNodes' in json_val:
            self._expectedNodes = json_val["expectedNodes"]
        if 'detectedNodes' in json_val:
            self._detectedNodes = json_val["detectedNodes"]
        if 'loopbackTest' in json_val:
            self._loopbackTest = json_val["loopbackTest"] > 0
        if 'refreshRate' in json_val:
            self._refreshRate = json_val["refreshRate"]
        if 'bitChain1' in json_val:
            self._bitChain1 = json_val["bitChain1"]
        if 'bitChain2' in json_val:
            self._bitChain2 = json_val["bitChain2"]
        if 'bitChain3' in json_val:
            self._bitChain3 = json_val["bitChain3"]
        if 'bitChain4' in json_val:
            self._bitChain4 = json_val["bitChain4"]
        if 'bitChain5' in json_val:
            self._bitChain5 = json_val["bitChain5"]
        if 'bitChain6' in json_val:
            self._bitChain6 = json_val["bitChain6"]
        if 'bitChain7' in json_val:
            self._bitChain7 = json_val["bitChain7"]
        if 'watchdogPeriod' in json_val:
            self._watchdogPeriod = json_val["watchdogPeriod"]
        if 'chainDiags' in json_val:
            self._chainDiags = json_val["chainDiags"]
        super()._parseAttr(json_val)

    async def get_expectedNodes(self) -> int:
        """
        Returns the number of nodes expected in the chain.

        @return an integer corresponding to the number of nodes expected in the chain

        On failure, throws an exception or returns YInputChain.EXPECTEDNODES_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YInputChain.EXPECTEDNODES_INVALID
        res = self._expectedNodes
        return res

    async def set_expectedNodes(self, newval: int) -> int:
        """
        Changes the number of nodes expected in the chain.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : an integer corresponding to the number of nodes expected in the chain

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("expectedNodes", rest_val)

    async def get_detectedNodes(self) -> int:
        """
        Returns the number of nodes detected in the chain.

        @return an integer corresponding to the number of nodes detected in the chain

        On failure, throws an exception or returns YInputChain.DETECTEDNODES_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YInputChain.DETECTEDNODES_INVALID
        res = self._detectedNodes
        return res

    async def get_loopbackTest(self) -> int:
        """
        Returns the activation state of the exhaustive chain connectivity test.
        The connectivity test requires a cable connecting the end of the chain
        to the loopback test connector.

        @return either YInputChain.LOOPBACKTEST_OFF or YInputChain.LOOPBACKTEST_ON, according to the
        activation state of the exhaustive chain connectivity test

        On failure, throws an exception or returns YInputChain.LOOPBACKTEST_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YInputChain.LOOPBACKTEST_INVALID
        res = self._loopbackTest
        return res

    async def set_loopbackTest(self, newval: int) -> int:
        """
        Changes the activation state of the exhaustive chain connectivity test.
        The connectivity test requires a cable connecting the end of the chain
        to the loopback test connector.

        If you want the change to be kept after a device reboot,
        make sure  to call the matching module saveToFlash().

        @param newval : either YInputChain.LOOPBACKTEST_OFF or YInputChain.LOOPBACKTEST_ON, according to
        the activation state of the exhaustive chain connectivity test

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return await self._setAttr("loopbackTest", rest_val)

    async def get_refreshRate(self) -> int:
        """
        Returns the desired refresh rate, measured in Hz.
        The higher the refresh rate is set, the higher the
        communication speed on the chain will be.

        @return an integer corresponding to the desired refresh rate, measured in Hz

        On failure, throws an exception or returns YInputChain.REFRESHRATE_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YInputChain.REFRESHRATE_INVALID
        res = self._refreshRate
        return res

    async def set_refreshRate(self, newval: int) -> int:
        """
        Changes the desired refresh rate, measured in Hz.
        The higher the refresh rate is set, the higher the
        communication speed on the chain will be.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : an integer corresponding to the desired refresh rate, measured in Hz

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("refreshRate", rest_val)

    async def get_bitChain1(self) -> str:
        """
        Returns the state of input 1 for all nodes of the input chain,
        as a hexadecimal string. The node nearest to the controller
        is the lowest bit of the result.

        @return a string corresponding to the state of input 1 for all nodes of the input chain,
                as a hexadecimal string

        On failure, throws an exception or returns YInputChain.BITCHAIN1_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YInputChain.BITCHAIN1_INVALID
        res = self._bitChain1
        return res

    async def get_bitChain2(self) -> str:
        """
        Returns the state of input 2 for all nodes of the input chain,
        as a hexadecimal string. The node nearest to the controller
        is the lowest bit of the result.

        @return a string corresponding to the state of input 2 for all nodes of the input chain,
                as a hexadecimal string

        On failure, throws an exception or returns YInputChain.BITCHAIN2_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YInputChain.BITCHAIN2_INVALID
        res = self._bitChain2
        return res

    async def get_bitChain3(self) -> str:
        """
        Returns the state of input 3 for all nodes of the input chain,
        as a hexadecimal string. The node nearest to the controller
        is the lowest bit of the result.

        @return a string corresponding to the state of input 3 for all nodes of the input chain,
                as a hexadecimal string

        On failure, throws an exception or returns YInputChain.BITCHAIN3_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YInputChain.BITCHAIN3_INVALID
        res = self._bitChain3
        return res

    async def get_bitChain4(self) -> str:
        """
        Returns the state of input 4 for all nodes of the input chain,
        as a hexadecimal string. The node nearest to the controller
        is the lowest bit of the result.

        @return a string corresponding to the state of input 4 for all nodes of the input chain,
                as a hexadecimal string

        On failure, throws an exception or returns YInputChain.BITCHAIN4_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YInputChain.BITCHAIN4_INVALID
        res = self._bitChain4
        return res

    async def get_bitChain5(self) -> str:
        """
        Returns the state of input 5 for all nodes of the input chain,
        as a hexadecimal string. The node nearest to the controller
        is the lowest bit of the result.

        @return a string corresponding to the state of input 5 for all nodes of the input chain,
                as a hexadecimal string

        On failure, throws an exception or returns YInputChain.BITCHAIN5_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YInputChain.BITCHAIN5_INVALID
        res = self._bitChain5
        return res

    async def get_bitChain6(self) -> str:
        """
        Returns the state of input 6 for all nodes of the input chain,
        as a hexadecimal string. The node nearest to the controller
        is the lowest bit of the result.

        @return a string corresponding to the state of input 6 for all nodes of the input chain,
                as a hexadecimal string

        On failure, throws an exception or returns YInputChain.BITCHAIN6_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YInputChain.BITCHAIN6_INVALID
        res = self._bitChain6
        return res

    async def get_bitChain7(self) -> str:
        """
        Returns the state of input 7 for all nodes of the input chain,
        as a hexadecimal string. The node nearest to the controller
        is the lowest bit of the result.

        @return a string corresponding to the state of input 7 for all nodes of the input chain,
                as a hexadecimal string

        On failure, throws an exception or returns YInputChain.BITCHAIN7_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YInputChain.BITCHAIN7_INVALID
        res = self._bitChain7
        return res

    async def get_watchdogPeriod(self) -> int:
        """
        Returns the wait time in seconds before triggering an inactivity
        timeout error.

        @return an integer corresponding to the wait time in seconds before triggering an inactivity
                timeout error

        On failure, throws an exception or returns YInputChain.WATCHDOGPERIOD_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YInputChain.WATCHDOGPERIOD_INVALID
        res = self._watchdogPeriod
        return res

    async def set_watchdogPeriod(self, newval: int) -> int:
        """
        Changes the wait time in seconds before triggering an inactivity
        timeout error. Remember to call the saveToFlash() method
        of the module if the modification must be kept.

        @param newval : an integer corresponding to the wait time in seconds before triggering an inactivity
                timeout error

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("watchdogPeriod", rest_val)

    async def get_chainDiags(self) -> int:
        """
        Returns the controller state diagnostics. Bit 0 indicates a chain length
        error, bit 1 indicates an inactivity timeout and bit 2 indicates
        a loopback test failure.

        @return an integer corresponding to the controller state diagnostics

        On failure, throws an exception or returns YInputChain.CHAINDIAGS_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YInputChain.CHAINDIAGS_INVALID
        res = self._chainDiags
        return res

    @staticmethod
    def FindInputChain(func: str) -> YInputChain:
        """
        Retrieves a digital input chain for a given identifier.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the digital input chain is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YInputChain.isOnline() to test if the digital input chain is
        indeed online at a given time. In case of ambiguity when looking for
        a digital input chain by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the digital input chain, for instance
                MyDevice.inputChain.

        @return a YInputChain object allowing you to drive the digital input chain.
        """
        obj: Union[YInputChain, None]
        obj = YFunction._FindFromCache("InputChain", func)
        if obj is None:
            obj = YInputChain(YAPI, func)
            YFunction._AddToCache("InputChain", func, obj)
        return obj

    @staticmethod
    def FindInputChainInContext(yctx: YAPIContext, func: str) -> YInputChain:
        """
        Retrieves a digital input chain for a given identifier in a YAPI context.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the digital input chain is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YInputChain.isOnline() to test if the digital input chain is
        indeed online at a given time. In case of ambiguity when looking for
        a digital input chain by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        @param yctx : a YAPI context
        @param func : a string that uniquely characterizes the digital input chain, for instance
                MyDevice.inputChain.

        @return a YInputChain object allowing you to drive the digital input chain.
        """
        obj: Union[YInputChain, None]
        obj = YFunction._FindFromCacheInContext(yctx, "InputChain", func)
        if obj is None:
            obj = YInputChain(yctx, func)
            YFunction._AddToCache("InputChain", func, obj)
        return obj

    if not _IS_MICROPYTHON:
        async def registerValueCallback(self, callback: YInputChainValueCallback) -> int:
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

    async def resetWatchdog(self) -> int:
        """
        Resets the application watchdog countdown.
        If you have set up a non-zero watchdogPeriod, you should
        call this function on a regular basis to prevent the application
        inactivity error to be triggered.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return await self.set_watchdogPeriod(-1)

    async def get_lastEvents(self) -> str:
        """
        Returns a string with last events observed on the digital input chain.
        This method return only events that are still buffered in the device memory.

        @return a string with last events observed (one per line).

        On failure, throws an exception or returns  YAPI.INVALID_STRING.
        """
        content: xarray

        content = await self._download("events.txt")
        return content.decode('latin-1')

    async def registerStateChangeCallback(self, callback: YStateChangeCallback) -> int:
        """
        Registers a callback function to be called each time that an event is detected on the
        input chain.The callback is invoked only during the execution of
        ySleep or yHandleEvents. This provides control over the time when
        the callback is triggered. For good responsiveness, remember to call one of these
        two functions periodically. To unregister a callback, pass a None pointer as argument.

        @param callback : the callback function to call, or a None pointer.
                The callback function should take four arguments:
                the YInputChain object that emitted the event, the
                UTC timestamp of the event, a character string describing
                the type of event and a character string with the event data.
                On failure, throws an exception or returns a negative error code.
        """
        if callback:
            await self.registerValueCallback(yInternalEventCallback)
        else:
            await self.registerValueCallback(None)
        # register user callback AFTER the internal pseudo-event,
        # to make sure we start with future events only
        self._stateChangeCallback = callback
        return 0

    async def _internalEventHandler(self, cbpos: str) -> int:
        newPos: int
        url: str
        content: xarray
        contentStr: str
        eventArr: list[str] = []
        arrLen: int
        lenStr: str
        arrPos: int
        eventStr: str
        eventLen: int
        hexStamp: str
        typePos: int
        dataPos: int
        evtStamp: int
        evtType: str
        evtData: str
        evtChange: str
        chainIdx: int
        newPos = YAPI._atoi(cbpos)
        if newPos < self._prevPos:
            self._eventPos = 0
        self._prevPos = newPos
        if newPos < self._eventPos:
            return YAPI.SUCCESS
        if not (self._stateChangeCallback):
            # first simulated event, use it to initialize reference values
            self._eventPos = newPos
            del self._eventChains[:]
            self._eventChains.append(await self.get_bitChain1())
            self._eventChains.append(await self.get_bitChain2())
            self._eventChains.append(await self.get_bitChain3())
            self._eventChains.append(await self.get_bitChain4())
            self._eventChains.append(await self.get_bitChain5())
            self._eventChains.append(await self.get_bitChain6())
            self._eventChains.append(await self.get_bitChain7())
            return YAPI.SUCCESS
        url = "events.txt?pos=%d" % self._eventPos

        content = await self._download(url)
        contentStr = content.decode('latin-1')
        eventArr = (contentStr).split('\n')
        arrLen = len(eventArr)
        if not (arrLen > 0):
            self._throw(YAPI.IO_ERROR, "fail to download events")
            return YAPI.IO_ERROR
        # last element of array is the new position preceeded by '@'
        arrLen = arrLen - 1
        lenStr = eventArr[arrLen]
        lenStr = lenStr[1: 1 + len(lenStr)-1]
        # update processed event position pointer
        self._eventPos = YAPI._atoi(lenStr)
        # now generate callbacks for each event received
        arrPos = 0
        while arrPos < arrLen:
            eventStr = eventArr[arrPos]
            eventLen = len(eventStr)
            if eventLen >= 1:
                hexStamp = eventStr[0: 0 + 8]
                evtStamp = int(hexStamp, 16)
                typePos = eventStr.find(":")+1
                if (evtStamp >= self._eventStamp) and(typePos > 8):
                    self._eventStamp = evtStamp
                    dataPos = eventStr.find("=")+1
                    evtType = eventStr[typePos: typePos + 1]
                    evtData = ""
                    evtChange = ""
                    if dataPos > 10:
                        evtData = eventStr[dataPos: dataPos + len(eventStr)-dataPos]
                        if ("1234567").find(evtType) >= 0:
                            chainIdx = YAPI._atoi(evtType) - 1
                            evtChange = await self._strXor(evtData, self._eventChains[chainIdx])
                            self._eventChains[chainIdx] = evtData
                    try:
                        retval = self._stateChangeCallback(self, evtStamp, evtType, evtData, evtChange)
                        if retval is not None: await retval
                    # noinspection PyBroadException
                    except Exception as e:
                        print('Exception in %s.stateChangeCallback:' % type(self).__name__, type(e).__name__, e)
            arrPos = arrPos + 1
        return YAPI.SUCCESS

    async def _strXor(self, a: str, b: str) -> str:
        lenA: int
        lenB: int
        res: str
        idx: int
        digitA: int
        digitB: int
        # make sure the result has the same length as first argument
        lenA = len(a)
        lenB = len(b)
        if lenA > lenB:
            res = a[0: 0 + lenA-lenB]
            a = a[lenA-lenB: lenA-lenB + lenB]
            lenA = lenB
        else:
            res = ""
            b = b[lenA-lenB: lenA-lenB + lenA]
        # scan strings and compare digit by digit
        idx = 0
        while idx < lenA:
            digitA = int(a[idx: idx + 1], 16)
            digitB = int(b[idx: idx + 1], 16)
            res = "%s%x" % (res, (digitA ^ digitB))
            idx = idx + 1
        return res

    async def hex2array(self, hexstr: str) -> list[int]:
        hexlen: int
        res: list[int] = []
        idx: int
        digit: int
        hexlen = len(hexstr)
        del res[:]

        idx = hexlen
        while idx > 0:
            idx = idx - 1
            digit = int(hexstr[idx: idx + 1], 16)
            res.append((digit & 1))
            res.append(((digit >> 1) & 1))
            res.append(((digit >> 2) & 1))
            res.append(((digit >> 3) & 1))

        return res

    # --- (end of YInputChain implementation)

