# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: svn_id $
#
#  Asyncio implementation of YMicroPython
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
Yoctopuce library: Asyncio implementation of YMicroPython
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
    YAPIContext, YAPI, YAPI_Exception, HwId, hwid2str, YFunction, xbytearray, xarray
)

async def yInternalEventCallback(obj: YMicroPython, value: str):
    await obj._internalEventHandler(value)

# --- (YMicroPython class start)
if not _IS_MICROPYTHON:
    # For CPython, use strongly typed callback types
    try:
        YMicroPythonValueCallback = Union[Callable[['YMicroPython', str], Any], None]
        YMicroPythonLogCallback = Union[Callable[['YMicroPython', str], Any], None]
    except TypeError:
        YMicroPythonValueCallback = Union[Callable, Awaitable]
        YMicroPythonLogCallback = Union[Callable, Awaitable]

# noinspection PyProtectedMember
class YMicroPython(YFunction):
    """
    The YMicroPython class provides control of the MicroPython interpreter
    that can be found on some Yoctopuce devices.

    """
    # --- (end of YMicroPython class start)
    if not _IS_MICROPYTHON:
        # --- (YMicroPython return codes)
        LASTMSG_INVALID: Final[str] = YAPI.INVALID_STRING
        HEAPUSAGE_INVALID: Final[int] = YAPI.INVALID_UINT
        XHEAPUSAGE_INVALID: Final[int] = YAPI.INVALID_UINT
        STACKUSAGE_INVALID: Final[int] = YAPI.INVALID_UINT
        CURRENTSCRIPT_INVALID: Final[str] = YAPI.INVALID_STRING
        STARTUPSCRIPT_INVALID: Final[str] = YAPI.INVALID_STRING
        STARTUPDELAY_INVALID: Final[float] = YAPI.INVALID_DOUBLE
        COMMAND_INVALID: Final[str] = YAPI.INVALID_STRING
        DEBUGMODE_OFF: Final[int] = 0
        DEBUGMODE_ON: Final[int] = 1
        DEBUGMODE_INVALID: Final[int] = -1
        # --- (end of YMicroPython return codes)

    # --- (YMicroPython attributes declaration)
    _lastMsg: str
    _heapUsage: int
    _xheapUsage: int
    _stackUsage: int
    _currentScript: str
    _startupScript: str
    _startupDelay: float
    _debugMode: int
    _command: str
    _valueCallback: YMicroPythonValueCallback
    _logCallback: YMicroPythonLogCallback
    _isFirstCb: bool
    _prevCbPos: int
    _logPos: int
    _prevPartialLog: str
    # --- (end of YMicroPython attributes declaration)


    def __init__(self, yctx: YAPIContext, func: str):
        super().__init__(yctx, func)
        self._className = 'MicroPython'
        # --- (YMicroPython constructor)
        self._lastMsg = YMicroPython.LASTMSG_INVALID
        self._heapUsage = YMicroPython.HEAPUSAGE_INVALID
        self._xheapUsage = YMicroPython.XHEAPUSAGE_INVALID
        self._stackUsage = YMicroPython.STACKUSAGE_INVALID
        self._currentScript = YMicroPython.CURRENTSCRIPT_INVALID
        self._startupScript = YMicroPython.STARTUPSCRIPT_INVALID
        self._startupDelay = YMicroPython.STARTUPDELAY_INVALID
        self._debugMode = YMicroPython.DEBUGMODE_INVALID
        self._command = YMicroPython.COMMAND_INVALID
        self._isFirstCb = False
        self._prevCbPos = 0
        self._logPos = 0
        self._prevPartialLog = ''
        # --- (end of YMicroPython constructor)

    # --- (YMicroPython implementation)

    @staticmethod
    def FirstMicroPython() -> Union[YMicroPython, None]:
        """
        Starts the enumeration of MicroPython interpreters currently accessible.
        Use the method YMicroPython.nextMicroPython() to iterate on
        next MicroPython interpreters.

        @return a pointer to a YMicroPython object, corresponding to
                the first MicroPython interpreter currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = YAPI._yHash.getFirstHardwareId('MicroPython')
        if not next_hwid:
            return None
        return YMicroPython.FindMicroPython(hwid2str(next_hwid))

    @staticmethod
    def FirstMicroPythonInContext(yctx: YAPIContext) -> Union[YMicroPython, None]:
        """
        Starts the enumeration of MicroPython interpreters currently accessible.
        Use the method YMicroPython.nextMicroPython() to iterate on
        next MicroPython interpreters.

        @param yctx : a YAPI context.

        @return a pointer to a YMicroPython object, corresponding to
                the first MicroPython interpreter currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = yctx._yHash.getFirstHardwareId('MicroPython')
        if not next_hwid:
            return None
        return YMicroPython.FindMicroPythonInContext(yctx, hwid2str(next_hwid))

    def nextMicroPython(self):
        """
        Continues the enumeration of MicroPython interpreters started using yFirstMicroPython().
        Caution: You can't make any assumption about the returned MicroPython interpreters order.
        If you want to find a specific a MicroPython interpreter, use MicroPython.findMicroPython()
        and a hardwareID or a logical name.

        @return a pointer to a YMicroPython object, corresponding to
                a MicroPython interpreter currently online, or a None pointer
                if there are no more MicroPython interpreters to enumerate.
        """
        next_hwid: Union[HwId, None] = None
        try:
            hwid: HwId = self._yapi._yHash.resolveHwID(self._className, self._func)
            next_hwid = self._yapi._yHash.getNextHardwareId(self._className, hwid)
        except YAPI_Exception:
            pass
        if not next_hwid:
            return None
        return YMicroPython.FindMicroPythonInContext(self._yapi, hwid2str(next_hwid))

    def _parseAttr(self, json_val: dict) -> None:
        if 'lastMsg' in json_val:
            self._lastMsg = json_val["lastMsg"]
        if 'heapUsage' in json_val:
            self._heapUsage = json_val["heapUsage"]
        if 'xheapUsage' in json_val:
            self._xheapUsage = json_val["xheapUsage"]
        if 'stackUsage' in json_val:
            self._stackUsage = json_val["stackUsage"]
        if 'currentScript' in json_val:
            self._currentScript = json_val["currentScript"]
        if 'startupScript' in json_val:
            self._startupScript = json_val["startupScript"]
        if 'startupDelay' in json_val:
            self._startupDelay = round(json_val["startupDelay"] / 65.536) / 1000.0
        if 'debugMode' in json_val:
            self._debugMode = json_val["debugMode"] > 0
        if 'command' in json_val:
            self._command = json_val["command"]
        super()._parseAttr(json_val)

    async def get_lastMsg(self) -> str:
        """
        Returns the last message produced by a python script.

        @return a string corresponding to the last message produced by a python script

        On failure, throws an exception or returns YMicroPython.LASTMSG_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMicroPython.LASTMSG_INVALID
        res = self._lastMsg
        return res

    async def get_heapUsage(self) -> int:
        """
        Returns the percentage of MicroPython main memory in use,
        as observed at the end of the last garbage collection.

        @return an integer corresponding to the percentage of MicroPython main memory in use,
                as observed at the end of the last garbage collection

        On failure, throws an exception or returns YMicroPython.HEAPUSAGE_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMicroPython.HEAPUSAGE_INVALID
        res = self._heapUsage
        return res

    async def get_xheapUsage(self) -> int:
        """
        Returns the percentage of MicroPython external memory in use,
        as observed at the end of the last garbage collection.

        @return an integer corresponding to the percentage of MicroPython external memory in use,
                as observed at the end of the last garbage collection

        On failure, throws an exception or returns YMicroPython.XHEAPUSAGE_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMicroPython.XHEAPUSAGE_INVALID
        res = self._xheapUsage
        return res

    async def get_stackUsage(self) -> int:
        """
        Returns the maximum percentage of MicroPython call stack in use,
        as observed at the end of the last garbage collection.

        @return an integer corresponding to the maximum percentage of MicroPython call stack in use,
                as observed at the end of the last garbage collection

        On failure, throws an exception or returns YMicroPython.STACKUSAGE_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMicroPython.STACKUSAGE_INVALID
        res = self._stackUsage
        return res

    async def get_currentScript(self) -> str:
        """
        Returns the name of currently active script, if any.

        @return a string corresponding to the name of currently active script, if any

        On failure, throws an exception or returns YMicroPython.CURRENTSCRIPT_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMicroPython.CURRENTSCRIPT_INVALID
        res = self._currentScript
        return res

    async def set_currentScript(self, newval: str) -> int:
        """
        Stops current running script, and/or selects a script to run immediately in a
        fresh new environment. If the MicroPython interpreter is busy running a script,
        this function will abort it immediately and reset the execution environment.
        If a non-empty string is given as argument, the new script will be started.

        @param newval : a string

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return await self._setAttr("currentScript", rest_val)

    async def get_startupScript(self) -> str:
        """
        Returns the name of the script to run when the device is powered on.

        @return a string corresponding to the name of the script to run when the device is powered on

        On failure, throws an exception or returns YMicroPython.STARTUPSCRIPT_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMicroPython.STARTUPSCRIPT_INVALID
        res = self._startupScript
        return res

    async def set_startupScript(self, newval: str) -> int:
        """
        Changes the script to run when the device is powered on.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a string corresponding to the script to run when the device is powered on

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return await self._setAttr("startupScript", rest_val)

    async def set_startupDelay(self, newval: float) -> int:
        """
        Changes the wait time before running the startup script on power on, between 0.1
        second and 25 seconds. Remember to call the saveToFlash() method of the
        module if the modification must be kept.

        @param newval : a floating point number corresponding to the wait time before running the startup
        script on power on, between 0.1
                second and 25 seconds

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return await self._setAttr("startupDelay", rest_val)

    async def get_startupDelay(self) -> float:
        """
        Returns the wait time before running the startup script on power on,
        between 0.1 second and 25 seconds.

        @return a floating point number corresponding to the wait time before running the startup script on power on,
                between 0.1 second and 25 seconds

        On failure, throws an exception or returns YMicroPython.STARTUPDELAY_INVALID.
        """
        res: float
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMicroPython.STARTUPDELAY_INVALID
        res = self._startupDelay
        return res

    async def get_debugMode(self) -> int:
        """
        Returns the activation state of MicroPython debugging interface.

        @return either YMicroPython.DEBUGMODE_OFF or YMicroPython.DEBUGMODE_ON, according to the activation
        state of MicroPython debugging interface

        On failure, throws an exception or returns YMicroPython.DEBUGMODE_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMicroPython.DEBUGMODE_INVALID
        res = self._debugMode
        return res

    async def set_debugMode(self, newval: int) -> int:
        """
        Changes the activation state of MicroPython debugging interface.

        @param newval : either YMicroPython.DEBUGMODE_OFF or YMicroPython.DEBUGMODE_ON, according to the
        activation state of MicroPython debugging interface

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return await self._setAttr("debugMode", rest_val)

    async def get_command(self) -> str:
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YMicroPython.COMMAND_INVALID
        res = self._command
        return res

    async def set_command(self, newval: str) -> int:
        rest_val = newval
        return await self._setAttr("command", rest_val)

    @staticmethod
    def FindMicroPython(func: str) -> YMicroPython:
        """
        Retrieves a MicroPython interpreter for a given identifier.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the MicroPython interpreter is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YMicroPython.isOnline() to test if the MicroPython interpreter is
        indeed online at a given time. In case of ambiguity when looking for
        a MicroPython interpreter by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the MicroPython interpreter, for instance
                MyDevice.microPython.

        @return a YMicroPython object allowing you to drive the MicroPython interpreter.
        """
        obj: Union[YMicroPython, None]
        obj = YFunction._FindFromCache("MicroPython", func)
        if obj is None:
            obj = YMicroPython(YAPI, func)
            YFunction._AddToCache("MicroPython", func, obj)
        return obj

    @staticmethod
    def FindMicroPythonInContext(yctx: YAPIContext, func: str) -> YMicroPython:
        """
        Retrieves a MicroPython interpreter for a given identifier in a YAPI context.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the MicroPython interpreter is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YMicroPython.isOnline() to test if the MicroPython interpreter is
        indeed online at a given time. In case of ambiguity when looking for
        a MicroPython interpreter by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        @param yctx : a YAPI context
        @param func : a string that uniquely characterizes the MicroPython interpreter, for instance
                MyDevice.microPython.

        @return a YMicroPython object allowing you to drive the MicroPython interpreter.
        """
        obj: Union[YMicroPython, None]
        obj = YFunction._FindFromCacheInContext(yctx, "MicroPython", func)
        if obj is None:
            obj = YMicroPython(yctx, func)
            YFunction._AddToCache("MicroPython", func, obj)
        return obj

    if not _IS_MICROPYTHON:
        async def registerValueCallback(self, callback: YMicroPythonValueCallback) -> int:
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

    async def eval(self, codeName: str, mpyCode: str) -> int:
        """
        Submit MicroPython code for execution in the interpreter.
        If the MicroPython interpreter is busy, this function will
        block until it becomes available. The code is then uploaded,
        compiled and executed on the fly, without beeing stored on the device filesystem.

        There is no implicit reset of the MicroPython interpreter with
        this function. Use method reset() if you need to start
        from a fresh environment to run your code.

        Note that although MicroPython is mostly compatible with recent Python 3.x
        interpreters, the limited ressources on the device impose some restrictions,
        in particular regarding the libraries that can be used. Please refer to
        the documentation for more details.

        @param codeName : name of the code file (used for error reporting only)
        @param mpyCode : MicroPython code to compile and execute

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        fullname: str
        res: int
        fullname = "mpy:%s" % codeName
        res = await self._upload(fullname, xbytearray(mpyCode, 'latin-1'))
        return res

    async def reset(self) -> int:
        """
        Stops current execution, and reset the MicroPython interpreter to initial state.
        All global variables are cleared, and all imports are forgotten.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        res: int
        state: str

        res = await self.set_command("Z")
        if not (res == YAPI.SUCCESS):
            self._throw(YAPI.IO_ERROR, "unable to trigger MicroPython reset")
            return YAPI.IO_ERROR
        # Wait until the reset is effective
        state = (await self.get_advertisedValue())[0: 0 + 1]
        while not (state == "z"):
            await YAPI.Sleep(50)
            state = (await self.get_advertisedValue())[0: 0 + 1]
        return YAPI.SUCCESS

    async def clearLogs(self) -> int:
        """
        Clears MicroPython interpreter console log buffer.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        res: int

        res = await self.set_command("z")
        return res

    async def get_lastLogs(self) -> str:
        """
        Returns a string with last logs of the MicroPython interpreter.
        This method return only logs that are still in the module.

        @return a string with last MicroPython logs.
                On failure, throws an exception or returns  YAPI.INVALID_STRING.
        """
        buff: xarray
        bufflen: int
        res: str

        buff = await self._download("mpy.txt")
        bufflen = len(buff) - 1
        while (bufflen > 0) and(buff[bufflen] != 64):
            bufflen = bufflen - 1
        res = (buff.decode('latin-1'))[0: 0 + bufflen]
        return res

    async def registerLogCallback(self, callback: YMicroPythonLogCallback) -> int:
        """
        Registers a device log callback function. This callback will be called each time
        microPython sends a new log message.

        @param callback : the callback function to invoke, or a None pointer.
                The callback function should take two arguments:
                the module object that emitted the log message,
                and the character string containing the log.
                On failure, throws an exception or returns a negative error code.
        """
        serial: str

        serial = await self.get_serialNumber()
        if serial == YAPI.INVALID_STRING:
            return YAPI.DEVICE_NOT_FOUND
        self._logCallback = callback
        self._isFirstCb = True
        if callback:
            await self.registerValueCallback(yInternalEventCallback)
        else:
            await self.registerValueCallback(None)
        return 0

    def get_logCallback(self) -> YMicroPythonLogCallback:
        return self._logCallback

    async def _internalEventHandler(self, cbVal: str) -> int:
        cbPos: int
        cbDPos: int
        url: str
        content: xarray
        endPos: int
        contentStr: str
        msgArr: list[str] = []
        arrLen: int
        lenStr: str
        arrPos: int
        logMsg: str
        # detect possible power cycle of the reader to clear event pointer
        cbPos = int(cbVal[1: 1 + len(cbVal)-1], 16)
        cbDPos = ((cbPos - self._prevCbPos) & 0xfffff)
        self._prevCbPos = cbPos
        if cbDPos > 65536:
            self._logPos = 0
        if not (self._logCallback):
            return YAPI.SUCCESS
        if self._isFirstCb:
            # use first emulated value callback caused by registerValueCallback:
            # to retrieve current logs position
            self._logPos = 0
            self._prevPartialLog = ""
            url = "mpy.txt"
        else:
            # load all messages since previous call
            url = "mpy.txt?pos=%d" % self._logPos

        content = await self._download(url)
        contentStr = content.decode('latin-1')
        # look for new position indicator at end of logs
        endPos = len(content) - 1
        while (endPos >= 0) and(content[endPos] != 64):
            endPos = endPos - 1
        if not (endPos > 0):
            self._throw(YAPI.IO_ERROR, "fail to download micropython logs")
            return YAPI.IO_ERROR
        lenStr = contentStr[endPos+1: endPos+1 + len(contentStr)-(endPos+1)]
        # update processed event position pointer
        self._logPos = YAPI._atoi(lenStr)
        if self._isFirstCb:
            # don't generate callbacks log messages before call to registerLogCallback
            self._isFirstCb = False
            return YAPI.SUCCESS
        # now generate callbacks for each complete log line
        endPos = endPos - 1
        if not (content[endPos] == 10):
            self._throw(YAPI.IO_ERROR, "fail to download micropython logs")
            return YAPI.IO_ERROR
        contentStr = contentStr[0: 0 + endPos]
        msgArr = (contentStr).split('\n')
        arrLen = len(msgArr) - 1
        if arrLen > 0:
            logMsg = "%s%s" % (self._prevPartialLog, msgArr[0])
            if self._logCallback:
                try:
                    retval = self._logCallback(self, logMsg)
                    if retval is not None: await retval
                # noinspection PyBroadException
                except Exception as e:
                    print('Exception in %s.logCallback:' % type(self).__name__, type(e).__name__, e)
            self._prevPartialLog = ""
            arrPos = 1
            while arrPos < arrLen:
                logMsg = msgArr[arrPos]
                if self._logCallback:
                    try:
                        retval = self._logCallback(self, logMsg)
                        if retval is not None: await retval
                    # noinspection PyBroadException
                    except Exception as e:
                        print('Exception in %s.logCallback:' % type(self).__name__, type(e).__name__, e)
                arrPos = arrPos + 1
        self._prevPartialLog = "%s%s" % (self._prevPartialLog, msgArr[arrLen])
        return YAPI.SUCCESS

    # --- (end of YMicroPython implementation)

