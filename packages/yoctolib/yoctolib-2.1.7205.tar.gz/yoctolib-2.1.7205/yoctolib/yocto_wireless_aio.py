# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_wireless_aio.py 66774 2025-05-20 10:15:17Z seb $
#
#  Implements the asyncio YWireless API for Wireless functions
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
Yoctopuce library: Asyncio implementation of YCellular
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
    from .yocto_api_aio import const, _IS_MICROPYTHON
else:
    # In our micropython VM, common generic types are global built-ins
    # Others such as TypeVar should be avoided when using micropython,
    # as they produce overhead in runtime code
    # Final is translated into const() expressions before compilation
    _IS_MICROPYTHON: Final[bool] = True # noqa

from .yocto_api_aio import (
    YAPIContext, YAPI, YAPI_Exception, YFunction, HwId, hwid2str, YModule
)

# --- (generated code: YWlanRecord class start)
# noinspection PyProtectedMember
class YWlanRecord:
    """
    YWlanRecord objects are used to describe a wireless network.
    These objects are  used in particular in conjunction with the
    YWireless class.

    """
    # --- (end of generated code: YWlanRecord class start)
    if not _IS_MICROPYTHON:
        # --- (generated code: YWlanRecord return codes)
        pass
        # --- (end of generated code: YWlanRecord return codes)
        pass

    # --- (generated code: YWlanRecord attributes declaration)
    _ssid: str
    _channel: int
    _sec: str
    _rssi: int
    # --- (end of generated code: YWlanRecord attributes declaration)

    def __init__(self, json_data: XStringIO):
        # --- (generated code: YWlanRecord constructor)
        self._ssid = ''
        self._channel = 0
        self._sec = ''
        self._rssi = 0
        # --- (end of generated code: YWlanRecord constructor)
        new_json: Any = json.load(json_data)
        self._ssid = new_json["ssid"]
        self._channel = new_json["channel"]
        self._sec = new_json["sec"]
        self._rssi = new_json["rssi"]

    # --- (generated code: YWlanRecord implementation)
    def get_ssid(self) -> str:
        """
        Returns the name of the wireless network (SSID).

        @return a string with the name of the wireless network (SSID).
        """
        return self._ssid

    def get_channel(self) -> int:
        """
        Returns the 802.11 b/g/n channel number used by this network.

        @return an integer corresponding to the channel.
        """
        return self._channel

    def get_security(self) -> str:
        """
        Returns the security algorithm used by the wireless network.
        If the network implements to security, the value is "OPEN".

        @return a string with the security algorithm.
        """
        return self._sec

    def get_linkQuality(self) -> int:
        """
        Returns the quality of the wireless network link, in per cents.

        @return an integer between 0 and 100 corresponding to the signal quality.
        """
        return self._rssi

    # --- (end of generated code: YWlanRecord implementation)


# --- (generated code: YWireless class start)
if not _IS_MICROPYTHON:
    # For CPython, use strongly typed callback types
    try:
        YWirelessValueCallback = Union[Callable[['YWireless', str], Any], None]
    except TypeError:
        YWirelessValueCallback = Union[Callable, Awaitable]

