# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: svn_id $
#
#  Asyncio implementation of YAudioIn
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
Yoctopuce library: Asyncio implementation of YAudioIn
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

# --- (YAudioIn class start)
if not _IS_MICROPYTHON:
    # For CPython, use strongly typed callback types
    try:
        YAudioInValueCallback = Union[Callable[['YAudioIn', str], Any], None]
    except TypeError:
        YAudioInValueCallback = Union[Callable, Awaitable]

# noinspection PyProtectedMember
class YAudioIn(YFunction):
    """
    The YAudioIn class allows you to configure the volume of an audio input.

    """
    # --- (end of YAudioIn class start)
    if not _IS_MICROPYTHON:
        # --- (YAudioIn return codes)
        VOLUME_INVALID: Final[int] = YAPI.INVALID_UINT
        VOLUMERANGE_INVALID: Final[str] = YAPI.INVALID_STRING
        SIGNAL_INVALID: Final[int] = YAPI.INVALID_INT
        NOSIGNALFOR_INVALID: Final[int] = YAPI.INVALID_INT
        MUTE_FALSE: Final[int] = 0
        MUTE_TRUE: Final[int] = 1
        MUTE_INVALID: Final[int] = -1
        # --- (end of YAudioIn return codes)

    # --- (YAudioIn attributes declaration)
    _volume: int
    _mute: int
    _volumeRange: str
    _signal: int
    _noSignalFor: int
    _valueCallback: YAudioInValueCallback
    # --- (end of YAudioIn attributes declaration)


    def __init__(self, yctx: YAPIContext, func: str):
        super().__init__(yctx, func)
        self._className = 'AudioIn'
        # --- (YAudioIn constructor)
        self._volume = YAudioIn.VOLUME_INVALID
        self._mute = YAudioIn.MUTE_INVALID
        self._volumeRange = YAudioIn.VOLUMERANGE_INVALID
        self._signal = YAudioIn.SIGNAL_INVALID
        self._noSignalFor = YAudioIn.NOSIGNALFOR_INVALID
        # --- (end of YAudioIn constructor)

    # --- (YAudioIn implementation)

    @staticmethod
    def FirstAudioIn() -> Union[YAudioIn, None]:
        """
        Starts the enumeration of audio inputs currently accessible.
        Use the method YAudioIn.nextAudioIn() to iterate on
        next audio inputs.

        @return a pointer to a YAudioIn object, corresponding to
                the first audio input currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = YAPI._yHash.getFirstHardwareId('AudioIn')
        if not next_hwid:
            return None
        return YAudioIn.FindAudioIn(hwid2str(next_hwid))

    @staticmethod
    def FirstAudioInInContext(yctx: YAPIContext) -> Union[YAudioIn, None]:
        """
        Starts the enumeration of audio inputs currently accessible.
        Use the method YAudioIn.nextAudioIn() to iterate on
        next audio inputs.

        @param yctx : a YAPI context.

        @return a pointer to a YAudioIn object, corresponding to
                the first audio input currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = yctx._yHash.getFirstHardwareId('AudioIn')
        if not next_hwid:
            return None
        return YAudioIn.FindAudioInInContext(yctx, hwid2str(next_hwid))

    def nextAudioIn(self):
        """
        Continues the enumeration of audio inputs started using yFirstAudioIn().
        Caution: You can't make any assumption about the returned audio inputs order.
        If you want to find a specific an audio input, use AudioIn.findAudioIn()
        and a hardwareID or a logical name.

        @return a pointer to a YAudioIn object, corresponding to
                an audio input currently online, or a None pointer
                if there are no more audio inputs to enumerate.
        """
        next_hwid: Union[HwId, None] = None
        try:
            hwid: HwId = self._yapi._yHash.resolveHwID(self._className, self._func)
            next_hwid = self._yapi._yHash.getNextHardwareId(self._className, hwid)
        except YAPI_Exception:
            pass
        if not next_hwid:
            return None
        return YAudioIn.FindAudioInInContext(self._yapi, hwid2str(next_hwid))

    def _parseAttr(self, json_val: dict) -> None:
        if 'volume' in json_val:
            self._volume = json_val["volume"]
        if 'mute' in json_val:
            self._mute = json_val["mute"] > 0
        if 'volumeRange' in json_val:
            self._volumeRange = json_val["volumeRange"]
        if 'signal' in json_val:
            self._signal = json_val["signal"]
        if 'noSignalFor' in json_val:
            self._noSignalFor = json_val["noSignalFor"]
        super()._parseAttr(json_val)

    async def get_volume(self) -> int:
        """
        Returns audio input gain, in per cents.

        @return an integer corresponding to audio input gain, in per cents

        On failure, throws an exception or returns YAudioIn.VOLUME_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YAudioIn.VOLUME_INVALID
        res = self._volume
        return res

    async def set_volume(self, newval: int) -> int:
        """
        Changes audio input gain, in per cents.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : an integer corresponding to audio input gain, in per cents

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("volume", rest_val)

    async def get_mute(self) -> int:
        """
        Returns the state of the mute function.

        @return either YAudioIn.MUTE_FALSE or YAudioIn.MUTE_TRUE, according to the state of the mute function

        On failure, throws an exception or returns YAudioIn.MUTE_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YAudioIn.MUTE_INVALID
        res = self._mute
        return res

    async def set_mute(self, newval: int) -> int:
        """
        Changes the state of the mute function. Remember to call the matching module
        saveToFlash() method to save the setting permanently.

        @param newval : either YAudioIn.MUTE_FALSE or YAudioIn.MUTE_TRUE, according to the state of the mute function

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return await self._setAttr("mute", rest_val)

    async def get_volumeRange(self) -> str:
        """
        Returns the supported volume range. The low value of the
        range corresponds to the minimal audible value. To
        completely mute the sound, use set_mute()
        instead of the set_volume().

        @return a string corresponding to the supported volume range

        On failure, throws an exception or returns YAudioIn.VOLUMERANGE_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YAudioIn.VOLUMERANGE_INVALID
        res = self._volumeRange
        return res

    async def get_signal(self) -> int:
        """
        Returns the detected input signal level.

        @return an integer corresponding to the detected input signal level

        On failure, throws an exception or returns YAudioIn.SIGNAL_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YAudioIn.SIGNAL_INVALID
        res = self._signal
        return res

    async def get_noSignalFor(self) -> int:
        """
        Returns the number of seconds elapsed without detecting a signal.

        @return an integer corresponding to the number of seconds elapsed without detecting a signal

        On failure, throws an exception or returns YAudioIn.NOSIGNALFOR_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YAudioIn.NOSIGNALFOR_INVALID
        res = self._noSignalFor
        return res

    @staticmethod
    def FindAudioIn(func: str) -> YAudioIn:
        """
        Retrieves an audio input for a given identifier.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the audio input is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YAudioIn.isOnline() to test if the audio input is
        indeed online at a given time. In case of ambiguity when looking for
        an audio input by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the audio input, for instance
                MyDevice.audioIn1.

        @return a YAudioIn object allowing you to drive the audio input.
        """
        obj: Union[YAudioIn, None]
        obj = YFunction._FindFromCache("AudioIn", func)
        if obj is None:
            obj = YAudioIn(YAPI, func)
            YFunction._AddToCache("AudioIn", func, obj)
        return obj

    @staticmethod
    def FindAudioInInContext(yctx: YAPIContext, func: str) -> YAudioIn:
        """
        Retrieves an audio input for a given identifier in a YAPI context.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the audio input is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YAudioIn.isOnline() to test if the audio input is
        indeed online at a given time. In case of ambiguity when looking for
        an audio input by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        @param yctx : a YAPI context
        @param func : a string that uniquely characterizes the audio input, for instance
                MyDevice.audioIn1.

        @return a YAudioIn object allowing you to drive the audio input.
        """
        obj: Union[YAudioIn, None]
        obj = YFunction._FindFromCacheInContext(yctx, "AudioIn", func)
        if obj is None:
            obj = YAudioIn(yctx, func)
            YFunction._AddToCache("AudioIn", func, obj)
        return obj

    if not _IS_MICROPYTHON:
        async def registerValueCallback(self, callback: YAudioInValueCallback) -> int:
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

    # --- (end of YAudioIn implementation)

