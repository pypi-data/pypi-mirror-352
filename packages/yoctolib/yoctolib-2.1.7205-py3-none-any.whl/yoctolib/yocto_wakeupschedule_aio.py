# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: svn_id $
#
#  Asyncio implementation of YWakeUpSchedule
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
Yoctopuce library: Asyncio implementation of YWakeUpSchedule
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

# --- (YWakeUpSchedule class start)
if not _IS_MICROPYTHON:
    # For CPython, use strongly typed callback types
    try:
        YWakeUpScheduleValueCallback = Union[Callable[['YWakeUpSchedule', str], Any], None]
    except TypeError:
        YWakeUpScheduleValueCallback = Union[Callable, Awaitable]

# noinspection PyProtectedMember
class YWakeUpSchedule(YFunction):
    """
    The YWakeUpSchedule class implements a wake up condition. The wake up time is
    specified as a set of months and/or days and/or hours and/or minutes when the
    wake up should happen.

    """
    # --- (end of YWakeUpSchedule class start)
    if not _IS_MICROPYTHON:
        # --- (YWakeUpSchedule return codes)
        MINUTESA_INVALID: Final[int] = YAPI.INVALID_UINT
        MINUTESB_INVALID: Final[int] = YAPI.INVALID_UINT
        HOURS_INVALID: Final[int] = YAPI.INVALID_UINT
        WEEKDAYS_INVALID: Final[int] = YAPI.INVALID_UINT
        MONTHDAYS_INVALID: Final[int] = YAPI.INVALID_UINT
        MONTHS_INVALID: Final[int] = YAPI.INVALID_UINT
        SECONDSBEFORE_INVALID: Final[int] = YAPI.INVALID_UINT
        NEXTOCCURENCE_INVALID: Final[int] = YAPI.INVALID_LONG
        # --- (end of YWakeUpSchedule return codes)

    # --- (YWakeUpSchedule attributes declaration)
    _minutesA: int
    _minutesB: int
    _hours: int
    _weekDays: int
    _monthDays: int
    _months: int
    _secondsBefore: int
    _nextOccurence: int
    _valueCallback: YWakeUpScheduleValueCallback
    # --- (end of YWakeUpSchedule attributes declaration)


    def __init__(self, yctx: YAPIContext, func: str):
        super().__init__(yctx, func)
        self._className = 'WakeUpSchedule'
        # --- (YWakeUpSchedule constructor)
        self._minutesA = YWakeUpSchedule.MINUTESA_INVALID
        self._minutesB = YWakeUpSchedule.MINUTESB_INVALID
        self._hours = YWakeUpSchedule.HOURS_INVALID
        self._weekDays = YWakeUpSchedule.WEEKDAYS_INVALID
        self._monthDays = YWakeUpSchedule.MONTHDAYS_INVALID
        self._months = YWakeUpSchedule.MONTHS_INVALID
        self._secondsBefore = YWakeUpSchedule.SECONDSBEFORE_INVALID
        self._nextOccurence = YWakeUpSchedule.NEXTOCCURENCE_INVALID
        # --- (end of YWakeUpSchedule constructor)

    # --- (YWakeUpSchedule implementation)

    @staticmethod
    def FirstWakeUpSchedule() -> Union[YWakeUpSchedule, None]:
        """
        Starts the enumeration of wake up schedules currently accessible.
        Use the method YWakeUpSchedule.nextWakeUpSchedule() to iterate on
        next wake up schedules.

        @return a pointer to a YWakeUpSchedule object, corresponding to
                the first wake up schedule currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = YAPI._yHash.getFirstHardwareId('WakeUpSchedule')
        if not next_hwid:
            return None
        return YWakeUpSchedule.FindWakeUpSchedule(hwid2str(next_hwid))

    @staticmethod
    def FirstWakeUpScheduleInContext(yctx: YAPIContext) -> Union[YWakeUpSchedule, None]:
        """
        Starts the enumeration of wake up schedules currently accessible.
        Use the method YWakeUpSchedule.nextWakeUpSchedule() to iterate on
        next wake up schedules.

        @param yctx : a YAPI context.

        @return a pointer to a YWakeUpSchedule object, corresponding to
                the first wake up schedule currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = yctx._yHash.getFirstHardwareId('WakeUpSchedule')
        if not next_hwid:
            return None
        return YWakeUpSchedule.FindWakeUpScheduleInContext(yctx, hwid2str(next_hwid))

    def nextWakeUpSchedule(self):
        """
        Continues the enumeration of wake up schedules started using yFirstWakeUpSchedule().
        Caution: You can't make any assumption about the returned wake up schedules order.
        If you want to find a specific a wake up schedule, use WakeUpSchedule.findWakeUpSchedule()
        and a hardwareID or a logical name.

        @return a pointer to a YWakeUpSchedule object, corresponding to
                a wake up schedule currently online, or a None pointer
                if there are no more wake up schedules to enumerate.
        """
        next_hwid: Union[HwId, None] = None
        try:
            hwid: HwId = self._yapi._yHash.resolveHwID(self._className, self._func)
            next_hwid = self._yapi._yHash.getNextHardwareId(self._className, hwid)
        except YAPI_Exception:
            pass
        if not next_hwid:
            return None
        return YWakeUpSchedule.FindWakeUpScheduleInContext(self._yapi, hwid2str(next_hwid))

    def _parseAttr(self, json_val: dict) -> None:
        if 'minutesA' in json_val:
            self._minutesA = json_val["minutesA"]
        if 'minutesB' in json_val:
            self._minutesB = json_val["minutesB"]
        if 'hours' in json_val:
            self._hours = json_val["hours"]
        if 'weekDays' in json_val:
            self._weekDays = json_val["weekDays"]
        if 'monthDays' in json_val:
            self._monthDays = json_val["monthDays"]
        if 'months' in json_val:
            self._months = json_val["months"]
        if 'secondsBefore' in json_val:
            self._secondsBefore = json_val["secondsBefore"]
        if 'nextOccurence' in json_val:
            self._nextOccurence = json_val["nextOccurence"]
        super()._parseAttr(json_val)

    async def get_minutesA(self) -> int:
        """
        Returns the minutes in the 00-29 interval of each hour scheduled for wake up.

        @return an integer corresponding to the minutes in the 00-29 interval of each hour scheduled for wake up

        On failure, throws an exception or returns YWakeUpSchedule.MINUTESA_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpSchedule.MINUTESA_INVALID
        res = self._minutesA
        return res

    async def set_minutesA(self, newval: int) -> int:
        """
        Changes the minutes in the 00-29 interval when a wake up must take place.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : an integer corresponding to the minutes in the 00-29 interval when a wake up must take place

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("minutesA", rest_val)

    async def get_minutesB(self) -> int:
        """
        Returns the minutes in the 30-59 interval of each hour scheduled for wake up.

        @return an integer corresponding to the minutes in the 30-59 interval of each hour scheduled for wake up

        On failure, throws an exception or returns YWakeUpSchedule.MINUTESB_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpSchedule.MINUTESB_INVALID
        res = self._minutesB
        return res

    async def set_minutesB(self, newval: int) -> int:
        """
        Changes the minutes in the 30-59 interval when a wake up must take place.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : an integer corresponding to the minutes in the 30-59 interval when a wake up must take place

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("minutesB", rest_val)

    async def get_hours(self) -> int:
        """
        Returns the hours scheduled for wake up.

        @return an integer corresponding to the hours scheduled for wake up

        On failure, throws an exception or returns YWakeUpSchedule.HOURS_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpSchedule.HOURS_INVALID
        res = self._hours
        return res

    async def set_hours(self, newval: int) -> int:
        """
        Changes the hours when a wake up must take place.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : an integer corresponding to the hours when a wake up must take place

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("hours", rest_val)

    async def get_weekDays(self) -> int:
        """
        Returns the days of the week scheduled for wake up.

        @return an integer corresponding to the days of the week scheduled for wake up

        On failure, throws an exception or returns YWakeUpSchedule.WEEKDAYS_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpSchedule.WEEKDAYS_INVALID
        res = self._weekDays
        return res

    async def set_weekDays(self, newval: int) -> int:
        """
        Changes the days of the week when a wake up must take place.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : an integer corresponding to the days of the week when a wake up must take place

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("weekDays", rest_val)

    async def get_monthDays(self) -> int:
        """
        Returns the days of the month scheduled for wake up.

        @return an integer corresponding to the days of the month scheduled for wake up

        On failure, throws an exception or returns YWakeUpSchedule.MONTHDAYS_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpSchedule.MONTHDAYS_INVALID
        res = self._monthDays
        return res

    async def set_monthDays(self, newval: int) -> int:
        """
        Changes the days of the month when a wake up must take place.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : an integer corresponding to the days of the month when a wake up must take place

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("monthDays", rest_val)

    async def get_months(self) -> int:
        """
        Returns the months scheduled for wake up.

        @return an integer corresponding to the months scheduled for wake up

        On failure, throws an exception or returns YWakeUpSchedule.MONTHS_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpSchedule.MONTHS_INVALID
        res = self._months
        return res

    async def set_months(self, newval: int) -> int:
        """
        Changes the months when a wake up must take place.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : an integer corresponding to the months when a wake up must take place

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("months", rest_val)

    async def get_secondsBefore(self) -> int:
        """
        Returns the number of seconds to anticipate wake-up time to allow
        the system to power-up.

        @return an integer corresponding to the number of seconds to anticipate wake-up time to allow
                the system to power-up

        On failure, throws an exception or returns YWakeUpSchedule.SECONDSBEFORE_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpSchedule.SECONDSBEFORE_INVALID
        res = self._secondsBefore
        return res

    async def set_secondsBefore(self, newval: int) -> int:
        """
        Changes the number of seconds to anticipate wake-up time to allow
        the system to power-up.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : an integer corresponding to the number of seconds to anticipate wake-up time to allow
                the system to power-up

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("secondsBefore", rest_val)

    async def get_nextOccurence(self) -> int:
        """
        Returns the date/time (seconds) of the next wake up occurrence.

        @return an integer corresponding to the date/time (seconds) of the next wake up occurrence

        On failure, throws an exception or returns YWakeUpSchedule.NEXTOCCURENCE_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpSchedule.NEXTOCCURENCE_INVALID
        res = self._nextOccurence
        return res

    @staticmethod
    def FindWakeUpSchedule(func: str) -> YWakeUpSchedule:
        """
        Retrieves a wake up schedule for a given identifier.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the wake up schedule is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YWakeUpSchedule.isOnline() to test if the wake up schedule is
        indeed online at a given time. In case of ambiguity when looking for
        a wake up schedule by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the wake up schedule, for instance
                YHUBGSM5.wakeUpSchedule1.

        @return a YWakeUpSchedule object allowing you to drive the wake up schedule.
        """
        obj: Union[YWakeUpSchedule, None]
        obj = YFunction._FindFromCache("WakeUpSchedule", func)
        if obj is None:
            obj = YWakeUpSchedule(YAPI, func)
            YFunction._AddToCache("WakeUpSchedule", func, obj)
        return obj

    @staticmethod
    def FindWakeUpScheduleInContext(yctx: YAPIContext, func: str) -> YWakeUpSchedule:
        """
        Retrieves a wake up schedule for a given identifier in a YAPI context.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the wake up schedule is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YWakeUpSchedule.isOnline() to test if the wake up schedule is
        indeed online at a given time. In case of ambiguity when looking for
        a wake up schedule by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        @param yctx : a YAPI context
        @param func : a string that uniquely characterizes the wake up schedule, for instance
                YHUBGSM5.wakeUpSchedule1.

        @return a YWakeUpSchedule object allowing you to drive the wake up schedule.
        """
        obj: Union[YWakeUpSchedule, None]
        obj = YFunction._FindFromCacheInContext(yctx, "WakeUpSchedule", func)
        if obj is None:
            obj = YWakeUpSchedule(yctx, func)
            YFunction._AddToCache("WakeUpSchedule", func, obj)
        return obj

    if not _IS_MICROPYTHON:
        async def registerValueCallback(self, callback: YWakeUpScheduleValueCallback) -> int:
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

    async def get_minutes(self) -> int:
        """
        Returns all the minutes of each hour that are scheduled for wake up.
        """
        res: int

        res = await self.get_minutesB()
        res = (res << 30)
        res = res + await self.get_minutesA()
        return res

    async def set_minutes(self, bitmap: int) -> int:
        """
        Changes all the minutes where a wake up must take place.

        @param bitmap : Minutes 00-59 of each hour scheduled for wake up.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        await self.set_minutesA((bitmap & 0x3fffffff))
        bitmap = (bitmap >> 30)
        return await self.set_minutesB((bitmap & 0x3fffffff))

    # --- (end of YWakeUpSchedule implementation)

