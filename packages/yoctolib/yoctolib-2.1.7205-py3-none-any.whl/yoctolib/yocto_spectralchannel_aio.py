# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: svn_id $
#
#  Asyncio implementation of YSpectralChannel
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
Yoctopuce library: Asyncio implementation of YSpectralChannel
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

# --- (YSpectralChannel class start)
if not _IS_MICROPYTHON:
    # For CPython, use strongly typed callback types
    try:
        YSpectralChannelValueCallback = Union[Callable[['YSpectralChannel', str], Any], None]
        YSpectralChannelTimedReportCallback = Union[Callable[['YSpectralChannel', YMeasure], Any], None]
    except TypeError:
        YSpectralChannelValueCallback = Union[Callable, Awaitable]
        YSpectralChannelTimedReportCallback = Union[Callable, Awaitable]

# noinspection PyProtectedMember
class YSpectralChannel(YSensor):
    """
    The YSpectralChannel class allows you to read and configure Yoctopuce spectral analysis channels.
    It inherits from YSensor class the core functions to read measures,
    to register callback functions, and to access the autonomous data logger.

    """
    # --- (end of YSpectralChannel class start)
    if not _IS_MICROPYTHON:
        # --- (YSpectralChannel return codes)
        RAWCOUNT_INVALID: Final[int] = YAPI.INVALID_INT
        CHANNELNAME_INVALID: Final[str] = YAPI.INVALID_STRING
        PEAKWAVELENGTH_INVALID: Final[int] = YAPI.INVALID_INT
        # --- (end of YSpectralChannel return codes)

    # --- (YSpectralChannel attributes declaration)
    _rawCount: int
    _channelName: str
    _peakWavelength: int
    _valueCallback: YSpectralChannelValueCallback
    _timedReportCallback: YSpectralChannelTimedReportCallback
    # --- (end of YSpectralChannel attributes declaration)


    def __init__(self, yctx: YAPIContext, func: str):
        super().__init__(yctx, func)
        self._className = 'SpectralChannel'
        # --- (YSpectralChannel constructor)
        self._rawCount = YSpectralChannel.RAWCOUNT_INVALID
        self._channelName = YSpectralChannel.CHANNELNAME_INVALID
        self._peakWavelength = YSpectralChannel.PEAKWAVELENGTH_INVALID
        # --- (end of YSpectralChannel constructor)

    # --- (YSpectralChannel implementation)

    @staticmethod
    def FirstSpectralChannel() -> Union[YSpectralChannel, None]:
        """
        Starts the enumeration of spectral analysis channels currently accessible.
        Use the method YSpectralChannel.nextSpectralChannel() to iterate on
        next spectral analysis channels.

        @return a pointer to a YSpectralChannel object, corresponding to
                the first spectral analysis channel currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = YAPI._yHash.getFirstHardwareId('SpectralChannel')
        if not next_hwid:
            return None
        return YSpectralChannel.FindSpectralChannel(hwid2str(next_hwid))

    @staticmethod
    def FirstSpectralChannelInContext(yctx: YAPIContext) -> Union[YSpectralChannel, None]:
        """
        Starts the enumeration of spectral analysis channels currently accessible.
        Use the method YSpectralChannel.nextSpectralChannel() to iterate on
        next spectral analysis channels.

        @param yctx : a YAPI context.

        @return a pointer to a YSpectralChannel object, corresponding to
                the first spectral analysis channel currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = yctx._yHash.getFirstHardwareId('SpectralChannel')
        if not next_hwid:
            return None
        return YSpectralChannel.FindSpectralChannelInContext(yctx, hwid2str(next_hwid))

    def nextSpectralChannel(self):
        """
        Continues the enumeration of spectral analysis channels started using yFirstSpectralChannel().
        Caution: You can't make any assumption about the returned spectral analysis channels order.
        If you want to find a specific a spectral analysis channel, use SpectralChannel.findSpectralChannel()
        and a hardwareID or a logical name.

        @return a pointer to a YSpectralChannel object, corresponding to
                a spectral analysis channel currently online, or a None pointer
                if there are no more spectral analysis channels to enumerate.
        """
        next_hwid: Union[HwId, None] = None
        try:
            hwid: HwId = self._yapi._yHash.resolveHwID(self._className, self._func)
            next_hwid = self._yapi._yHash.getNextHardwareId(self._className, hwid)
        except YAPI_Exception:
            pass
        if not next_hwid:
            return None
        return YSpectralChannel.FindSpectralChannelInContext(self._yapi, hwid2str(next_hwid))

    def _parseAttr(self, json_val: dict) -> None:
        if 'rawCount' in json_val:
            self._rawCount = json_val["rawCount"]
        if 'channelName' in json_val:
            self._channelName = json_val["channelName"]
        if 'peakWavelength' in json_val:
            self._peakWavelength = json_val["peakWavelength"]
        super()._parseAttr(json_val)

    async def get_rawCount(self) -> int:
        """
        Retrieves the raw spectral intensity value as measured by the sensor, without any scaling or calibration.

        @return an integer

        On failure, throws an exception or returns YSpectralChannel.RAWCOUNT_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YSpectralChannel.RAWCOUNT_INVALID
        res = self._rawCount
        return res

    async def get_channelName(self) -> str:
        """
        Returns the target spectral band name.

        @return a string corresponding to the target spectral band name

        On failure, throws an exception or returns YSpectralChannel.CHANNELNAME_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YSpectralChannel.CHANNELNAME_INVALID
        res = self._channelName
        return res

    async def get_peakWavelength(self) -> int:
        """
        Returns the target spectral band peak wavelength, in nm.

        @return an integer corresponding to the target spectral band peak wavelength, in nm

        On failure, throws an exception or returns YSpectralChannel.PEAKWAVELENGTH_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YSpectralChannel.PEAKWAVELENGTH_INVALID
        res = self._peakWavelength
        return res

    @staticmethod
    def FindSpectralChannel(func: str) -> YSpectralChannel:
        """
        Retrieves a spectral analysis channel for a given identifier.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the spectral analysis channel is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YSpectralChannel.isOnline() to test if the spectral analysis channel is
        indeed online at a given time. In case of ambiguity when looking for
        a spectral analysis channel by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the spectral analysis channel, for instance
                MyDevice.spectralChannel1.

        @return a YSpectralChannel object allowing you to drive the spectral analysis channel.
        """
        obj: Union[YSpectralChannel, None]
        obj = YFunction._FindFromCache("SpectralChannel", func)
        if obj is None:
            obj = YSpectralChannel(YAPI, func)
            YFunction._AddToCache("SpectralChannel", func, obj)
        return obj

    @staticmethod
    def FindSpectralChannelInContext(yctx: YAPIContext, func: str) -> YSpectralChannel:
        """
        Retrieves a spectral analysis channel for a given identifier in a YAPI context.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the spectral analysis channel is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YSpectralChannel.isOnline() to test if the spectral analysis channel is
        indeed online at a given time. In case of ambiguity when looking for
        a spectral analysis channel by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        @param yctx : a YAPI context
        @param func : a string that uniquely characterizes the spectral analysis channel, for instance
                MyDevice.spectralChannel1.

        @return a YSpectralChannel object allowing you to drive the spectral analysis channel.
        """
        obj: Union[YSpectralChannel, None]
        obj = YFunction._FindFromCacheInContext(yctx, "SpectralChannel", func)
        if obj is None:
            obj = YSpectralChannel(yctx, func)
            YFunction._AddToCache("SpectralChannel", func, obj)
        return obj

    if not _IS_MICROPYTHON:
        async def registerValueCallback(self, callback: YSpectralChannelValueCallback) -> int:
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
        async def registerTimedReportCallback(self, callback: YSpectralChannelTimedReportCallback) -> int:
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

    # --- (end of YSpectralChannel implementation)

