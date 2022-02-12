from collections.abc import Generator
from contextlib import contextmanager
import xbmc  # type: ignore
import xbmcaddon  # type: ignore
import xbmcgui  # type: ignore
import xbmcplugin  # type: ignore
from .bluetoothctl import Bluetoothctl
from .endpoints import Endpoints
from .logging import loginfo


@contextmanager
def busy_dialog() -> Generator[None, None, None]:
    """
    Display a busy dialog box
    """
    xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
    try:
        yield
    finally:
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')


def main(base_url: str, addon_handle: str, args: dict[str, str]):
    # Create endpoint generating object
    endpoints = Endpoints(base_url)

    # Create bluetoothctl object
    bt = Bluetoothctl()

    # Get addon name
    addon = xbmcaddon.Addon()
    addon_name = addon.getAddonInfo('name')

    # Get 'mode' argument, default to None
    mode = args.get('mode', None)

    if mode is None:
        # Initial endpoint
        mode_entry(endpoints, addon_handle)
        return
    elif mode[0] == 'available_devices':
        # Available devices endpoint
        mode_available_devices(bt, endpoints, addon_handle)
    elif mode[0] == 'paired_devices':
        # Paired devices endpoint
        mode_paired_devices(bt, endpoints, addon_handle)

    if mode[0] in ['connect', 'disconnect', 'pair', 'remove']:
        device = args['device'][0]
        address = args['address'][0]

        if mode[0] == 'connect':
            # Connect endpoint
            mode_connect(bt, device, address, addon_name)
        elif mode[0] == 'disconnect':
            # Disconnect endpoint
            mode_disconnect(bt, device, address, addon_name)
        elif mode[0] == 'pair':
            # Pair endpoint
            mode_pair(bt, args, addon_name)
        elif mode[0] == 'remove':
            # Remove endpoint
            mode_remove(bt, args, addon_name)


def mode_entry(endpoints, addon_handle):
    """Initial endpoint"""
    url = endpoints.build_url({'mode': 'available_devices'})
    li = xbmcgui.ListItem('Available Devices')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    url = endpoints.build_url({'mode': 'paired_devices'})
    li = xbmcgui.ListItem('Paired Devices')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)


def mode_available_devices(bt, endpoints, addon_handle):
    with busy_dialog():
        bt.scan()
        devices = bt.get_devices()

    for device, address in devices.items():
        loginfo(f'listing device {device}')
        li = xbmcgui.ListItem(device)
        li.addContextMenuItems([
            ('Pair',
             f'RunPlugin({endpoints.build_url_pair(device, address)})'),
            ('Connect',
             f'RunPlugin({endpoints.build_url_connect(device, address)})'),
            ('Disconnect',
             f'RunPlugin({endpoints.build_url_disconnect(device, address)})')
        ])
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=endpoints.build_url_pair(device, address),
            listitem=li
        )

    xbmcplugin.endOfDirectory(addon_handle)


def mode_paired_devices(bt, endpoints, addon_handle):
    with busy_dialog():
        devices = bt.get_paired_devices()

    for device, address in devices.items():
        loginfo(f'listing device {device}')
        li = xbmcgui.ListItem(device)
        li.addContextMenuItems([
            ('Connect',
             f'RunPlugin({endpoints.build_url_connect(device, address)})'),
            ('Disconnect',
             f'RunPlugin({endpoints.build_url_disconnect(device, address)})'),
            ('Un-pair',
             f'RunPlugin({endpoints.build_url_remove(device, address)})')
        ])
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=endpoints.build_url_connect(device, address),
            listitem=li
        )

    xbmcplugin.endOfDirectory(addon_handle)


def mode_connect(bt, device, address, addon_name):

    loginfo(f'attempting connection to {device} {address}')
    message = bt.connect(address)

    xbmc.executebuiltin(f'Notification({addon_name}, {message})')


def mode_disconnect(bt, device, address, addon_name):
    loginfo(f'attempting to disconnect from {device} {address}')
    message = bt.disconnect(address)

    xbmc.executebuiltin(f'Notification({addon_name}, {message})')


def mode_pair(bt, device, address, addon_name):
    loginfo(f'attempting to pair with {device} {address}')
    message = bt.pair(address)

    xbmc.executebuiltin(f'Notification({addon_name}, {message})')


def mode_remove(bt, device, address, addon_name):
    loginfo(f'attempting to remove {device} {address}')
    message = bt.remove(address)

    xbmc.executebuiltin(f'Notification({addon_name}, {message})')
