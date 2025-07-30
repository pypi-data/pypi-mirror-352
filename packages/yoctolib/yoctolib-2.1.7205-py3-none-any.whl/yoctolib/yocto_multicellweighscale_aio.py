# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: svn_id $
#
#  Asyncio implementation of YMultiCellWeighScale
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
Yoctopuce library: Asyncio implementation of YMultiCellWeighScale
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

# --- (YMultiCellWeighScale class start)
if not _IS_MICROPYTHON:
    # For CPython, use strongly typed callback types
    try:
        YMultiCellWeighScaleValueCallback = Union[Callable[['YMultiCellWeighScale', str], Any], None]
        YMultiCellWeighScaleTimedReportCallback = Union[Callable[['YMultiCellWeighScale', YMeasure], Any], None]
    except TypeError:
        YMultiCellWeighScaleValueCallback = Union[Callable, Awaitable]
        YMultiCellWeighScaleTimedReportCallback = Union[Callable, Awaitable]

# noinspection PyProtectedMember
class YMultiCellWeighScale(YSensor):
    """
    The YMultiCellWeighScale class provides a weight measurement from a set of ratiometric
    sensors. It can be used to control the bridge excitation parameters, in order to avoid
    measure shifts caused by temperature variation in the electronics, and can also
    automatically apply an additional correction factor based on temperature to
    compensate for offsets in the load cells themselves.

    """
    # --- (end of YMultiCellWeighScale class start)
    if not _IS_MICROPYTHON:
        # --- (YMultiCellWeighScale return codes)
        CELLCOUNT_INVALID: Final[int] = YAPI.INVALID_UINT
        TEMPAVGADAPTRATIO_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        TEMPCHGADAPTRATIO_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        COMPTEMPAVG_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        COMPTEMPCHG_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        COMPENSATION_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        ZEROTRACKING_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        COMMAND_INVALID: Final[str] = YAPI.INVALID_STRING
        EXTERNALSENSE_FALSE: Final[int] = 0
        EXTERNALSENSE_TRUE: Final[int] = 1
        EXTERNALSENSE_INVALID: Final[int] = -1
        EXCITATION_OFF: Final[int] = 0
        EXCITATION_DC: Final[int] = 1
        EXCITATION_AC: Final[int] = 2
        EXCITATION_INVALID: Final[int] = -1
        # --- (end of YMultiCellWeighScale return codes)

    # --- (YMultiCellWeighScale attributes declaration)
    _cellCount: int
    _externalSense: int
    _excitation: int
    _tempAvgAdaptRatio: float
    _tempChgAdaptRatio: float
    _compTempAvg: float
    _compTempChg: float
    _compensation: float
    _zeroTracking: float
    _command: str
    _valueCallback: YMultiCellWeighScaleValueCallback
    _timedReportCallback: YMultiCellWeighScaleTimedReportCallback
    # --- (end of YMultiCellWeighScale attributes declaration)


    def __init__(self, yctx: YAPIContext, func: str):
        super().__init__(yctx, func)
        self._className = 'MultiCellWeighScale'
        # --- (YMultiCellWeighScale constructor)
        self._cellCount = YMultiCellWeighScale.CELLCOUNT_INVALID
        self._externalSense = YMultiCellWeighScale.EXTERNALSENSE_INVALID
        self._excitation = YMultiCellWeighScale.EXCITATION_INVALID
        self._tempAvgAdaptRatio = YMultiCellWeighScale.TEMPAVGADAPTRATIO_INVALID
        self._tempChgAdaptRatio = YMultiCellWeighScale.TEMPCHGADAPTRATIO_INVALID
        self._compTempAvg = YMultiCellWeighScale.COMPTEMPAVG_INVALID
        self._compTempChg = YMultiCellWeighScale.COMPTEMPCHG_INVALID
        self._compensation = YMultiCellWeighScale.COMPENSATION_INVALID
        self._zeroTracking = YMultiCellWeighScale.ZEROTRACKING_INVALID
        self._command = YMultiCellWeighScale.COMMAND_INVALID
        # --- (end of YMultiCellWeighScale constructor)

    # --- (YMultiCellWeighScale implementation)

    @staticmethod
    def FirstMultiCellWeighScale() -> Union[YMultiCellWeighScale, None]:
        """
        Starts the enumeration of multi-cell weighing scale sensors currently accessible.
        Use the method YMultiCellWeighScale.nextMultiCellWeighScale() to iterate on
        next multi-cell weighing scale sensors.

        @return a pointer to a YMultiCellWeighScale object, corresponding to
                the first multi-cell weighing scale sensor currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = YAPI._yHash.getFirstHardwareId('MultiCellWeighScale')
        if not next_hwid:
            return None
        return YMultiCellWeighScale.FindMultiCellWeighScale(hwid2str(next_hwid))

    @staticmethod
    def FirstMultiCellWeighScaleInContext(yctx: YAPIContext) -> Union[YMultiCellWeighScale, None]:
        """
        Starts the enumeration of multi-cell weighing scale sensors currently accessible.
        Use the method YMultiCellWeighScale.nextMultiCellWeighScale() to iterate on
        next multi-cell weighing scale sensors.

        @param yctx : a YAPI context.

        @return a pointer to a YMultiCellWeighScale object, corresponding to
                the first multi-cell weighing scale sensor currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = yctx._yHash.getFirstHardwareId('MultiCellWeighScale')
        if not next_hwid:
            return None
        return YMultiCellWeighScale.FindMultiCellWeighScaleInContext(yctx, hwid2str(next_hwid))

    def nextMultiCellWeighScale(self):
        """
        Continues the enumeration of multi-cell weighing scale sensors started using yFirstMultiCellWeighScale().
        Caution: You can't make any assumption about the returned multi-cell weighing scale sensors order.
        If you want to find a specific a multi-cell weighing scale sensor, use
        MultiCellWeighScale.findMultiCellWeighScale()
        and a hardwareID or a logical name.

        @return a pointer to a YMultiCellWeighScale object, corresponding to
                a multi-cell weighing scale sensor currently online, or a None pointer
                if there are no more multi-cell weighing scale sensors to enumerate.
        """
        next_hwid: Union[HwId, None] = None
        try:
            hwid: HwId = self._yapi._yHash.resolveHwID(self._className, self._func)
            next_hwid = self._yapi._yHash.getNextHardwareId(self._className, hwid)
        except YAPI_Exception:
            pass
        if not next_hwid:
            return None
        return YMultiCellWeighScale.FindMultiCellWeighScaleInContext(self._yapi, hwid2str(next_hwid))

    def _parseAttr(self, json_val: dict) -> None:
        if 'cellCount' in json_val:
            self._cellCount = json_val["cellCount"]
        if 'externalSense' in json_val:
            self._externalSense = json_val["externalSense"] > 0
        if 'excitation' in json_val:
            self._excitation = json_val["excitation"]
        if 'tempAvgAdaptRatio' in json_val:
            self._tempAvgAdaptRatio = round(json_val["tempAvgAdaptRatio"] / 65.536) / 1000.0
        if 'tempChgAdaptRatio' in json_val:
            self._tempChgAdaptRatio = round(json_val["tempChgAdaptRatio"] / 65.536) / 1000.0
        if 'compTempAvg' in json_val:
            self._compTempAvg = round(json_val["compTempAvg"] / 65.536) / 1000.0
        if 'compTempChg' in json_val:
            self._compTempChg = round(json_val["compTempChg"] / 65.536) / 1000.0
        if 'compensation' in json_val:
            self._compensation = round(json_val["compensation"] / 65.536) / 1000.0
        if 'zeroTracking' in json_val:
            self._zeroTracking = round(json_val["zeroTracking"] / 65.536) / 1000.0
        if 'command' in json_val:
            self._command = json_val["command"]
        super()._parseAttr(json_val)

    async def set_unit(self, newval: str) -> int:
        """
        Changes the measuring unit for the weight.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a string corresponding to the measuring unit for the weight

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return await self._setAttr("unit", rest_val)

    async def get_cellCount(self) -> int:
        """
        Returns the number of load cells in use.

        @return an integer corresponding to the number of load cells in use

        On failure, throws an exception or returns YMultiCellWeighScale.CELLCOUNT_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMultiCellWeighScale.CELLCOUNT_INVALID
        res = self._cellCount
        return res

    async def set_cellCount(self, newval: int) -> int:
        """
        Changes the number of load cells in use. Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : an integer corresponding to the number of load cells in use

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("cellCount", rest_val)

    async def get_externalSense(self) -> int:
        """
        Returns true if entry 4 is used as external sense for 6-wires load cells.

        @return either YMultiCellWeighScale.EXTERNALSENSE_FALSE or YMultiCellWeighScale.EXTERNALSENSE_TRUE,
        according to true if entry 4 is used as external sense for 6-wires load cells

        On failure, throws an exception or returns YMultiCellWeighScale.EXTERNALSENSE_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMultiCellWeighScale.EXTERNALSENSE_INVALID
        res = self._externalSense
        return res

    async def set_externalSense(self, newval: int) -> int:
        """
        Changes the configuration to tell if entry 4 is used as external sense for
        6-wires load cells. Remember to call the saveToFlash() method of the
        module if the modification must be kept.

        @param newval : either YMultiCellWeighScale.EXTERNALSENSE_FALSE or
        YMultiCellWeighScale.EXTERNALSENSE_TRUE, according to the configuration to tell if entry 4 is used
        as external sense for
                6-wires load cells

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return await self._setAttr("externalSense", rest_val)

    async def get_excitation(self) -> int:
        """
        Returns the current load cell bridge excitation method.

        @return a value among YMultiCellWeighScale.EXCITATION_OFF, YMultiCellWeighScale.EXCITATION_DC and
        YMultiCellWeighScale.EXCITATION_AC corresponding to the current load cell bridge excitation method

        On failure, throws an exception or returns YMultiCellWeighScale.EXCITATION_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMultiCellWeighScale.EXCITATION_INVALID
        res = self._excitation
        return res

    async def set_excitation(self, newval: int) -> int:
        """
        Changes the current load cell bridge excitation method.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a value among YMultiCellWeighScale.EXCITATION_OFF,
        YMultiCellWeighScale.EXCITATION_DC and YMultiCellWeighScale.EXCITATION_AC corresponding to the
        current load cell bridge excitation method

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return await self._setAttr("excitation", rest_val)

    async def set_tempAvgAdaptRatio(self, newval: float) -> int:
        """
        Changes the averaged temperature update rate, in per mille.
        The purpose of this adaptation ratio is to model the thermal inertia of the load cell.
        The averaged temperature is updated every 10 seconds, by applying this adaptation rate
        to the difference between the measures ambient temperature and the current compensation
        temperature. The standard rate is 0.2 per mille, and the maximal rate is 65 per mille.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a floating point number corresponding to the averaged temperature update rate, in per mille

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return await self._setAttr("tempAvgAdaptRatio", rest_val)

    async def get_tempAvgAdaptRatio(self) -> float:
        """
        Returns the averaged temperature update rate, in per mille.
        The purpose of this adaptation ratio is to model the thermal inertia of the load cell.
        The averaged temperature is updated every 10 seconds, by applying this adaptation rate
        to the difference between the measures ambient temperature and the current compensation
        temperature. The standard rate is 0.2 per mille, and the maximal rate is 65 per mille.

        @return a floating point number corresponding to the averaged temperature update rate, in per mille

        On failure, throws an exception or returns YMultiCellWeighScale.TEMPAVGADAPTRATIO_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMultiCellWeighScale.TEMPAVGADAPTRATIO_INVALID
        res = self._tempAvgAdaptRatio
        return res

    async def set_tempChgAdaptRatio(self, newval: float) -> int:
        """
        Changes the temperature change update rate, in per mille.
        The temperature change is updated every 10 seconds, by applying this adaptation rate
        to the difference between the measures ambient temperature and the current temperature used for
        change compensation. The standard rate is 0.6 per mille, and the maximal rate is 65 per mille.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a floating point number corresponding to the temperature change update rate, in per mille

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return await self._setAttr("tempChgAdaptRatio", rest_val)

    async def get_tempChgAdaptRatio(self) -> float:
        """
        Returns the temperature change update rate, in per mille.
        The temperature change is updated every 10 seconds, by applying this adaptation rate
        to the difference between the measures ambient temperature and the current temperature used for
        change compensation. The standard rate is 0.6 per mille, and the maximal rate is 65 per mille.

        @return a floating point number corresponding to the temperature change update rate, in per mille

        On failure, throws an exception or returns YMultiCellWeighScale.TEMPCHGADAPTRATIO_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMultiCellWeighScale.TEMPCHGADAPTRATIO_INVALID
        res = self._tempChgAdaptRatio
        return res

    async def get_compTempAvg(self) -> float:
        """
        Returns the current averaged temperature, used for thermal compensation.

        @return a floating point number corresponding to the current averaged temperature, used for thermal compensation

        On failure, throws an exception or returns YMultiCellWeighScale.COMPTEMPAVG_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMultiCellWeighScale.COMPTEMPAVG_INVALID
        res = self._compTempAvg
        return res

    async def get_compTempChg(self) -> float:
        """
        Returns the current temperature variation, used for thermal compensation.

        @return a floating point number corresponding to the current temperature variation, used for
        thermal compensation

        On failure, throws an exception or returns YMultiCellWeighScale.COMPTEMPCHG_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMultiCellWeighScale.COMPTEMPCHG_INVALID
        res = self._compTempChg
        return res

    async def get_compensation(self) -> float:
        """
        Returns the current current thermal compensation value.

        @return a floating point number corresponding to the current current thermal compensation value

        On failure, throws an exception or returns YMultiCellWeighScale.COMPENSATION_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMultiCellWeighScale.COMPENSATION_INVALID
        res = self._compensation
        return res

    async def set_zeroTracking(self, newval: float) -> int:
        """
        Changes the zero tracking threshold value. When this threshold is larger than
        zero, any measure under the threshold will automatically be ignored and the
        zero compensation will be updated.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a floating point number corresponding to the zero tracking threshold value

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return await self._setAttr("zeroTracking", rest_val)

    async def get_zeroTracking(self) -> float:
        """
        Returns the zero tracking threshold value. When this threshold is larger than
        zero, any measure under the threshold will automatically be ignored and the
        zero compensation will be updated.

        @return a floating point number corresponding to the zero tracking threshold value

        On failure, throws an exception or returns YMultiCellWeighScale.ZEROTRACKING_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMultiCellWeighScale.ZEROTRACKING_INVALID
        res = self._zeroTracking
        return res

    async def get_command(self) -> str:
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMultiCellWeighScale.COMMAND_INVALID
        res = self._command
        return res

    async def set_command(self, newval: str) -> int:
        rest_val = newval
        return await self._setAttr("command", rest_val)

    @staticmethod
    def FindMultiCellWeighScale(func: str) -> YMultiCellWeighScale:
        """
        Retrieves a multi-cell weighing scale sensor for a given identifier.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the multi-cell weighing scale sensor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YMultiCellWeighScale.isOnline() to test if the multi-cell weighing scale sensor is
        indeed online at a given time. In case of ambiguity when looking for
        a multi-cell weighing scale sensor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the multi-cell weighing scale sensor, for instance
                YWMBRDG1.multiCellWeighScale.

        @return a YMultiCellWeighScale object allowing you to drive the multi-cell weighing scale sensor.
        """
        obj: Union[YMultiCellWeighScale, None]
        obj = YFunction._FindFromCache("MultiCellWeighScale", func)
        if obj is None:
            obj = YMultiCellWeighScale(YAPI, func)
            YFunction._AddToCache("MultiCellWeighScale", func, obj)
        return obj

    @staticmethod
    def FindMultiCellWeighScaleInContext(yctx: YAPIContext, func: str) -> YMultiCellWeighScale:
        """
        Retrieves a multi-cell weighing scale sensor for a given identifier in a YAPI context.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the multi-cell weighing scale sensor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YMultiCellWeighScale.isOnline() to test if the multi-cell weighing scale sensor is
        indeed online at a given time. In case of ambiguity when looking for
        a multi-cell weighing scale sensor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        @param yctx : a YAPI context
        @param func : a string that uniquely characterizes the multi-cell weighing scale sensor, for instance
                YWMBRDG1.multiCellWeighScale.

        @return a YMultiCellWeighScale object allowing you to drive the multi-cell weighing scale sensor.
        """
        obj: Union[YMultiCellWeighScale, None]
        obj = YFunction._FindFromCacheInContext(yctx, "MultiCellWeighScale", func)
        if obj is None:
            obj = YMultiCellWeighScale(yctx, func)
            YFunction._AddToCache("MultiCellWeighScale", func, obj)
        return obj

    if not _IS_MICROPYTHON:
        async def registerValueCallback(self, callback: YMultiCellWeighScaleValueCallback) -> int:
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
        async def registerTimedReportCallback(self, callback: YMultiCellWeighScaleTimedReportCallback) -> int:
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

    async def tare(self) -> int:
        """
        Adapts the load cell signal bias (stored in the corresponding genericSensor)
        so that the current signal corresponds to a zero weight. Remember to call the
        saveToFlash() method of the module if the modification must be kept.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return await self.set_command("T")

    async def setupSpan(self, currWeight: float, maxWeight: float) -> int:
        """
        Configures the load cells span parameters (stored in the corresponding genericSensors)
        so that the current signal corresponds to the specified reference weight.

        @param currWeight : reference weight presently on the load cell.
        @param maxWeight : maximum weight to be expected on the load cell.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return await self.set_command("S%d:%d" % (int(round(1000*currWeight)), int(round(1000*maxWeight))))

    # --- (end of YMultiCellWeighScale implementation)