# noinspection PyProtectedMember
class YWireless(YFunction):
    """
    The YWireless class provides control over wireless network parameters
    and status for devices that are wireless-enabled.
    Note that TCP/IP parameters are configured separately, using class YNetwork.

    """
    # --- (end of generated code: YWireless class start)
    if not _IS_MICROPYTHON:
        # --- (generated code: YWireless return codes)
        LINKQUALITY_INVALID: Final[int] = YAPI.INVALID_UINT
        SSID_INVALID: Final[str] = YAPI.INVALID_STRING
        CHANNEL_INVALID: Final[int] = YAPI.INVALID_UINT
        MESSAGE_INVALID: Final[str] = YAPI.INVALID_STRING
        WLANCONFIG_INVALID: Final[str] = YAPI.INVALID_STRING
        SECURITY_UNKNOWN: Final[int] = 0
        SECURITY_OPEN: Final[int] = 1
        SECURITY_WEP: Final[int] = 2
        SECURITY_WPA: Final[int] = 3
        SECURITY_WPA2: Final[int] = 4
        SECURITY_INVALID: Final[int] = -1
        WLANSTATE_DOWN: Final[int] = 0
        WLANSTATE_SCANNING: Final[int] = 1
        WLANSTATE_CONNECTED: Final[int] = 2
        WLANSTATE_REJECTED: Final[int] = 3
        WLANSTATE_INVALID: Final[int] = -1
        # --- (end of generated code: YWireless return codes)

    # --- (generated code: YWireless attributes declaration)
    _linkQuality: int
    _ssid: str
    _channel: int
    _security: int
    _message: str
    _wlanConfig: str
    _wlanState: int
    _valueCallback: YWirelessValueCallback
    # --- (end of generated code: YWireless attributes declaration)

    def __init__(self, yctx: YAPIContext, func: str):
        super().__init__(yctx, func)
        self._className = 'Wireless'
        # --- (generated code: YWireless constructor)
        self._linkQuality = YWireless.LINKQUALITY_INVALID
        self._ssid = YWireless.SSID_INVALID
        self._channel = YWireless.CHANNEL_INVALID
        self._security = YWireless.SECURITY_INVALID
        self._message = YWireless.MESSAGE_INVALID
        self._wlanConfig = YWireless.WLANCONFIG_INVALID
        self._wlanState = YWireless.WLANSTATE_INVALID
        # --- (end of generated code: YWireless constructor)

    # --- (generated code: YWireless implementation)

    @staticmethod
    def FirstWireless() -> Union[YWireless, None]:
        """
        Starts the enumeration of wireless LAN interfaces currently accessible.
        Use the method YWireless.nextWireless() to iterate on
        next wireless LAN interfaces.

        @return a pointer to a YWireless object, corresponding to
                the first wireless LAN interface currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = YAPI._yHash.getFirstHardwareId('Wireless')
        if not next_hwid:
            return None
        return YWireless.FindWireless(hwid2str(next_hwid))

    @staticmethod
    def FirstWirelessInContext(yctx: YAPIContext) -> Union[YWireless, None]:
        """
        Starts the enumeration of wireless LAN interfaces currently accessible.
        Use the method YWireless.nextWireless() to iterate on
        next wireless LAN interfaces.

        @param yctx : a YAPI context.

        @return a pointer to a YWireless object, corresponding to
                the first wireless LAN interface currently online, or a None pointer
                if there are none.
        """
        next_hwid: Union[HwId, None] = yctx._yHash.getFirstHardwareId('Wireless')
        if not next_hwid:
            return None
        return YWireless.FindWirelessInContext(yctx, hwid2str(next_hwid))

    def nextWireless(self):
        """
        Continues the enumeration of wireless LAN interfaces started using yFirstWireless().
        Caution: You can't make any assumption about the returned wireless LAN interfaces order.
        If you want to find a specific a wireless LAN interface, use Wireless.findWireless()
        and a hardwareID or a logical name.

        @return a pointer to a YWireless object, corresponding to
                a wireless LAN interface currently online, or a None pointer
                if there are no more wireless LAN interfaces to enumerate.
        """
        next_hwid: Union[HwId, None] = None
        try:
            hwid: HwId = self._yapi._yHash.resolveHwID(self._className, self._func)
            next_hwid = self._yapi._yHash.getNextHardwareId(self._className, hwid)
        except YAPI_Exception:
            pass
        if not next_hwid:
            return None
        return YWireless.FindWirelessInContext(self._yapi, hwid2str(next_hwid))

    def _parseAttr(self, json_val: dict) -> None:
        if 'linkQuality' in json_val:
            self._linkQuality = json_val["linkQuality"]
        if 'ssid' in json_val:
            self._ssid = json_val["ssid"]
        if 'channel' in json_val:
            self._channel = json_val["channel"]
        if 'security' in json_val:
            self._security = json_val["security"]
        if 'message' in json_val:
            self._message = json_val["message"]
        if 'wlanConfig' in json_val:
            self._wlanConfig = json_val["wlanConfig"]
        if 'wlanState' in json_val:
            self._wlanState = json_val["wlanState"]
        super()._parseAttr(json_val)

    async def get_linkQuality(self) -> int:
        """
        Returns the link quality, expressed in percent.

        @return an integer corresponding to the link quality, expressed in percent

        On failure, throws an exception or returns YWireless.LINKQUALITY_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YWireless.LINKQUALITY_INVALID
        res = self._linkQuality
        return res

    async def get_ssid(self) -> str:
        """
        Returns the wireless network name (SSID).

        @return a string corresponding to the wireless network name (SSID)

        On failure, throws an exception or returns YWireless.SSID_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YWireless.SSID_INVALID
        res = self._ssid
        return res

    async def get_channel(self) -> int:
        """
        Returns the 802.11 channel currently used, or 0 when the selected network has not been found.

        @return an integer corresponding to the 802.11 channel currently used, or 0 when the selected
        network has not been found

        On failure, throws an exception or returns YWireless.CHANNEL_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YWireless.CHANNEL_INVALID
        res = self._channel
        return res

    async def get_security(self) -> int:
        """
        Returns the security algorithm used by the selected wireless network.

        @return a value among YWireless.SECURITY_UNKNOWN, YWireless.SECURITY_OPEN, YWireless.SECURITY_WEP,
        YWireless.SECURITY_WPA and YWireless.SECURITY_WPA2 corresponding to the security algorithm used by
        the selected wireless network

        On failure, throws an exception or returns YWireless.SECURITY_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YWireless.SECURITY_INVALID
        res = self._security
        return res

    async def get_message(self) -> str:
        """
        Returns the latest status message from the wireless interface.

        @return a string corresponding to the latest status message from the wireless interface

        On failure, throws an exception or returns YWireless.MESSAGE_INVALID.
        """
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YWireless.MESSAGE_INVALID
        res = self._message
        return res

    async def get_wlanConfig(self) -> str:
        res: str
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YWireless.WLANCONFIG_INVALID
        res = self._wlanConfig
        return res

    async def set_wlanConfig(self, newval: str) -> int:
        rest_val = newval
        return await self._setAttr("wlanConfig", rest_val)

    async def get_wlanState(self) -> int:
        """
        Returns the current state of the wireless interface. The state YWireless.WLANSTATE_DOWN means that
        the network interface is
        not connected to a network. The state YWireless.WLANSTATE_SCANNING means that the network interface
        is scanning available
        frequencies. During this stage, the device is not reachable, and the network settings are not yet
        applied. The state
        YWireless.WLANSTATE_CONNECTED means that the network settings have been successfully applied ant
        that the device is reachable
        from the wireless network. If the device is configured to use ad-hoc or Soft AP mode, it means that
        the wireless network
        is up and that other devices can join the network. The state YWireless.WLANSTATE_REJECTED means
        that the network interface has
        not been able to join the requested network. The description of the error can be obtain with the
        get_message() method.

        @return a value among YWireless.WLANSTATE_DOWN, YWireless.WLANSTATE_SCANNING,
        YWireless.WLANSTATE_CONNECTED and YWireless.WLANSTATE_REJECTED corresponding to the current state
        of the wireless interface

        On failure, throws an exception or returns YWireless.WLANSTATE_INVALID.
        """
        res: int
        if self._cacheExpiration <= YAPI.GetTickCount():
            if await self.load(self._yapi.GetCacheValidity()) != YAPI.SUCCESS:
                return YWireless.WLANSTATE_INVALID
        res = self._wlanState
        return res

    @staticmethod
    def FindWireless(func: str) -> YWireless:
        """
        Retrieves a wireless LAN interface for a given identifier.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the wireless LAN interface is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YWireless.isOnline() to test if the wireless LAN interface is
        indeed online at a given time. In case of ambiguity when looking for
        a wireless LAN interface by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the wireless LAN interface, for instance
                YHUBWLN1.wireless.

        @return a YWireless object allowing you to drive the wireless LAN interface.
        """
        obj: Union[YWireless, None]
        obj = YFunction._FindFromCache("Wireless", func)
        if obj is None:
            obj = YWireless(YAPI, func)
            YFunction._AddToCache("Wireless", func, obj)
        return obj

    @staticmethod
    def FindWirelessInContext(yctx: YAPIContext, func: str) -> YWireless:
        """
        Retrieves a wireless LAN interface for a given identifier in a YAPI context.
        The identifier can be specified using several formats:

        - FunctionLogicalName
        - ModuleSerialNumber.FunctionIdentifier
        - ModuleSerialNumber.FunctionLogicalName
        - ModuleLogicalName.FunctionIdentifier
        - ModuleLogicalName.FunctionLogicalName


        This function does not require that the wireless LAN interface is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YWireless.isOnline() to test if the wireless LAN interface is
        indeed online at a given time. In case of ambiguity when looking for
        a wireless LAN interface by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        @param yctx : a YAPI context
        @param func : a string that uniquely characterizes the wireless LAN interface, for instance
                YHUBWLN1.wireless.

        @return a YWireless object allowing you to drive the wireless LAN interface.
        """
        obj: Union[YWireless, None]
        obj = YFunction._FindFromCacheInContext(yctx, "Wireless", func)
        if obj is None:
            obj = YWireless(yctx, func)
            YFunction._AddToCache("Wireless", func, obj)
        return obj

    if not _IS_MICROPYTHON:
        async def registerValueCallback(self, callback: YWirelessValueCallback) -> int:
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

    async def startWlanScan(self) -> int:
        """
        Triggers a scan of the wireless frequency and builds the list of available networks.
        The scan forces a disconnection from the current network. At then end of the process, the
        the network interface attempts to reconnect to the previous network. During the scan, the wlanState
        switches to YWireless.WLANSTATE_DOWN, then to YWireless.WLANSTATE_SCANNING. When the scan is completed,
        get_wlanState() returns either YWireless.WLANSTATE_DOWN or YWireless.WLANSTATE_SCANNING. At this
        point, the list of detected network can be retrieved with the get_detectedWlans() method.

        On failure, throws an exception or returns a negative error code.
        """
        config: str
        config = await self.get_wlanConfig()
        # a full scan is triggered when a config is applied
        return await self.set_wlanConfig(config)

    async def joinNetwork(self, ssid: str, securityKey: str) -> int:
        """
        Changes the configuration of the wireless lan interface to connect to an existing
        access point (infrastructure mode).
        Remember to call the saveToFlash() method and then to reboot the module to apply this setting.

        @param ssid : the name of the network to connect to
        @param securityKey : the network key, as a character string

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return await self.set_wlanConfig("INFRA:%s\\%s" % (ssid, securityKey))

    async def adhocNetwork(self, ssid: str, securityKey: str) -> int:
        """
        Changes the configuration of the wireless lan interface to create an ad-hoc
        wireless network, without using an access point. On the YoctoHub-Wireless-g
        and YoctoHub-Wireless-n,
        you should use softAPNetwork() instead, which emulates an access point
        (Soft AP) which is more efficient and more widely supported than ad-hoc networks.

        When a security key is specified for an ad-hoc network, the network is protected
        by a WEP40 key (5 characters or 10 hexadecimal digits) or WEP128 key (13 characters
        or 26 hexadecimal digits). It is recommended to use a well-randomized WEP128 key
        using 26 hexadecimal digits to maximize security.
        Remember to call the saveToFlash() method and then to reboot the module
        to apply this setting.

        @param ssid : the name of the network to connect to
        @param securityKey : the network key, as a character string

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return await self.set_wlanConfig("ADHOC:%s\\%s" % (ssid, securityKey))

    async def softAPNetwork(self, ssid: str, securityKey: str) -> int:
        """
        Changes the configuration of the wireless lan interface to create a new wireless
        network by emulating a WiFi access point (Soft AP). This function can only be
        used with the YoctoHub-Wireless-g and the YoctoHub-Wireless-n.

        On the YoctoHub-Wireless-g, when a security key is specified for a SoftAP network,
        the network is protected by a WEP40 key (5 characters or 10 hexadecimal digits) or
        WEP128 key (13 characters or 26 hexadecimal digits). It is recommended to use a
        well-randomized WEP128 key using 26 hexadecimal digits to maximize security.

        On the YoctoHub-Wireless-n, when a security key is specified for a SoftAP network,
        the network will be protected by WPA2.

        Remember to call the saveToFlash() method and then to reboot the module to apply this setting.

        @param ssid : the name of the network to connect to
        @param securityKey : the network key, as a character string

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return await self.set_wlanConfig("SOFTAP:%s\\%s" % (ssid, securityKey))

    async def get_detectedWlans(self) -> list[YWlanRecord]:
        """
        Returns a list of YWlanRecord objects that describe detected Wireless networks.
        This list is not updated when the module is already connected to an access point (infrastructure mode).
        To force an update of this list, startWlanScan() must be called.
        Note that an languages without garbage collections, the returned list must be freed by the caller.

        @return a list of YWlanRecord objects, containing the SSID, channel,
                link quality and the type of security of the wireless network.

        On failure, throws an exception or returns an empty list.
        """
        json: xarray
        wlanlist: list[xarray] = []
        res: Union[list[YWlanRecord], None] = []

        json = await self._download("wlan.json?by=name")
        wlanlist = self._json_get_array(json)
        del res[:]
        for y in wlanlist:
            res.append(YWlanRecord(y.decode('latin-1')))
        return res

    # --- (end of generated code: YWireless implementation)
