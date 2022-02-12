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

    addon = xbmcaddon.Addon()
    addon_name = addon.getAddonInfo('name')

    # Get 'mode' argument, default to None
    mode = args.get('mode', None)

    if mode is None:
        # Initial entry point
        url = endpoints.build_url({'mode': 'available_devices'})
        li = xbmcgui.ListItem('Available Devices')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)

        url = endpoints.build_url({'mode': 'paired_devices'})
        li = xbmcgui.ListItem('Paired Devices')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)

        xbmcplugin.endOfDirectory(addon_handle)

    elif mode[0] == 'available_devices':
        # Available devices entry point
        bt = Bluetoothctl()
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

    elif mode[0] == 'paired_devices':
        # Paired devices entry point
        bt = Bluetoothctl()
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

    elif mode[0] == 'connect':
        # Connect entry point
        bt = Bluetoothctl()

        device = args['device'][0]
        address = args['address'][0]

        loginfo(f'attempting connection to {device} {address}')
        message = bt.connect(address)

        xbmc.executebuiltin(f'Notification({addon_name}, {message})')

    elif mode[0] == 'disconnect':
        # Disconnect entry point
        bt = Bluetoothctl()

        device = args['device'][0]
        address = args['address'][0]

        loginfo(f'attempting to disconnect from {device} {address}')
        message = bt.disconnect(address)

        xbmc.executebuiltin(f'Notification({addon_name}, {message})')

    elif mode[0] == 'pair':
        # Pair entry point
        bt = Bluetoothctl()

        device = args['device'][0]
        address = args['address'][0]

        loginfo(f'attempting to pair with {device} {address}')
        message = bt.pair(address)

        xbmc.executebuiltin(f'Notification({addon_name}, {message})')

    elif mode[0] == 'remove':
        # Remove entry point
        bt = Bluetoothctl()

        device = args['device'][0]
        address = args['address'][0]

        loginfo(f'attempting to remove {device} {address}')
        message = bt.remove(address)

        xbmc.executebuiltin(f'Notification({addon_name}, {message})')
