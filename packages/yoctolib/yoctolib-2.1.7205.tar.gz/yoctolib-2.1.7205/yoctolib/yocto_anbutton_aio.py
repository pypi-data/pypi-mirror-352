# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: svn_id $
#
#  Asyncio implementation of YAnButton
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
Yoctopuce library: Asyncio implementation of YAnButton
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

# --- (YAnButton class start)
if not _IS_MICROPYTHON:
    # For CPython, use strongly typed callback types
    try:
        YAnButtonValueCallback = Union[Callable[['YAnButton', str], Any], None]
    except TypeError:
        YAnButtonValueCallback = Union[Callable, Awaitable]

# noinspection PyProtectedMember
class YAnButton(YFunction):
    """
    The YAnButton class provide access to basic resistive inputs.
    Such inputs can be used to measure the state
    of a simple button as well as to read an analog potentiometer (variable resistance).
    This can be use for instance with a continuous rotating knob, a throttle grip
    or a joystick. The module is capable to calibrate itself on min and max values,
    in order to compute a calibrated value that varies proportionally with the
    potentiometer position, regardless of its total resistance.

    """
    # --- (end of YAnButton class start)
    if not _IS_MICROPYTHON:
        # --- (YAnButton return codes)
        CALIBRATEDVALUE_INVALID: Final[int] = YAPI.INVALID_UINT
        RAWVALUE_INVALID: Final[int] = YAPI.INVALID_UINT
        CALIBRATIONMAX_INVALID: Final[int] = YAPI.INVALID_UINT
        CALIBRATIONMIN_INVALID: Final[int] = YAPI.INVALID_UINT
        SENSITIVITY_INVALID: Final[int] = YAPI.INVALID_UINT
        LASTTIMEPRESSED_INVALID: Final[int] = YAPI.INVALID_LONG
        LASTTIMERELEASED_INVALID: Final[int] = YAPI.INVALID_LONG
        PULSECOUNTER_INVALID: Final[int] = YAPI.INVALID_LONG
        PULSETIMER_INVALID: Final[int] = YAPI.INVALID_LONG
        ANALOGCALIBRATION_OFF: Final[int] = 0
        ANALOGCALIBRATION_ON: Final[int] = 1
        ANALOGCALIBRATION_INVALID: Final[int] = -1
        ISPRESSED_FALSE: Final[int] = 0
        ISPRESSED_TRUE: Final[int] = 1
        ISPRESSED_INVALID: Final[int] = -1
        INPUTTYPE_ANALOG_FAST: Final[int] = 0
        INPUTTYPE_DIGITAL4: Final[int] = 1
        INPUTTYPE_ANALOG_SMOOTH: Final[int] = 2
        INPUTTYPE_DIGITAL_FAST: Final[int] = 3
        INPUTTYPE_INVALID: Final[int] = -1
        # --- (end of YAnButton return codes)

    # --- (YAnButton attributes declaration)
    _calibratedValue: int
    _rawValue: int
    _analogCalibration: int
    _calibrationMax: int
    _calibrationMin: int
    _sensitivity: int
    _isPressed: int
    _lastTimePressed: int
    _lastTimeReleased: int
    _pulseCounter: int
    _pulseTimer: int
    _inputType: int
    _valueCallback: YAnButtonValueCallback
    # --- (end of YAnButton attributes declaration)


    def __init__(self, yctx: YAPIContext, func: str):
        super().__init__(yctx, func)
        self._className = 'AnButton'
        # --- (YAnButton constructor)
        self._calibratedValue = YAnButton.CALIBRATEDVALUE_INVALID
        self._rawValue = YAnButton.RAWVALUE_INVALID
        self._analogCalibration = YAnButton.ANALOGCALIBRATION_INVALID
        self._calibrationMax = YAnButton.CALIBRATIONMAX_INVALID
        self._calibrationMin = YAnButton.CALIBRATIONMIN_INVALID
        self._sensitivity = YAnButton.SENSITIVITY_INVALID
        self._isPressed = YAnButton.ISPRESSED_INVALID
        self._lastTimePressed = YAnButton.LASTTIMEPRESSED_INVALID
        self._lastTimeReleased = YAnButton.LASTTIMERELEASED_INVALID
        self._pulseCounter = YAnButton.PULSECOUNTER_INVALID
        self._pulseTimer = YAnButton.PULSETIMER_INVALID
        self._inputType = YAnButton.INPUTTYPE_INVALID
        # --- (end of YAnButton constructor)

    # --- (YAnButton implementation)

    @staticmethod
    def FirstAnButton() -> Union[YAnButton, None]:
        """
        Starts the enumeration of analog inputs currently accessible.
        Use the method YAnButton.nextAnButton() to iterate on
        next analog inputs.

        @return a pointer to a YAnButton object, corresponding to
                the first analog input currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = YAPI._yHash.getFirstHardwareId('AnButton')
        if not next_hwid:
            return None
        return YAnButton.FindAnButton(hwid2str(next_hwid))

    @staticmethod
    def FirstAnButtonInContext(yctx: YAPIContext) -> Union[YAnButton, None]:
        """
        Starts the enumeration of analog inputs currently accessible.
        Use the method YAnButton.nextAnButton() to iterate on
        next analog inputs.

        @param yctx : a YAPI context.

        @return a pointer to a YAnButton object, corresponding to
                the first analog input currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = yctx._yHash.getFirstHardwareId('AnButton')
        if not next_hwid:
            return None
        return YAnButton.FindAnButtonInContext(yctx, hwid2str(next_hwid))

    def nextAnButton(self):
        """
        Continues the enumeration of analog inputs started using yFirstAnButton().
        Caution: You can't make any assumption about the returned analog inputs order.
        If you want to find a specific an analog input, use AnButton.findAnButton()
        and a hardwareID or a logical name.

        @return a pointer to a YAnButton object, corresponding to
                an analog input currently online, or a None pointer
                if there are no more analog inputs to enumerate.
        """
        next_hwid: Union[HwId, None] = None
        try:
            hwid: HwId = self._yapi._yHash.resolveHwID(self._className, self._func)
            next_hwid = self._yapi._yHash.getNextHardwareId(self._className, hwid)
        except YAPI_Exception:
            pass
        if not next_hwid:
            return None
        return YAnButton.FindAnButtonInContext(self._yapi, hwid2str(next_hwid))

    def _parseAttr(self, json_val: dict) -> None:
        if 'calibratedValue' in json_val:
            self._calibratedValue = json_val["calibratedValue"]
        if 'rawValue' in json_val:
            self._rawValue = json_val["rawValue"]
        if 'analogCalibration' in json_val:
            self._analogCalibration = json_val["analogCalibration"] > 0
        if 'calibrationMax' in json_val:
            self._calibrationMax = json_val["calibrationMax"]
        if 'calibrationMin' in json_val:
            self._calibrationMin = json_val["calibrationMin"]
        if 'sensitivity' in json_val:
            self._sensitivity = json_val["sensitivity"]
        if 'isPressed' in json_val:
            self._isPressed = json_val["isPressed"] > 0
        if 'lastTimePressed' in json_val:
            self._lastTimePressed = json_val["lastTimePressed"]
        if 'lastTimeReleased' in json_val:
            self._lastTimeReleased = json_val["lastTimeReleased"]
        if 'pulseCounter' in json_val:
            self._pulseCounter = json_val["pulseCounter"]
        if 'pulseTimer' in json_val:
            self._pulseTimer = json_val["pulseTimer"]
        if 'inputType' in json_val:
            self._inputType = json_val["inputType"]
        super()._parseAttr(json_val)

    async def get_calibratedValue(self) -> int:
        """
        Returns the current calibrated input value (between 0 and 1000, included).

        @return an integer corresponding to the current calibrated input value (between 0 and 1000, included)

        On failure, throws an exception or returns YAnButton.CALIBRATEDVALUE_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YAnButton.CALIBRATEDVALUE_INVALID
        res = self._calibratedValue
        return res

    async def get_rawValue(self) -> int:
        """
        Returns the current measured input value as-is (between 0 and 4095, included).

        @return an integer corresponding to the current measured input value as-is (between 0 and 4095, included)

        On failure, throws an exception or returns YAnButton.RAWVALUE_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YAnButton.RAWVALUE_INVALID
        res = self._rawValue
        return res

    async def get_analogCalibration(self) -> int:
        """
        Tells if a calibration process is currently ongoing.

        @return either YAnButton.ANALOGCALIBRATION_OFF or YAnButton.ANALOGCALIBRATION_ON

        On failure, throws an exception or returns YAnButton.ANALOGCALIBRATION_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YAnButton.ANALOGCALIBRATION_INVALID
        res = self._analogCalibration
        return res

    async def set_analogCalibration(self, newval: int) -> int:
        """
        Starts or stops the calibration process. Remember to call the saveToFlash()
        method of the module at the end of the calibration if the modification must be kept.

        @param newval : either YAnButton.ANALOGCALIBRATION_OFF or YAnButton.ANALOGCALIBRATION_ON

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return await self._setAttr("analogCalibration", rest_val)

    async def get_calibrationMax(self) -> int:
        """
        Returns the maximal value measured during the calibration (between 0 and 4095, included).

        @return an integer corresponding to the maximal value measured during the calibration (between 0
        and 4095, included)

        On failure, throws an exception or returns YAnButton.CALIBRATIONMAX_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YAnButton.CALIBRATIONMAX_INVALID
        res = self._calibrationMax
        return res

    async def set_calibrationMax(self, newval: int) -> int:
        """
        Changes the maximal calibration value for the input (between 0 and 4095, included), without actually
        starting the automated calibration.  Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : an integer corresponding to the maximal calibration value for the input (between 0
        and 4095, included), without actually
                starting the automated calibration

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("calibrationMax", rest_val)

    async def get_calibrationMin(self) -> int:
        """
        Returns the minimal value measured during the calibration (between 0 and 4095, included).

        @return an integer corresponding to the minimal value measured during the calibration (between 0
        and 4095, included)

        On failure, throws an exception or returns YAnButton.CALIBRATIONMIN_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YAnButton.CALIBRATIONMIN_INVALID
        res = self._calibrationMin
        return res

    async def set_calibrationMin(self, newval: int) -> int:
        """
        Changes the minimal calibration value for the input (between 0 and 4095, included), without actually
        starting the automated calibration.  Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : an integer corresponding to the minimal calibration value for the input (between 0
        and 4095, included), without actually
                starting the automated calibration

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("calibrationMin", rest_val)

    async def get_sensitivity(self) -> int:
        """
        Returns the sensibility for the input (between 1 and 1000) for triggering user callbacks.

        @return an integer corresponding to the sensibility for the input (between 1 and 1000) for
        triggering user callbacks

        On failure, throws an exception or returns YAnButton.SENSITIVITY_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YAnButton.SENSITIVITY_INVALID
        res = self._sensitivity
        return res

    async def set_sensitivity(self, newval: int) -> int:
        """
        Changes the sensibility for the input (between 1 and 1000) for triggering user callbacks.
        The sensibility is used to filter variations around a fixed value, but does not preclude the
        transmission of events when the input value evolves constantly in the same direction.
        Special case: when the value 1000 is used, the callback will only be thrown when the logical state
        of the input switches from pressed to released and back.
        Remember to call the saveToFlash() method of the module if the modification must be kept.

        @param newval : an integer corresponding to the sensibility for the input (between 1 and 1000) for
        triggering user callbacks

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("sensitivity", rest_val)

    async def get_isPressed(self) -> int:
        """
        Returns true if the input (considered as binary) is active (closed contact), and false otherwise.

        @return either YAnButton.ISPRESSED_FALSE or YAnButton.ISPRESSED_TRUE, according to true if the
        input (considered as binary) is active (closed contact), and false otherwise

        On failure, throws an exception or returns YAnButton.ISPRESSED_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YAnButton.ISPRESSED_INVALID
        res = self._isPressed
        return res

    async def get_lastTimePressed(self) -> int:
        """
        Returns the number of elapsed milliseconds between the module power on and the last time
        the input button was pressed (the input contact transitioned from open to closed).

        @return an integer corresponding to the number of elapsed milliseconds between the module power on
        and the last time
                the input button was pressed (the input contact transitioned from open to closed)

        On failure, throws an exception or returns YAnButton.LASTTIMEPRESSED_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YAnButton.LASTTIMEPRESSED_INVALID
        res = self._lastTimePressed
        return res

    async def get_lastTimeReleased(self) -> int:
        """
        Returns the number of elapsed milliseconds between the module power on and the last time
        the input button was released (the input contact transitioned from closed to open).

        @return an integer corresponding to the number of elapsed milliseconds between the module power on
        and the last time
                the input button was released (the input contact transitioned from closed to open)

        On failure, throws an exception or returns YAnButton.LASTTIMERELEASED_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YAnButton.LASTTIMERELEASED_INVALID
        res = self._lastTimeReleased
        return res

    async def get_pulseCounter(self) -> int:
        """
        Returns the pulse counter value. The value is a 32 bit integer. In case
        of overflow (>=2^32), the counter will wrap. To reset the counter, just
        call the resetCounter() method.

        @return an integer corresponding to the pulse counter value

        On failure, throws an exception or returns YAnButton.PULSECOUNTER_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YAnButton.PULSECOUNTER_INVALID
        res = self._pulseCounter
        return res

    async def set_pulseCounter(self, newval: int) -> int:
        rest_val = str(newval)
        return await self._setAttr("pulseCounter", rest_val)

    async def get_pulseTimer(self) -> int:
        """
        Returns the timer of the pulses counter (ms).

        @return an integer corresponding to the timer of the pulses counter (ms)

        On failure, throws an exception or returns YAnButton.PULSETIMER_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YAnButton.PULSETIMER_INVALID
        res = self._pulseTimer
        return res

    async def get_inputType(self) -> int:
        """
        Returns the decoding method applied to the input (analog or multiplexed binary switches).

        @return a value among YAnButton.INPUTTYPE_ANALOG_FAST, YAnButton.INPUTTYPE_DIGITAL4,
        YAnButton.INPUTTYPE_ANALOG_SMOOTH and YAnButton.INPUTTYPE_DIGITAL_FAST corresponding to the
        decoding method applied to the input (analog or multiplexed binary switches)

        On failure, throws an exception or returns YAnButton.INPUTTYPE_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YAnButton.INPUTTYPE_INVALID
        res = self._inputType
        return res

    async def set_inputType(self, newval: int) -> int:
        """
        Changes the decoding method applied to the input (analog or multiplexed binary switches).
        Remember to call the saveToFlash() method of the module if the modification must be kept.

        @param newval : a value among YAnButton.INPUTTYPE_ANALOG_FAST, YAnButton.INPUTTYPE_DIGITAL4,
        YAnButton.INPUTTYPE_ANALOG_SMOOTH and YAnButton.INPUTTYPE_DIGITAL_FAST corresponding to the
        decoding method applied to the input (analog or multiplexed binary switches)

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("inputType", rest_val)

    @staticmethod
    def FindAnButton(func: str) -> YAnButton:
        """
        Retrieves an analog input for a given identifier.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the analog input is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YAnButton.isOnline() to test if the analog input is
        indeed online at a given time. In case of ambiguity when looking for
        an analog input by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the analog input, for instance
                YBUZZER2.anButton1.

        @return a YAnButton object allowing you to drive the analog input.
        """
        obj: Union[YAnButton, None]
        obj = YFunction._FindFromCache("AnButton", func)
        if obj is None:
            obj = YAnButton(YAPI, func)
            YFunction._AddToCache("AnButton", func, obj)
        return obj

    @staticmethod
    def FindAnButtonInContext(yctx: YAPIContext, func: str) -> YAnButton:
        """
        Retrieves an analog input for a given identifier in a YAPI context.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the analog input is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YAnButton.isOnline() to test if the analog input is
        indeed online at a given time. In case of ambiguity when looking for
        an analog input by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        @param yctx : a YAPI context
        @param func : a string that uniquely characterizes the analog input, for instance
                YBUZZER2.anButton1.

        @return a YAnButton object allowing you to drive the analog input.
        """
        obj: Union[YAnButton, None]
        obj = YFunction._FindFromCacheInContext(yctx, "AnButton", func)
        if obj is None:
            obj = YAnButton(yctx, func)
            YFunction._AddToCache("AnButton", func, obj)
        return obj

    if not _IS_MICROPYTHON:
        async def registerValueCallback(self, callback: YAnButtonValueCallback) -> int:
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

    async def resetCounter(self) -> int:
        """
        Returns the pulse counter value as well as its timer.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return await self.set_pulseCounter(0)

    # --- (end of YAnButton implementation)

