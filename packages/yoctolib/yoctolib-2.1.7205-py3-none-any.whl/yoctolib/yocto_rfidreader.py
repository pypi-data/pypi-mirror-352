# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_rfidreader.py 66774 2025-05-20 10:15:17Z seb $
#
#  Implements the asyncio YRfidReader API for RfidReader functions
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
Yoctopuce library: High-level API for YRfidReader
version: PATCH_WITH_VERSION
requires: yocto_api
requires: yocto_rfidreader_aio
"""
from __future__ import annotations
import sys

# On MicroPython, code below will be wiped out at compile time
if sys.implementation.name != "micropython":
    # In CPython, enable edit-time type checking, including Final declaration
    from typing import Any, Union, Final
    from collections.abc import Callable, Awaitable
    from .yocto_api import const, _IS_MICROPYTHON, _DYNAMIC_HELPERS
else:
    # In our micropython VM, common generic types are global built-ins
    # Others such as TypeVar should be avoided when using micropython,
    # as they produce overhead in runtime code
    # Final is translated into const() expressions before compilation
    _IS_MICROPYTHON: Final[bool] = True
    _DYNAMIC_HELPERS: Final[bool] = True

from .yocto_rfidreader_aio import (
    YRfidReader as YYRfidReader_aio,
    YRfidTagInfo, YRfidOptions, YRfidStatus
)
from .yocto_api import (
    YAPIContext, YAPI, YFunction
)

def yInternalEventCallback(obj, value):
    obj._internalEventHandler(value)


# --- (generated code: YRfidReader class start)
if not _IS_MICROPYTHON:
    # For CPython, use strongly typed callback types
    try:
        YRfidReaderValueCallback = Union[Callable[['YRfidReader', str], Any], None]
        YEventCallback = Union[Callable[['YRfidReader', float, str, str], Any], None]
    except TypeError:
        YRfidReaderValueCallback = Union[Callable, Awaitable]
        YEventCallback = Union[Callable, Awaitable]

# noinspection PyProtectedMember
class YRfidReader(YFunction):
    """
    The YRfidReader class allows you to detect RFID tags, as well as
    read and write on these tags if the security settings allow it.

    Short reminder:

    - A tag's memory is generally organized in fixed-size blocks.
    - At tag level, each block must be read and written in its entirety.
    - Some blocks are special configuration blocks, and may alter the tag's behavior
    if they are rewritten with arbitrary data.
    - Data blocks can be set to read-only mode, but on many tags, this operation is irreversible.


    By default, the RfidReader class automatically manages these blocks so that
    arbitrary size data  can be manipulated of  without risk and without knowledge of
    tag architecture.

    """
    _aio: YRfidReader_aio
    # --- (end of generated code: YRfidReader class start)
    if not _IS_MICROPYTHON:
        # --- (generated code: YRfidReader return codes)
        NTAGS_INVALID: Final[int] = YAPI.INVALID_UINT
        REFRESHRATE_INVALID: Final[int] = YAPI.INVALID_UINT
        # --- (end of generated code: YRfidReader return codes)

    # --- (generated code: YRfidReader attributes declaration)
    _nTags: int
    _refreshRate: int
    _valueCallbackRfidReader: YRfidReaderValueCallback
    _eventCallback: YEventCallback
    _isFirstCb: bool
    _prevCbPos: int
    _eventPos: int
    _eventStamp: int
    # --- (end of generated code: YRfidReader attributes declaration)

    # --- (generated code: YRfidReader implementation)

    @classmethod
    def FirstRfidReader(cls) -> Union[YRfidReader, None]:
        """
        Starts the enumeration of RFID readers currently accessible.
        Use the method YRfidReader.nextRfidReader() to iterate on
        next RFID readers.

        @return a pointer to a YRfidReader object, corresponding to
                the first RFID reader currently online, or a None pointer
                if there are none.
        """
        return cls._proxy(cls, YRfidReader_aio.FirstRfidReader())

    @classmethod
    def FirstRfidReaderInContext(cls, yctx: YAPIContext) -> Union[YRfidReader, None]:
        """
        Starts the enumeration of RFID readers currently accessible.
        Use the method YRfidReader.nextRfidReader() to iterate on
        next RFID readers.

        @param yctx : a YAPI context.

        @return a pointer to a YRfidReader object, corresponding to
                the first RFID reader currently online, or a None pointer
                if there are none.
        """
        return cls._proxy(cls, YRfidReader_aio.FirstRfidReaderInContext(yctx))

    def nextRfidReader(self):
        """
        Continues the enumeration of RFID readers started using yFirstRfidReader().
        Caution: You can't make any assumption about the returned RFID readers order.
        If you want to find a specific a RFID reader, use RfidReader.findRfidReader()
        and a hardwareID or a logical name.

        @return a pointer to a YRfidReader object, corresponding to
                a RFID reader currently online, or a None pointer
                if there are no more RFID readers to enumerate.
        """
        return self._proxy(type(self), self._aio.nextRfidReader())

    if not _DYNAMIC_HELPERS:
        def get_nTags(self) -> int:
            """
            Returns the number of RFID tags currently detected.

            @return an integer corresponding to the number of RFID tags currently detected

            On failure, throws an exception or returns YRfidReader.NTAGS_INVALID.
            """
            return self._run(self._aio.get_nTags())

    if not _DYNAMIC_HELPERS:
        def get_refreshRate(self) -> int:
            """
            Returns the tag list refresh rate, measured in Hz.

            @return an integer corresponding to the tag list refresh rate, measured in Hz

            On failure, throws an exception or returns YRfidReader.REFRESHRATE_INVALID.
            """
            return self._run(self._aio.get_refreshRate())

    if not _DYNAMIC_HELPERS:
        def set_refreshRate(self, newval: int) -> int:
            """
            Changes the present tag list refresh rate, measured in Hz. The reader will do
            its best to respect it. Note that the reader cannot detect tag arrival or removal
            while it is  communicating with a tag.  Maximum frequency is limited to 100Hz,
            but in real life it will be difficult to do better than 50Hz.  A zero value
            will power off the device radio.
            Remember to call the saveToFlash() method of the module if the
            modification must be kept.

            @param newval : an integer corresponding to the present tag list refresh rate, measured in Hz

            @return YAPI.SUCCESS if the call succeeds.

            On failure, throws an exception or returns a negative error code.
            """
            return self._run(self._aio.set_refreshRate(newval))

    @classmethod
    def FindRfidReader(cls, func: str) -> YRfidReader:
        """
        Retrieves a RFID reader for a given identifier.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the RFID reader is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YRfidReader.isOnline() to test if the RFID reader is
        indeed online at a given time. In case of ambiguity when looking for
        a RFID reader by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the RFID reader, for instance
                MyDevice.rfidReader.

        @return a YRfidReader object allowing you to drive the RFID reader.
        """
        return cls._proxy(cls, YRfidReader_aio.FindRfidReader(func))

    @classmethod
    def FindRfidReaderInContext(cls, yctx: YAPIContext, func: str) -> YRfidReader:
        """
        Retrieves a RFID reader for a given identifier in a YAPI context.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the RFID reader is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YRfidReader.isOnline() to test if the RFID reader is
        indeed online at a given time. In case of ambiguity when looking for
        a RFID reader by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        @param yctx : a YAPI context
        @param func : a string that uniquely characterizes the RFID reader, for instance
                MyDevice.rfidReader.

        @return a YRfidReader object allowing you to drive the RFID reader.
        """
        return cls._proxy(cls, YRfidReader_aio.FindRfidReaderInContext(yctx, func))

    if not _IS_MICROPYTHON:
        def registerValueCallback(self, callback: YRfidReaderValueCallback) -> int:
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
            return super().registerValueCallback(callback)

    if not _DYNAMIC_HELPERS:
        def get_tagIdList(self) -> list[str]:
            """
            Returns the list of RFID tags currently detected by the reader.

            @return a list of strings, corresponding to each tag identifier (UID).

            On failure, throws an exception or returns an empty list.
            """
            return self._run(self._aio.get_tagIdList())

    def get_tagInfo(self, tagId: str, status: YRfidStatus) -> YRfidTagInfo:
        """
        Returns a description of the properties of an existing RFID tag.
        This function can cause communications with the tag.

        @param tagId : identifier of the tag to check
        @param status : an RfidStatus object that will contain
                the detailled status of the operation

        @return a YRfidTagInfo object.

        On failure, throws an exception or returns an empty YRfidTagInfo objact.
        When it happens, you can get more information from the status object.
        """
        return self._proxy(YRfidTagInfo, self._run(self._aio.get_tagInfo(tagId, status)))

    if not _DYNAMIC_HELPERS:
        def tagLockBlocks(self, tagId: str, firstBlock: int, nBlocks: int, options: YRfidOptions, status: YRfidStatus) -> int:
            """
            Changes an RFID tag configuration to prevents any further write to
            the selected blocks. This operation is definitive and irreversible.
            Depending on the tag type and block index, adjascent blocks may become
            read-only as well, based on the locking granularity.

            @param tagId : identifier of the tag to use
            @param firstBlock : first block to lock
            @param nBlocks : number of blocks to lock
            @param options : an YRfidOptions object with the optional
                    command execution parameters, such as security key
                    if required
            @param status : an RfidStatus object that will contain
                    the detailled status of the operation

            @return YAPI.SUCCESS if the call succeeds.

            On failure, throws an exception or returns a negative error code. When it
            happens, you can get more information from the status object.
            """
            return self._run(self._aio.tagLockBlocks(tagId, firstBlock, nBlocks, options, status))

    if not _DYNAMIC_HELPERS:
        def get_tagLockState(self, tagId: str, firstBlock: int, nBlocks: int, options: YRfidOptions, status: YRfidStatus) -> list[bool]:
            """
            Reads the locked state for RFID tag memory data blocks.
            FirstBlock cannot be a special block, and any special
            block encountered in the middle of the read operation will be
            skipped automatically.

            @param tagId : identifier of the tag to use
            @param firstBlock : number of the first block to check
            @param nBlocks : number of blocks to check
            @param options : an YRfidOptions object with the optional
                    command execution parameters, such as security key
                    if required
            @param status : an RfidStatus object that will contain
                    the detailled status of the operation

            @return a list of booleans with the lock state of selected blocks

            On failure, throws an exception or returns an empty list. When it
            happens, you can get more information from the status object.
            """
            return self._run(self._aio.get_tagLockState(tagId, firstBlock, nBlocks, options, status))

    if not _DYNAMIC_HELPERS:
        def get_tagSpecialBlocks(self, tagId: str, firstBlock: int, nBlocks: int, options: YRfidOptions, status: YRfidStatus) -> list[bool]:
            """
            Tells which block of a RFID tag memory are special and cannot be used
            to store user data. Mistakely writing a special block can lead to
            an irreversible alteration of the tag.

            @param tagId : identifier of the tag to use
            @param firstBlock : number of the first block to check
            @param nBlocks : number of blocks to check
            @param options : an YRfidOptions object with the optional
                    command execution parameters, such as security key
                    if required
            @param status : an RfidStatus object that will contain
                    the detailled status of the operation

            @return a list of booleans with the lock state of selected blocks

            On failure, throws an exception or returns an empty list. When it
            happens, you can get more information from the status object.
            """
            return self._run(self._aio.get_tagSpecialBlocks(tagId, firstBlock, nBlocks, options, status))

    if not _DYNAMIC_HELPERS:
        def tagReadHex(self, tagId: str, firstBlock: int, nBytes: int, options: YRfidOptions, status: YRfidStatus) -> str:
            """
            Reads data from an RFID tag memory, as an hexadecimal string.
            The read operation may span accross multiple blocks if the requested
            number of bytes is larger than the RFID tag block size. By default
            firstBlock cannot be a special block, and any special block encountered
            in the middle of the read operation will be skipped automatically.
            If you rather want to read special blocks, use the EnableRawAccess
            field from the options parameter.

            @param tagId : identifier of the tag to use
            @param firstBlock : block number where read should start
            @param nBytes : total number of bytes to read
            @param options : an YRfidOptions object with the optional
                    command execution parameters, such as security key
                    if required
            @param status : an RfidStatus object that will contain
                    the detailled status of the operation

            @return an hexadecimal string if the call succeeds.

            On failure, throws an exception or returns an empty binary buffer. When it
            happens, you can get more information from the status object.
            """
            return self._run(self._aio.tagReadHex(tagId, firstBlock, nBytes, options, status))

    if not _DYNAMIC_HELPERS:
        def tagReadBin(self, tagId: str, firstBlock: int, nBytes: int, options: YRfidOptions, status: YRfidStatus) -> xarray:
            """
            Reads data from an RFID tag memory, as a binary buffer. The read operation
            may span accross multiple blocks if the requested number of bytes
            is larger than the RFID tag block size.  By default
            firstBlock cannot be a special block, and any special block encountered
            in the middle of the read operation will be skipped automatically.
            If you rather want to read special blocks, use the EnableRawAccess
            field frrm the options parameter.

            @param tagId : identifier of the tag to use
            @param firstBlock : block number where read should start
            @param nBytes : total number of bytes to read
            @param options : an YRfidOptions object with the optional
                    command execution parameters, such as security key
                    if required
            @param status : an RfidStatus object that will contain
                    the detailled status of the operation

            @return a binary object with the data read if the call succeeds.

            On failure, throws an exception or returns an empty binary buffer. When it
            happens, you can get more information from the status object.
            """
            return self._run(self._aio.tagReadBin(tagId, firstBlock, nBytes, options, status))

    if not _DYNAMIC_HELPERS:
        def tagReadArray(self, tagId: str, firstBlock: int, nBytes: int, options: YRfidOptions, status: YRfidStatus) -> list[int]:
            """
            Reads data from an RFID tag memory, as a byte list. The read operation
            may span accross multiple blocks if the requested number of bytes
            is larger than the RFID tag block size.  By default
            firstBlock cannot be a special block, and any special block encountered
            in the middle of the read operation will be skipped automatically.
            If you rather want to read special blocks, use the EnableRawAccess
            field from the options parameter.

            @param tagId : identifier of the tag to use
            @param firstBlock : block number where read should start
            @param nBytes : total number of bytes to read
            @param options : an YRfidOptions object with the optional
                    command execution parameters, such as security key
                    if required
            @param status : an RfidStatus object that will contain
                    the detailled status of the operation

            @return a byte list with the data read if the call succeeds.

            On failure, throws an exception or returns an empty list. When it
            happens, you can get more information from the status object.
            """
            return self._run(self._aio.tagReadArray(tagId, firstBlock, nBytes, options, status))

    if not _DYNAMIC_HELPERS:
        def tagReadStr(self, tagId: str, firstBlock: int, nChars: int, options: YRfidOptions, status: YRfidStatus) -> str:
            """
            Reads data from an RFID tag memory, as a text string. The read operation
            may span accross multiple blocks if the requested number of bytes
            is larger than the RFID tag block size.  By default
            firstBlock cannot be a special block, and any special block encountered
            in the middle of the read operation will be skipped automatically.
            If you rather want to read special blocks, use the EnableRawAccess
            field from the options parameter.

            @param tagId : identifier of the tag to use
            @param firstBlock : block number where read should start
            @param nChars : total number of characters to read
            @param options : an YRfidOptions object with the optional
                    command execution parameters, such as security key
                    if required
            @param status : an RfidStatus object that will contain
                    the detailled status of the operation

            @return a text string with the data read if the call succeeds.

            On failure, throws an exception or returns an empty string. When it
            happens, you can get more information from the status object.
            """
            return self._run(self._aio.tagReadStr(tagId, firstBlock, nChars, options, status))

    if not _DYNAMIC_HELPERS:
        def tagWriteBin(self, tagId: str, firstBlock: int, buff: xarray, options: YRfidOptions, status: YRfidStatus) -> int:
            """
            Writes data provided as a binary buffer to an RFID tag memory.
            The write operation may span accross multiple blocks if the
            number of bytes to write is larger than the RFID tag block size.
            By default firstBlock cannot be a special block, and any special block
            encountered in the middle of the write operation will be skipped
            automatically. The last data block affected by the operation will
            be automatically padded with zeros if neccessary.  If you rather want
            to rewrite special blocks as well,
            use the EnableRawAccess field from the options parameter.

            @param tagId : identifier of the tag to use
            @param firstBlock : block number where write should start
            @param buff : the binary buffer to write
            @param options : an YRfidOptions object with the optional
                    command execution parameters, such as security key
                    if required
            @param status : an RfidStatus object that will contain
                    the detailled status of the operation

            @return YAPI.SUCCESS if the call succeeds.

            On failure, throws an exception or returns a negative error code. When it
            happens, you can get more information from the status object.
            """
            return self._run(self._aio.tagWriteBin(tagId, firstBlock, buff, options, status))

    if not _DYNAMIC_HELPERS:
        def tagWriteArray(self, tagId: str, firstBlock: int, byteList: list[int], options: YRfidOptions, status: YRfidStatus) -> int:
            """
            Writes data provided as a list of bytes to an RFID tag memory.
            The write operation may span accross multiple blocks if the
            number of bytes to write is larger than the RFID tag block size.
            By default firstBlock cannot be a special block, and any special block
            encountered in the middle of the write operation will be skipped
            automatically. The last data block affected by the operation will
            be automatically padded with zeros if neccessary.
            If you rather want to rewrite special blocks as well,
            use the EnableRawAccess field from the options parameter.

            @param tagId : identifier of the tag to use
            @param firstBlock : block number where write should start
            @param byteList : a list of byte to write
            @param options : an YRfidOptions object with the optional
                    command execution parameters, such as security key
                    if required
            @param status : an RfidStatus object that will contain
                    the detailled status of the operation

            @return YAPI.SUCCESS if the call succeeds.

            On failure, throws an exception or returns a negative error code. When it
            happens, you can get more information from the status object.
            """
            return self._run(self._aio.tagWriteArray(tagId, firstBlock, byteList, options, status))

    if not _DYNAMIC_HELPERS:
        def tagWriteHex(self, tagId: str, firstBlock: int, hexString: str, options: YRfidOptions, status: YRfidStatus) -> int:
            """
            Writes data provided as an hexadecimal string to an RFID tag memory.
            The write operation may span accross multiple blocks if the
            number of bytes to write is larger than the RFID tag block size.
            By default firstBlock cannot be a special block, and any special block
            encountered in the middle of the write operation will be skipped
            automatically. The last data block affected by the operation will
            be automatically padded with zeros if neccessary.
            If you rather want to rewrite special blocks as well,
            use the EnableRawAccess field from the options parameter.

            @param tagId : identifier of the tag to use
            @param firstBlock : block number where write should start
            @param hexString : a string of hexadecimal byte codes to write
            @param options : an YRfidOptions object with the optional
                    command execution parameters, such as security key
                    if required
            @param status : an RfidStatus object that will contain
                    the detailled status of the operation

            @return YAPI.SUCCESS if the call succeeds.

            On failure, throws an exception or returns a negative error code. When it
            happens, you can get more information from the status object.
            """
            return self._run(self._aio.tagWriteHex(tagId, firstBlock, hexString, options, status))

    if not _DYNAMIC_HELPERS:
        def tagWriteStr(self, tagId: str, firstBlock: int, text: str, options: YRfidOptions, status: YRfidStatus) -> int:
            """
            Writes data provided as an ASCII string to an RFID tag memory.
            The write operation may span accross multiple blocks if the
            number of bytes to write is larger than the RFID tag block size.
            Note that only the characters present in the provided string
            will be written, there is no notion of string length. If your
            string data have variable length, you'll have to encode the
            string length yourself, with a terminal zero for instannce.

            This function only works with ISO-latin characters, if you wish to
            write strings encoded with alternate character sets, you'll have to
            use tagWriteBin() function.

            By default firstBlock cannot be a special block, and any special block
            encountered in the middle of the write operation will be skipped
            automatically. The last data block affected by the operation will
            be automatically padded with zeros if neccessary.
            If you rather want to rewrite special blocks as well,
            use the EnableRawAccess field from the options parameter
            (definitely not recommanded).

            @param tagId : identifier of the tag to use
            @param firstBlock : block number where write should start
            @param text : the text string to write
            @param options : an YRfidOptions object with the optional
                    command execution parameters, such as security key
                    if required
            @param status : an RfidStatus object that will contain
                    the detailled status of the operation

            @return YAPI.SUCCESS if the call succeeds.

            On failure, throws an exception or returns a negative error code. When it
            happens, you can get more information from the status object.
            """
            return self._run(self._aio.tagWriteStr(tagId, firstBlock, text, options, status))

    if not _DYNAMIC_HELPERS:
        def tagGetAFI(self, tagId: str, options: YRfidOptions, status: YRfidStatus) -> int:
            """
            Reads an RFID tag AFI byte (ISO 15693 only).

            @param tagId : identifier of the tag to use
            @param options : an YRfidOptions object with the optional
                    command execution parameters, such as security key
                    if required
            @param status : an RfidStatus object that will contain
                    the detailled status of the operation

            @return the AFI value (0...255)

            On failure, throws an exception or returns a negative error code. When it
            happens, you can get more information from the status object.
            """
            return self._run(self._aio.tagGetAFI(tagId, options, status))

    if not _DYNAMIC_HELPERS:
        def tagSetAFI(self, tagId: str, afi: int, options: YRfidOptions, status: YRfidStatus) -> int:
            """
            Changes an RFID tag AFI byte (ISO 15693 only).

            @param tagId : identifier of the tag to use
            @param afi : the AFI value to write (0...255)
            @param options : an YRfidOptions object with the optional
                    command execution parameters, such as security key
                    if required
            @param status : an RfidStatus object that will contain
                    the detailled status of the operation

            @return YAPI.SUCCESS if the call succeeds.

            On failure, throws an exception or returns a negative error code. When it
            happens, you can get more information from the status object.
            """
            return self._run(self._aio.tagSetAFI(tagId, afi, options, status))

    if not _DYNAMIC_HELPERS:
        def tagLockAFI(self, tagId: str, options: YRfidOptions, status: YRfidStatus) -> int:
            """
            Locks the RFID tag AFI byte (ISO 15693 only).
            This operation is definitive and irreversible.

            @param tagId : identifier of the tag to use
            @param options : an YRfidOptions object with the optional
                    command execution parameters, such as security key
                    if required
            @param status : an RfidStatus object that will contain
                    the detailled status of the operation

            @return YAPI.SUCCESS if the call succeeds.

            On failure, throws an exception or returns a negative error code. When it
            happens, you can get more information from the status object.
            """
            return self._run(self._aio.tagLockAFI(tagId, options, status))

    if not _DYNAMIC_HELPERS:
        def tagGetDSFID(self, tagId: str, options: YRfidOptions, status: YRfidStatus) -> int:
            """
            Reads an RFID tag DSFID byte (ISO 15693 only).

            @param tagId : identifier of the tag to use
            @param options : an YRfidOptions object with the optional
                    command execution parameters, such as security key
                    if required
            @param status : an RfidStatus object that will contain
                    the detailled status of the operation

            @return the DSFID value (0...255)

            On failure, throws an exception or returns a negative error code. When it
            happens, you can get more information from the status object.
            """
            return self._run(self._aio.tagGetDSFID(tagId, options, status))

    if not _DYNAMIC_HELPERS:
        def tagSetDSFID(self, tagId: str, dsfid: int, options: YRfidOptions, status: YRfidStatus) -> int:
            """
            Changes an RFID tag DSFID byte (ISO 15693 only).

            @param tagId : identifier of the tag to use
            @param dsfid : the DSFID value to write (0...255)
            @param options : an YRfidOptions object with the optional
                    command execution parameters, such as security key
                    if required
            @param status : an RfidStatus object that will contain
                    the detailled status of the operation

            @return YAPI.SUCCESS if the call succeeds.

            On failure, throws an exception or returns a negative error code. When it
            happens, you can get more information from the status object.
            """
            return self._run(self._aio.tagSetDSFID(tagId, dsfid, options, status))

    if not _DYNAMIC_HELPERS:
        def tagLockDSFID(self, tagId: str, options: YRfidOptions, status: YRfidStatus) -> int:
            """
            Locks the RFID tag DSFID byte (ISO 15693 only).
            This operation is definitive and irreversible.

            @param tagId : identifier of the tag to use
            @param options : an YRfidOptions object with the optional
                    command execution parameters, such as security key
                    if required
            @param status : an RfidStatus object that will contain
                    the detailled status of the operation

            @return YAPI.SUCCESS if the call succeeds.

            On failure, throws an exception or returns a negative error code. When it
            happens, you can get more information from the status object.
            """
            return self._run(self._aio.tagLockDSFID(tagId, options, status))

    if not _DYNAMIC_HELPERS:
        def get_lastEvents(self) -> str:
            """
            Returns a string with last tag arrival/removal events observed.
            This method return only events that are still buffered in the device memory.

            @return a string with last events observed (one per line).

            On failure, throws an exception or returns  YAPI.INVALID_STRING.
            """
            return self._run(self._aio.get_lastEvents())

    def registerEventCallback(self, callback: YEventCallback) -> int:
        """
        Registers a callback function to be called each time that an RFID tag appears or
        disappears. The callback is invoked only during the execution of
        ySleep or yHandleEvents. This provides control over the time when
        the callback is triggered. For good responsiveness, remember to call one of these
        two functions periodically. To unregister a callback, pass a None pointer as argument.

        @param callback : the callback function to call, or a None pointer.
                The callback function should take four arguments:
                the YRfidReader object that emitted the event, the
                UTC timestamp of the event, a character string describing
                the type of event ("+" or "-") and a character string with the
                RFID tag identifier.
                On failure, throws an exception or returns a negative error code.
        """
        return self._run(self._aio.registerEventCallback(self._proxyCb(type(self), callback)))

    # --- (end of generated code: YRfidReader implementation)

